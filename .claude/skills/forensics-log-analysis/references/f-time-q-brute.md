# a brute-force via the timestamp field

To answer a brute-force: distribute the timestamp field (cut|sort|uniq -c|sort -rn), then window the outlier. The count outlier + the verbatim line is the evidence.
