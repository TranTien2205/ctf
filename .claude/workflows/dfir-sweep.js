// dfir-sweep.js -- fan the ctf-dfir-* fleet over ONE artifact bundle and hand
// back the answers with the record that each was measured, not inferred.
//
//   Workflow({ name: 'dfir-sweep',
//              args: { challenge: 'brutus', bundle: 'challenges/brutus/triage',
//                      questions: ['What is the attacker IP?', '...'] } })
//
// HOW A SHERLOCK DIFFERS FROM A WEB CHALLENGE, which is why this is its own file
// rather than a flag on web-sweep.js:
//
//  * The deliverable is a LIST OF ANSWERS, not one flag. Each question is scored
//    separately, so a bundle where six of eight questions are answerable is a
//    good result and must not be reported as a failure.
//  * Recording goes through `tools/hooks.py pre-flag ... --source artifact`, not
//    post-probe. A Sherlock answer is read out of a supplied artifact, which the
//    proof standard accepts exactly as it accepts a live response.
//  * No family is write-shaped. There is no target to mutate; every artifact is
//    read-only by nature, so the whole --write-ack path is irrelevant here.
//  * The expensive mistake is spending an hour inside the WRONG artifact family.
//    That is why recon runs alone first and routes, and why every other family
//    probes against its inventory.
//
// WHAT IT DOES NOT DO. It never writes state, never runs the gate, and never
// fills in an answer the artifacts did not carry. The `<ANSWER>` placeholder in
// the emitted pre-flag command is left for a human on purpose: deciding which
// of several timestamps answers "when did the attacker first log in" is
// judgement, and a workflow that guessed it would be inventing evidence.

export const meta = {
  name: 'dfir-sweep',
  description: 'Fan the ctf-dfir-* fleet over one artifact bundle and return per-question answers with their measurements',
  phases: [
    { title: 'Inventory', detail: 'ctf-dfir-recon opens the bundle alone and routes each question' },
    { title: 'Measure', detail: 'one ctf-dfir-* agent per artifact family that is actually present' },
    { title: 'Collect', detail: 'validate every report, then emit the pre-flag commands' },
  ],
}

const A = args || {}
const CHALLENGE = A.challenge || 'unnamed'
const BUNDLE = A.bundle || ''
const QUESTIONS = Array.isArray(A.questions) ? A.questions : []
const FORCE_ALL = A.all === true

// ---------------------------------------------------------------- schemas

const CONTRACT = {
  type: 'object',
  properties: {
    layer_id: { type: 'string', description: 'the family id from the brief' },
    challenge: { type: 'string' },
    class: { type: ['string', 'null'], description: 'a dfir-* class id, or null' },
    files_read: { type: 'array', items: { type: 'string' } },
    probes: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          request: { type: 'string', description: 'the exact command run against the artifact' },
          transport: { type: 'string', enum: ['ok', 'timeout', 'reset', 'error', 'empty'] },
          status: { type: ['number', 'null'] },
          response_excerpt: { type: 'string', description: 'the verbatim record, pasted from tool output' },
          evidence: { type: 'string', description: 'MUST be a substring of response_excerpt' },
          evidence_kind: { type: 'string', enum: ['surface', 'class', 'impact', 'transport'] },
          verdict: { type: 'string', enum: ['confirms', 'refutes', 'falsifies', 'inconclusive'] },
        },
        required: ['request', 'transport', 'verdict'],
      },
    },
    answers: {
      type: 'array',
      description: 'one entry per question this family can answer from its own artifacts',
      items: {
        type: 'object',
        properties: {
          question: { type: 'string' },
          answer: { type: ['string', 'null'] },
          record: { type: 'string', description: 'the verbatim artifact record the answer was read from' },
          command: { type: 'string', description: 'the exact command that produced that record' },
          confidence: { type: 'string', enum: ['measured', 'inferred', 'unknown'] },
        },
        required: ['question', 'answer', 'confidence'],
      },
    },
    parsers_absent: {
      type: 'array', items: { type: 'string' },
      description: 'parsers this family needed that are not installed, with the install command',
    },
    falsifier_outcome: { type: 'string', enum: ['held', 'broken', 'not-measured'] },
    conclusion: { type: 'string' },
    cost_minutes: { type: 'number' },
  },
  required: ['layer_id', 'challenge', 'probes', 'falsifier_outcome', 'conclusion'],
}

