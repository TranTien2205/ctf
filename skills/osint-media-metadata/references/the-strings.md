# strings — the token hunt

    strings -n 6 file | grep -iE 'flag|gps|key|pass'

Surfaces embedded ASCII tokens the tag readers miss — a flag
string appended raw or inside a tag's tail.
