/**
 * @name if true sso
 * @id java/if-cfg
 * @kind problem
 * @problem.severity warning
 */

import java
import lib.taint

string getReceiverType(MethodAccess methodAccess) {
    if methodAccess.hasQualifier()
    then 
        result = methodAccess.getQualifier().getType().toString()+"."
    else
        result = ""
}

class ControllableSensitiveOperation extends MethodAccess {
    ControllableSensitiveOperation() {
        this.getCallee() instanceof SensitiveOperation
    }
}

// statement / expression version
MethodAccess ifTrueSSO(IfCond ifstmt) {
    exists(MethodAccess ma | 
        ifstmt.inExtendedTrueBlock(ma.getAnEnclosingStmt()) and 
        ma instanceof ControllableSensitiveOperation and
        result = ma
    )
}

from IfCond ifstmt, MethodAccess ma
where ma = ifTrueSSO(ifstmt)
select ifstmt, getReceiverType(ma)+ma.getMethod().getName()