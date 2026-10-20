#!/usr/bin/env python3
"""Match the current observation or source against chains this toolkit already solved.

A match is a candidate hypothesis and its cheapest confirming probe. It is never
proof. The tool reports which signals were actually found, which were not, and
which preconditions a human still has to confirm; it never asserts that a
precondition holds.
"""
import argparse
import glob
import json
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAINS = os.path.join(ROOT, "knowledge", "chains")
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}
SIGNAL_STATS = os.path.join(ROOT, "knowledge", "signal-stats.json")
# Separates a real match from a coincidence. See the comment in score_card.
STRONG_COVERAGE = 0.5
STRONG_MIN_SIGNALS = 3
MAX_FILE_BYTES = 1024 * 1024
MAX_PER_FILE = 40000
MAX_TOTAL = 400000


def load_chains(directory=CHAINS):
    cards = []
    for path in sorted(glob.glob(os.path.join(directory, "*.json"))):
        try:
            with open(path, encoding="utf-8") as handle:
                card = json.load(handle)
        except (OSError, ValueError) as exc:
            cards.append({"_error": str(exc), "_path": path})
            continue
        card["_path"] = os.path.relpath(path, ROOT)
        cards.append(card)
    return cards


# Assets carry no signals but happily consume the whole read budget. An
# asset-heavy challenge used to spend all 400 KB on a sourcemap and a few JPEGs,
# so the matcher never saw its own Dockerfile or handler code and the card could
# not be retrieved from its own handout at all.
SKIP_EXT = {
    ".jpg", ".jpeg", ".png", ".gif", ".ico", ".bmp", ".webp", ".svg",
    ".woff", ".woff2", ".ttf", ".otf", ".eot",
    ".pdf", ".zip", ".gz", ".tgz", ".xz", ".bz2", ".7z", ".rar",
    ".mp3", ".mp4", ".wav", ".avi", ".mov", ".webm",
    ".so", ".dll", ".dylib", ".class", ".jar", ".wasm", ".pyc",
    ".map", ".lock", ".ttc", ".db", ".sqlite", ".sqlite3", ".pack", ".idx",
}
SKIP_NAME_PARTS = (".min.js", ".min.css", "package-lock.json", "yarn.lock",
                   "pnpm-lock.yaml", "go.sum", "composer.lock", "Gemfile.lock")
# read the files most likely to define the challenge first
PRIORITY_EXT = (".vcl", ".conf", ".cfg", ".ini", ".toml", ".env",
                ".go", ".py", ".js", ".ts", ".jsx", ".tsx", ".vue", ".rb",
                ".php", ".java", ".rs", ".zig", ".c", ".cpp", ".sh", ".sql",
                ".json", ".yml", ".yaml", ".html", ".txt", ".md")


def _worth_reading(path):
    name = os.path.basename(path)
    if any(part in name for part in SKIP_NAME_PARTS):
        return False
    return os.path.splitext(name)[1].lower() not in SKIP_EXT


def _read_order(path):
    """Dockerfiles and entrypoints first, then source, then everything else."""
    name = os.path.basename(path).lower()
    ext = os.path.splitext(name)[1].lower()
    if name.startswith("dockerfile") or name in ("entrypoint.sh", "docker-compose.yml",
                                                 "supervisord.conf"):
        rank = 0
    elif ext in PRIORITY_EXT:
        rank = 1 + PRIORITY_EXT.index(ext)
    else:
        rank = len(PRIORITY_EXT) + 2
    try:
        size = os.path.getsize(path)
    except OSError:
        size = MAX_FILE_BYTES
    return (rank, size)


def read_source(target, skip_names=()):
    """Read a bounded amount of a challenge's text.

    skip_names drops this toolkit's own artefacts (a ledger, a solve script) so
    they cannot be counted as if they were part of the handout.
    """
    if os.path.isfile(target):
        paths = [target]
    else:
        paths = []
        for base, dirs, names in os.walk(target):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            paths.extend(os.path.join(base, name) for name in names
                         if name not in skip_names)
        paths = sorted((p for p in paths if _worth_reading(p)), key=_read_order)
    chunks, total = [], 0
    for path in paths:
        try:
            if os.path.getsize(path) > MAX_FILE_BYTES:
                continue
            with open(path, encoding="utf-8", errors="replace") as handle:
                data = handle.read(MAX_PER_FILE)
        except OSError:
            continue
        chunks.append(os.path.basename(path) + "\n" + data)
        total += len(data)
        if total >= MAX_TOTAL:
            break
    return "\n".join(chunks)


