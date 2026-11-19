# Boundary — the pyc-embedded-in-binary case

A PyInstaller/Nuitka binary embeds .pyc — it LOOKS native but the
check is in the embedded bytecode, not the native code.

## The discriminate

- Extract the .pyc (pyinstxtractor, or the embedded marshal blob).
- If the check is in the .pyc → this class.
- If it's in compiled native code → rev-native-check.
