// solver-fleet.js -- run a whole specialised SOLVER fleet at once on one
// authorized challenge, and bring back a flag candidate with its proof.
//
//   Workflow({ name: 'solver-fleet',
//              args: { challenge: 'nameless', category: 'crypto',
//                      handout: 'challenges/nameless', target: 'nc host 1337' } })
//
// HOW THIS DIFFERS FROM web-sweep.js, which is the important part.
//
// The ctf-web-* fleet is MEASURE-ONLY by design: each agent runs at most five
// read-only probes and hands a measurement back, and the main thread alone
// chains them. That is correct for web, where the chain usually crosses several
// bug classes and the next probe depends on the last.
//
// crypto, pwn, rev, osint and misc are not shaped that way. There the chain is
// almost always inside ONE family: recover the RSA key and you have the
// plaintext; find the deciding check and you have the input; peel the encoding
// and you have the answer. Splitting that across a measure-then-record boundary
// adds a 7-10 minute round trip per step and buys nothing. So these agents are
// SOLVERS: they are permitted to chain their own findings all the way to a flag.
//
// WHAT IS STILL NOT DELEGATED, and why. No agent runs tools/hooks.py or
// tools/state.py. A flag they return is a CANDIDATE. The main thread runs
// pre-flag. That gate costs seconds, it is what stops a wrong submission, and it
// was never what made this system slow -- the slow parts were the manual spawn,
// the manual report staging and the manual merge, which this file removes.
//
// ONE CHECK THIS SCRIPT PERFORMS ITSELF. tools/hooks.py post-probe has no
// --response input, so the repository cannot verify that a quoted excerpt really
// came from a response. Here the script can do the narrower check that matters
// most for a flag: the claimed flag string must literally appear inside the
// claimed bytes. A candidate that fails it is downgraded before any human sees
// it, in plain JavaScript, with no agent in the loop to be persuaded.

export const meta = {
  name: 'solver-fleet',
  description: 'Run a specialised crypto, pwn, rev, osint or misc solver fleet on one challenge and return a proven flag candidate',
  phases: [
    { title: 'Triage', detail: 'the category recon agent names the structure, alone' },
    { title: 'Solve', detail: 'the whole family fleet in parallel, each permitted to reach a flag' },
    { title: 'Prove', detail: 'flag candidates checked against their own evidence bytes' },
  ],
}

// Fleets as they exist in .claude/agents/. The triage member runs alone first;
// the solvers probe against its answer. osint and misc have no triage member,
// which is stated rather than faked with a stand-in.
const FLEETS = {
  crypto: {
    triage: 'ctf-crypto-recon',
    solvers: ['ctf-crypto-rsa', 'ctf-crypto-prng', 'ctf-crypto-ecc', 'ctf-crypto-symmetric'],
    triage_is: 'the parameter sheet: every given and withheld parameter with path:line, and which of four families this is',
  },
  pwn: {
    triage: 'ctf-pwn-triage',
    solvers: ['ctf-pwn-stack', 'ctf-pwn-format', 'ctf-pwn-heap', 'ctf-pwn-rop'],
    triage_is: 'protections with the evidence that decided each, dangerous imports, gadgets, and which routes remain open',
  },
  rev: {
    triage: 'ctf-rev-triage',
    solvers: ['ctf-rev-native', 'ctf-rev-managed', 'ctf-rev-bytecode'],
    triage_is: 'what the artifact IS from its bytes: type, architecture, runtime, packed or not, and which depth agent owns it',
  },
  osint: {
    triage: null,
    solvers: ['ctf-osint-image', 'ctf-osint-identity', 'ctf-osint-infra'],
    triage_is: null,
  },
  misc: {
    triage: null,
    solvers: ['ctf-misc-jail', 'ctf-misc-encoding'],
    triage_is: null,
  },
}

