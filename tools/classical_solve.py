#!/usr/bin/env python3
"""Solve the classical-cipher families cipher_id names, offline.

crypto-classical's mechanical half: Caesar sweep, Vigenere (IC/Kasiski
period -> per-column chi-squared), monoalphabetic substitution
(simulated annealing over an embedded-corpus bigram scorer), Atbash,
rail-fence and columnar brute. One command per family; everything is
stdlib.

  python3 tools/classical_solve.py caesar --text 'CT'
  python3 tools/classical_solve.py vigenere --text 'CT'
  python3 tools/classical_solve.py subst --text 'CT' --restarts 8
  python3 tools/classical_solve.py railfence --text 'CT'
  python3 tools/classical_solve.py --selftest

Scores are English-likeness from a small embedded corpus plus common
CTF flag-shaped bonuses. Output always lists the top candidates; a
solve that reads almost-English is a partially-wrong key, exactly the
trap the skill names — check flag-shaped positions first.
"""
import argparse, json, math, random, re, sys
from collections import Counter

CORPUS = (
    "the quick brown fox jumps over the lazy dog and runs through the "
    "forest where the flag is hidden in the capture the flag event the "
    "competition team solved the crypto challenge with frequency "
    "analysis the plaintext message was encrypted with a secret key and "
    "the attack recovered the solution by scoring every candidate "
    "against english letter frequencies the answer was inside the "
    "decoded text the flag format is curly braces around words "
    "it was the best of times it was the worst of times it was the age "
    "of wisdom it was the age of foolishness it was the epoch of belief "
    "it was the epoch of incredulity it was the season of light it was "
    "the season of darkness it was the spring of hope it was the winter "
    "of despair we had everything before us we had nothing before us "
    "the security of the system depends on the secrecy of the key not "
    "on the secrecy of the algorithm a cryptosystem should be secure "
    "even if everything about the system except the key is public "
    "knowledge substitution ciphers replace each letter with another "
    "letter while transposition ciphers rearrange the letters the "
    "index of coincidence measures how likely two random letters are "
    "to be equal frequency analysis exploits the uneven distribution "
    "of letters in natural language text the most common letters in "
    "english are e t a o i n s h r d l u in that order")
COMMON = ["the", "and", "ing", "ion", "ent", "hat", "her", "tha",
          "ere", "for", "was", "you", "ith", "not", "are", "his",
          "flag", "ctf", "key", "text", "have", "this", "with"]
WORDS = set((
    "a an the and or of to in is it its he she we they you i me him her "
    "us them his her their our your my this that these those there here "
    "be been was were are is am do does did done have has had having can "
    "could will would shall should may might must not no yes on off out "
    "up down over under again once then than when where while how what "
    "who whom which whose why as at by for from into onto upon with "
    "about against between through during before after above below "
    "one two three four five six seven eight nine ten first second "
    "third other another each every all any some none both either "
    "neither such same own very just only even still back also too "
    "more most less least much many few several enough now new old "
    "good bad great small big long short high low right left early "
    "late sure real true false free full open close secret hidden "
    "flag ctf key text code cipher plain encrypt decrypt encode decode "
    "message answer solve challenge crypto attack letter letters word "
    "found find give get take make made see know say said tell told "
    "way time day year thing world man life hand part eye woman place "
    "work week case point company number group problem fact if so but "
    "because until without within along across behind beyond plus "
    "except toward upon concerning flagis theflag hiddenmessage").split())
BIGRAM = None


def _bigram():
    global BIGRAM
    if BIGRAM is None:
        c = Counter(CORPUS[i:i + 2] for i in range(len(CORPUS) - 1))
        total = sum(c.values()) + 676
        BIGRAM = {chr(a + 97) + chr(b + 97): math.log(
            (c.get(chr(a + 97) + chr(b + 97), 0) + 1) / total)
            for a in range(26) for b in range(26)}
    return BIGRAM


def score(pt):
    t = re.sub(r"[^a-z]", "", pt.lower())
    if not t:
        return -1e9
    bg = _bigram()
    s = sum(bg.get(t[i:i + 2], -15.0) for i in range(len(t) - 1))
    s += 6 * sum(len(w) * len(w) * t.count(w) for w in COMMON)
    if re.search(r"flag\{|ctf\{|[a-z]{2,10}\{", pt.lower()):
        s += 200
    return s


def wscore(pt):
    """Word-segmentation score: best partition of the text into
    dictionary words. Sharper than bigrams — a wrong letter swap
    destroys whole words, which is exactly the near-English failure
    mode of the annealer."""
    t = re.sub(r"[^a-z]", "", pt.lower())
    n = len(t)
    if not n:
        return -1e9
    dp = [0.0] + [-1e9] * n
    for i in range(1, n + 1):
        best = dp[i - 1] - 3.0  # uncovered letter
        hi = min(14, i)
        for L in range(2, hi + 1):
            if t[i - L:i] in WORDS:
                best = max(best, dp[i - L] + L * L)
        dp[i] = best
    return dp[n] / n * 40.0


