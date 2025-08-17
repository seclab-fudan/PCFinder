/**
 * @name Methods in If Stmts
 * @id java/if-code
 * @kind problem
 */

import java
import lib.sensi
import lib.util


from IfCond ifcond, RedirectStmt redirectstmt
where ifcond.inExtendedTrueBlock(redirectstmt)
or exists(TryStmt try | 
    (try.getBlock() = redirectstmt.getParent() or try.getACatchClause() = redirectstmt.getParent()) 
    and ifcond.getThen() = try.getParent()
    )
select ifcond,  getIfResult(redirectstmt)+"<SEP>"+
                getStrs(redirectstmt)+"<SEP>"+
                getVars(redirectstmt)+"<SEP>"+
                getMethods(redirectstmt)+"<SEP>"+
                getConsts(redirectstmt)