const A = args || {}
const CHALLENGE = A.challenge || 'unnamed'
const CATEGORY = (A.category || '').toLowerCase()
const HANDOUT = A.handout || ''
const TARGET = A.target || ''
const QUESTION = A.question || ''

const fleet = FLEETS[CATEGORY]
if (!fleet) {
  return {
    ok: false,
    reason: 'no solver fleet exists for category ' + JSON.stringify(CATEGORY),
    categories_with_a_fleet: Object.keys(FLEETS),
    note: 'web and dfir split by bug-class family instead; use the web-sweep '
        + 'workflow, or tools/subagent_fanout.py --dfir. Inventing a fleet name '
        + 'here would name agents that do not exist on disk.',
  }
}

// ---------------------------------------------------------------- schema

// Shared by every solver in these fleets. The four flag_* keys are the contract
// that lets the script check a candidate without trusting the prose around it.
const SOLVER = {
  type: 'object',
  properties: {
    family: { type: 'string' },
    challenge: { type: 'string' },
    structure_or_primitive: { type: 'string', description: 'what the target actually is' },
    evidence: {
      type: 'array',
      items: {
        type: 'object',
        properties: { fact: { type: 'string' }, where: { type: 'string' } },
        required: ['fact', 'where'],
      },
    },
    attempts: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          what: { type: 'string', description: 'the exact command or attack run' },
          result: { type: 'string', description: 'its real output, truncated' },
          verdict: { type: 'string', enum: ['worked', 'failed', 'inconclusive'] },
        },
        required: ['what', 'verdict'],
      },
    },
    flag_candidate: { type: ['string', 'null'] },
    flag_source: { type: ['string', 'null'], enum: ['live-response', 'artifact', null] },
    flag_evidence: { type: ['string', 'null'], description: 'the verbatim bytes the flag was read from' },
    flag_command: { type: ['string', 'null'], description: 'the exact command that produced those bytes' },
    measured_dead: {
      type: 'array',
      items: {
        type: 'object',
        properties: { layer: { type: 'string' }, how: { type: 'string' } },
        required: ['layer', 'how'],
      },
    },
    next_lead: { type: ['string', 'null'] },
    conclusion: { type: 'string' },
  },
  required: ['family', 'structure_or_primitive', 'attempts', 'flag_candidate', 'conclusion'],
}

// ---------------------------------------------------------------- prompts

const SCOPE = [
  'SCOPE: this is an AUTHORIZED jeopardy CTF challenge. Work only on the',
  'supplied handout and the supplied target. Do not scan the host, do not touch',
  'any other port, and do not reach anything the challenge did not give you.',
].join('\n')

const SOLVER_RULES = [
  'YOU ARE A SOLVER, not a measurement. Unlike the ctf-web-* fleet you may',
  'chain your own findings all the way to a flag and return it.',
  '',
  'Two limits do not move:',
  '  1. You never run tools/hooks.py or tools/state.py, and you never edit any',
  '     file in /home/kali/ctf-v2. Write only under your own workspace',
  '     directory in /home/kali/ctf-work. The main thread alone runs the flag',
  '     gate: it is the one check that stops a wrong flag being submitted, it',
  '     costs seconds, and it is not what slows this system down.',
  '  2. A flag you return MUST carry flag_evidence (the verbatim bytes you read',
  '     it from) and flag_command (the exact command that produced them). The',
  '     orchestrator mechanically checks that your flag string actually appears',
  '     inside your evidence bytes and DOWNGRADES it if it does not, so a',
  '     reconstructed, inferred or retyped flag will be caught. If you cannot',
  '     paste the real bytes, set flag_candidate null and say why.',
  '',
  'A timeout, a reset or an empty body is never a result.',
  'A script written but not run has produced nothing: run it, then quote the',
  'output you actually got.',
  '',
  'WHEN YOU CANNOT REACH A FLAG, measured_dead is the deliverable. Each entry',
  'needs the layer you ruled out AND the measurement that ruled it out. That is',
  'what stops the next agent re-walking your ground, and it is what the',
  'controller escalation ladder consumes.',
].join('\n')

