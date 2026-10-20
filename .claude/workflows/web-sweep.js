// web-sweep.js -- fan the ctf-web-* fleet over ONE authorized web challenge and
// hand back the ledger commands. Run it with the Workflow tool:
//
//   Workflow({ name: 'web-sweep',
//              args: { challenge: 'acme', handout: 'challenges/acme/src',
//                      target: 'http://10.0.0.5:3000/' } })
//
// WHY THIS FILE EXISTS. tools/subagent_fanout.py only PRINTS briefs: every
// branch of its main() ends in print(json.dumps(...)) and the field it emits is
// literally named "spawn_agent", a string telling a human which agent to launch.
// Measured end to end, the path from a challenge to a flag was 13 steps of which
// only 3 were automatic -- the fan-out print, --validate and --merge. Every
// launch, every report hand-off and every ledger write was manual. This script
// closes exactly those gaps and nothing else.
//
// WHAT IT DELIBERATELY DOES NOT DO. It never writes challenges/<name>/state.json
// and never runs tools/hooks.py. ORCHESTRATION.md and AGENTS.md both forbid
// delegating the ledger, for a concrete reason: tools/decide.py enforces five
// probes per class and twenty-five per challenge, and ten agents recording
// probes in parallel would spend that budget in one round and force a class
// switch on classes nobody worked. Agents measure; the main thread records. This
// script returns the commands for the main thread to run.
//
// SANDBOX FACTS this script is written around: there is no filesystem and no
// Node API here, so it cannot run subagent_fanout.py itself -- a cheap agent
// does that in the Brief phase. Date.now(), new Date() and Math.random() all
// throw, so nothing here is timed or randomised.

export const meta = {
  name: 'web-sweep',
  description: 'Fan the ctf-web-* fleet over one authorized web challenge and return the ledger commands',
  phases: [
    { title: 'Spec', detail: 'four requests for a published API spec; a spec ends the sweep' },
    { title: 'Brief', detail: 'subagent_fanout --web, handouts on disk, chain-card short-circuit' },
    { title: 'Recon', detail: 'the endpoint inventory every other family probes against' },
    { title: 'Sweep', detail: 'one ctf-web-* agent per family whose source signals actually fired' },
    { title: 'Merge', detail: 'validate each report, merge, emit the hooks commands' },
  ],
}

const A = args || {}
const CHALLENGE = A.challenge || 'unnamed'
const HANDOUT = A.handout || ''
const TARGET = A.target || ''
const FORCE_ALL = A.all === true
// Skips the published-spec stop condition. There when the spec turns out to be
// a dead end, not as a default: the default exists because the sweep it skips
// cost 42 minutes and 1.1M tokens to rediscover a document already on disk.
const FORCE_SWEEP = A.forceSweep === true
// The harness caps concurrent agents at min(16, cpus - 2); measured 6 on this
// box. tools/contest/dispatch.py caps a wave at MAX_USEFUL_WIDTH = 6 for the
// same reason and HOLDS the rest, because a queued agent is serial time wearing
// a parallel costume. This workflow had no cap at all and launched ten, so the
// two components disagreed and the first live run paid for it in wall clock.
const MAX_WIDTH = typeof A.maxWidth === 'number' ? A.maxWidth : 6
const WRITE_BUDGET = typeof A.writeBudget === 'number' ? A.writeBudget : 0

// ---------------------------------------------------------------- schemas