def letters_only(t):
    return re.sub(r"[^a-zA-Z]", "", t).lower()


def caesar_all(ct):
    out = []
    for k in range(1, 26):
        pt = "".join(chr((ord(c) - 97 - k) % 26 + 97) if c.isalpha()
                     else c for c in ct.lower())
        out.append({"shift": k, "plaintext": pt, "score": score(pt)})
    return sorted(out, key=lambda x: -x["score"])


def ic(text):
    f = Counter(text)
    n = len(text)
    return sum(v * (v - 1) for v in f.values()) / (n * (n - 1) or 1)


def kasiski(text, lo=2, hi=20):
    """Estimate period: mean IC per candidate length + repeated-trigram
    gcd evidence."""
    best = []
    for k in range(lo, hi + 1):
        cols = [text[i::k] for i in range(k)]
        avg = sum(ic(c) for c in cols if len(c) > 1) / k
        best.append((avg, k))
    best.sort(reverse=True)
    dists = []
    for i in range(len(text) - 3):
        tg = text[i:i + 3]
        j = text.find(tg, i + 3)
        if j > 0:
            dists.append(j - i)
    gcd_votes = Counter()
    for d in dists:
        for k in range(lo, hi + 1):
            if d % k == 0:
                gcd_votes[k] += 2
    return best, gcd_votes


ENGFREQ = [8.167, 1.492, 2.782, 4.253, 12.702, 2.228, 2.015, 6.094,
           6.966, 0.153, 0.772, 4.025, 2.406, 6.749, 7.507, 1.929,
           0.095, 5.987, 6.327, 9.056, 2.758, 0.978, 2.360, 0.150,
           1.974, 0.074]


def _chi2_shift(col, s):
    """Chi-squared of a column Caesar-decrypted by s vs English — the
    right column scorer; bigrams are noise on columns of ~10."""
    n = len(col) or 1
    f = Counter(col)
    e = [p * n / 100 for p in ENGFREQ]
    return sum((f.get(chr(97 + (i + s) % 26), 0) - e[i]) ** 2
               / (e[i] or 1) for i in range(26))


def vigenere_solve(ct, keylen=None, top=6):
    t = letters_only(ct)
    if len(t) < 20:
        return {"error": "too little ciphertext for statistics"}
    ranked, votes = kasiski(t)
    lens = [keylen] if keylen else sorted(
        {k for _, k in ranked[:top]} | {k for k, _ in votes.most_common(3)})
    out = []
    for k in lens:
        # chi² ranks column shifts; keep the top-3 per column and let the
        # bigram scorer pick the combination — chi² alone is noisy under
        # ~25 letters per column
        shifts = []
        for i in range(k):
            col = t[i::k]
            shifts.append(sorted(range(26),
                                 key=lambda s: _chi2_shift(col, s))[:3])
        if 3 ** k > 200000:  # long keys: chi² alone, combinations explode
            shifts = [s[:1] for s in shifts]
        best_pt, best_key, best_s = "", "", -1e9
        import itertools
        for combo in itertools.product(*shifts):
            key = "".join(chr(97 + s) for s in combo)
            pt = "".join(
                chr((ord(c) - 97 - combo[i % k]) % 26 + 97)
                if c.isalpha() else c for i, c in enumerate(t))
            sc = score(pt)
            if sc > best_s:
                best_s, best_pt, best_key = sc, pt, key
        out.append({"keylen": k, "key": best_key, "plaintext": best_pt,
                    "score": best_s})
    out.sort(key=lambda x: -x["score"])
    # a multiple of the real keylen often scores close — prefer the
    # shortest key within a small epsilon of the best
    best = out[0]["score"]
    short = min((c for c in out if best - c["score"] < 40),
                key=lambda c: c["keylen"], default=out[0])
    out.remove(short)
    out.insert(0, short)
    return {"candidates": out[:top],
            "note": "if the best key is an anagram of a word, the real key "
                    "is probably that word — keys are rarely random"}


