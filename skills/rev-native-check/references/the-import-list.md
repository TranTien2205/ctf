# The import list — the check's vocabulary


The imports hint the check's shape:

- strcmp/strncmp/memcmp/bcmp — literal compares.
- strlen — a length gate.
- memcpy/strcpy — the buffer handling.
- ptrace — anti-debug.
- EVP_/MD5/SHA — a digest check.

## The command

    python3 tools/elf_info.py ./chal --symbols-only
    nm -D ./chal