function context(extra) {
  return [
    'Challenge: ' + CHALLENGE,
    HANDOUT ? 'Handout: ' + HANDOUT : 'Handout: none supplied',
    TARGET ? 'Target: ' + TARGET : 'Target: none supplied (offline artifact)',
    QUESTION ? 'The question to answer: ' + QUESTION : '',
    '',
    SCOPE,
    '',
    extra || '',
  ].join('\n')
}

// ---------------------------------------------------------------- phase 1

let triageOut = null

if (fleet.triage) {
  phase('Triage')
  log(CATEGORY + ': ' + fleet.triage + ' runs first and alone')
  triageOut = await agent([
    context(),
    'You are the triage member of the ' + CATEGORY + ' fleet. Your job is ' +
      fleet.triage_is + '.',
    '',
    'Run FIRST and ALONE: the four solvers behind you all probe against your',
    'answer, and a solver that starts from a guessed parameter is the measured',
    'way this category loses an hour.',
    '',
    'You run no heavy attack and write no exploit. Your flag_candidate is',
    'normally null and that is the correct outcome - say so rather than',
    'manufacturing one. If the flag is simply sitting in the artifact and a',
    'single command reads it out, return it with its real bytes.',
    '',
    SOLVER_RULES,
  ].join('\n'), {
    label: 'triage:' + fleet.triage,
    phase: 'Triage',
    agentType: fleet.triage,
    schema: SOLVER,
  })
}

const triageNote = triageOut
  ? [
      'TRIAGE ALREADY RAN. Start from this rather than re-deriving it:',
      JSON.stringify({
        structure: triageOut.structure_or_primitive,
        evidence: triageOut.evidence,
        measured_dead: triageOut.measured_dead,
        next_lead: triageOut.next_lead,
        conclusion: triageOut.conclusion,
      }, null, 2),
      '',
      'If the triage answer contradicts what you measure, trust your own',
      'measurement and say where it diverged.',
    ].join('\n')
  : ''

// Triage may already have the flag. Stopping here saves the whole fleet.
if (triageOut && triageOut.flag_candidate) {
  log('triage already returned a flag candidate; skipping the solve wave')
}

// ---------------------------------------------------------------- phase 2

let solverOut = []

if (!(triageOut && triageOut.flag_candidate)) {
  phase('Solve')
  log('solving with ' + fleet.solvers.length + ' agents in parallel: '
      + fleet.solvers.join(', '))

  // Barrier rather than a pipeline: the Prove stage ranks candidates against
  // each other and needs the whole set, and a solver that finished early has
  // nothing useful to do with another's partial result.
  solverOut = (await parallel(fleet.solvers.map(function (name) {
    return function () {
      return agent([
        context(triageNote),
        'You are ' + name + '. Work ONLY your own family. If the challenge',
        'turns out to belong to a sibling family, say so in conclusion and stop',
        'rather than straying - a sibling agent is already running in parallel',
        'on exactly that.',
        '',
        'Respect the attempt ceiling written in your own prompt file. On',
        'exhaustion report measured_dead rather than trying a further variant;',
        'a further variant of the same idea produces no new signal.',
        '',
        SOLVER_RULES,
      ].join('\n'), {
        label: 'solve:' + name,
        phase: 'Solve',
        agentType: name,
        schema: SOLVER,
      })
    }
  }))).filter(Boolean)
}

const everything = (triageOut ? [triageOut] : []).concat(solverOut)

if (!everything.length) {
  return {
    ok: false,
    stage: 'Solve',
    reason: 'no agent in the ' + CATEGORY + ' fleet returned a report',
    fleet: fleet,
  }
}

// ---------------------------------------------------------------- phase 3

phase('Prove')

