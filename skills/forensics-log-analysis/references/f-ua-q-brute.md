# a brute-force via the user-agent field

To answer a brute-force: distribute the user-agent field (cut|sort|uniq -c|sort -rn), then window the outlier. The count outlier + the verbatim line is the evidence.
