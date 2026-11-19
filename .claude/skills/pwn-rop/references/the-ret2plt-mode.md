# ret2plt — calling an import's stub


Calls a PLT entry by name — the stub is decoded from the binary, the
GOT slot resolved from .rela.plt; no leak needed for imported
functions.

    python3 tools/rop_chain.py ./chal ret2plt --plt puts --arg 0x404018

## The use

The leak primitive: puts(got[x]) prints a resolved address — the
stage-1 chain.

## The falsifier

The name isn't a PLT symbol, or the stub can't be decoded.
