# ANY — the sweep query

`--type ANY` asks for every record type at once — many resolvers
now refuse/limit it, so it's a sweep, not a substitute for the
per-type queries. Follow with TXT/SPF/SRV explicitly.

## The limitation

Modern resolvers often return a minimal ANY (or refuse it) as an
anti-amplification measure — so treat ANY as a hint, then sweep
the specific types that carry data.

## Reading ANY

A minimal ANY response may omit types — treat its absence as no-signal, not proof; sweep the types explicitly.
