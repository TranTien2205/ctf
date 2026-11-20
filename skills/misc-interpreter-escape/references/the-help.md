# help() / __doc__ — the docstring leak

`help(obj)`/`__doc__` leak names and methods without calling them —
free recon when the attr/call surface is tight.