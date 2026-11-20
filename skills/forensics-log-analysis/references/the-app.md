# Application logs — the varied shape

App logs have no standard format — the first move is to identify
the field layout from head lines, then cut by the right column or
use --regex to name the field.

## The approach

1. `head -10` — identify the delimiter and field order.
2. Check for a timestamp + level + message shape (most app logs).
3. Distribute by level (INFO/WARN/ERROR) — the ERROR distribution
   is usually the anomaly surface.
4. The flag may be a logged value, an exception message, or a
   deliberately planted line — grep widely.

`log_summary.py field --regex` names the field when the column
isn't positional.
