---
name: ai-iot-triage
description: >
  Router for the AI and IoT category. Identifies the sub-type first, then routes:
  an LLM endpoint to prompt handling, a model file to deserialization, firmware
  to reverse engineering, an embedded binary to pwn. Thin by design; extend it
  when a real challenge shape is observed.
tags: [ctf, ai, iot, firmware, prompt-injection, jeopardy]
environment: [ctf, lab]
---

# AI / IoT — Router

This category is not standardised across events. Decide the sub-type before
anything else: AI and IoT challenges share nothing but the label.

## AI branch

| Observed | Direction |
|---|---|
| A chatbot or LLM endpoint whose hidden instructions hold the flag | Prompt handling: get the model to reveal its instructions; try indirect injection through data the model reads back |
| A model file such as `.pkl`, `.pt`, `.h5`, `.pb` or `.joblib`, or source calling a loader on one | Deserialization — route to `../web-deserialization/` |
| A classifier where a specific output is required, or training data must leak | Adversarial input, model inversion, membership inference — `../ctf-ai-ml/adversarial-ml.md` |
| An agent or tool-calling configuration | Map every tool the agent can reach and what data crosses into it |

Start with the simplest separation test: ask for the instructions directly, then
try the same request separated by formatting or an encoding layer, then try
placing the request inside data the model will read later. Stay inside the
challenge's own scope.

## IoT branch

| Observed | Direction |
|---|---|
| A firmware image such as `.bin`, squashfs or uImage | `binwalk -e` to extract, mount the root filesystem, look for credentials, backdoors and keys; depth in `../rev-triage/references/firmware-analysis.md` |
| A protocol capture: MQTT, CoAP, Modbus, BLE | For MQTT subscribe to the wildcard topic; otherwise read the spec. A PCAP goes to `../forensics-triage/` |
| An ARM or MIPS binary | Run it under `qemu-<arch>-static`, optionally chrooted, then `../pwn-binary-triage/` |
| A hardware dump: UART, SPI flash, RF capture | Carve with `binwalk`; radio captures go to `../ctf-misc/rf-sdr.md` |

## Tools

`binwalk`, `unblob`, `qemu-user-static`, `mosquitto_sub`, `strings`. Confirm each
with `which` before relying on it.

## Discipline

- Fix the sub-type first. Read what the challenge actually supplies: source, a
  model file, firmware, or a chat endpoint.
- If the sub-type overlaps another category — firmware is reversing, a model file
  is deserialization, an embedded binary is pwn — use that category's skill
  instead of starting over here.
- Prompt-handling work is in scope only against the challenge's own endpoint.
- Budget and escalation as in `../LOOP_DISCIPLINE.md`.
