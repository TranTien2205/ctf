# Evidence locators by family

Method module for `dfir-parallel-sweep`. One artifact bundle,
eight bounded measurements: subagent_fanout --dfir splits by
artifact family, one ctf-dfir-* agent each, validate, merge.
Agents measure artifacts; they never answer investigation
questions directly.

evtx: event id + record id; registry: key path
+ value; fs: $MFT record + attr; pcap: packet
#; cloud: eventName + requestId; logs: line #.

## Exit

Step done -> next phase module or merge rules.
