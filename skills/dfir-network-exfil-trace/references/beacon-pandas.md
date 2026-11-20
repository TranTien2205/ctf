# Beacon: The pandas one-liner

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

```python
import pandas
net = pandas.read_csv('net.csv')
net['ts'] = pandas.to_datetime(net['frame.time_epoch'], unit='s', utc=True)
net.sort_values('ts', inplace=True)
key = ['ip.src','ip.dst','tcp.dstport']
net['delta'] = net.groupby(key)['ts'].diff().dt.total_seconds()
print(net.dropna(subset=['delta']).groupby(key)['delta'].agg(n='count',median='median',mad=lambda s:(s-s.median()).abs().median(),cv=lambda s:s.std()/s.mean()).sort_values('cv'))
```
`utc=True` is not optional: a mixed-offset column degrades to object dtype and sorts as TEXT.

## Evidence rule

A cadence claim needs the numbers: n, median, mad, cv — or the quoted
io,stat series. 'Looked regular' is not measurable and not recordable.

## Pivot

cv low AND peer suspicious -> `q-periodic-beacon`; cv high -> drop the
beacon hypothesis for this peer and record the negative.