const INVENTORY = {
  type: 'object',
  properties: {
    ran: { type: 'string' },
    bundle_opened: { type: 'boolean' },
    artifact_families_present: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          family: { type: 'string' },
          evidence: { type: 'string', description: 'the file and the bytes that identify it' },
        },
        required: ['family', 'evidence'],
      },
    },
    briefs: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          family: { type: 'string' },
          spawn_agent: { type: 'string' },
          artifacts_fired: { type: 'number' },
          brief_json: { type: 'string', description: 'the whole brief object, JSON-encoded' },
        },
        required: ['family', 'spawn_agent', 'brief_json'],
      },
    },
    question_routing: {
      type: 'array',
      items: {
        type: 'object',
        properties: { question: { type: 'string' }, family: { type: 'string' } },
        required: ['question', 'family'],
      },
    },
    parsers_absent: { type: 'array', items: { type: 'string' } },
  },
  required: ['ran', 'briefs'],
}

// ---------------------------------------------------------------- phase 1

phase('Inventory')

const invPrompt = [
  'You are the inventory stage of an authorized DFIR investigation on the',
  'supplied artifact bundle. Open the container, inventory what is present, and',
  'route the questions. Answer nothing yourself and parse nothing deeply.',
  '',
  'Working directory: /home/kali/ctf-v2',
  'Bundle: ' + (BUNDLE || '(none supplied)'),
  '',
  'STEP 1 - run the fan-out and report its JSON verbatim:',
  '    python3 tools/subagent_fanout.py --dfir ' + (BUNDLE || '<no bundle>') +
    ' --challenge ' + CHALLENGE,
  '',
  'STEP 2 - for every artifact family you can see in the bundle, record the file',
  'and the BYTES that identify it. A family named without the bytes that prove it',
  'is a guess, and an hour spent inside the wrong artifact family is the',
  'expensive mistake in this category.',
  '',
  'STEP 3 - say which parsers are ABSENT on this box. Measured today: no EVTX',
  'parser (no evtx_dump), no registry parser, no volatility3, no yara. The',
  'Sleuth Kit IS installed via fls, mmls and icat even though no binary named',
  'sleuthkit exists; tshark and capinfos are installed. Name the install command',
  'for each absent parser rather than guessing around it.',
  '',
  QUESTIONS.length
    ? 'STEP 4 - route each question to exactly ONE family from your inventory:\n'
      + QUESTIONS.map(function (q, i) { return '  ' + (i + 1) + '. ' + q }).join('\n')
    : 'STEP 4 - no questions were supplied, so leave question_routing empty.',
  '',
  'brief_json must be the COMPLETE brief object re-encoded as a JSON string;',
  'the downstream agents are driven from it and a truncated brief breaks them.',
  '',
  'Invent no family and no agent name. Report what the tool printed.',
].join('\n')

const inv = await agent(invPrompt, {
  label: 'inventory:dfir-recon',
  phase: 'Inventory',
  agentType: 'ctf-dfir-recon',
  schema: INVENTORY,
})

if (!inv || !inv.briefs || !inv.briefs.length) {
  return {
    ok: false,
    stage: 'Inventory',
    reason: 'the inventory stage returned no briefs; run '
          + 'tools/subagent_fanout.py --dfir by hand',
    bundle: BUNDLE,
  }
}

// ---------------------------------------------------------------- phase 2

phase('Measure')

