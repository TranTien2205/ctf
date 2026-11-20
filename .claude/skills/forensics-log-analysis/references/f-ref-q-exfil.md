# data exfil via the referer field

To answer data exfil: distribute the referer field (cut|sort|uniq -c|sort -rn), then window the outlier. The count outlier + the verbatim line is the evidence.
