# The wildcard trap

A wildcard DNS record makes every subdomain resolve — a found
"name" isn't real until confirmed with a real query; the wildcard
inflates enumeration. Check a random name resolves to the same
answer to detect it.

## The detection

    python3 tools/dns_query.py --name asdfqwer123.<domain> --type A

If a random name resolves, a wildcard exists — every subsequent
"found" name must be confirmed against a distinct, real answer
(different IP, a distinct record) to count.
