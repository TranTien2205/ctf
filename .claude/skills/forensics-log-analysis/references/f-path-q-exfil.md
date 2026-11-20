# data exfil via the request path field

To answer data exfil: distribute the request path field (cut|sort|uniq -c|sort -rn), then window the outlier. The count outlier + the verbatim line is the evidence.