_WORDISH = re.compile(r"[A-Za-z]{1,5}\Z")
_EMBEDDED = {}


def found(signal, text):
    """Case-insensitive containment, refusing a short word buried inside another.

    Plain containment made short alphabetic signals fire constantly: measured
    over the 40 handouts on disk, `lua` matched 9 of them and every single hit
    was inside `evaluate`; `mail` matched 16 and 13 were inside `email`; `eval`
    matched 17 and 10 were inside words like `retrieval`. Because the scorer
    weights rare signals highest, a phantom hit on a rare short signal moved
    cards up the ranking.

    Only letters are treated as a boundary, not \\b. `lua_State` and `redis.lua`
    must still match, and \\b would reject the first because `_` is a word
    character. Longer signals keep plain containment so `template` still matches
    `templates`.
    """
    lowered = signal.lower()
    if not _WORDISH.match(signal):
        return lowered in text
    pattern = _EMBEDDED.get(lowered)
    if pattern is None:
        pattern = re.compile(r"(?<![a-z])%s(?![a-z])" % re.escape(lowered))
        _EMBEDDED[lowered] = pattern
    return pattern.search(text) is not None


def load_signal_stats(path=SIGNAL_STATS):
    """Document frequency of each signal across the handout corpus.

    Scoring a match by how RARE its signal is fixes a bias that grows with the
    library: the old score was matched/len(signals), which handed a card with
    three vague signals a near-perfect ratio on every source while a card with
    fifteen precise ones was penalised for the five that happened not to appear.
    Measured over the cards whose handout is still on disk, the old score put the
    right card first 73% of the time with 1.91 wrong cards outranking it; this
    one scores 91% with 0.55. Rebuild with --rebuild-stats.
    """
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict) or "corpus" not in data:
        return None
    return data


def signal_weight(signal, stats):
    """Rarer signals count for more. Unknown signals are treated as rare."""
    total = max(1, int(stats.get("corpus", 1)))
    df = int(stats.get("df", {}).get(signal, 0))
    return math.log((total + 1.0) / (df + 1.0))


# --------------------------------------------------------------- stage index
# The transfer path, and the one that measured best. A card's `signals` are
# literals copied from its own handout, so a NEW challenge sharing the MECHANISM
# shares none of them: tools/holdout_eval.py measures card-level transfer at
# 0.0. Its `chain[]` stages are different -- each one is a sentence a human
# wrote about a mechanism ("HAProxy strips only SP and HTAB from header values
# so -m beg no longer matches, while Werkzeug's parse_options_header uses
# str.strip()"), naming real components rather than this handout's variable
# names. 426 such stages exist across the 72 cards, a median of 5.9 per card.
#
# MEASURED, by sweeping scorers against test/baselines/mechanism_families.json
# (16 challenges whose correct peer is known), so nobody re-tunes this blind:
#
#   scorer            stages used   min len   top-1   top-3   top-10   median rank
#   full IDF overlap  all           4         18.8%   25.0%   37.5%    12 of 71
#   plain overlap     all           4         12.5%   25.0%   50.0%    13 of 71
#   anything          OPENING only  4 or 6     0.0%    0.0%   <=12.5%  27-30
#
# Two results worth keeping, because both contradict a reasonable guess:
#
#  * Restricting to the OPENING stages destroys the signal, even though the
#    ground truth is defined by whether the opening move transfers. One stage's
#    prose is simply too short to match a whole source tree; the chain entire is
#    what carries enough vocabulary.
#  * An earlier attempt scored 0.0% everywhere. The cause was a token filter
#    that kept only identifier-shaped words -- underscores, dots, digits,
#    internal capitals. That threw away `cache`, `proxy`, `parser`, `boundary`,
#    exactly the shared vocabulary that makes two mechanisms alike. Plain words
#    of four letters or more, weighted by rarity, beat a clever filter.
#
# 18.8% top-1 is still far too low to grade a match `candidate`: that gate feeds
# decide.py a probe, and being wrong four times in five would be worse than
# silence. So a stage hit is always `weak` -- a card to READ, never a probe to
# run -- and transfer_rate in holdout_eval stays strong-only on purpose.
STAGE_TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_.\-]{3,}")
STAGE_MIN_LEN = 4
STAGE_MIN_HITS = 3


