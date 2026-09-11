# Managed Code Reverse Engineering (.NET / Java)

## .NET (C#) Decompilation

### Tools
```
dnSpy              # Full decompiler + debugger, allows editing/patching IL
ILSpy              # Decompiler, lighter weight
dotPeek            # JetBrains decompiler
```

### Basic Workflow
```
1. Open .exe/.dll in dnSpy
2. Navigate namespace tree to find Main/entry point
3. Right-click > Decompile to view C# source approximation
4. For obfuscated code, look for [Obfuscated] attributes or garbled names
```

### Patching with dnSpy
```
1. Right-click method > Edit Method (C#)
2. Modify logic (e.g., bypass license check)
3. Compile (Ctrl+Shift+F5) and save module
```

### .NET Obfuscation Recognition
```
ConfuserEx          # Common free obfuscator, string encryption + control flow
Dotfuscator          # Commercial obfuscator
Babel Obfuscator      # Another common one

# De4dot tool for automated deobfuscation of known obfuscators
de4dot ./obfuscated.exe
```

### Extracting Embedded Resources
```
dnSpy: Resources tab in module tree
Or: ILSpy > right-click resource > save
```

## Java Decompilation

### Tools
```
JD-GUI / JD-Core     # Quick decompiler, GUI
CFR                  # Better decompilation for modern Java (lambdas, etc)
Procyon              # Alternative decompiler
Bytecode Viewer       # Multi-decompiler comparison tool
jadx                  # Best for Android APK/DEX decompilation
```

### Basic Workflow
```bash
# Extract class files from JAR
unzip application.jar -d extracted/

# Decompile with CFR
java -jar cfr.jar extracted/com/example/Main.class

# Or use JD-GUI for interactive browsing
jd-gui application.jar
```

### Java Obfuscation Recognition
```
ProGuard              # Common Android/Java obfuscator - renames classes/methods
Allatori               # Commercial obfuscator with control flow obfuscation

# ProGuard mapping file (if leaked) can de-obfuscate names
```

## Android APK Reverse Engineering
```bash
# Decompile APK to Java-like source
jadx-gui application.apk

# Extract and view smali (Dalvik bytecode)
apktool d application.apk -o extracted/

# Repack after modification
apktool b extracted/ -o modified.apk

# Sign repacked APK
apksigner sign --ks keystore.jks modified.apk
```

### Common Android CTF Patterns
```
- Hardcoded flags/keys in strings.xml or decompiled Java
- Native library (.so) doing actual check - need combined with rev of ARM/x86 .so
- Root/emulator detection bypass (patch smali conditional jumps)
- SSL pinning bypass (Frida scripts or smali patch)
```

## Frida for Dynamic Instrumentation (Both .NET/Java/Android)
```bash
# Attach to running process, hook methods at runtime
frida -U -f com.example.app -l hook_script.js --no-pause

# Example hook script (Java/Android)
Java.perform(function() {
    var MainActivity = Java.use("com.example.MainActivity");
    MainActivity.checkLicense.implementation = function() {
        console.log("Bypassing license check");
        return true;
    };
});
```

## Quick Decision Tree
```
1. .NET assembly (PE with .NET metadata)? → dnSpy first
2. JAR/class files? → JD-GUI or CFR
3. APK? → jadx-gui, apktool for smali if native issues
4. Obfuscated? → try de4dot (.NET) or check for ProGuard mapping
5. Native library involved? → combine with standard rev-triage static/dynamic analysis
```
