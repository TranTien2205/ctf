# franklin-reiter — the related-message attack

`m2=a·m1+b` linear, `a`,`b` known, same `n`,`e` → `gcd(x^e-c1,(ax+b)^e-c2)=x-m`.
Detection: `m2=a·m1+b` in keygen. Bound: linear relation, `a`,`b` known.
Verify: `pow(m,e,n)==c1`. Command: `franklin-reiter --n --e --a
--b --c1 --c2`. See `per-attack-franklin-reiter.md`.
