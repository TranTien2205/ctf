# The hooks by glibc — the version line


<= 2.34: __free_hook/__malloc_hook/realloc_hook writable+callable.
>= 2.35: the hooks are gone — use _IO_list_all or a different
redirect.
