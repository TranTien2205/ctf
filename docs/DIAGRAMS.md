# Diagrams

Mermaid, so GitHub renders them in the browser. `ARCHITECTURE.md` carries the
same structure as ASCII, which works in a terminal where this file does not.
A Vietnamese edition with fuller commentary is at `docs/vi/SO-DO.md`.

Each diagram is followed by the thing a diagram cannot show: why an arrow is
there, or the failure it prevents.

---

## 1. The four planes, and one path through them

```mermaid
flowchart TD
    U["Operator<br/>prompt · skill · workflow"]

    subgraph RUNTIME["harness plane — argus/runtime"]
        LLM["LLM<br/>one loop, one profile per model"]
        CTX["session contract + ledger digest<br/>+ the controller's next action"]
    end

    subgraph BROKER["tool plane — argus/broker · 57 tools · 10 servers"]
        GATE{"the gate<br/>scope · risk tier<br/>hypothesis · budget"}
        EXEC["exec: argv only, no shell<br/>own process group · timeout · output cap"]
    end

    TOOLS["nmap · httpx · ffuf · nuclei · nikto · sqlmap<br/>playwright · per-CVE scripts"]

    subgraph LEDGER["control plane — argus/ledger"]
        EV["evidence<br/>redacted and bounded on the write path"]
        MATRIX{"proof matrix<br/>21 classes"}
        FIND["findings<br/>confirmed / candidate"]
        REF[("refusal log")]
    end

    REPORT["report<br/>confirmed · candidate · not demonstrated"]

    U --> LLM
    CTX --> LLM
    LLM -->|"MCP tools/call"| GATE
    GATE -->|"refused"| REF
    GATE -->|"allowed"| EXEC
    EXEC --> TOOLS
    TOOLS -->|"observation"| EV
    EV --> MATRIX
    MATRIX -->|"proven"| FIND
    MATRIX -->|"supported: names the missing check"| FIND
    MATRIX -->|"unproven: not recorded"| REF
    EV --> CTX
    FIND --> REPORT
    REF --> REPORT

    style GATE fill:#fde68a,stroke:#b45309,color:#000
    style MATRIX fill:#fde68a,stroke:#b45309,color:#000
    style REF fill:#fecaca,stroke:#b91c1c,color:#000
    style FIND fill:#bbf7d0,stroke:#15803d,color:#000
```

The arrow that matters most is `EV --> CTX`. The model's next decision is
computed from the ledger on disk rather than from its own summary of what
happened, which is why a run can be interrupted and resumed by a **different
model** with the engagement still exactly where it was.

---

## 2. One command through the gate

```mermaid
sequenceDiagram
    autonumber
    participant M as LLM
    participant B as broker Server.call
    participant H as hooks, the only write path
    participant T as the real tool
    participant L as ledger

    M->>B: tools/call proof.exec_marker
    B->>B: validate the argument schema
    B->>H: pre_probe: scope, tier, hypothesis, budget

    alt Refused
        H-->>L: append to the refusal log
        H-->>B: out-of-scope / tier-not-enabled /<br/>class-mismatch / budget-spent
        B-->>M: ok=false with the reason, NO probe charged
        Note over M,B: A refusal is a decision.<br/>Retrying it verbatim is never the answer.
    else Allowed
        H-->>B: allowed, with the remaining budget
        B->>T: argv, no shell, timeout
        T-->>B: bounded stdout/stderr
        B->>H: post_probe(evidence)
        H->>L: redact, write atomically, charge the budget
        H-->>B: probe_id + evidence_id
        B-->>M: summary first, then data, then "next"
    end
```

Two things the diagram does not say. `summary` comes first because a model reads
the first lines of a tool result far more reliably than the last. And a refusal
charges no probe: a refusal is not an observation, and charging one punishes the
model for asking correctly.

---

## 3. How a grade is decided

