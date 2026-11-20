# CAA — which CAs issue

CAA records name the permitted CAs — the operators; an empty or
odd CAA set is a signal.

## Reading it

`0 issue "letsencrypt.org"` — only that CA may issue; a mismatch
between the cert's issuer and the CAA is a finding. An empty CAA
means any CA may issue.
