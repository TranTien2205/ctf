# a brute-force via the HTTP method field

To answer a brute-force: distribute the HTTP method field (cut|sort|uniq -c|sort -rn), then window the outlier. The count outlier + the verbatim line is the evidence.