// The fan-out return contract, from `python3 tools/subagent_fanout.py --contract`.
// Passing this as `schema` is what removes the measured report-staging gap: the
// agents used to return JSON in chat while --validate and --merge read files off
// disk, so a human had to paste every report into a file first. With a schema the
// value comes back already validated and structured.
const CONTRACT = {
  type: 'object',
  properties: {
    layer_id: { type: 'string', description: 'the family id from the brief' },
    challenge: { type: 'string' },
    class: { type: ['string', 'null'], description: 'bug class id from knowledge/bug-classes.json, or null if undecided' },
    files_read: { type: 'array', items: { type: 'string' }, description: 'path:line entries' },
    probes: {
      type: 'array',
      description: 'at most five, read-only',
      items: {
        type: 'object',
        properties: {
          request: { type: 'string' },
          transport: { type: 'string', enum: ['ok', 'timeout', 'reset', 'error', 'empty'] },
          status: { type: ['number', 'null'] },
          response_excerpt: { type: 'string', description: 'verbatim bytes, pasted from tool output, never from memory' },
          evidence: { type: 'string', description: 'MUST be a substring of response_excerpt' },
          evidence_kind: { type: 'string', enum: ['surface', 'class', 'impact', 'transport'] },
          verdict: { type: 'string', enum: ['confirms', 'refutes', 'falsifies', 'inconclusive'] },
        },
        required: ['request', 'transport', 'verdict'],
      },
    },
    falsifier_outcome: { type: 'string', enum: ['held', 'broken', 'not-measured'] },
    conclusion: { type: 'string' },
    cost_minutes: { type: 'number' },
  },
  required: ['layer_id', 'challenge', 'probes', 'falsifier_outcome', 'conclusion'],
}

const BRIEF_OUT = {
  type: 'object',
  properties: {
    ran: { type: 'string', description: 'the exact fan-out command executed' },
    strong_chain_match: {
      type: ['object', 'null'],
      description: 'the card subagent_fanout graded a candidate, or null',
      properties: {
        id: { type: 'string' },
        first_confirming_probe: { type: 'string' },
        known_traps: { type: 'array', items: { type: 'string' } },
        blast_radius: { type: ['string', 'null'] },
      },
    },
    launch_order: { type: 'array', items: { type: 'string' } },
    briefs: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          family: { type: 'string' },
          spawn_agent: { type: 'string' },
          write_shaped: { type: 'boolean' },
          signals_fired: { type: 'number' },
          brief_json: { type: 'string', description: 'the whole brief object, JSON-encoded' },
        },
        required: ['family', 'spawn_agent', 'brief_json'],
      },
    },
    handouts_on_disk: {
      type: 'array', items: { type: 'string' },
      description: 'what ls challenges/<name>* actually found',
    },
    source_present: { type: 'boolean' },
  },
  required: ['ran', 'briefs', 'source_present'],
}

const MERGE_OUT = {
  type: 'object',
  properties: {
    validated: { type: 'number' },
    rejected: { type: 'array', items: { type: 'string' } },
    commands_for_the_main_thread: { type: 'array', items: { type: 'string' } },
    confirming_families: { type: 'array', items: { type: 'string' } },
    reports_dir: { type: 'string' },
    summary: { type: 'string' },
  },
  required: ['commands_for_the_main_thread', 'summary'],
}

// ------------------------------------------------------------- phase 0: spec

// THE STOP CONDITION THIS SWEEP WAS MISSING, and it is the expensive lesson of
// its first live run. On GoNuclear (HTB easy) this workflow spawned twelve
// agents, ran 42 minutes and spent 1.1M tokens. The answer was a 7 KB document
// at /api/openapi.json: it declared `POST /userDetails` with NO `security` key
// and a response schema containing `verifyToken`, so the registration
// email-verification gate was readable by anyone. One agent found that file in
// the first wave; the other eleven added nothing that led to the flag, and the
// solve afterwards took six requests.
//
// A fan-out is for mapping an UNKNOWN surface. A published spec IS the surface,
// so finding one must END the sweep rather than start it. FastAPI, Flask-RESTX,
// Spring and ASP.NET all publish one by default, so this costs four requests
// and can save the whole run.

