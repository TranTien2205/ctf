# Worked — Linux bash history

1. banners → kernel + ISF.
2. linux.bash → the typed command history — `cat /flag` or a flag
   passed as an argument.
Often the single fastest Linux route.

## Notes

- linux.bash reads bash history resident in memory — typed
  commands survive even if the file was cleared.
- If ISF symbols are missing, ioc_scan --pattern 'flag\\{' on the
  image recovers the same strings without the plugin.
