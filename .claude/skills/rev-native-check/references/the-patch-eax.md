# Patching the result — the eax fix


Alternatively: after the compare call, force eax=0 — `xor eax,eax`
or `mov eax,0` patched in — the subsequent test sees "equal".
