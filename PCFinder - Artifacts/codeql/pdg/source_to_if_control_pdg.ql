/**
 * @name output if's user-control pdg
 * @id java/if-pdg
 * @kind problem
 * @problem.severity warning
 */

import java
import lib.taint

Expr getAllVars(Expr expr) {
    exists(VarAccess var | var = expr.getAChildExpr*() and not var.getParent() instanceof VarAccess | 
        result = var
    )
    or
    (
        expr instanceof ClassInstanceExpr and 
        result = expr.(ClassInstanceExpr).getTypeName()
    )
}

from DataFlow::Node source, DataFlow::Node sink, ControllableTracking ift, IfCond ifs, Expr cond, Expr var 
where
    cond = ifs.getAllConditionExprs() and
    var = getAllVars(cond) and
    sink.asExpr() = var and
    ift.hasFlow(source, sink)
select ifs, source.toString() + "<DOT>" + sink.toString()