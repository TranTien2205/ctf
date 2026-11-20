# Identifying the image — the profile step

volatility3 auto-detects via `windows.info`; a wrong assumption
makes every later plugin lie silently.

## The check

    vol -f mem.raw windows.info      # Windows
    vol -f mem.raw banners           # Linux banner strings

Look at: kernel build/version, the DTB, PsActiveProcessHead. If
windows.info errors or prints nonsense, the image may be a
different OS or corrupt — stop and re-identify, don't continue.
