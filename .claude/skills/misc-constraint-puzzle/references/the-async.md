# Async solvers — usually overkill

A single connection, sequential rounds — plain blocking sockets +
until() is enough; asyncio adds complexity the deadline doesn't
need.

## Blocking wins

Sequential rounds — blocking until() is enough.

## Blocking

until() suffices; async adds nothing here.
