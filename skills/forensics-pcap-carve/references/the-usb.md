# USB — not a network flow

A USB capture (linktype 189/220) is interrupt reports, not network
— usb_hid.py decodes `keys` (keystrokes) or `mouse` (pen strokes);
`--raw hexlines` on exported reports.