def stage_tokens(text):
    return {t for t in (raw.strip("._-").lower()
                        for raw in STAGE_TOKEN.findall(text or ""))
            if len(t) >= STAGE_MIN_LEN}


def stage_text(card):
    """Every stage's own prose: the phase name, the action and the why."""
    return " ".join(str(step.get(key) or "")
                    for step in (card.get("chain") or [])
                    for key in ("stage", "action", "why"))


def build_stage_index(cards):
    """Token sets per card plus document frequency, for rarity weighting."""
    units, df = {}, {}
    for card in cards:
        if "_error" in card:
            continue
        toks = stage_tokens(stage_text(card))
        units[card["id"]] = toks
        for token in toks:
            df[token] = df.get(token, 0) + 1
    return {"units": units, "df": df, "n": max(1, len(units))}


def stage_lead_score(card, present, index):
    """Rarity-weighted overlap between a card's stage prose and the query."""
    if not index or not present:
        return 0.0, 0
    toks = index["units"].get(card.get("id"))
    if not toks:
        return 0.0, 0
    hit = toks & present
    if len(hit) < STAGE_MIN_HITS:
        return 0.0, len(hit)
    df, n = index["df"], index["n"]
    weight = sum(math.log((n + 1.0) / (df.get(t, 0) + 1.0)) for t in hit)
    return weight, len(hit)


_CARD_CLASS_CACHE = {}


def card_class_of(card):
    """The mechanism class of a card, by the best source available.

    Order matters and is about trust, not convenience:

    1. a `classification.primary` with no `derived_by` marker -- a reviewer wrote
       it, and the card schema calls it authoritative;
    2. one marked `derived_by` -- tools/backfill_classification.py proposed it at
       a measured 91% precision on the reviewed labels;
    3. computed here from the card's own prose, for the 28 cards the backfill
       honestly refused to label.

    Step 3 exists because the alternative is worse. Measured: the peers that
    should be reachable in tools/holdout_eval.py are mostly unlabelled, so
    without it the whole class path reaches nothing. A class guessed this way is
    only ever used to offer a card as a LEAD TO READ, never to grade a match
    `candidate`, so a wrong guess costs a reading suggestion rather than a probe.
    """
    cid = card.get("id")
    if cid in _CARD_CLASS_CACHE:
        return _CARD_CLASS_CACHE[cid]
    block = card.get("classification") or {}
    primary = block.get("primary")
    if primary:
        out = (primary, "reviewed" if not block.get("derived_by") else "derived")
        _CARD_CLASS_CACHE[cid] = out
        return out
    try:
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import backfill_classification as backfill
        import classify as classifier
        taxonomy = classifier.load_taxonomy()
        try:
            cstats = classifier.load_signal_stats()
        except Exception:
            cstats = None
        result = backfill.propose(card, taxonomy["classes"], cstats)
        # Accept the top class even when the proposer would REFUSE to write it.
        # Writing a label is a durable claim about the card; offering it as a
        # lead is not, so the bar is lower here and is stated as such.
        top = (result.get("top") or {}).get("class")
        out = (top, "computed") if top else (None, None)
    except Exception:
        out = (None, None)
    _CARD_CLASS_CACHE[cid] = out
    return out


