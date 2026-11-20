# The issuer — which CA

The cert's Issuer + CAA records name the CA — corroborating who
operates the domain; a LetsEncrypt cert on a serious domain is a
signal.

## Reading it

- The Issuer CN/O names the CA.
- CAA `issue` should list that CA — a mismatch is a finding.
- A free CA (LetsEncrypt) on a "serious" target is a data point.
