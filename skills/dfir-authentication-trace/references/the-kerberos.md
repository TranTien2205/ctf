# Kerberos — 4768/4769/4771

4768 TGT: `0x6` principal unknown, `0x12` revoked, `0x17` key
expired, `0x25` skew. `0x18` wrong password lives on **4771**, never
4768. `TicketEncryptionType` 0x17/0x18 = RC4 — the downgrade tell;
`PreAuthType` 0 = "Do not require preauthentication".

## The codes

0x6 unknown, 0x12 revoked, 0x17 expired, 0x25 skew; 0x18 lives on 4771.

## DC only

4768-4776 log on the DC.
