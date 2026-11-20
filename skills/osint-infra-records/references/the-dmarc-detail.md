# DMARC — _dmarc policy

`_dmarc.<d>` TXT — the mail policy; occasionally a planted field.

## The shape

`v=DMARC1; p=reject; rua=mailto:dmarc@domain` — the policy and the
report address; the rua/ruf addresses can name a sibling mailbox.
