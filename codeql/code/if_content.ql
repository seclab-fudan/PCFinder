/**
 * @name If block
 * @id java/if-code
 * @kind problem
 */

import java
import lib.sensi
import lib.taint

VarAccess getAllVars(Expr expr) {
    exists(VarAccess var | var = expr.getAChildExpr*() and not var.getParent() instanceof VarAccess |
        result = var
    )
}


string hasControllable(IfCond ifcond) {
    if exists(DataFlow::Node sink, ControllableTracking ift
            |
            sink.asExpr()= getAllVars(ifcond.getCondition()) and
            ift.hasFlow(_, sink)
        )
    then 
        result = "1"
    else
        result = "0"
}

Stmt getElseOrNull(IfStmt ifstmt){
    if exists(Stmt elseStmt | elseStmt = ifstmt.getElse() and (not elseStmt instanceof IfStmt))
    then
        result = ifstmt.getElse()
    else
        result = ifstmt.getThen()
}

from IfCond ifcond
select ifcond, ifcond.getThen().getLocation().getStartLine()+"<SEP>"+
       ifcond.getThen().getLocation().getStartColumn()+"<SEP>"+
       getElseOrNull(ifcond).getLocation().getEndLine()+"<SEP>"+
       getElseOrNull(ifcond).getLocation().getEndColumn()+"<SEP>"+
       getMethodName(ifcond)