def local_solve(name):
    """Has THIS CHALLENGE, by name, already been solved on this disk?

    The cheapest possible match and the one nothing checked. Measured, at a cost
    worth stating: on a target called NovaCore this tree already held
    `solved/novacore.md` and `challenges/novacore/solver.py` -- a 498-line
    working solver from a previous solve. Nothing looked. chain_match reads only
    knowledge/chains/ and matches card SIGNALS against an observation string, so
    a weak observation abstained; the chain card itself was read and then
    DISMISSED on a wrong inference. The run that followed cost a 13-agent sweep
    and 1.03M tokens, and the flag in the end came from running that solver with
    one line changed.

    A solved note or a solver whose name matches is stronger evidence than any
    signal overlap, so it is checked first and reported before the index.
    Prefix-matched because a re-spawned instance is usually registered under a
    suffixed name: `novacore2` must find `novacore`.
    """
    slug = re.sub(r"[^a-z0-9]+", "", (name or "").lower())
    if len(slug) < 4:
        return None                       # too short to match on safely
    hits = {"notes": [], "solvers": [], "handouts": []}
    notes = os.path.join(ROOT, "solved")
    if os.path.isdir(notes):
        for entry in sorted(os.listdir(notes)):
            if not entry.endswith(".md"):
                continue
            other = re.sub(r"[^a-z0-9]+", "", entry[:-3].lower())
            if other and (other in slug or slug in other):
                hits["notes"].append("solved/" + entry)
    chdir = os.path.join(ROOT, "challenges")
    if os.path.isdir(chdir):
        for entry in sorted(os.listdir(chdir)):
            other = re.sub(r"[^a-z0-9]+", "", entry.lower())
            if not other or not (other in slug or slug in other):
                continue
            if other == slug:
                continue                  # this challenge's own directory
            for candidate in ("solver.py", "exploit.py", "solve.py"):
                path = os.path.join(chdir, entry, candidate)
                if os.path.isfile(path):
                    hits["solvers"].append("challenges/%s/%s" % (entry, candidate))
            if os.path.isdir(os.path.join(chdir, entry, "handout")):
                hits["handouts"].append("challenges/%s/handout" % entry)
    if not any(hits.values()):
        return None
    hits["read_these_before_any_probe"] = hits["notes"] + hits["solvers"]
    hits["why"] = ("a solved note or a working solver whose NAME matches this "
                   "challenge is stronger than any signal overlap. Read it "
                   "first; a re-spawned instance usually only needs its host "
                   "and port changed.")
    return hits


def class_scope(text, source_mode=True, top=4):
    """The mechanism classes the taxonomy ranks for this query.

    This is the generalising layer, and the reason it is worth adding. A card's
    own `signals` are literal strings copied from that card's handout -- a
    variable name, a path, a version -- so a NEW challenge with the same
    mechanism shares the mechanism but not the literals, matches nothing, and is
    dropped by the `not matched` test below. Measured by tools/holdout_eval.py:
    the library stays silent on roughly 69% of held-out challenges.

    The taxonomy's own `source_signals` and `observation_signals` are written at
    the level of the mechanism instead, and tools/observation_eval.py shows they
    generalise across the words a solver actually types. So a card can also be
    reached through its class.

    Returns {class_id: score}. Failing to load the classifier is not fatal: the
    literal path is unchanged and still works, so this degrades to the old
    behaviour rather than breaking the match.

    MEASURED CEILING, so nobody re-tunes this blind. With leads unbounded and
    the scope widened to the top twelve classes, the correct peer appears at all
    in only 2 of the 16 measurable held-out challenges -- 12.5%. The shipped
    settings (top 4, at most 3 leads) reach 1 of those 2, moving
    tools/holdout_eval.py's silent_rate from 0.688 to 0.625. Widening the scope
    from 4 to 12 changes the rate by nothing; raising the lead cap to about 20
    would reach the full 12.5% while printing 10 to 25 "leads" per query, which
    is noise rather than help.

    WHY THE CEILING IS LOW, which is the useful part. Every measurable card here
    is a multi-stage chain -- `hopbyhop-cache-overflow-domclobber`,
    `charset-xss-cache-deception-orm`, `ssrf-crlf-request-smuggling`. Each spans
    three or four mechanisms, and one `classification.primary` cannot represent
    that, so class agreement between two multi-stage chains is close to random.
    The unit of retrieval is wrong: what transfers between challenges is a
    single STAGE, not a whole chain. Fixing transfer properly means indexing
    `chain[].stage` and `chain[].action` as separate retrievable units, which is
    a redesign of this file rather than a tuning pass on it.
    """
    try:
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import classify as classifier
        taxonomy = classifier.load_taxonomy()
        try:
            cstats = classifier.load_signal_stats()
        except Exception:
            cstats = None
        field = "source_signals" if source_mode else "observation_signals"
        hits = classifier.scan_text(
            text, classifier.compile_signals(taxonomy["classes"], field))
        if not hits:
            return {}
        ranked = classifier.rank(hits, taxonomy["classes"], cstats)
        return {r["class"]: r["score"] for r in ranked[:top]}
    except Exception:
        return {}


