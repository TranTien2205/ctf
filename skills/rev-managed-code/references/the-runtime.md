# The runtime — prove it from the header bytes

Before any decompile: name the runtime from the header bytes and
quote them. A PE with a non-zero CLR data directory is .NET;
0xCAFEBABE is a Java .class; a dex/apk is Dalvik; a PyInstaller
bundle is bytecode (rev-bytecode-vm).

## The reads

    file ./chal
    rabin2 -I ./chal | grep -i clr    # CLR data directory non-zero?
    strings ./chal | grep -iE "dotnet|mscoree|java|kotlin"
    xxd ./chal | head                 # CAFEBABE = class

## The boundary

A managed-looking binary that's a thin native stub — empty CLR
directory, a jar that's only a launcher — is native work
(rev-native-check). Prove the runtime BEFORE assuming managed.
