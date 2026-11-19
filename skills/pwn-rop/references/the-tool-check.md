# Checking the tools — before relying


    which r2 socat
    python3 -c "import struct, socket"
    python3 tools/rop_chain.py --selftest
    python3 tools/pwnstatic/selftest.py

The selftests prove the local tools before the exploit depends on
them.
