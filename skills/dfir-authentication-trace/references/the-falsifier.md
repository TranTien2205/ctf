# The falsifier — nothing authenticated from outside

Every 4624 carries LogonType 4/5 with a `$`-suffixed or service
TargetUserName, and the bundle holds no 4625/4648/4768/4776 ->
nothing authenticated from outside; reroute.

## The close

All 4624 service/batch + no failure IDs -> nothing external.

## Nothing external

Service/batch only -> reroute.
