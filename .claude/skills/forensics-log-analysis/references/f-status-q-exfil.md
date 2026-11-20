# data exfil via the status code field

To answer data exfil: distribute the status code field (cut|sort|uniq -c|sort -rn), then window the outlier. The count outlier + the verbatim line is the evidence.