const SPEC_OUT = {
  type: 'object',
  properties: {
    spec_found: { type: 'boolean' },
    spec_url: { type: ['string', 'null'] },
    spec_status: { type: ['number', 'null'] },
    spec_kind: { type: ['string', 'null'], description: 'openapi | swagger | graphql | none' },
    paths_total: { type: ['number', 'null'] },
    operations: {
      type: 'array',
      description: 'every operation the spec declares',
      items: {
        type: 'object',
        properties: {
          method: { type: 'string' },
          path: { type: 'string' },
          summary: { type: ['string', 'null'] },
          has_security: { type: 'boolean', description: 'false when the spec declares NO security for it' },
          request_fields: { type: 'array', items: { type: 'string' } },
          response_fields: { type: 'array', items: { type: 'string' } },
        },
        required: ['method', 'path', 'has_security'],
      },
    },
    unauthenticated_operations: {
      type: 'array', items: { type: 'string' },
      description: 'METHOD path for every operation with no security; read these first',
    },
    secret_shaped_response_fields: {
      type: 'array', items: { type: 'string' },
      description: 'response fields whose NAME suggests a secret: token, secret, key, hash, password, otp, code',
    },
    evidence: { type: ['string', 'null'], description: 'verbatim bytes proving the spec is served' },
    tried: { type: 'array', items: { type: 'string' } },
  },
  required: ['spec_found', 'tried'],
}

phase('Spec')

const spec = await agent([
  'You are the spec stage of an authorized CTF web sweep. Four to eight GET',
  'requests, read-only, on the supplied port only. Do not probe anything else',
  'and do not try to exploit what you find.',
  '',
  'Target: ' + (TARGET || '(none supplied)'),
  '',
  'Ask one question: does this app PUBLISH its own API specification? Try these',
  'and report every one in `tried` with its status, so a miss is a measured',
  'negative rather than an untried path:',
  '    /openapi.json          /api/openapi.json',
  '    /swagger.json          /api/swagger.json',
  '    /v3/api-docs           /v2/api-docs            (Spring)',
  '    /swagger/v1/swagger.json                       (ASP.NET)',
  '',
  'Use: python3 tools/web/http_probe.py --url <url> --challenge ' + CHALLENGE,
  'or plain curl with -w for the status. Stop at the first 200 that parses as a',
  'spec; there is no reason to collect two.',
  '',
  'IF YOU FIND ONE, this is the whole job and you must do it carefully, because',
  'the sweep behind you is cancelled on your answer:',
  '  * list EVERY operation with its method and path;',
  '  * for each, set has_security FALSE when the spec declares no security for',
  '    it. This is the single most valuable field in the document. An operation',
  '    with no security is reachable with no credentials, and on the challenge',
  '    that produced this stop condition exactly one such operation returned',
  '    another user\'s verification token;',
  '  * list the request and response FIELD NAMES from the referenced schemas,',
  '    following $ref into components.schemas;',
  '  * put every response field whose NAME suggests a secret into',
  '    secret_shaped_response_fields: token, verifyToken, secret, key, hash,',
  '    password, otp, code, session. Name-shaped is enough; do not fetch them.',
  '  * paste a verbatim excerpt into `evidence`.',
  '',
  'IF YOU FIND NONE, set spec_found false and list what you tried. That is a',
  'useful measured negative and the sweep continues.',
  '',
  'Report only what you read. Do not infer an operation the spec does not list.',
].join('\n'), {
  label: 'spec:published-api',
  phase: 'Spec',
  agentType: 'general-purpose',
  model: 'haiku',
  effort: 'low',
  schema: SPEC_OUT,
})

