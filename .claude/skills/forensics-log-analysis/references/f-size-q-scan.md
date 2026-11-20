# a scanner burst via the response size field

To answer a scanner burst: distribute the response size field (cut|sort|uniq -c|sort -rn), then window the outlier. The count outlier + the verbatim line is the evidence.