```mermaid
flowchart TD
    E["evidence records"] --> V{"VETO checks<br/>pass?"}
    V -->|"no — e.g. a destructive payload"| U1["unproven<br/>the evidence is disqualified"]
    V -->|"yes"| F{"FLOOR check<br/>passes?"}
    F -->|"no — e.g. only the control"| U2["unproven<br/>not about this class at all"]
    F -->|"yes"| R{"all REQUIRED<br/>checks pass?"}
    R -->|"all"| P["proven<br/>reportable as a finding"]
    R -->|"some"| S["supported<br/>recorded as a CANDIDATE,<br/>with the missing check named"]
    R -->|"none"| U3["unproven<br/>not recorded"]

    style P fill:#bbf7d0,stroke:#15803d,color:#000
    style S fill:#fde68a,stroke:#b45309,color:#000
    style U1 fill:#fecaca,stroke:#b91c1c,color:#000
    style U2 fill:#fecaca,stroke:#b91c1c,color:#000
    style U3 fill:#fecaca,stroke:#b91c1c,color:#000
```

| Mechanism | The measured failure behind it |
|---|---|
| **veto** | "proof command stayed benign" passes trivially when no command ran. As a *required* check it made any record whatsoever under an `rce` hypothesis recordable as a critical candidate. |
| **floor** | A record set carrying only its control graded `supported`: "every redirect destination stayed in origin" came back as partial progress toward an open redirect. |
| **required** | `rce` needs a declared command, the nonce in the **output**, and an identity line. Before the fix, a parameter that merely reflected the probe's token satisfied "the nonce was echoed" and the class graded `proven` with nothing executed — reproduced end to end, twice, independently. |

---

## 4. A hypothesis, from open to closed

```mermaid
stateDiagram-v2
    [*] --> open: ledger.open_hypothesis — one class, one entry point, one falsifier

    open --> open: probe, at most 6 per class
    open --> falsified: ledger.falsify — an evidence id is REQUIRED
    open --> parked: ledger.park — budget spent, or a change of direction
    open --> confirmed: the evidence meets the requirement

    parked --> open: ledger.revive — new evidence bears on it
    confirmed --> candidate: ledger.cross_verify — a different family DISAGREES

    falsified --> [*]
    candidate --> [*]
    confirmed --> [*]

    note right of parked
        Park, do not delete.
        A direction that looks wrong
        is usually unfinished.
    end note
```

A spent budget changes strategy rather than ending the engagement: reuse a known
chain, reclassify the surface, research the stack, widen the surface, fan out a
fleet, hand off to a human. `report` fires only when every rung is spent.

---

## 5. The orchestrator

```mermaid
flowchart LR
    OBJ["objective"] --> PLAN

    subgraph PLAN["planner — runs ONCE"]
        P1["the strongest model<br/>reads the ledger, writes tasks, STOPS"]
        P2{"validate the plan"}
        P1 --> P2
        P2 -->|"out of scope"| X1["task dropped"]
        P2 -->|"refused class"| X2["task dropped"]
        P2 -->|"dependency cycle"| X3["plan rejected"]
    end

    P2 -->|"valid"| ART[("plan.json + tasks/<br/>an artifact on disk")]
    ART --> ROUTE

    subgraph ROUTE["router"]
        R1["kind → role → candidates"]
        R2["two rules that are not negotiable"]
        R1 --> R2
    end

    ROUTE --> SCHED["scheduler<br/>ready queue + fixed slots<br/>a free slot is filled AT ONCE"]
    SCHED --> H1["our harness<br/>tightest control"]
    SCHED --> H2["claude code<br/>its own loop"]
    SCHED --> H3["opencode<br/>different credentials"]

    H1 --> BUS
    H2 --> BUS
    H3 --> BUS
    BUS[("shared context on disk<br/>decisions.json · briefs · reports · ledger")]
    BUS --> VER["verify<br/>a DIFFERENT FAMILY reads the evidence,<br/>never the reasoning"]
    VER --> OUT["report"]

    style R2 fill:#fde68a,stroke:#b45309,color:#000
    style BUS fill:#dbeafe,stroke:#1d4ed8,color:#000
```

