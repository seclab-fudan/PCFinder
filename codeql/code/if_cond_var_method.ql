/**
 * @name Methods in if cond
 * @id java/if-code
 * @kind problem
 */

import java

import semmle.code.java.dataflow.DataFlow
import semmle.code.java.dataflow.TaintTracking
import lib.sensi
import lib.util
import lib.taint

string getVarType(Expr var) {
    if var instanceof VarAccess
    then
        if var.(VarAccess).hasQualifier()
        then
            result = var.(VarAccess).getQualifier().getType().toString()
        else
            result = var.(VarAccess).getType().toString()
    else
        result = var.getType().toString()
}

string getAllVars(Expr expr) {
    result = 
    concat(Expr var | 
        var = expr.getAChildExpr*()
        and (
            (var instanceof VarAccess and not var.getParent() instanceof VarAccess)
            or 
            var instanceof StringLiteral
            )
        |
        var.toString() + "<SPLIT>" + getVarType(var) + "<SPLIT>" + var.getLocation().toString(), "<DOT>"
    ) 
    // + "<DOT>" +
    // concat(StringLiteral str | 
    //     str = expr.getAChildExpr*()
    //     |
    //     str.getValue() + "<SPLIT>String<SPLIT>" + str.getLocation().toString(), "<DOT>"
    // )
}

string getGetterCall(Expr expr) {
    result = "" + concat(MethodAccess ma |
            ma = expr.getAChildExpr*() and ma.getMethod() instanceof GetterMethod
            |
            ma.getQualifier().getType()+"."+ma.getMethod().getName()+"."+ma.getMethod().(GetterMethod).getField(), "<DOT>"
        )
}

// string getFieldAccess

from IfCond ifcond, Expr expr
where expr = ifcond.getAllConditionExprs()

select ifcond, expr.getLocation() + "<SEP>" + getAllVars(expr) + "<SEP>" + getMethod(expr) + "<SEP>" + getGetterCall(expr)