if (!FORCE_SWEEP && spec && spec.spec_found && (spec.operations || []).length) {
  const open = spec.unauthenticated_operations || []
  const secrets = spec.secret_shaped_response_fields || []
  log('published spec at ' + spec.spec_url + ' -- cancelling the sweep')
  return {
    ok: true,
    short_circuit: 'published_api_spec',
    challenge: CHALLENGE,
    spec: spec,
    why: 'the app publishes its own specification, so the surface is KNOWN and a '
       + 'fan-out has nothing left to map. Measured on the run that produced this '
       + 'stop condition: twelve agents, 42 minutes and 1.1M tokens to find this '
       + 'same document, then six requests to the flag once it was read.',
    read_these_first: open,
    secret_shaped_fields: secrets,
    the_main_thread_must_now: [
      '# 1. read the spec field by field. The operations with NO security are the',
      '#    surface that needs no credentials at all:',
      ...open.map(function (o) { return '#      ' + o }),
      ...(secrets.length
        ? ['# 2. these response field NAMES look like secrets, and an unauthenticated',
           '#    operation that returns one is the whole bug:',
           ...secrets.map(function (s) { return '#      ' + s })]
        : ['# 2. no secret-shaped response field name; look instead for an object id',
           '#    in a path and test ownership on it']),
      'python3 tools/state.py ' + CHALLENGE + ' --hypothesis "<the unauthenticated '
        + 'operation and what it returns>" --bug-class <class> --next "<one request>"',
      'python3 tools/web/http_probe.py --url <the unauthenticated operation> '
        + '--challenge ' + CHALLENGE + '   # emits post-probe with --response filled in',
      '# re-run this workflow with args.forceSweep true ONLY if the spec turns out '
        + 'to be a dead end',
    ],
    note: 'args.forceSweep true skips this stop condition when you want the sweep anyway',
  }
}

log(spec && spec.spec_found
  ? 'a spec was reported but it listed no operation; sweeping anyway'
  : 'no published spec (' + ((spec && (spec.tried || []).length) || 0)
    + ' path(s) tried) -- the surface is unknown, so the sweep is justified')

// ---------------------------------------------------------------- phase 1

phase('Brief')

const briefPrompt = [
  'You are the brief stage of an authorized CTF web sweep. Run commands and',
  'report their real output. Do not probe the target and do not solve anything.',
  '',
  'Working directory: /home/kali/ctf-v2',
  '',
  'STEP 1 - check what is already on disk. A measured 12 minutes was once lost',
  'reconstructing a 236-line source file over HTTP while it sat in the handout',
  'directory, so this runs first:',
  '    ls -la challenges/' + CHALLENGE + '* 2>/dev/null',
  'Report every path found in handouts_on_disk.',
  '',
  'STEP 2 - run the fan-out and return its JSON verbatim:',
  // The SOURCE argument is optional (nargs="?"), so a black-box target OMITS it
  // entirely. An earlier version interpolated the string "<no handout>" here,
  // which the tool correctly rejected as "not a directory" -- and that made it
  // look as if there were no black-box mode when there always was one.
  '    python3 tools/subagent_fanout.py --web' + (HANDOUT ? ' ' + HANDOUT : '') +
    ' --challenge ' + CHALLENGE + (TARGET ? ' --target ' + TARGET : '') +
    ' --write-budget ' + WRITE_BUDGET,
  '',
  HANDOUT
    ? 'If that path does not exist, re-run the command with the --web flag and NO '
      + 'path at all, and set source_present false.'
    : 'No handout was supplied, so the command above deliberately passes --web '
      + 'with no path: that is the black-box mode and all ten families come back '
      + 'with no reading list. Set source_present false.',
  '',
  'STEP 3 - fill the output schema from that JSON:',
  '  * strong_chain_match: the tool computes this itself. If it is set, copy the',
  '    card id, its first_confirming_probe, its known_traps and its blast_radius.',
  '    If the tool reports nothing, set it null. Do NOT invent a card.',
  '  * briefs: one entry per brief the tool printed. brief_json must be the',
  '    COMPLETE brief object re-encoded as a JSON string - the downstream agents',
  '    are driven from it, so a truncated brief breaks the sweep.',
  '  * signals_fired: the length of that brief\'s source_signals_that_fired array.',
  '',
  'Report exactly what the tool printed. Invent no family and no agent name.',
].join('\n')

