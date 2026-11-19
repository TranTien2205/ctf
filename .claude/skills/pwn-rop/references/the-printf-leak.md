# printf leak — the formatted address


printf("%p", x) prints "0x7f..." — parse as hex text, not raw bytes:

    addr = int(re.search(rb'0x([0-9a-f]+)', out).group(1), 16)
