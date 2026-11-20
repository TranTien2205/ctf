# a scanner burst via the timestamp field

To answer a scanner burst: distribute the timestamp field (cut|sort|uniq -c|sort -rn), then window the outlier. The count outlier + the verbatim line is the evidence.
