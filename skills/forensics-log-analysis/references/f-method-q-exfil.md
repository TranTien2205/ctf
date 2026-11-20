# data exfil via the HTTP method field

To answer data exfil: distribute the HTTP method field (cut|sort|uniq -c|sort -rn), then window the outlier. The count outlier + the verbatim line is the evidence.
