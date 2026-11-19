# Worked — a .class flag-checker

1. CAFEBABE magic.
2. jclass_info --strings: 'flag{' + suspicious consts.
3. javap -c Check.check: a per-char compare to a char array const.
4. The constant's chars = the flag.
5. Run → accepted.
