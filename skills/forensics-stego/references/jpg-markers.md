# JPEG markers

FFD8 SOI, FFD9 EOI, FFE0-FFEF APPn, FFDB DQT, FFC4 DHT, FFC0 SOF, FFDA SOS.

## The route

Identify the carrier, walk the extraction order (appended → metadata → format channel → bit planes), record each channel's negative. See the-workflow.md.