// The mechanical check, done here in plain JavaScript so there is no agent in
// the loop that could be talked out of it. A flag must appear inside the bytes
// it was supposedly read from. This is narrower than "the excerpt is real" --
// nothing offline can prove that -- but it catches the failure that actually
// happens: a flag reconstructed from memory or assembled from a partial read.
function assess(r) {
  const flag = r.flag_candidate
  if (!flag) return null
  const bytes = r.flag_evidence || ''
  const problems = []
  if (!bytes) problems.push('no flag_evidence: nothing to check the flag against')
  else if (bytes.indexOf(flag) === -1) {
    problems.push('the flag string does not appear inside flag_evidence, so it '
                + 'was reconstructed rather than read')
  }
  if (!r.flag_command) problems.push('no flag_command: the bytes cannot be reproduced')
  if (!r.flag_source) problems.push('no flag_source: pre-flag needs live-response or artifact')
  return {
    family: r.family,
    flag: flag,
    source: r.flag_source || null,
    command: r.flag_command || null,
    evidence_excerpt: bytes ? bytes.slice(0, 400) : null,
    proven_in_its_own_evidence: problems.length === 0,
    problems: problems,
  }
}

const candidates = everything.map(assess).filter(Boolean)
const proven = candidates.filter(function (c) { return c.proven_in_its_own_evidence })
const downgraded = candidates.filter(function (c) { return !c.proven_in_its_own_evidence })

for (let i = 0; i < downgraded.length; i++) {
  log('DOWNGRADED a flag from ' + downgraded[i].family + ': '
      + downgraded[i].problems.join('; '))
}

const dead = []
for (let i = 0; i < everything.length; i++) {
  const m = everything[i].measured_dead || []
  for (let j = 0; j < m.length; j++) {
    dead.push({ family: everything[i].family, layer: m[j].layer, how: m[j].how })
  }
}

const leads = everything
  .filter(function (r) { return r.next_lead })
  .map(function (r) { return { family: r.family, lead: r.next_lead } })

const commands = []
if (proven.length) {
  const best = proven[0]
  commands.push("python3 tools/hooks.py pre-flag " + CHALLENGE
    + " --value '" + best.flag + "'"
    + " --source " + (best.source || 'artifact')
    + " --evidence '<paste the bytes from the report; they are in this result>'")
  commands.push('python3 tools/decide.py ' + CHALLENGE + '   # must answer record_solve')
} else if (candidates.length) {
  commands.push('# every flag candidate failed its own evidence check. Re-run the '
    + 'family that produced it and have it paste the real bytes, or run the '
    + 'command it reported yourself from this thread.')
} else {
  commands.push('python3 tools/decide.py ' + CHALLENGE
    + '   # no flag: expect escalate, and spend the rung it names')
  commands.push('# the measured_dead list below is what the next attempt must not re-walk;'
    + ' it belongs in knowledge/attempts/' + CHALLENGE + '.json')
}

return {
  ok: true,
  challenge: CHALLENGE,
  category: CATEGORY,
  fleet_run: (fleet.triage ? [fleet.triage] : []).concat(
    (triageOut && triageOut.flag_candidate) ? [] : fleet.solvers),
  structure: everything.map(function (r) {
    return { family: r.family, says: r.structure_or_primitive }
  }),
  flag_candidates_proven_in_their_own_evidence: proven,
  flag_candidates_downgraded: downgraded,
  measured_dead: dead,
  next_leads: leads,
  attempts_by_family: everything.map(function (r) {
    return { family: r.family, attempts: r.attempts, conclusion: r.conclusion }
  }),
  the_main_thread_must_now: commands,
  reminder: [
    'This workflow wrote no state and ran no gate.',
    'A flag is a CANDIDATE until tools/hooks.py pre-flag accepts it. The check '
      + 'done here is narrower: it only proves the flag string appears inside '
      + 'the bytes the agent quoted, not that those bytes came from the target.',
    'Paste the evidence bytes from this result into pre-flag; do not retype them.',
  ],
}
