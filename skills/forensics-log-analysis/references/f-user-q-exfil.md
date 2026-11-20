# data exfil via the username field

To answer data exfil: distribute the username field (cut|sort|uniq -c|sort -rn), then window the outlier. The count outlier + the verbatim line is the evidence.
