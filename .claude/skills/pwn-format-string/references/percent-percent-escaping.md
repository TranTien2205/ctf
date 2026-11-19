# %% escaping — the literal percent


%% in a format string emits a literal % — it doesn't consume an argument.
Useful for padding the printed count without consuming args.

## Use

- %% outputs one % char — counts toward the running total.
- Use %% to pad the count without consuming argument positions.
- A %% between specifiers pads the count by one per %%.

## Falsifier

None; %% is a literal, not a primitive — it just adds to the count.
