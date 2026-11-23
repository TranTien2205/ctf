# Service recon: elk

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

ELK stack surfaces: ES :9200 (svc-elastic), Kibana
:5601 (/api/status = version+plugins verbatim), Logstash
:9600 (_node/stats). A kibana /app/dev_tools or saved-objects
surface = the web recon side of the data stack.
## Pivot

Signal harvested -> out-*; route named -> that skill.