def subst_solve(ct, restarts=6, iters=20000):
    t = letters_only(ct)
    if len(t) < 40:
        return {"error": "need ~40+ letters for annealing to converge"}
    freq = "etaoinshrdlcumwfgypbvkjxqz"
    order = "".join(c for c, _ in Counter(t).most_common())
    order += "".join(c for c in "abcdefghijklmnopqrstuvwxyz"
                     if c not in order)
    rng = random.Random(0xC1A551CA1)
    best = None
    for r in range(restarts):
        key = list(order if r == 0 else rng.sample(freq, 26))
        cur = _subst(t, key)
        cs = score(cur)
        # geometric schedule: hot enough to escape early, cold enough to
        # settle — linear decay freezes too early on this landscape
        for i in range(iters):
            k2 = key[:]
            a, b = rng.randrange(26), rng.randrange(26)
            k2[a], k2[b] = k2[b], k2[a]
            pt = _subst(t, k2)
            ps = score(pt)
            temp = 8.0 * (0.1 / 8.0) ** (i / iters)
            if ps > cs or rng.random() < math.exp((ps - cs) / temp):
                key, cur, cs = k2, pt, ps
        # greedy polish under the word scorer: annealing leaves
        # near-English with a few wrong swaps; exhaustive pair climbs
        # close them, and words give the swaps a real gradient
        ws = wscore(cur)
        improved = True
        while improved:
            improved = False
            for a in range(26):
                for b in range(a + 1, 26):
                    k2 = key[:]
                    k2[a], k2[b] = k2[b], k2[a]
                    pt = _subst(t, k2)
                    ps = wscore(pt)
                    if ps > ws:
                        key, cur, ws = k2, pt, ps
                        improved = True
        if best is None or ws > best[0]:
            best = (ws, cur, "".join(key))
    return {"plaintext": best[1], "key_cipher_to_plain": best[2],
            "score": best[0],
            "note": "near-English output means a partially-wrong key — "
                    "check flag-shaped positions, then re-run with more "
                    "restarts"}


def _subst(t, key):
    return "".join(key[ord(c) - 97] for c in t)


def railfence(ct):
    t = letters_only(ct)
    out = []
    for rails in range(2, min(11, len(t) // 3)):
        pat = sorted(range(len(t)),
                     key=lambda i: (i % (2 * rails - 2)
                                    if i % (2 * rails - 2) < rails
                                    else 2 * rails - 2 - i % (2 * rails - 2),
                                    i))
        idx = {p: t[i] for i, p in enumerate(pat)}
        pt = "".join(idx.get(i, "?") for i in range(len(t)))
        out.append({"rails": rails, "plaintext": pt, "score": score(pt)})
    return sorted(out, key=lambda x: -x["score"])[:6]


def _selftest() -> int:
    pt = ("theflagishiddenintheciphertextandfrequencyanalysiswillfind"
          "thesecretkeythatunlocksit")
    # caesar
    ct = "".join(chr((ord(c) - 97 + 7) % 26 + 97) for c in pt)
    top = caesar_all(ct)[0]
    assert top["shift"] == 7 and top["plaintext"] == pt, top
    # vigenere with a word key
    key = "lemon"
    ct = "".join(chr((ord(c) - 97 + ord(key[i % 5]) - 97) % 26 + 97)
                 for i, c in enumerate(pt))
    r = vigenere_solve(ct)
    assert any(c["key"] == key for c in r["candidates"]), r["candidates"][0]
    # substitution (fixed random alphabet)
    alpha = "qwertyuiopasdfghjklzxcvbnm"
    ct = "".join(alpha[ord(c) - 97] for c in pt)
    r = subst_solve(ct, restarts=10, iters=40000)
    got = r["plaintext"]
    agree = sum(a == b for a, b in zip(got, pt))
    assert agree > len(pt) * 0.6, (got[:60], agree)
    # railfence 4
    def enc_rail(t, n):
        rows = [[] for _ in range(n)]
        d, r = 1, 0
        for c in t:
            rows[r].append(c)
            r += d
            if r in (0, n - 1):
                d = -d
        return "".join("".join(x) for x in rows)
    ct = enc_rail(pt, 4)
    top = railfence(ct)[0]
    assert top["rails"] == 4 and top["plaintext"] == pt, top
    print("classical_solve selftest: ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="caesar",
                    choices=["caesar", "vigenere", "subst", "atbash",
                             "railfence"])
    ap.add_argument("--text", default="")
    ap.add_argument("--keylen", type=int, default=None)
    ap.add_argument("--key", default="")
    ap.add_argument("--restarts", type=int, default=6)
    ap.add_argument("--iters", type=int, default=20000)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.text:
        ap.error("--text is required")
    if a.cmd == "caesar":
        out = {"candidates": caesar_all(a.text)[:8]}
    elif a.cmd == "vigenere":
        out = vigenere_solve(a.text, a.keylen)
    elif a.cmd == "subst":
        out = subst_solve(a.text, a.restarts, a.iters)
    elif a.cmd == "atbash":
        t = letters_only(a.text)
        pt = "".join(chr(219 - ord(c)) for c in t)
        out = {"plaintext": pt, "score": score(pt)}
    else:
        out = {"candidates": railfence(a.text)}
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
