# Decoding the GOT — the slot table


    readelf -r ./chal

Each .rela.plt entry: the GOT slot's address for that import — the
read target for a leak, the write target for a redirect.

## The split

- .rela.plt: the import functions — the lazy-bound ones.
- .rela.dyn: data relocations — resolved at load.
