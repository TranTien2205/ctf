# a brute-force via the referer field

To answer a brute-force: distribute the referer field (cut|sort|uniq -c|sort -rn), then window the outlier. The count outlier + the verbatim line is the evidence.
