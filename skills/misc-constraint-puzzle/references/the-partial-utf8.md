# Partial utf8 at the buffer edge

A multi-byte char can split across recv() boundaries — decode only
after the terminator arrives, never per-chunk, or a split codepoint
mangles the parse.
