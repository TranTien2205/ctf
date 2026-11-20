# Guard cell: brief-leak / kill-map

Method module for `web-parallel-sweep`. The sweep splits a web target by bug-class family into bounded measurements; this file is one named piece of that method. Ten families reporting is not ten families closed.

Whether `kill-map` guards against the `brief-leak` failure.

## Read

Map the failure's mechanism to the guard's enforcement point - a
guard only counts if it sits on the path the failure travels
(validator on evidence shape, contract on report fields,
main-thread on ledger writes, kill-map on re-walking, scope on
target bounds, budget on time).

## Note

A guard that does not sit on the failure's path is decoration -
the cell states whether this pairing is real or residual.
