# Per-falsifier — each falsifier's exact closure test

| Falsifier | The closure test | What it closes |
|---|---|---|
| body-uniform | masked `good`==`bad`, `bad1`==`bad2` | the text/code channel |
| status-uniform | identical code + `Location` across all arms | the status/redirect channel |
| timing-uniform | median delta <~1x jitter, N>=8, re-run | the timing channel |
| side-uniform | identical cookies/headers/JSON-fields | the side channel |
| send-uniform | both arms queue/send the email | the send side-effect |
| lock-uniform | both lock or neither locks | the lock oracle |
| direct-uniform | no `check`/`available` endpoint, or a uniform bool | the direct oracle |
| register-uniform | both names accepted or both rejected | the register oracle |
| reset-uniform | identical response + timing + send | the reset oracle |
| throttle-present | a `429`/`423`/captcha/delay in the burst | the "no-throttle" claim |
| bypass-fails | a spoofed request still `429`s | the "bypassed" claim |
| one-off-anomaly | the anomaly does not repeat on re-send | that anomaly's channel |

## The falsifier-to-verdict map

- a cell falsifier fires → that (form × channel) cell is `closed`
- all cells in a form fire → the form is `closed`
- all forms fire → the class is `closed` for this target
- a throttle falsifier fires → the "no-throttle" claim is dead; record
  the threshold instead

## The unmeasured-vs-closed rule

A falsifier only counts when the measurement is complete — a masked,
repeated, N>=8, both-arms read. A partial read is `unmeasured`, not
`closed`.
