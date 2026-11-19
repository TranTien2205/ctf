# The send sequence — the ordered delivery


    send(stage1) → recv(leak) → compute → send(stage2) → recv(flag)

The sequence is synchronous — each step waits the prior's response.
