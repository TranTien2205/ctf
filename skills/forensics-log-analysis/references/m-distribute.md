# Method — distribute the field

cut|sort|uniq -c|sort -rn — the per-value count. The top outlier
and the one-off tail are both anomalies.

## The fields worth it

- Source IP ($1 in access, the "from" in auth)
- Status code ($9)
- Request path ($7)
- User-agent, method, username, daemon
Distribute the field the question names, plus the IP always.
