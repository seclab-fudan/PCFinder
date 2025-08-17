/**
 * @name get all class and method
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

// class SourceToIfCondTracking extends DataFlow::Configuration {
class SourceToIfCondTracking extends TaintTracking::Configuration {
    SourceToIfCondTracking() { this = "SourceToIfCondTracking" }

    override predicate isSource(DataFlow::Node source) {
        not source.asExpr().getAChildExpr*() instanceof ThisAccess and
        (
            // source.asExpr() instanceof TrustedVarAccess or
            source.asExpr() instanceof TrustedMethodAccess
            // or
            // source.asParameter() instanceof TrustedParameter
        )
    }
    
    override predicate isSink(DataFlow::Node sink) {
        exists(SetterMethod setter | setter.getAReference().getAnArgument().getAChildExpr*() = sink.asExpr())
    }

    override predicate isAdditionalTaintStep(DataFlow::Node fromNode, DataFlow::Node toNode) {
        // Additional step for itranswarp's `CONTEXT_THREAD_LOCAL.get().user`;
        DFP::readStep(fromNode, any(DataFlow::FieldContent f | f.getField().getDeclaringType().hasQualifiedName("_", "_")), toNode)
        // for (Long num : nums)
        or exists(EnhancedForStmt for, SsaExplicitUpdate v |
            for.getExpr() = fromNode.asExpr() and
            v.getDefiningExpr() = for.getVariable() and
            v.getAUse() = toNode.asExpr()
        ) 
        or exists(MethodAccess call |
            call.getMethod().getName() = "valueOf" and
            call.getAChildExpr*() = fromNode.asExpr() and
            toNode.asExpr() = call
        )
    }

    override predicate isSanitizer(DataFlow::Node node) {
        sanitizer(node)
    }
}


from SourceToIfCondTracking sti, Node source, Node sink, Credentials cred, MethodAccess ma 
where
    sink.asExpr() = cred
    and
    sti.hasFlow(source, sink)
    and 
    ma.getAnArgument() = cred

select ma, ma.getQualifier().getType().getName()+"."+ma.getMethod().(SetterMethod).getField().getName()