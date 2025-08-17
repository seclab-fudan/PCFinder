/**
 * @name get all class and method
 * @id java/if-code
 * @kind problem
 */

import java
import lib.sensi

string getSuperClass(Class c) {
    result = concat(Class cc | cc = c.getASupertype() | 
                cc.getName(), "<DOT>"
            )
}

string getFields(Class c) {
    result = concat(Field f | f = c.getAField() | 
                concat(f.getAModifier().toString(), ":")+"<SEP>"+f.getType()+"<SEP>"+f.getName(), "<DOT>"
            )
}

string getMethods(Class c){
    result = concat(Method m | m = c.getAMethod() | 
                concat(m.getAModifier().toString(), ":")+"<SEP>"+m.getReturnType()+"<SEP>"+m.getName(), "<DOT>"
            )
}

string getInstanceName(Class c) {
    exists(LocalVariableDecl lv | lv.getType() = c | result = lv.getName())
}

string getParamName(Class c) {
    exists(Parameter p | p.getType() = c | result = p.toString())
}

string getInstances(Class c) {
    result = concat(getInstanceName(c), "<DOT>") + "<DOT>" + concat(getParamName(c), "<DOT>")
}

string getAllFieldAndMethod(Class c) {
    result = c.getName() + "<SPLIT>" + 
                getSuperClass(c) + "<SPLIT>" +
                getInstances(c) + "<SPLIT>" +
                getFields(c) + "<SPLIT>" +
                getMethods(c)
}

from Class c
where 
    not c instanceof AnonymousClass
select c, getAllFieldAndMethod(c)