// Only families whose artifacts are actually in the bundle. A family with
// nothing to read costs a 7-10 minute round trip to report an empty hand, and
// the DFIR sweep method is explicit that an absent family is parked, not run.
let selected = inv.briefs.filter(function (b) {
  return b.family !== 'recon'
})
if (!FORCE_ALL) {
  const fired = selected.filter(function (b) { return (b.artifacts_fired || 0) > 0 })
  if (fired.length) selected = fired
}
const parked = inv.briefs.filter(function (b) {
  return b.family !== 'recon' && selected.indexOf(b) === -1
})
if (parked.length) {
  log('parked ' + parked.length + ' family(ies) with no artifact in the bundle: '
      + parked.map(function (b) { return b.family }).join(', '))
}

const inventoryNote = [
  'THE INVENTORY ALREADY RAN. Probe against this rather than re-opening the',
  'bundle yourself:',
  JSON.stringify({
    families_present: inv.artifact_families_present,
    parsers_absent: inv.parsers_absent,
  }, null, 2),
].join('\n')

const routedFor = {}
const routing = inv.question_routing || []
for (let i = 0; i < routing.length; i++) {
  const f = routing[i].family
  if (!routedFor[f]) routedFor[f] = []
  routedFor[f].push(routing[i].question)
}

log('measuring ' + selected.length + ' artifact family(ies) in parallel')

// Barrier: the Collect stage reconciles answers ACROSS families -- two families
// often answer the same question from different artifacts, and disagreement
// between them is itself the finding. That needs the whole set.
const reports = (await parallel(selected.map(function (b) {
  return function () {
    const mine = routedFor[b.family] || []
    return agent([
      'You are the ' + b.family + ' family of an authorized DFIR investigation',
      'on challenge "' + CHALLENGE + '".',
      '',
      'Your brief, from tools/subagent_fanout.py --dfir. Every field was read',
      'from knowledge/bug-classes.json or from the artifact inventory:',
      '',
      b.brief_json,
      '',
      inventoryNote,
      '',
      mine.length
        ? 'THE QUESTIONS ROUTED TO YOU:\n'
          + mine.map(function (q, i) { return '  ' + (i + 1) + '. ' + q }).join('\n')
          + '\n\nFill one `answers` entry per question. If your artifacts cannot'
          + '\nanswer one, set answer null and confidence unknown rather than'
          + '\nreaching into another family\'s artifacts.'
        : 'No question was routed to you. Report what your artifacts carry that'
          + '\nbears on the investigation, and leave answers empty.',
      '',
      'HARD LIMITS:',
      '  * read-only on the supplied artifacts. Send no packet, resolve no name,',
      '    call no cloud API, and never EXECUTE anything out of the bundle.',
      '  * every answer needs the VERBATIM record it was read from and the exact',
      '    command that produced it. Paste it from the tool output, never from',
      '    memory.',
      '  * confidence is `measured` ONLY when the record contains the answer.',
      '    A timestamp you computed from a log with no year, or a name you',
      '    reasoned to, is `inferred` -- say so. This category is scored on',
      '    exactness, and an inferred answer presented as measured is the way it',
      '    is lost.',
      '  * if the parser you need is absent, report it in parsers_absent with the',
      '    install command. Do not guess around a missing parser.',
      '  * do NOT run tools/hooks.py or tools/state.py. The main thread records.',
      '',
      'Return the contract JSON.',
    ].join('\n'), {
      label: 'measure:' + b.family,
      phase: 'Measure',
      agentType: b.spawn_agent,
      schema: CONTRACT,
    })
  }
}))).filter(Boolean)

if (!reports.length) {
  return {
    ok: false,
    stage: 'Measure',
    reason: 'no artifact family returned a report',
    parked_families: parked.map(function (b) { return b.family }),
  }
}

// ---------------------------------------------------------------- phase 3

phase('Collect')

