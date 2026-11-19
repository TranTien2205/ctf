# Alternate input shape — when the smash isn't the first read


The program may read several inputs; the overflow may be the second or
third, after prompts that must be answered correctly first.

## Shapes

- A menu/prompt before the vulnerable read.
- A size prompt then the data read.
- A name/comment/title sequence — the smash is one of them.

## The discipline

Map the full input protocol first; the smash only fires when the earlier
prompts are answered in the expected shape.
