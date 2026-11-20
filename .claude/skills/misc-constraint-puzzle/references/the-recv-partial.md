# recv() is bytes-available — never assume

`recv(4096)` returns 1..4096 bytes — whatever the kernel has. Every
protocol layer must assemble; there is no 'read a line' syscall on
TCP.