const brief = await agent(briefPrompt, {
  label: 'brief:fanout',
  phase: 'Brief',
  agentType: 'general-purpose',
  model: 'haiku',
  effort: 'low',
  schema: BRIEF_OUT,
})

if (!brief) {
  return {
    ok: false,
    stage: 'Brief',
    reason: 'the brief agent returned nothing; run tools/subagent_fanout.py --web by hand',
  }
}

// THE FASTEST PATH TO A FLAG, and it is already computed for us. A card graded
// `candidate` hands back a probe proven in this tree, costs no request, and was
// derived offline from the handout. Sweeping past it would pay the 7-10 minute
// spawn floor, several times over, to rediscover an answer we already hold.
if (brief.strong_chain_match && brief.strong_chain_match.id) {
  const card = brief.strong_chain_match
  log('strong chain card ' + card.id + ' -- skipping the sweep entirely')
  return {
    ok: true,
    short_circuit: 'strong_chain_match',
    card: card,
    handouts_on_disk: brief.handouts_on_disk || [],
    why: 'a chain card graded candidate carries a first probe already proven '
       + 'here. ORCHESTRATION.md: a known answer beats ten parallel guesses, and '
       + 'ten agents cost 7-10 minutes each to rediscover it.',
    commands_for_the_main_thread: [
      'python3 tools/chain_match.py --source ' + (HANDOUT || '<handout>')
        + ' --record ' + CHALLENGE,
      'python3 tools/decide.py ' + CHALLENGE + '   # must hand back the card probe',
      '# read blast_radius before any write-shaped probe: '
        + (card.blast_radius || '(none recorded on the card)'),
      '# then run the card probe through the gate, from THIS thread:',
      'python3 tools/web/http_probe.py --url <url> --emit-hook-cmd',
    ],
    known_traps: card.known_traps || [],
  }
}

// ---------------------------------------------------------------- phase 2

const allBriefs = brief.briefs || []

// Recon and bundle produce the endpoint inventory every other family probes
// against, which is why subagent_fanout orders them first. This barrier is
// deliberate and justified, not habit: a family probing without the inventory
// re-derives it or misses an endpoint, and a missed endpoint is the measured
// most common cause of a stuck web challenge in this tree.
const firstWave = allBriefs.filter(function (b) {
  return b.family === 'recon' || b.family === 'bundle'
})
const rest = allBriefs.filter(function (b) {
  return b.family !== 'recon' && b.family !== 'bundle'
})

function probePrompt(b, inventoryNote) {
  return [
    'You are the ' + b.family + ' family of an authorized CTF web sweep on',
    'challenge "' + CHALLENGE + '"' + (TARGET ? ' at ' + TARGET : '') + '.',
    '',
    'Your brief, from tools/subagent_fanout.py --web. Every field in it was read',
    'from knowledge/bug-classes.json or from the handout; none of it is invented.',
    'Follow it rather than your own plan:',
    '',
    b.brief_json,
    '',
    inventoryNote || '',
    '',
    'HARD LIMITS, from the fan-out contract:',
    '  * at most five probes, read-only. GET and HEAD only.',
    '  * only the supplied port. Never scan the host.',
    '  * evidence MUST be a verbatim substring of response_excerpt from the SAME',
    '    probe. Paste the excerpt from the tool output, never from memory -- a',
    '    subagent once mistyped one word of a 404 body and the validator accepted',
    '    the report because the evidence substring sat outside the typo. Prefer',
    '    python3 tools/web/http_probe.py, which holds request and response',
    '    together for exactly this reason.',
    '  * verdict confirms requires transport ok AND evidence_kind class or impact.',
    '    A login redirect, a registration success or a rendered form is SURFACE',
    '    evidence and cannot confirm a class. A timeout is never a confirm.',
    '  * you have no Edit tool. Write only under your own workspace directory.',
    '  * do NOT run tools/hooks.py or tools/state.py. The main thread records.',
    '',
    'If your falsifier breaks, say so and stop early; a measured negative is a',
    'result and it is what stops the next agent re-walking this layer.',
    '',
    'Return the contract JSON.',
  ].join('\n')
}

