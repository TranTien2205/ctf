# the top talker via the source IP field

To answer the top talker: distribute the source IP field (cut|sort|uniq -c|sort -rn), then window the outlier. The count outlier + the verbatim line is the evidence.
