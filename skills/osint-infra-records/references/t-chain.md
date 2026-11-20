# Following a record chain

A CNAME → a real host; an MX → a mail host; an SRV → a service —
each answer names a next host to query. Follow the chain.

## Following it

`www.example.com CNAME cdn.example.net` — now query the cdn name's
own records. Each answer is a lead to another host; the chain ends
at an A/AAAA or a leaf hostname.
