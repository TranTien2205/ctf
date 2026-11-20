# the top talker via the timestamp field

To answer the top talker: distribute the timestamp field (cut|sort|uniq -c|sort -rn), then window the outlier. The count outlier + the verbatim line is the evidence.
