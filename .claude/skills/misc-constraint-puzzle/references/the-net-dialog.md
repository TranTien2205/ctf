# net_dialog — the scripted probe

    net_dialog host port --steps 'wait:> ; send:1\n ; dump'
    net_dialog host port --send 'hello\n' --recv-until '> '

The step script reproduces a captured exchange without a solver —
probe the protocol before writing the client.

## The probe

wait/send/dump steps replay the captured exchange.
