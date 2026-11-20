# Corrupt/mangled files

Depth module for `ctf-forensics`. Open `../SKILL.md` for the
shared-file index first; this file is one named piece of the corpus -
never a finding by itself.

Truncated headers, XOR'd magic, swapped chunks, wrong checksums - the repair recipe differs per format: PNG needs valid IHDR+CRCs, ZIP needs the central directory, ELF needs the e_ident magic; the fix is usually a 4-16 byte patch.

## Pivot

Module read -> the shared file or class skill it names.
