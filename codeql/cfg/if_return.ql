/**
 * @name Methods in If Stmts
 * @id java/if-code
 * @kind problem
 */

import java
import lib.sensi
import lib.util


from IfCond ifcond, ReturnStmt returnstmt
where ifcond.inExtendedTrueBlock(returnstmt)
or exists(TryStmt try | 
    (try.getBlock() = returnstmt.getParent() or try.getACatchClause() = returnstmt.getParent()) 
    and ifcond.getThen() = try.getParent()
    )
select ifcond,  getIfResult(returnstmt)+"<SEP>"+
                getStrs(returnstmt)+"<SEP>"+
                getVars(returnstmt)+"<SEP>"+
                getMethods(returnstmt)+"<SEP>"+
                getConsts(returnstmt)