let inventory = ''
let reconOut = []
if (firstWave.length) {
  phase('Recon')
  log('recon wave first, alone: ' + firstWave.map(function (b) { return b.family }).join(', '))
  const reconReports = await parallel(firstWave.map(function (b) {
    return function () {
      return agent(probePrompt(b, ''), {
        label: 'recon:' + b.family,
        phase: 'Recon',
        agentType: b.spawn_agent,
        schema: CONTRACT,
      })
    }
  }))
  const got = reconReports.filter(Boolean)
  if (got.length) {
    inventory = [
      'RECON ALREADY RAN. Probe against this inventory rather than re-deriving it:',
      JSON.stringify(got.map(function (r) {
        return { family: r.layer_id, files_read: r.files_read,
                 conclusion: r.conclusion,
                 endpoints_seen: (r.probes || []).map(function (p) { return p.request }) }
      })),
    ].join('\n')
  }
    reconOut = got
}

// ---------------------------------------------------------------- phase 3

phase('Sweep')

// Width by EVIDENCE, not by appetite. A family whose source_signals_that_fired
// is empty is the cheapest to park, not the cheapest to run: nothing in the
// handout points at it, and one agent costs 7-10 minutes whatever it finds.
// With no source present nothing can fire, so a black-box target sweeps wide.
const blackBox = !brief.source_present
let selected = rest
if (!FORCE_ALL && !blackBox) {
  const fired = rest.filter(function (b) { return (b.signals_fired || 0) > 0 })
  if (fired.length) selected = fired
}

// Width cap, so this workflow and tools/contest/dispatch.py stop disagreeing.
// The harness caps concurrent agents at min(16, cpus - 2), measured 6 here, and
// dispatch.py already holds anything over MAX_USEFUL_WIDTH because a queued
// agent is serial time wearing a parallel costume. This workflow had no cap and
// launched ten, so the first live run paid for the disagreement in wall clock.
//
// Declared at module scope on purpose: the return envelope at the bottom reports
// what was held, and an earlier version declared this inside the block below,
// which cost a completed 13-agent run to `ReferenceError: held is not defined`
// AFTER every agent had finished. A variable the envelope reads is part of the
// envelope's scope, not the phase's.
let held = []
if (selected.length > MAX_WIDTH) {
  held = selected.slice(MAX_WIDTH)
  selected = selected.slice(0, MAX_WIDTH)
  log('HELD ' + held.length + ' family(ies) over the width cap of ' + MAX_WIDTH
      + ': ' + held.map(function (b) { return b.family }).join(', ')
      + ' -- they would only queue behind the first wave. Re-run with a higher '
      + 'args.maxWidth, or after reading what the first wave returned.')
}

const parked = rest.filter(function (b) {
  return selected.indexOf(b) === -1 && held.indexOf(b) === -1
})
if (parked.length) {
  log('parked ' + parked.length + ' family(ies) with no source signal: '
      + parked.map(function (b) { return b.family }).join(', '))
}

// The race family's winning probe is write-shaped by nature. The subagent
// proposes it; the main thread executes it after reading blast_radius and
// passing --write-ack. Running it here would be a write we never acknowledged.
const writeShaped = selected.filter(function (b) { return b.write_shaped === true })
const readOnly = selected.filter(function (b) { return b.write_shaped !== true })

log('sweeping ' + readOnly.length + ' read-only family(ies)'
    + (writeShaped.length ? ' plus ' + writeShaped.length + ' write-shaped (proposal only)' : ''))

