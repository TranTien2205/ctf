# Boundary and flow flaws

Logic flaws are validated by *comparison*, not by payload: a correct input and
one input that crosses a documented boundary, side by side.

## Probe that worked (Pachinko / Pachinko Revisited)

Submit the minimal correct circuit, then the same circuit with one node id
just past the checker's documented limit, and compare the two responses:

```text
arm A: valid minimal circuit          -> accepted
arm B: same circuit, node id = max+1  -> ?
```

Expected: arm B is accepted or processed past the guard — the check compared
against the wrong bound (`<` vs `<=`, off-by-one in id space, or a limit read
from a different field than the one validated). Falsifier: arm B is rejected
with the same shape as every other invalid input — the boundary is enforced.

## The boundary alphabet

| Boundary | The probe pair |
|---|---|
| documented max / limit | value at limit, value at limit+1 |
| integer width | `2^31-1` vs `2^31`, negative where unsigned is assumed |
| array length | exactly N, N+1 |
| uniqueness | submit twice, interleaved |
| price/quantity/amount | 0, negative, very large, float vs int |
| step order | skip a step, reorder steps, replay a step |

## The flow questions

Every business flow has assumptions the code never states — find them:

- **Sequence**: can step 3 run before step 1? Can a step repeat?
- **Amount**: does the server recompute price, or trust a client field?
- **Identity**: whose record does the action touch — is ownership re-checked
  on *this* step?
- **State**: does a flag set by step A survive when step B fails?

The pattern is always the pair: the intended input, then the input that
violates exactly one assumption — and the comparison of the two responses is
the evidence.

## Falsifier

Every out-of-bounds or out-of-order input is rejected with the same uniform
error — the assumption is enforced server-side on all paths.

## Traps

- A `200` that does nothing is not a bypass — the effect must land in state
  (re-read the object).
- Two different error shapes for "invalid" is already signal: the inputs took
  different code paths.
