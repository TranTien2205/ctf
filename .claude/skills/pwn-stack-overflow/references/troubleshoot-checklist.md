# Troubleshooting â€” symptom â†’ cause â†’ fix — checklist

Companion to `troubleshoot.md`.

## Checklist

- [ ] Symptom
- [ ] crash but RIP isn't pattern bytes
- [ ] cyclic --find returns -1
- [ ] works locally, crashes remotely
- [ ] system@plt crashes inside libc
- [ ] ROP chain runs but execve fails
- [ ] canary check fires before return
- [ ] exploit works then crashes
- [ ] offset differs per run
- [ ] one-shot service, need two stages
- [ ] PIE, everything's unknown
- [ ] 'ret' before call crashes
- [ ] payload gets truncated
