# The half-close — the shutdown write


Some reads need EOF to return (read-until-close) — s.shutdown(SHUT_WR)
sends the EOF while keeping the recv side open.
