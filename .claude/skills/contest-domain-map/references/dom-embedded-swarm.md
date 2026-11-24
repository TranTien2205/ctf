# Domain: embedded, hardware and swarm protocols

Reference module for `contest-domain-map`. The event vocabulary sounds
like "the drone swarm", "firmware image", "the vehicles stopped
listening", "telemetry capture". Owning router:
`skills/ai-iot-triage/SKILL.md`.

## Route by artifact

| What arrived | Open |
|---|---|
| pcap / telemetry capture | `skills/forensics-pcap-carve/SKILL.md` |
| firmware image, flash dump | `skills/rev-triage/SKILL.md` (fw-* families in ai-iot-triage) |
| ELF from the device | `skills/pwn-binary-triage/SKILL.md` |
| live device / service port | `skills/target-recon/SKILL.md` then this file's protocol table |
| model file | `skills/ctf-ai-ml/SKILL.md` |

`cq-*` families in ai-iot-triage already cover: uartdump, spiflash,
rfcapture, protocolcapture, **mqttpcap**, modelfile, trainingdataq.

## Swarm protocol playbook — MQTT, MAVLink, CAN, ROS

**MQTT** (the most likely swarm bus):
- Broker on 1883 (or 8883/TLS). Recon: `mosquitto_sub -h <host> -t '#' -v`
  if a client exists, else `tshark -Y mqtt`. A `connack` accepted with no
  auth IS the finding's first half.
- Wildcard `#` subscription enumerates the topic tree — topics are the
  endpoint inventory: `swarm/<id>/cmd`, `swarm/+/telemetry`.
- Message shapes: JSON command payloads with fields like `cmd`, `node`,
  `seq`; a retained message = the standing order (persistence on a bus).
- Publish is write-shaped: replaying a captured `cmd` to `swarm/*/cmd`
  moves a fleet, not a process. Explicit acknowledgment before any
  publish; the traffic capture replays read-only first.

**MAVLink** (drones / unmanned systems):
- Frame: `0xFE` (v1) or `0xFD` (v2) start byte; payload ids map to a
  dialect (common.xml): HEARTBEAT(0), SYS_STATUS(1), COMMAND_LONG(76),
  MISSION_ITEM(39), SET_MODE(11), STATUSTEXT(253).
- In a pcap: `tshark -Y mavlink` if the dissector is built in, else carve
  on start-byte and decode ids; `tools/forensics/pcap_parse.py` splits
  flows first.
- Hijack signatures: a second GCS heartbeat (two system ids claiming the
  link), COMMAND_LONG ARM/DISARM or SET_MODE from an unexpected sysid,
  mission upload messages mid-flight.
- The flag usually sits in STATUSTEXT or a signed/unsigned-param gap:
  unsigned MAVLink accepts any sender — the observation to report is
  "commands accepted without signing".

**CAN bus** (vehicle/autonomous chassis):
- candump/SocketCAN capture or a .log/.asc file. No addresses — only
  arbitration ids; the lower the id, the higher the priority on the bus.
- Recon: `skills/forensics-pcap-carve/references/can-note-checklist.md`; group
  frames by id, chart data-byte deltas per id, and the control channel
  stands out as the id whose payload changes on command events.
- Injection tells: one id suddenly carrying two distinct value rhythms
  (ECU + injector both transmitting it), periodic frames with missing
  periods (DoS on the bus), diagnostic/UDS ids (0x7DF broadcast,
  0x7E0-0x7EF) appearing outside a service session.

**ROS / ROS2** (robot middleware):
- Topics `/cmd_vel`, `/scan`, `/tf`; services under `/rosservice` (v1) or
  DDS discovery traffic (v2). A rosbag file is SQLite (v2) or a custom
  container (v1) — `ros2 bag` / `rosbag` tooling replays it read-only.
- Exposed master/discovery on 11311 (v1) or multicast (v2 DDS) is the
  entry; an open ROS network lets any publisher onto `/cmd_vel`.

## First commands

```bash
python3 tools/file_type.py <artifact>            # never trust the extension
tshark -r cap.pcap -q -z io,phs                  # protocol hierarchy = the bus list
binwalk -e firmware.bin                          # carve before you read
python3 tools/forensics/pcap_parse.py convs cap.pcap           # who talks to whom, on what
```
