# The .apk — the Android bundle

An .apk is a zip with classes.dex + resources — jadx decompiles to
Java-like source; baksmali gives smali.

## The smali

    if-eqz v0, :fail       ; the deciding branch
    const-string v1, "exp" ; the expected