The two rules: review is cross-family, because two models that agree from a
shared prior are not a check; and breadth goes to the cheapest capable model
while judgement does not, because a plan written by the cheapest model is a false
economy — it is the one artifact the whole engagement is shaped by.

What is absent: nothing here understands the whole engagement. A plan on disk, a
decisions store any agent can read, and a ledger every tool call writes to, so an
agent joining at task nine knows what the first eight established.

---

## 6. What this machine actually routes to

Measured with `argus fleet` under the default `balanced` policy.

```mermaid
flowchart LR
    subgraph JUDGE["judgement — full capability kept"]
        PL["plan"] --> OPUS["claude-opus-5-5<br/>via Claude Code"]
        RV["review"] --> DS["deepseek-v4-pro<br/>via opencode-go<br/>CROSS-FAMILY to Claude"]
        RP["report"] --> SON["claude-sonnet-5-5"]
    end

    subgraph EXECW["execution"]
        PB["probe · exploit · prove"] --> SON2["claude-sonnet-5-5<br/>our harness"]
    end

    subgraph BREADTH["breadth — cheapest capable"]
        RC["recon · triage"] --> FLASH["deepseek-flash"]
        RS["research<br/>whole bundles, advisories"] --> GEM["gemini-3.5-flash<br/>1M context"]
    end

    style OPUS fill:#fde68a,stroke:#b45309,color:#000
    style DS fill:#ddd6fe,stroke:#6d28d9,color:#000
    style FLASH fill:#bbf7d0,stroke:#15803d,color:#000
    style GEM fill:#bbf7d0,stroke:#15803d,color:#000
```

The `strengths` fields in `argus/runtime/profiles/models.json` are **routing
hypotheses, not measurements**. Correcting one is a JSON edit, and `argus metrics`
is how a measurement would contradict it.

---

## 7. The six refusals

```mermaid
flowchart TD
    C["one tool call"] --> S{"target in scope?"}
    S -->|"no"| R1["out-of-scope<br/>an empty scope allows NOTHING,<br/>deny wins over allow"]
    S -->|"yes"| T{"tool's risk tier<br/>enabled?"}
    T -->|"no"| R2["tier-not-enabled<br/>intrusive will not open without<br/>an authorisation note"]
    T -->|"yes"| HY{"names a hypothesis?"}
    HY -->|"no / wrong class"| R3["class-mismatch<br/>a probe that names none<br/>cannot falsify anything"]
    HY -->|"yes"| B{"class budget left?"}
    B -->|"spent"| R4["budget-spent<br/>change the QUESTION,<br/>not the payload"]
    B -->|"left"| RUN["the command runs"]
    RUN --> P{"record a finding?"}
    P -->|"evidence falls short"| R5["unproven<br/>not recorded"]
    P -->|"class not provable here"| R6["refused-class<br/>e.g. DoS: the proof is the damage"]
    P -->|"meets it"| OK["recorded"]

    style R1 fill:#fecaca,stroke:#b91c1c,color:#000
    style R2 fill:#fecaca,stroke:#b91c1c,color:#000
    style R3 fill:#fecaca,stroke:#b91c1c,color:#000
    style R4 fill:#fecaca,stroke:#b91c1c,color:#000
    style R5 fill:#fecaca,stroke:#b91c1c,color:#000
    style R6 fill:#fecaca,stroke:#b91c1c,color:#000
    style OK fill:#bbf7d0,stroke:#15803d,color:#000
```

All six go to `log/refusals.jsonl`, which is what lets `argus metrics` answer
"how many times did this agent try to act outside what it was allowed to do" —
the number claim 3 in `ARCHITECTURE.md` section 6 is about.

---

## 8. The measured live run

`deepseek-v4-pro` through `opencode-go`, driven by our harness against the
loopback fixture. Task: prove or kill command injection in the `host` parameter
of `/ping`.

