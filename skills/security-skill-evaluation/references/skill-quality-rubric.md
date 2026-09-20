# Skill Quality Rubric

Score each skill on a 0-2 scale per dimension (0 = missing/poor, 1 =
partial, 2 = fully meets the bar). A skill scoring below 12/20 total
should be revised before being considered production-ready in the library.

## 1. Trigger Clarity (0-2)
```
0 - Description is vague; an agent couldn't reliably decide when to load
    this skill vs. a different one
1 - Description mentions the general domain but lacks specific trigger
    conditions (e.g. "web security" instead of "SSRF via URL-fetching
    functionality")
2 - Description gives specific, distinguishing trigger conditions that
    clearly differentiate this skill from adjacent ones
```

## 2. Scope & Safety Section (0-2)
```
0 - No safety/scope guidance at all
1 - Generic boilerplate safety note without skill-specific risk
    considerations
2 - Specific safety guidance tailored to this skill's actual risk profile
    (e.g. instance-corruption risk for a broad write, crash risk for kernel
    exploits, data handling for exfiltration)
```

## 3. Actionability (0-2)
```
0 - Purely abstract/conceptual advice, no concrete commands or examples
1 - Some concrete examples but missing key steps or requiring the agent
    to infer significant detail
2 - Concrete, copy-adaptable commands/code covering the main use cases,
    with enough context to adapt to the specific target
```

## 4. Decision Routing (0-2)
```
0 - No indication of when to move to a different skill or reference file
1 - Vague pointers ("see other resources") without specific routing logic
2 - Clear decision tree mapping specific signals/findings to specific
    next skills or reference files
```

## 5. Reference File Integrity (0-2)
```
0 - References listed that don't exist, or exist but are empty/truncated
1 - References exist but are shallow/low-value relative to what the
    SKILL.md implies they'll contain
2 - All referenced files exist, are substantive, and match what the
    SKILL.md describes them as covering
```

## 6. Currency/Accuracy (0-2)
```
0 - Contains techniques known to be broken/patched without any caveat
1 - Mostly current but missing version applicability notes
2 - Current techniques, with explicit notes on version/patch applicability
    where relevant (e.g. "works on Windows Server 2012-2022, verify
    against exact build")
```

## 7. Output Specification (0-2)
```
0 - No indication of what the agent should produce/report after using
    this skill
1 - Vague output expectation ("document findings")
2 - Specific output structure (e.g. "endpoint, parameter, DBMS type,
    confidence level, extracted data summary")
```

## 8. Focus/Cohesion (0-2)
```
0 - Skill tries to cover too many unrelated topics, diluting usefulness
1 - Mostly focused but has some tangential content that belongs elsewhere
2 - Tightly focused on its stated purpose, with tangential topics properly
    delegated to other skills via decision tree routing
```

## 9. Reversibility/Blast-Radius Awareness (0-2)
```
0 - No distinction made between low-risk and high-risk actions within
    the skill
1 - Some risk awareness but inconsistent application
2 - Explicitly flags higher-risk actions within the skill (destructive,
    detection-sensitive, or irreversible) distinctly from routine ones
```

## 10. Practical Testability (0-2)
```
0 - No way to verify the skill actually works as described (no eval task
    defined, content unverifiable)
1 - Content is plausible/sourced from reliable references but untested
    in a lab
2 - At least one eval task defined and/or content verified against a real
    lab/CTF environment
```

## Total Scoring Guide
```
18-20: Excellent, production-ready
14-17: Good, minor improvements recommended
12-13: Acceptable but should be revised soon
Below 12: Needs significant revision before relying on it
```

## Applying the Rubric
Use this rubric periodically (e.g. quarterly, or whenever a technique in
the skill's domain is known to have changed significantly) to re-score
existing skills and prioritize maintenance effort on the lowest-scoring,
most-frequently-used skills first.
