# Probing the chain — the staged verify


Don't fire the whole chain blind: test the first gadget lands, then
the first call, then the full sequence — staged verification catches
the early bug before it compounds.
