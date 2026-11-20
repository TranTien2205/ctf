# Answer sanity — sanity-check before send

A parse that yields `solve -> -1` on a counting puzzle is a parse bug,
not an answer — sanity-check shape (nonnegative count, in-range grid
move) before sending; a wrong answer may cost the whole run.