```mermaid
sequenceDiagram
    autonumber
    participant M as deepseek-v4-pro
    participant L as ledger
    participant K as proof matrix
    participant T as target (fixture)

    M->>L: ledger.open_hypothesis (rce)
    L-->>M: hy-38453b6a67 open
    M->>K: proof.requirement (rce)
    K-->>M: declared command + nonce in output + identity line
    Note over M,K: It read the requirement BEFORE probing.<br/>Exactly the discipline the contract asks for.
    M->>T: http.probe (baseline)
    T-->>M: 200, 29 bytes
    M->>T: proof.exec_marker (id; echo nonce)
    T-->>M: nonce returned, uid=1000(kali)
    M->>K: grade
    K-->>M: proven
    M->>L: ledger.record_finding
    L-->>M: fi-18417e082e — confirmed
    M->>L: ledger.read_evidence
    L-->>M: 2 records — it re-read its own work
```

| Measurement | Value |
|---|---|
| probes spent | 2 |
| refusals | 0 |
| findings | 1, graded `proven` |
| tokens | 54,083 |
| cost | $0.017 |
| wall clock | 777s — **129s per step** |

129 seconds per step is the number worth keeping: it is the price of a stateless
CLI backend, which re-sends the whole prompt and pays a process start every step.
The key-based HTTP adapters would not, and they still have no live run behind
them.

---

## 9. The repository, as components

```mermaid
flowchart TD
    subgraph PKG["argus/ — 6,400 lines"]
        LED["ledger/<br/>scope · state · proof · hooks<br/>decide · report · lock · identities"]
        BRK["broker/<br/>mcp · exec · httpkit · collector<br/>servers/ ×10"]
        RUN["runtime/<br/>loop · context · prompts<br/>providers/ ×8 · profiles/"]
        ORC["orchestrator/<br/>planner · workflows · router<br/>scheduler · runner · bus · verify · metrics"]
        KNW["knowledge/<br/>playbook · chains"]
        CLI["cli.py"]
    end

    subgraph DATA["data — extending means editing JSON, not code"]
        PB["knowledge/playbook.json<br/>21 ladders"]
        MD["profiles/models.json<br/>12 profiles"]
        WF["workflows/ ×4"]
        EX["scripts/exploits/<br/>registry + template"]
        SK["skills/ ×18"]
    end

    subgraph TEST["test/ — five layers, 1,226 checks"]
        T1["unit 159"]
        T2["consistency 995"]
        T3["harness 12"]
        T4["e2e 60"]
        T5["baselines"]
        FX["fixtures/vulnapp.py<br/>deliberately vulnerable, loopback only"]
    end

    CLI --> ORC --> RUN --> BRK --> LED
    KNW --> LED
    PB --> KNW
    MD --> RUN
    WF --> ORC
    EX --> BRK
    SK --> KNW
    FX --> T4
    LED --> T1
    BRK --> T2

    style LED fill:#fde68a,stroke:#b45309,color:#000
    style DATA fill:#dbeafe,stroke:#1d4ed8,color:#000
    style TEST fill:#dcfce7,stroke:#15803d,color:#000
```

Four extension points, and three of them are data files: a vulnerability class, a
probe ladder, a per-CVE script, a model profile. Only adding an MCP tool takes
code, and that is one decorated function.
`skills/extending-argus/SKILL.md` holds the contract for all four.

---

## 10. What these diagrams do not show

- **Three of the five research claims need live models and have not been run.**
  `ARCHITECTURE.md` section 6 names each with the baseline it needs.
- **The offline half exists**, and its subject is a scripted driver rather than a
  model: it measures what the *gate* does to a given sequence of actions. The
  ungated write path admitted 4 findings whose evidence meets no part of its
  class requirement; the gated path admitted 0 — and `test/baselines.py` says
  that is a property of the gate, not a discovery about models.
- **No run has reused a chain card on a second target**, so "the second run
  against a stack is cheaper" is a design claim.
- **Seven classes have no depth skill**, named in `skills/INDEX.md`.
- **The fixture is a fixture, not a benchmark**: exact ground truth, and no
  evidence about generalisation.
