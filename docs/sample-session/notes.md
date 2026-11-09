# Working notes - http://127.0.0.1:38689

## Agent summary (agent)

Demo run. Proven: SQL injection (engine named plus five rows from users), OS command injection (identity line with the probe nonce), IDOR across two principals, exposed secrets, and a forged JWT accepted against a rejected control. Candidate: reflected XSS - unescaped, but no browser executed it. Host-header reflection left as a lead.

