# The stream note — the flow's bytes

## The follow

    pcap_parse cap follow N
    tshark -r cap -z follow,tcp,ascii,N

The reassembled stream is the flow's full byte content in seq
order — the cleartext conversation or the transferred data.

## The limit

follow is TCP-only — UDP/ICMP/DNS channels carve fields, not
streams.