def score_card(card, text, lowered, stats=None, source_mode=True, scope=None,
               stage_index=None, query_tokens=None):
    signals = card.get("signals", [])
    if not signals:
        return None
    matched = [s for s in signals if found(s, lowered)]
    stack = [s for s in card.get("stack", []) if found(s, lowered)]

    card_class, class_origin = card_class_of(card) if scope else (None, None)
    class_score = (scope or {}).get(card_class)

    if not matched:
        # The transfer path. No literal of this card appears, so it is NOT a
        # match in the old sense and must never be graded `candidate` -- that
        # grade gates --record, and this evidence is far too weak to hand
        # decide.py a probe. What it IS worth is a named lead: "a solved card in
        # this mechanism family exists, read it", instead of silence.
        #
        # Two routes, in measured order of quality. Stage overlap reaches the
        # right peer at 25% in the top three; class agreement alone ceilings at
        # 12.5% with leads unbounded. So stages decide, and class is the weaker
        # fallback for a card whose stage prose is thin.
        stage_weight, stage_hits = stage_lead_score(card, query_tokens, stage_index)
        if stage_weight <= 0 and class_score is None:
            return None
        via = "stage" if stage_weight > 0 else "class"
        if stage_weight > 0:
            lead_rank = stage_weight
            confidence = min(0.30, round(0.08 + 0.01 * stage_weight, 3))
            why = ("not one of this card's own signals appears. It is offered "
                   "because %d term(s) of its chain prose appear in this target, "
                   "which is the mechanism vocabulary rather than the other "
                   "handout's names. Measured top-3 accuracy of this route: 25%%. "
                   "READ the chain for the mechanism and the traps; do NOT run "
                   "its probe as if it matched" % stage_hits)
        else:
            lead_rank = class_score
            confidence = min(0.20, round(0.06 + 0.01 * class_score, 3))
            why = ("not one of this card's own signals appears and its chain "
                   "prose did not overlap either; it is offered only because the "
                   "taxonomy ranks its class (%s) for this target, a route that "
                   "measured 12.5%% at best. Treat it as the weakest kind of "
                   "lead" % card_class)
        return {
            "match_via": via,
            "lead_rank": round(lead_rank, 3),
            "stage_terms_matched": stage_hits,
            "why_weak": why,
            "match_confidence": confidence,
            "id": card["id"],
            "match_weight": None,
            "class_of_card": card_class,
            "class_label_origin": class_origin,
            "class_score": None if class_score is None else round(class_score, 2),
            "card": card["_path"],
            "source_note": card.get("source_note"),
            "challenge": card.get("challenge", {}).get("name"),
            "category": card.get("challenge", {}).get("category"),
            "stack_matched": stack,
            "signals_matched": [],
            "signals_missing": list(signals),
            "signal_coverage": 0.0,
            # Deliberately low and bounded well under the weak/strong boundary.
            # This number must never read like a literal match.
            "suggested_priority": 10,
            "status": "weak",
            "preconditions_to_confirm": card.get("preconditions", {}),
            "first_confirming_probe": card.get("first_confirming_probe"),
            "blast_radius": card.get("blast_radius"),
            "known_traps": card.get("known_traps", []),
            "verification_of_original": card.get("verification", {}),
            "chain_outline": [s["stage"] + ": " + s["action"]
                              for s in card.get("chain", [])],
        }
    ratio = len(matched) / len(signals)
    # The coverage bar was measured on source trees, where the right card matches
    # a median 0.89 of its own signals. A one-line black-box observation cannot
    # reach that however good the match is — it simply does not contain enough
    # text — so holding it to the same bar graded real matches as coincidence.
    # Out of source mode the count of distinct matched signals is the only
    # honest test available.
    strong = len(matched) >= STRONG_MIN_SIGNALS and (
        ratio >= STRONG_COVERAGE or not source_mode)
    if stats:
        # rank on the raw summed rarity. An earlier attempt squashed it with
        # 1-exp(-weight) so the reported number would stay inside 0..1, but that
        # saturates above about weight 3, every strong card reported 0.95 and the
        # real ordering was decided by card id. Keep the weight for ranking and
        # derive a bounded number only for display.
        weight = sum(signal_weight(s, stats) for s in matched)
        confidence = min(0.95, round(weight / (weight + 3.0), 3))
    else:
        weight = None
        bonus = min(0.15, 0.05 * len(stack))
        confidence = min(0.95, round(ratio + bonus, 3))
    return {
        "id": card["id"],
        "match_weight": None if weight is None else round(weight, 4),
        # Recorded so a reader can tell a literal match from a family lead, and
        # so holdout_eval can score the two paths separately.
        "match_via": "signals+class" if class_score is not None else "signals",
        "class_of_card": card_class,
        "class_label_origin": class_origin,
        "card": card["_path"],
        "source_note": card.get("source_note"),
        "challenge": card.get("challenge", {}).get("name"),
        "category": card.get("challenge", {}).get("category"),
        "stack_matched": stack,
        "signals_matched": matched,
        "signals_missing": [s for s in signals if s not in matched],
        "signal_coverage": round(ratio, 3),
        "match_confidence": confidence,
        "suggested_priority": (max(10, min(90, int(round(confidence * 100))))
                               if strong else 10),
        # A card whose own signature is barely present is a coincidence, not a
        # lead. Measured by tools/holdout_eval.py over 24 held-out cards: the
        # right card matches a median 0.89 of its own signals, a wrong one 0.27,
        # yet match_confidence is computed from summed rarity and never saw that
        # difference — so the index reported a median 0.65 confidence on a card
        # that was not the answer, and never once abstained. decide.py rule 6
        # then ran that card's probe ahead of the agent's own hypothesis.
        "status": "candidate" if strong else "weak",
        "preconditions_to_confirm": card.get("preconditions", {}),
        "first_confirming_probe": card.get("first_confirming_probe"),
        "blast_radius": card.get("blast_radius"),
        "known_traps": card.get("known_traps", []),
        "verification_of_original": card.get("verification", {}),
        "chain_outline": [step["stage"] + ": " + step["action"] for step in card.get("chain", [])],
    }


