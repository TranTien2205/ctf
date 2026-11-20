# data exfil via the response size field

To answer data exfil: distribute the response size field (cut|sort|uniq -c|sort -rn), then window the outlier. The count outlier + the verbatim line is the evidence.
