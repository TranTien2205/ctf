# Walk: challenge statement to domain to router

Reference module for `contest-domain-map`. An end-to-end intake trace for
the multi-domain event — how a challenge handoff lands on exactly one
router.

## Scenario

The event brief names six focus areas (logs/attack-chain, OSINT identity,
AI attack/defense, Linux exploit, embedded/hardware, memory+malware). A
challenge card on the platform says:

> "Node KESTREL-4 stopped answering heartbeat 90 minutes ago. We pulled
> its telemetry topic feed and the ops dashboard transcript. Figure out
> who sent it away and where it went."

## The trace

1. **Vocabulary check.** "Telemetry topic feed" = MQTT (dom-embedded),
   "ops dashboard transcript" = agent/insider instruction channel
   (dom-ai), "who sent it away" = attribution question across artifacts
   (dom-logs). Three candidate domains — pick by the ARTIFACT in hand:
   the topic feed is a pcap or log export, which is data, not a live
   endpoint.
2. **File first.** `tools/file_type.py feed.bin` — a pcap goes to
   `forensics-pcap-carve`; a text topic dump goes to `dom-logs` ->
   dfir-sherlock-triage.
3. **Entity key.** The node id `KESTREL-4` is the pivot — every artifact
   is queried by it, never skimmed.
4. **The command question.** "Who sent it away" asks for the cmd message:
   MQTT `swarm/kestrel-4/cmd` publisher field or the dashboard transcript's
   tool-call entry. That is a dom-ai tool-boundary record — the answer
   lives in the tool-call log, not the model's own narration.
5. **Merge and order.** Telemetry timestamps (pcap) + transcript tool
   calls + any auth record -> one timeline -> TTP slots: access (the
   dashboard session), command (the publish), effect (telemetry stops),
   persistence (a retained cmd message re-arms it).
6. **Answer.** "Identity X published cmd=reroute to topic Y at T; the
   node's telemetry then points at Z" — a fact with two artifacts behind
   it, not a guess.

## The decision rule restated

- Artifact in hand decides the domain, not the theme words.
- Live endpoint present? `skills/target-recon/` runs first regardless of
  domain.
- Two domains tie? Open the one whose artifact you already hold; the
  other becomes a `family_leads` read, not a parallel dive.
