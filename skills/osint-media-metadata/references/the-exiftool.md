# exiftool — the canonical reader

    exiftool -a -u -g1 file.jpg

-a duplicates, -u unknown, -g1 grouped — prints every tag group.
Absent here → meta_read.py is the stdlib route. A partial output
(reading one -GPS tag) misses the answer in an odd corner.