const sweepReports = await parallel(readOnly.concat(writeShaped).map(function (b) {
  return function () {
    const extra = b.write_shaped
      ? '\nYOUR FAMILY IS WRITE-SHAPED. Do NOT fire the write. Measure the '
        + 'check-then-act pair in source, establish the SERIAL baseline, and '
        + 'return the exact interleaving run, its concurrency, its attribution '
        + 'and its cleanup as a PROPOSAL. The main thread fires it with '
        + '--write-ack after reading blast_radius.'
      : ''
    return agent(probePrompt(b, inventory) + extra, {
      label: 'sweep:' + b.family,
      phase: 'Sweep',
      agentType: b.spawn_agent,
      schema: CONTRACT,
    })
  }
}))

const reports = reconOut.concat(sweepReports.filter(Boolean))

if (!reports.length) {
  return {
    ok: false,
    stage: 'Sweep',
    reason: 'no family returned a report',
    parked_families: parked.map(function (b) { return b.family }),
  }
}

// ---------------------------------------------------------------- phase 4

phase('Merge')

// The schema above guarantees SHAPE. It does not check the semantic rules, and
// those are the ones that matter: evidence inside excerpt, confirms requires
// transport ok, a write-shaped request needs an ack. So --validate still runs,
// on every report, before anything reaches the ledger.
const mergePrompt = [
  'You are the merge stage of an authorized CTF web sweep. Validate and merge;',
  'probe nothing, and write nothing into /home/kali/ctf-v2.',
  '',
  'Working directory: /home/kali/ctf-v2',
  '',
  'STEP 1 - stage the reports. Write each JSON object below to its own file:',
  '    D=/home/kali/ctf-work/challenges/' + CHALLENGE + '/reports',
  '    mkdir -p "$D"',
  'one file per report, named "$D/<layer_id>.json".',
  '',
  'The reports:',
  JSON.stringify(reports, null, 2),
  '',
  'STEP 2 - validate every one of them, individually:',
  '    for f in "$D"/*.json; do python3 tools/subagent_fanout.py --validate "$f"; done',
  'A refusal is a RESULT, not an error to work around. Record each refusal and',
  'its stated reason in `rejected`. Never edit a report to make it pass; the',
  'validator refusing means the subagent claimed more than it measured.',
  '',
  'STEP 3 - merge the ones that passed:',
  '    python3 tools/subagent_fanout.py --merge "$D"/*.json --challenge ' + CHALLENGE,
  '',
  'STEP 4 - copy commands_for_the_main_thread out of that output VERBATIM into',
  'the schema field of the same name. Add nothing and reword nothing. Each',
  'post-probe line needs --hypothesis-id added before it can run, which the main',
  'thread does because only it knows the ledger; leave the placeholder in place.',
  '',
  'Report reports_dir as the directory you used.',
].join('\n')

const merged = await agent(mergePrompt, {
  label: 'merge:validate',
  phase: 'Merge',
  agentType: 'general-purpose',
  schema: MERGE_OUT,
})

return {
  ok: true,
  challenge: CHALLENGE,
  handouts_on_disk: brief.handouts_on_disk || [],
  families_swept: reports.map(function (r) { return r.layer_id }),
  families_parked: parked.map(function (b) { return b.family }),
  families_held_over_width_cap: held.map(function (b) { return b.family }),
  width_cap: MAX_WIDTH,
  black_box: blackBox,
  reports: reports,
  merge: merged,
  the_main_thread_must_now: (merged && merged.commands_for_the_main_thread) || [
    'tools/subagent_fanout.py --merge did not return commands; run it by hand',
  ],
  reminder: [
    'This workflow wrote no state. Run the commands above from the main thread.',
    'A flag is a CANDIDATE until tools/hooks.py pre-flag accepts it with its '
      + 'verbatim excerpt and --source live-response|artifact.',
    'Then: python3 tools/decide.py ' + CHALLENGE,
  ],
}
