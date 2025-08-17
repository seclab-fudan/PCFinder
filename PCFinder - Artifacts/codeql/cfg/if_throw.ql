/**
 * @name Methods in If Stmts
 * @id java/if-code
 * @kind problem
 */

import java
import lib.sensi
import lib.util

string getException(Stmt stmt) {
    if stmt instanceof ThrowStmt
    then result = "" + concat(ClassInstanceExpr expr 
        | 
        expr = stmt.(ThrowStmt).getExpr()
        |
        expr.getConstructor().getName(), "<DOT>"
    )
    else result = ""

}

class ExtendedThrowStmt extends Stmt {
    ExtendedThrowStmt(){
        this instanceof ThrowStmt 
        or exists(MethodAccess ma | ma.getEnclosingStmt() = this |
            (
                ma.getMethod().hasQualifiedName("org.springframework.ui", "ModelMap", "addAttribute") and
                exists(ReturnStmt returnstmt | this.getParent() = returnstmt.getParent())
            ) or (
                ma.getMethod().hasQualifiedName("com.macro.mall.common.exception", "Asserts", "fail")
            )
        )
    }
}

from IfCond ifcond, ExtendedThrowStmt throwstmt
where ifcond.inExtendedTrueBlock(throwstmt)
or exists(TryStmt try | 
    (try.getBlock() = throwstmt.getParent() or try.getACatchClause() = throwstmt.getParent()) 
    and ifcond.getThen() = try.getParent()
    )
select ifcond,  getIfResult(throwstmt)+"<SEP>"+
                getException(throwstmt)+"<SEP>"+
                getStrs(throwstmt)+"<SEP>"+
                getVars(throwstmt)+"<SEP>"+
                getMethods(throwstmt)+"<SEP>"+
                getConsts(throwstmt)

