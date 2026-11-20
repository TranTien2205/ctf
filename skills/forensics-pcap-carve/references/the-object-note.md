# The object note — export then read

## The export

    pcap_parse cap http --out objs/
    tshark -r cap --export-objects http,objs/

## The read

Each exported file must be OPENED — a file listing is a lead. A
renamed file: `file` it, read the magic. A transferred archive:
extract it. The flag rides inside one of them.