// Reconcile in plain JavaScript, with no agent to be persuaded. Two families
// answering the same question from different artifacts is common and useful;
// them DISAGREEING is a finding in its own right and must surface rather than
// be silently resolved in favour of whichever ran last.
const byQuestion = {}
for (let i = 0; i < reports.length; i++) {
  const list = reports[i].answers || []
  for (let j = 0; j < list.length; j++) {
    const a = list[j]
    if (!a || !a.question) continue
    if (!byQuestion[a.question]) byQuestion[a.question] = []
    byQuestion[a.question].push({
      family: reports[i].layer_id,
      answer: a.answer,
      confidence: a.confidence,
      record: a.record || null,
      command: a.command || null,
      // The same check solver-fleet.js applies to a flag: the answer must
      // actually appear in the record it was supposedly read from.
      answer_is_in_its_own_record: !!(a.answer && a.record
        && a.record.indexOf(a.answer) !== -1),
    })
  }
}

const resolved = []
const keys = Object.keys(byQuestion)
for (let i = 0; i < keys.length; i++) {
  const q = keys[i]
  const all = byQuestion[q]
  const measured = all.filter(function (x) {
    return x.confidence === 'measured' && x.answer_is_in_its_own_record
  })
  const distinct = {}
  for (let j = 0; j < measured.length; j++) distinct[String(measured[j].answer)] = true
  resolved.push({
    question: q,
    answered_by: all.map(function (x) { return x.family }),
    measured_answers: measured,
    disagreement: Object.keys(distinct).length > 1,
    best: measured.length ? measured[0].answer : null,
    status: measured.length
      ? (Object.keys(distinct).length > 1 ? 'conflicting' : 'measured')
      : (all.length ? 'inferred-or-unknown-only' : 'unanswered'),
  })
}

const absent = []
for (let i = 0; i < reports.length; i++) {
  const list = reports[i].parsers_absent || []
  for (let j = 0; j < list.length; j++) absent.push(list[j])
}
for (let i = 0; i < (inv.parsers_absent || []).length; i++) {
  absent.push(inv.parsers_absent[i])
}

const commands = []
for (let i = 0; i < resolved.length; i++) {
  const r = resolved[i]
  if (r.status !== 'measured') continue
  // A Sherlock answer is read from a supplied artifact, which the proof
  // standard accepts. The <ANSWER> is already known here, so unlike the
  // hand-written template this emits the real value -- but the EVIDENCE must
  // still be pasted by the main thread from the record below, not retyped.
  commands.push("python3 tools/hooks.py pre-flag " + CHALLENGE + "-q" + (i + 1)
    + " --value '" + String(r.best).replace(/'/g, "'\\''") + "'"
    + " --source artifact"
    + " --evidence '<paste the record from measured_answers below>'")
}
if (!commands.length) {
  commands.push('# nothing reached `measured`. Read the inferred answers and the'
    + ' parsers_absent list before recording anything.')
}

return {
  ok: true,
  challenge: CHALLENGE,
  bundle: BUNDLE,
  artifact_families_present: inv.artifact_families_present || [],
  families_measured: reports.map(function (r) { return r.layer_id }),
  families_parked: parked.map(function (b) { return b.family }),
  questions: resolved,
  answered_measured: resolved.filter(function (r) { return r.status === 'measured' }).length,
  of_questions: resolved.length,
  conflicting: resolved.filter(function (r) { return r.disagreement }),
  parsers_absent: absent,
  reports: reports,
  the_main_thread_must_now: commands,
  reminder: [
    'This workflow wrote no state and ran no gate.',
    'A `measured` answer means the value appears inside the record quoted for '
      + 'it. An `inferred` one does not, and this category is scored on '
      + 'exactness, so do not record an inferred answer as if it were measured.',
    'Where two families disagree, read both records before choosing: the '
      + 'disagreement is usually a timezone or a clock, not a mistake.',
  ],
}