def rebuild_stats(chains_dir):
    """Count, for every signal any card names, how many handouts contain it.

    A directory is excluded only when nothing but this toolkit's own scratch
    files is in it. Excluding every directory that merely *contains* a
    state.json shrank the corpus to 19 of 103, because tools/state.py writes the
    ledger into the challenge directory itself: every challenge actually worked
    on removed itself from the rarity statistics, so the more the toolkit was
    used the weaker its own ranking became.
    """
    workdir_names = {"solve.py", "state.json", "anomaly_map.json", "notes.md"}
    corpus = []
    base = os.path.join(ROOT, "challenges")
    for entry in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        path = os.path.join(base, entry)
        if not os.path.isdir(path):
            continue
        handout_files = 0
        for _, _, files in os.walk(path):
            handout_files += sum(1 for f in files if f not in workdir_names)
        if handout_files < 3:
            continue          # nothing but this toolkit's own scratch files
        corpus.append(read_source(path, skip_names=workdir_names).lower())

    signals = set()
    for card in load_chains(chains_dir):
        if "_error" not in card:
            signals.update(card.get("signals", []))
    # Count with found(), not raw containment: the denominator of the rarity
    # weight has to be measured the same way a hit is decided, or a signal is
    # scored against a frequency it can never actually reach.
    df = {s: sum(1 for t in corpus if found(s, t)) for s in sorted(signals)}
    data = {"corpus": len(corpus), "signals": len(df), "df": df}
    with open(SIGNAL_STATS, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(json.dumps({"written": os.path.relpath(SIGNAL_STATS, ROOT),
                      "corpus": data["corpus"], "signals": data["signals"]}, indent=2))
    return 0


def record_candidates(challenge, candidates):
    """Write the candidates into the challenge ledger.

    tools/decide.py rule 6 reads state["chain_candidates"] to return the card's
    own probe before the agent invents a new one. Nothing wrote that key, so the
    rule could only ever fire on a regression fixture. A card with no
    first_confirming_probe is dropped: rule 6 would hand the agent a null request.
    """
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import state as state_mod  # noqa: E402

    path = state_mod.path_for(challenge)
    if not os.path.isfile(path):
        return {"recorded": False,
                "reason": "no ledger for %r; run tools/state.py %s --category <cat> "
                          "--target <target> first" % (challenge, challenge)}
    with open(path, encoding="utf-8") as handle:
        current = json.load(handle)
    if not isinstance(current, dict):
        return {"recorded": False, "reason": "ledger is not an object; state not changed"}
    # Only a strong match is written to the ledger. decide.py rule 6 runs a
    # recorded card's probe ahead of the agent's own hypothesis, so a weak card
    # there spends a probe on a coincidence.
    candidates = [c for c in candidates if c.get("status") == "candidate"]
    kept = [{"id": c["id"],
             "first_confirming_probe": c["first_confirming_probe"],
             "blast_radius": c.get("blast_radius"),
             "known_traps": c.get("known_traps", []),
             "suggested_priority": c["suggested_priority"],
             "match_confidence": c["match_confidence"]}
            for c in candidates if c.get("first_confirming_probe")]
    current["chain_candidates"] = kept
    state_mod.atomic_json(path, current)
    return {"recorded": True, "count": len(kept),
            "dropped_without_probe": len(candidates) - len(kept),
            "ledger": os.path.relpath(path, ROOT),
            "next": "python3 tools/decide.py %s" % challenge}


def main():
    parser = argparse.ArgumentParser(description="Match observations against solved chains")
    parser.add_argument("observation", nargs="?")
    parser.add_argument("--source", help="challenge source path for white-box matching")
    parser.add_argument("-n", type=int, default=3, help="maximum candidates to return")
    parser.add_argument("--min-coverage", type=float, default=0.15,
                        help="minimum fraction of a card's signals that must appear")
    parser.add_argument("--chains", default=CHAINS)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--rebuild-stats", action="store_true",
                        help="recount signal frequencies over challenges/ and write "
                             "knowledge/signal-stats.json, then exit")
    parser.add_argument("--name", metavar="CHALLENGE",
                        help="the challenge name, for the local-solve check; "
                             "defaults to --record, else the --source basename")
    parser.add_argument("--record", metavar="CHALLENGE",
                        help="write the candidates into that challenge's ledger so "
                             "tools/decide.py returns the card's own probe first")
    args = parser.parse_args()

    if args.rebuild_stats:
        return rebuild_stats(args.chains)
    if not args.observation and not args.source:
        parser.error("provide an observation or --source")

    if args.source:
        if not os.path.exists(args.source):
            print(json.dumps({"mode": "chain-match", "error": "source path does not exist",
                              "path": args.source}), file=sys.stderr)
            return 2
        text = read_source(args.source)
        kind = "source"
    else:
        text = args.observation
        kind = "observation"
    lowered = text.lower()

    cards = load_chains(args.chains)
    stats = load_signal_stats()
    scope = class_scope(text, source_mode=bool(args.source))
    stage_index = build_stage_index(cards)
    query_tokens = stage_tokens(text)
    broken = [{"path": c.get("_path"), "error": c["_error"]} for c in cards if "_error" in c]
    scored, leads = [], []
    for card in cards:
        if "_error" in card:
            continue
        result = score_card(card, text, lowered, stats,
                            source_mode=bool(args.source), scope=scope,
                            stage_index=stage_index, query_tokens=query_tokens)
        if not result:
            continue
        # The coverage floor rejects a weak LITERAL match. A class lead has no
        # literal coverage by definition, so the floor does not apply to it; it
        # is bounded instead by being graded weak and by the cap below.
        if result.get("match_via") in ("stage", "class"):
            leads.append(result)
        elif result["signal_coverage"] >= args.min_coverage:
            scored.append(result)
    scored.sort(key=lambda item: (-(item.get("match_weight") or 0.0),
                                  -item["match_confidence"], item["id"]))
    top = scored[: max(1, args.n)]
    # Family leads are capped hard. Without a cap a broad class would surface a
    # dozen cards and the output would read as a dozen matches, which is the
    # opposite of what this adds.
    # Stage leads outrank class leads, because they measured twice as well.
    leads.sort(key=lambda item: (0 if item["match_via"] == "stage" else 1,
                                 -item["lead_rank"], item["id"]))
    leads = leads[:3]

    # Cheapest check in the tool and the one it did not have: has THIS NAME
    # already been solved on this disk? It runs before the index is consulted
    # and its result is placed first, because a recorded solve for this exact
    # challenge outranks every similarity score below it.
    name = args.name or args.record
    if not name and args.source:
        parts = [p for p in os.path.normpath(os.path.abspath(args.source)).split(os.sep) if p]
        # challenges/<name>/handout -> <name>, not "handout"
        skip = {"handout", "handouts", "src", "source", "app", "web", "dist", "files"}
        for part in reversed(parts):
            if part.lower() not in skip:
                name = part
                break
    already = local_solve(name)

    output = {
        "mode": "chain-match",
        "local_solve": already,
        "input": {"kind": kind, "value": args.source or args.observation,
                  "name_checked": name},
        "cards_available": len([c for c in cards if "_error" not in c]),
        "scoring": "signal-rarity" if stats else "signal-ratio",
        "candidates": top,
        "class_scope": scope,
        "family_leads": leads,
        "broken_cards": broken,
        "rules": [
            "A candidate is a hypothesis, not proof. Run its first confirming probe before acting on the chain.",
            "Confirm every precondition from your own evidence; this tool does not check them.",
            "On mismatch lower the priority and keep the hypothesis open; do not delete it.",
            "Read blast_radius before any write on a shared instance.",
        ],
    }
    strong = [c for c in top if c.get("status") == "candidate"]
    if already:
        output["next_action"] = (
            "STOP AND READ THESE FIRST -- this challenge name is already solved "
            "on this disk: " + ", ".join(already["read_these_before_any_probe"]) +
            ". A recorded solve for this exact name beats every score below it; "
            "a re-spawned instance usually needs only its host and port changed. "
            "Measured cost of not checking: a 13-agent sweep and 1.03M tokens on "
            "a challenge whose working solver was already on disk.")
    elif not strong:
        output["abstained"] = True
        output["next_action"] = (
            "no solved chain is a strong match" +
            (" (%d weak one(s) shown: their own signature is mostly absent, so "
             "treat them as coincidence, not as a lead)" % len(top) if top else "") +
            (" -- but %d card(s) in the same mechanism family are listed under "
             "family_leads: READ them for the mechanism and the traps, and do "
             "NOT run their probes as if they matched" % len(leads) if leads else "") +
            "; plan from source with tools/novel_plan.py and take the opening layer")
    elif not top:
        output["next_action"] = "no solved chain matches; proceed from the router's first probe"
    else:
        output["next_action"] = ("run the first_confirming_probe of " + top[0]["id"]
                                 + " and record the exact result")
    if args.record:
        try:
            output["recorded"] = record_candidates(args.record, top)
        except (ValueError, OSError) as exc:
            # a rejected challenge id, an unreadable ledger or malformed JSON.
            # Recording is a convenience; never lose the match output over it.
            output["recorded"] = {"recorded": False, "reason": str(exc)}
    print(json.dumps(output, ensure_ascii=False) if args.json
          else json.dumps(output, ensure_ascii=False, indent=2))
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
