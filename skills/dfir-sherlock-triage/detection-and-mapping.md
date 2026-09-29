# Detection rules, SIEM queries and technique mapping

The file for three question shapes the other depth files do not own:

- *"Provide the MITRE ATT&CK technique ID for ..."* - the answer is a string like
  `T1136.001`, and it has to be produced offline, from data, not from memory.
- *"Write a detection for ..."* or *"which rule would have caught this"* - the
  answer is a rule, and a rule with an invalid `condition` is a wrong answer.
- *"How many / which account / what time"* over an artifact set already loaded into
  a SIEM, where the fastest path is one query rather than five parses.

Evidence level: catalogue for the rule and query languages - they are published
specifications. Everything marked **measured** below was run on this box on
2026-09-28 and the number is what came back. Nothing in this tree has solved a
Sherlock, so no part of this is local experience.

## 1. Writing a Sigma rule

Sigma is YAML with a fixed schema. Mandatory keys: `title`, `logsource`,
`detection`, and inside detection a `condition`. Optional keys the graders and the
engines actually read: `id` (a UUID), `status`, `level`, `description`,
`references`, `author`, `date`, `fields`, `falsepositives`, `tags`
(SigmaHQ sigma-rules-specification).

`status` takes exactly one of `stable`, `test`, `experimental`, `deprecated`,
`unsupported`. `level` takes exactly one of `informational`, `low`, `medium`,
`high`, `critical` (same spec). Anything else is invalid, not merely unusual.

A complete rule, valid against that specification:

```yaml
title: Scheduled Task Registered From A User-Writable Path
id: b1234817-ec0b-48a8-9cd9-3b6adad2d6b9
status: experimental
description: >
    schtasks.exe or at.exe registering a task whose action runs from AppData,
    Users\Public or a Temp directory. Corroborate with Security 4698 for the
    registration and Microsoft-Windows-TaskScheduler/Operational 200 for the
    first execution, which 4698 does not give.
references:
    - https://attack.mitre.org/techniques/T1053/005/
author: ctf-v2
date: 2026-09-28
logsource:
    product: windows
    category: process_creation
    definition: >
        Sysmon event 1, or Security 4688 with command-line auditing enabled.
        A 4688 with an empty CommandLine is an audit-policy gap, not an absence
        of execution.
detection:
    selection_img:
        - Image|endswith:
            - '\schtasks.exe'
            - '\at.exe'
        - OriginalFileName:
            - 'schtasks.exe'
            - 'at.exe'
    selection_create:
        CommandLine|windash|contains: ' -create'
    sel_path_appdata:
        CommandLine|contains: '\AppData\'
    sel_path_public:
        CommandLine|contains: '\Users\Public\'
    sel_path_temp:
        CommandLine|re|i: '\\Temp\\[^\\]+\.(exe|dll|ps1|bat|vbs|js)'
    filter_installer:
        ParentImage|endswith: '\TrustedInstaller.exe'
    condition: all of selection_* and (1 of sel_path_*) and not filter_installer
fields:
    - CommandLine
    - ParentImage
    - User
falsepositives:
    - Software updaters that register a per-user task from AppData
level: high
tags:
    - attack.execution
    - attack.persistence
    - attack.privilege_escalation
    - attack.t1053.005
```

Four things in that rule are the parts people get wrong.

**A search identifier may be a list of maps.** `selection_img` is a list, so its
two maps are ORed: `Image|endswith` any of two values, OR `OriginalFileName` any
of two values. Inside one map, keys are ANDed and a list of values under one key is
ORed.

**Condition operators and their precedence.** Lowest to highest:
`or` < `and` < `not` < `x of <search-identifier-pattern>` < `( expression )`
(SigmaHQ spec). So `not 1 of filter_*` already parses as `not (1 of filter_*)`; the
parentheses above are for the reader, not the parser. The forms that matter:

| Condition | Meaning |
|---|---|
| `selection` | that identifier alone |
| `selection and not filter` | the whitelist idiom; `filter` subtracts |
| `1 of selection_*` | any identifier whose name matches the glob |
| `all of selection_*` | every identifier matching the glob |
| `1 of them` / `all of them` | every identifier not starting with `_` |
| `selection and (filter_a or filter_b)` | explicit grouping |

**Null and empty string are distinct values**, and a null test needs its own
identifier because there is no `not null` in a map. Verbatim shape from the spec:

```yaml
detection:
    selection:
        EventID: 4738
    filter:
        PasswordLastSet: null
    condition: selection and not filter
```

**Modifiers**, appended to the field name with `|`, in the order they apply.
Every row below is verbatim from specification/sigma-appendix-modifiers.md in the
SigmaHQ/sigma-specification repository - *not* from the rules specification, which
does not carry the modifier list:

| Modifier | What it does |
|---|---|
| `contains` | "Puts `*` wildcards around the values" - substring anywhere |
| `startswith` / `endswith` | anchored prefix / suffix; the appendix gives `adm*` and `*\\cmd.exe` as the wildcard forms they replace |
| `all` | turns the list under this key from OR into AND. **A single-item value is not allowed to carry `all`** - the appendix says some back-ends cannot support it, so that rule is invalid, not merely odd |
| `cased` | match case-sensitively. Without it, **plain Sigma matching is case-INsensitive** |
| `neq` | field is different from the values; also combinable with `fieldref` |
| `re` | the value is a PCRE regular expression and `*`/`?` stop being wildcards. **Case-SENSITIVE by default** - the one asymmetry in the language, because every other string match is not. Only these metacharacters are supported: `.` `^` `$` `*` `+` `?` `{n,m}` `[a-z]` `[^a-z]` `|` `()`. Anything else - `\d`, `\s`, `\w`, `\b`, lookaround - is **unsupported and cannot be used** |
| `re` sub-modifiers | `|re|i` case-insensitive, `|re|m` multiline (`^`/`$` match line bounds), `|re|s` dot matches newline |
| `base64` | match the base64 encoding of the value |
| `base64offset` | match the value at all three base64 phase offsets - the one to use when the value sits mid-string inside an encoded command, and it is almost always written `base64offset|contains` |
| `utf16le` | `cmd` becomes the bytes `63 00 6d 00 64 00`. **This is the one for PowerShell `-EncodedCommand`**, which is UTF-16LE |
| `wide` | an alias for `utf16le`, nothing more |
| `utf16be` | `cmd` becomes `00 63 00 6d 00 64` |
| `utf16` | **not a synonym for `utf16le`**: it *prepends a byte order mark*, so `cmd` becomes `FF FE 63 00 6d 00 64 00`. A BOM only exists at the start of the blob, so using `utf16` where the value sits mid-command is a rule that can never fire |
| `cidr` | the value is a CIDR network; IPv4 and IPv6 both, e.g. `DestinationIp|cidr: 10.0.0.0/8` |
| `windash` | **five characters, not two**: it permutes ASCII `-` (0x2D), ASCII `/` (0x2F), en dash U+2013, em dash U+2014 and horizontal bar U+2015. The three Unicode dashes are exactly the flag-obfuscation trick a Sherlock question tests, so `windash` is not an optional nicety on a command-line selection |
| `exists` | `true`/`false` on field **presence only** - "not its value, be it empty or null". A field present and null satisfies `exists: true` |
| `fieldref` | the value names another field to compare against, not a literal |
| `lt` / `lte` / `gt` / `gte` | numeric comparison; numeric values only |
| `minute` `hour` `day` `week` `month` `year` | extract that component from a date value. The appendix warns they are "not designed to handle timezone or format conversions", so an off-hours question answered with `|hour` inherits whatever timezone the records already carry |

The plain `?` and `*` wildcards work inside any string value: `?` is one mandatory
character, `*` is unbounded.

**The case trap in the rule above.** `sel_path_appdata` and `sel_path_public` use
`|contains`, which is case-insensitive, but `sel_path_temp` uses `|re|i` - the `i`
is load-bearing. Written as a bare `|re` it would match `\Temp\` and miss
`\temp\` and `\TEMP\`, and a command line is free to spell the path either way.

The encoded-command idiom, spelled out, because it is the one a PowerShell question
needs:

```yaml
    selection_enc:
        CommandLine|base64offset|utf16le|contains: 'IEX(New-Object'
```

### The field-name problem, and why chainsaw needs --mapping

A Sigma field name is a name in Sigma's taxonomy. It is **not** the path to that
value in a converted EVTX record. Nothing in the rule says where `CommandLine`
lives. The mapping file supplies that, and chainsaw refuses to run Sigma rules
without one - not a style preference but a clap constraint: in chainsaw's
`src/main.rs` the `sigma` argument is declared
`#[arg(short = 's', long = "sigma", number_of_values = 1, requires = "mapping")]`,
so `-s` without `-m` fails at argument parsing before a single record is read. The
README's prose does not say this; the source does.

Measured on 2026-09-28 against chainsaw's own `mappings/sigma-event-logs-all.yml`
(825 lines, fetched from raw.githubusercontent.com/WithSecureOpenSource/chainsaw/
master/mappings/): one group named `Sigma`, its timestamp field
`Event.System.TimeCreated`, its group filter `Provider: "*"`, **164** field
mappings (`grep -c 'from:'`), **28** `logsource.category` preconditions and **36**
`logsource.service` preconditions. Only two mapping files ship at all - that one
and `sigma-event-logs-legacy.yml`.

The group header, verbatim, file lines 328-338:

```yaml
groups:
  - name: Sigma
    timestamp: Event.System.TimeCreated
    filter:
      Provider: "*"
    fields:
      - from: Provider
        to: Event.System.Provider
      - name: Event ID
        from: EventID
        to: Event.System.EventID
```

and the `CommandLine` entry, verbatim, file lines 409-411 - a different part of the
file, and note the third key:

```yaml
      - from: CommandLine
        to: Event.EventData.CommandLine
        visible: false
```

So `CommandLine` in the rule becomes `Event.EventData.CommandLine` in the record,
and `EventID` becomes `Event.System.EventID`. `visible: false` means the field is
used for matching but is **not printed in the default tabular output**, so a hit on
a command-line rule shows you nothing about the command line until you add `--full`
or `--json`. That is the whole of what `--mapping` buys, and it is why the same rule
needs a different mapping for a JSONL export than for a Splunk index.

`logsource.category` is resolved to a Provider plus an event ID set, verbatim from
that file:

```yaml
    - for:
        logsource.category: process_creation
      filter:
        - Provider: Microsoft-Windows-Sysmon
          int(EventID): 1
        - Provider: Microsoft-Windows-Security-Auditing
          int(EventID): 4688
```

All **28** categories in that file, measured by walking its `preconditions:`
block. Every one but `process_creation` resolves to `Provider:
Microsoft-Windows-Sysmon` alone:

| category | Sysmon event ID(s) | category | Sysmon event ID(s) |
|---|---|---|---|
| `process_creation` | 1 (+ Security 4688) | `dns_query` | 22 |
| `network_connection` | 3 | `file_delete` | 23 |
| `sysmon_status` | 4, 16 | `clipboard_change` | 24 |
| `process_termination` | 5 | `process_tampering` | 25 |
| `driver_load` | 6 | `file_delete_detected` | 26 |
| `image_load` | 7 | `file_block` | 27 |
| `create_remote_thread` | 8 | `file_block_executable` | 27 |
| `raw_access_thread` | 9 | `file_block_shredding` | 28 |
| `process_access` | 10 | `file_executable_detected` | 29 |
| `file_event` | 11 | `registry_event` | 12, 13, 14 |
| `registry_add` | 12 | `registry_set` | 13 |
| `registry_delete` | 12 | `registry_rename` | 14 |
| `create_stream_hash` | 15 | `pipe_created` | 17, 18 |
| `wmi_event` | 19, 20, 21 | `sysmon_error` | 255 |

**Two collisions in that table, and both cost answers.** `registry_add` and
`registry_delete` both resolve to event ID **12** only, so a rule written under
`registry_delete` is offered every registry *creation* as well. Microsoft names
event 12 "RegistryEvent (Object create and delete)" and says "Registry key and
value create and delete operations map to this event type" (Microsoft Learn,
Sysmon) - the add/delete distinction lives in the record's `EventType` field, which
the precondition never looks at. That field is real and mapped: line 466 of the
same mapping reads `from: EventType` / `to: Event.EventData.EventType`, and
SwiftOnSecurity's `sysmonconfig-export.xml` filters it as
`<EventType condition="is">CreateKey</EventType>`. Same collision shape for
`file_block` and `file_block_executable`, both event ID **27**. If a question turns
on a deletion, filter `Event.EventData.EventType` yourself rather than trusting the
category.

`logsource.service` is resolved to a **Provider**, not a Channel. The Provider is
what chainsaw filters on; the Channel is what the file on disk is named after.
**12 of the 36** services below, chosen because they are the ones a Sherlock
bundle actually ships. The other 24 include `capi2`, `codeintegrity-operational`,
`dhcp`, `printservice-admin`, `shell-core`, `openssh`, `ldap`, `dns-client`,
`ntfs`, `msexchange-management` -> Provider `MSExchange CmdletLogs`, and
`lsa-server`, whose Provider is the bare string `LsaSrv` with no
`Microsoft-Windows-` prefix at all. Four services share a Provider in pairs
(`ldap`/`ldap_debug`, `smbclient-security`/`smbclient-connectivity`,
`printservice-admin`/`printservice-operational`), so the service name alone does
not narrow the channel. **Measured oddity:** one precondition in that file is keyed
on a rule UUID rather than on a logsource at all -
`id: 4a3a2b96-d7fc-4cb9-80e4-4a545fe95f46` with a `# Remote Service Creation Rule`
comment, filtered to `Microsoft-Windows-Security-Auditing` or `System`. A rule can
therefore be re-scoped by its id, invisibly to anyone reading only its logsource:

| `service:` | Provider (verbatim from the mapping) | Channel |
|---|---|---|
| `security` | `Microsoft-Windows-Security-Auditing` | `Security` |
| `sysmon` | `Microsoft-Windows-Sysmon` | `Microsoft-Windows-Sysmon/Operational` |
| `taskscheduler` | `Microsoft-Windows-TaskScheduler` | `.../TaskScheduler/Operational` |
| `terminalservices-localsessionmanager` | `Microsoft-Windows-TerminalServices-LocalSessionManager` | `.../LocalSessionManager/Operational` |
| `windefend` | `Microsoft-Windows-Windows Defender` | `.../Windows Defender/Operational` |
| `bits-client` | `Microsoft-Windows-Bits-Client` | `.../Bits-Client/Operational` |
| `wmi` | `Microsoft-Windows-WMI-Activity` | `.../WMI-Activity/Operational` |
| `ntlm` | `Microsoft-Windows-NTLM` | `.../NTLM/Operational` |
| `smbclient-security` | `Microsoft-Windows-SMBClient` | `.../SMBClient/Security` |
| `firewall-as` | `Microsoft-Windows-Windows Firewall With Advanced Security` | `.../Firewall` |
| `applocker` | `Microsoft-Windows-AppLocker` | four channels under `.../AppLocker/`: `EXE and DLL`, `MSI and Script`, `Packaged app-Deployment`, `Packaged app-Execution` |

Only the `security` row is confirmed end to end. SigmaHQ's upstream logsource
guide, at the repository path documentation/logsource-guides/windows/service/
security (not a file in this tree), gives
`Provider: Microsoft Windows Security Auditing`,
`GUID: {54849625-5478-4994-a5ba-3e3b0328c30d}`, `Channel: Security`, and Microsoft
Learn's 4624 page shows the same GUID in the event XML. The Provider strings in the
other rows are verbatim from chainsaw's mapping; the Channel column is from
`windows-event-logs.md` in this directory. **Measured:** the sibling logsource
guides upstream for sysmon, powershell and taskscheduler, and the rest of
that directory, are still stubs reading `Coming Soon`, so there is no upstream
authority to cite for them today.

**Measured trap:** neither `ps_script` nor a `powershell` service appears in
`sigma-event-logs-all.yml`'s preconditions, and the group filter is `Provider: "*"`.
A PowerShell 4104 rule under that mapping is therefore not narrowed to the
PowerShell provider at all - it is offered every record. Check the hit count against
a `chainsaw search -t 'Event.System.EventID: =4104'` baseline before believing it.
The file also carries a title-based `exclusions:` list (16 rule titles, including
`Non Interactive PowerShell`), so a rule can be silently skipped by name.

## 2. Running a rule set

**All three engines below are ABSENT on this box.** `toolchain.md` in this
directory has the one-line apt install that brings `chainsaw` (with its own
mappings and rules under `/usr/share/chainsaw/`), and the rank-5 route for hayabusa
and Zircolite. Until that has been run, section 2 is reference and the working path
is the last two blocks of this section.

### chainsaw

Flags below are from the `chainsaw` README's own usage blocks
(WithSecureOpenSource/chainsaw - the Labs and countercept URLs 301 to it).

```bash
chainsaw hunt <evtx dir> -s <sigma dir> --mapping <mapping file> \
  --level high --level critical --status stable \
  --from 2026-09-01T00:00:00 --to 2026-09-30T00:00:00 --json -o hunt.json
chainsaw hunt <evtx dir> -r <chainsaw rule dir> --csv -o hunt/
```

`-s/--sigma`, `-r/--rule`, `--mapping`, `--level`, `--status`, `--kind` and
`--extension` are all repeatable (`...` in the usage block). `--mapping` is what
tells chainsaw "which fields in the event logs to use for rule matching" and is
required alongside `-s` (the `requires = "mapping"` attribute quoted in section 1);
`-r` rules are chainsaw's own format and carry their own field paths, so they need
no mapping.

Timestamps: `src/main.rs` declares `--local` and `--timezone <timezone>` both with
`group = "tz"`, which makes them mutually exclusive opt-ins with no third member,
so the unflagged default is neither - chainsaw renders **UTC**. The README states
no default, so this is derived from the argument definitions, not quoted. Do not
pass `--local` and then answer a UTC question.

Search, which is the part that answers a Sherlock question directly. Two distinct
matchers: `-t` is a Tau expression over the mapped record path, and `-e` is a
regular expression over the record text.

```bash
chainsaw search <evtx dir> -t 'Event.System.EventID: =4624' --json
chainsaw search <evtx dir> -t 'Event.EventData.LogonType: =10' --json
chainsaw search <evtx dir> -e '(?i)\-enc(odedcommand)?\s' -i --json
chainsaw search <evtx dir> -t 'Event.System.EventID: =4698' \
  --from 2026-09-14T00:00:00 --timestamp Event.System.TimeCreated --json
```

`=4624` with the leading `=` is Tau's integer equality; without it the value is
matched as a string and an integer-typed `EventID` will not match.

```bash
chainsaw analyse gaps <evtx dir>          # chronological and RecordID gaps
chainsaw analyse shimcache <SYSTEM hive>  # execution timeline, amcache enrichment
chainsaw analyse srum <SRUDB.dat> <SOFTWARE hive>
chainsaw dump <artefact> --jsonl -o out.jsonl
```

`analyse gaps` is the check to run after a 1102: it detects "chronological or
RecordID gaps in evtx files (possible selective record deletion)", which dates a
clearing even when the 1102 itself was carved out.

### hayabusa

**The stale-snippet trap:** `csv-timeline` and `json-timeline` do not exist in
current hayabusa. Release v4.0.0 merged them into one `dfir-timeline` command, and
the same release lower-cased every long option name. So:

```bash
hayabusa dfir-timeline -d <evtx dir> -t jsonl -o timeline.jsonl -O
hayabusa dfir-timeline -f <one.evtx> -t csv  -o timeline.csv  -U
```

**Measured from `src/detections/configs.rs` on the `main` branch, 2026-09-28** -
hayabusa is ABSENT on this box, so these are read off the clap attributes, not off
a `--help` run here:

| Flag | Declaration in `configs.rs` | What it does |
|---|---|---|
| `-d`, `--directory <DIR>` | `Option<Vec<PathBuf>>`, `conflicts_with_all = ["filepath", "live_analysis"]` | a directory of `.evtx` |
| `-f`, `--file <FILE>` | long name is `file`, **not** `filepath` | one `.evtx` |
| `-t`, `--output-type <OUTPUT_FORMAT>` | `default_value = "csv"`, `ignore_case = true` | `csv`, `json` or `jsonl` |
| `-U`, `--utc` | doc comment: "Output time in UTC format (default: local time)" | **this is the sentence that proves the default is local** |
| `-O`, `--iso-8601` | doc comment: "Output timestamp in original ISO-8601 format (ex: 2022-02-22T10:10:10.1234567Z) **(Always UTC)**" | ISO-8601, and UTC on its own |

`is_utc_output()` in that file is literally `self.utc || self.iso_8601`, so
`-U --iso-8601` is redundant: **`-O` alone already gives UTC.** The other three time
formats are *not* UTC - `--european-time`, `--rfc-2822` and `--rfc-3339` all render
local, so picking a human-readable format silently changes the timezone of every
answer you copy out.

On the long-flag spelling: v4.0.0 lower-cased every long option (`--UTC` became
`--utc`, `--ISO-8601` became `--iso-8601`). The shorts `-U` and `-O` are stable
across 3.x and 4.x, so prefer the shorts and the version question disappears.
Run `hayabusa --help` once the binary exists and trust that over this table.

### Zircolite - the one that covers Linux

Zircolite loads events into SQLite and runs a converted Sigma ruleset over it,
which is why it is the engine for auditd and Sysmon for Linux (its README):

```bash
python3 zircolite.py --events auditd.log  --ruleset rules/rules_linux.json --auditd
python3 zircolite.py --events sysmon.log  --ruleset rules/rules_linux.json --sysmon4linux
python3 zircolite.py --evtx <evtx dir>    --ruleset rules/rules_windows_merged.json
python3 zircolite.py --evtx sample.evtx   --ruleset ./sigma/rules/windows/process_creation \
  --pipeline sysmon --pipeline windows-logsources
```

`--ruleset` may be a prebuilt JSON ruleset, a single `.yml` rule, or a directory of
Sigma rules; `--pipeline` supplies the field mapping in the directory case. Other
input shapes: `--jsononly`, `--json-array`, `--csv-input`, `--xml-input`.

### The parser-free route: sigma-cli

`sigma-cli` converts rules to a target query language and never touches an EVTX
file, so it works on this box today. Its own README:

```bash
sigma plugin list
sigma plugin install splunk
sigma list targets
sigma list pipelines
sigma convert -t splunk -p sysmon <rule dir or file>
sigma convert -t esql -p ecs_windows --output-dir translated/ rules/
```

`-t` is the backend, `-p` a processing pipeline (repeatable), `-f` a backend output
format (`sigma list formats <backend>`), `-O key=value` a backend option. This is
how a rule written in section 1 becomes the SPL of section 3 or the Elastic query of
section 4 without installing a hunting engine.

### Day zero, with nothing installed

```bash
python3 tools/forensics/evtx_query.py --input security.jsonl --event-id 4698 \
  --field-contains TaskName=\\ --challenge <sherlock>-q7 --answer TaskName
python3 tools/forensics/evtx_query.py --input sysmon.jsonl --event-id 1 \
  --field ProcessGuid='{...}' --challenge <sherlock>-q7 --excerpt 400
```

`evtx_query.py` resolves a field by dotted path (`Event.System.EventID`), by bare
name (`EventID`), and case-insensitively, and it flattens both the
`TimeCreated_attributes.SystemTime` shape and the `<Data Name="...">` list shape,
so the same filter works across converters. `--answer FIELD` emits the
`tools/hooks.py pre-flag` argv for the value it found, which is how a query result
becomes a recorded answer instead of a claim.

## 3. Splunk SPL

Assume the bundle has been indexed. **First command of the session**, because field
names are add-on dependent and guessing them wastes the whole budget:

```
index=<idx> | fieldsummary maxvals=5
```

The Splunk Add-on for Windows renders 4624 with `EventCode`, `Account_Name`,
`Logon_Type`, `Source_Network_Address`; a JSONL import of an `evtx_dump` export
keeps `Event.EventData.TargetUserName`. They are not interchangeable.

**Counting, which answers "how many" and "which account":**

```
index=<idx> EventCode=4625
| stats count AS attempts, dc(Account_Name) AS distinct_names,
        values(Source_Network_Address) AS sources,
        earliest(_time) AS first, latest(_time) AS last BY Account_Name
| sort - attempts
```

Many distinct names with one attempt each is enumeration; one name with many
attempts is a password attack. The 4625 `Status`/`SubStatus` split in
`windows-event-logs.md` is the confirming field.

**Sessionising a logon, which answers "for how long":** `transaction` groups events
by shared field values and **adds `duration` and `eventcount`** to the result
(Splunk search reference, transaction).

```
index=<idx> (EventCode=4624 OR EventCode=4634)
| transaction Logon_ID maxspan=24h keepevicted=true
    startswith="EventCode=4624" endswith="EventCode=4634"
| table Logon_ID, Account_Name, Logon_Type, duration, eventcount
```

`maxspan` caps the whole transaction, `maxpause` the gap between consecutive
events, `maxevents` the count. Set `maxspan` deliberately: the default lets a
`Logon_ID` value reused days later collapse into one session.

**streamstats for "the gap between consecutive events":** `current=f` makes the
aggregate use the *previous* event, which is what a delta needs
(Splunk search reference, streamstats).

```
index=<idx> EventCode=4625 | sort 0 _time
| streamstats current=f last(_time) AS prev_time BY Account_Name
| eval gap_secs = _time - prev_time
| where gap_secs < 2
```

Its full option list is
`streamstats [reset_on_change=<bool>] [reset_before="(<eval-expression>)"]
[reset_after="(<eval-expression>)"] [current=<bool>] [window=<int>]
[time_window=<span-length>] [global=<bool>] [allnum=<bool>] <stats-agg-term>...
[BY <field-list>]`. `window` needs `global=false` to window per group.

**eventstats for "which one is unusual":** same aggregation syntax as `stats`, but
the result is attached to every event instead of replacing them, so the next
`where` can compare an event to its own group's baseline.

```
index=<idx> EventCode=3
| eventstats avg(bytes_out) AS avg_out, stdev(bytes_out) AS sd_out BY dest_ip
| where bytes_out > avg_out + 3 * sd_out
```

**bin for "which hour / which 5 minutes":**

```
index=<idx> EventCode=4624 Logon_Type=10
| bin _time span=5m
| stats count, values(Account_Name) AS accounts BY _time, Source_Network_Address
| sort - count
```

`bin [<bin-options>] <field> [AS <newfield>]` with `span`, `bins` (default 100),
`minspan`, `start`/`end`, `aligntime`.

**rex for a value that was never extracted:** named capture groups only, in the
`(?<name>pattern)` form.

```
index=<idx> | rex field=_raw "Logon Type:\s+(?<logon_type>\d+)"
index=<idx> | rex field=CommandLine "(?i)-e(?:nc|ncodedcommand)?\s+(?<b64>[A-Za-z0-9+/=]{40,})"
index=<idx> | rex field=Message max_match=0 "(?<ip>\d{1,3}(?:\.\d{1,3}){3})"
```

`max_match=0` returns every match as a multivalue field rather than the first.

**tstats when the set is large:**

```
| tstats count WHERE index=<idx> BY _time span=1h, host
| tstats summariesonly=f prestats=t count FROM datamodel=<dm> WHERE earliest=-3h BY _time span=1h
| timechart span=1h count
```

**The tstats trap:** it reads the index-time tsidx files, so only indexed fields
are available - `_time`, `host`, `source`, `sourcetype`, `index`, plus the fields of
an accelerated data model. `BY EventCode` is a search-time extraction and returns
nothing. Either go through `FROM datamodel=` or drop back to `stats`.

**Answering a timestamp question in UTC.** `_time` is epoch, stored UTC.
`strftime(<time>,<format>)` takes exactly two arguments (Splunk date-and-time
functions) - there is **no timezone argument** - and it renders in the timezone of
the user account running the search. So this is correct only if that account's
timezone preference is UTC:

```
index=<idx> EventCode=4720
| eval when = strftime(_time, "%Y-%m-%d %H:%M:%S")
| table when, Account_Name, Security_ID
```

Two ways to stop guessing. Render the offset and read it:

```
| eval when = strftime(_time, "%Y-%m-%dT%H:%M:%S%z")
```

Or take the epoch out of Splunk and convert where the timezone is explicit:

```
| eval epoch = _time | table epoch, Account_Name
```

```bash
python3 -c 'import datetime,sys; print(datetime.datetime.fromtimestamp(float(sys.argv[1]), datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))' 1757836800
```

`strptime(<str>,<format>)` has the same timezone behaviour on the way in, so a
string parsed without an offset in it is parsed as the searching user's local time.
`answer-discipline.md` in this directory owns the format rules for the submission
itself.

## 4. Elastic: KQL and EQL

### KQL - filtering

`field: value`, with the field name optional (omit it and KQL searches all fields)
(Elastic KQL reference).

```
event.code: "4624" and winlog.event_data.LogonType: "10"
event.code: "4625" and not user.name: ("SYSTEM" or "DWM-1")
process.command_line: *EncodedCommand*
winlog.event_data.IpAddress: *
winlog.channel: "Microsoft-Windows-Sysmon/Operational" and event.code: ("3" or "22")
http.response.bytes > 10000 and http.response.bytes <= 20000
user.names: { first: "Alice" and last: "White" }
```

Quoting a value makes it a phrase and enforces term order. `field: *` is the
existence test. `and`/`or`/`not` are case-insensitive and parentheses set
precedence. The `{ }` form is for nested objects and needs the full path.

### EQL - sequences, which is the ProcessGuid pivot as a query

EQL is the reason to reach for Elastic on a Sherlock: the execution chain in
`method.md` is a join on `ProcessGuid`, and EQL expresses that join as a first-class
construct instead of two greps and a copy-paste.

ECS names the field `process.entity_id`, and its own definition says the
implementation is source-specific with "Sysmon Process GUIDs" given as an example
(ECS process field reference). So for a Sysmon-sourced index, `process.entity_id`
*is* the `ProcessGuid`.

```eql
sequence by process.entity_id with maxspan=10m
  [ process where process.name : "powershell.exe" ]
  [ network where true ]
```

The pieces, all from the Elastic EQL syntax reference:

```eql
sequence
  [ event_category_1 where condition_1 ]
  [ event_category_2 where condition_2 ]
```

- events are listed in ascending chronological order, most recent last;
- `sequence by <field>` joins on one field shared by every item; a per-item
  `by <field>` joins fields with *different* names, e.g.
  `[ file where ... ] by file.path` then `[ process where ... ] by process.executable`;
- `with maxspan=15m` constrains the whole sequence from the first event's timestamp;
- `until [ ... ]` is an expiration event: a sequence whose expiration event falls
  *between* its matches is discarded, one whose expiration falls after is kept, and
  the expiration event is not returned;
- `![ ... ]` matches a **missing** event, and `with maxspan` is mandatory when a
  missing-event clause is present.

The missing-event example from that page is a Sherlock question verbatim - a logon
with no logoff:

```eql
sequence by host.name, user.name with maxspan=5s
  [ authentication where event.code : "4624" ]
  ![ authentication where event.code : "4647" ]
```

Operators: `==` and `!=` are case-sensitive and do **not** support wildcards; `:` is
case-insensitive string equality and does support wildcards and list lookups; `<`,
`<=`, `>=`, `>` compare, using case-sensitive lexicographic order on strings. `=`
is not an equality operator at all. Pattern matching is `like` / `like~` (wildcard,
case-sensitive / insensitive) and `regex` / `regex~`. A list lookup is
`my_field : ("value-1", "value2", "val3")`, with `in` / `in~` as the keyword form.

## 5. ATT&CK mapping, offline

`mitre-attack/attack-stix-data` is the current distribution: STIX **2.1**, with
collections. `mitre/cti` is the same dataset in STIX 2.0 and without collections -
older, and the wrong one to fetch now (attack-stix-data README).

```bash
mkdir -p attack && cd attack
curl -sSL -C - --retry 20 --retry-all-errors -O \
  https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/enterprise-attack/enterprise-attack.json
curl -sSL -O \
  https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/index.json
```

**Measured on 2026-09-28:** `enterprise-attack.json` is 53,835,637 bytes and holds
**26,086** objects; the `x-mitre-collection` object in it reports
`x_mitre_version` **19.2**, which `index.json` agrees is the latest Enterprise
version. The bundle's `type` is `bundle` and it carries **no** top-level
`spec_version` key - a 2.1 bundle omits it, so do not test for it. Download it
before a Sherlock; on this box the transfer ran at roughly 25 KB/s and needed a
resumed `-C -` fetch to finish.

An ATT&CK ID lives in `external_references` where `source_name == "mitre-attack"`,
as `external_id`; a sub-technique carries `x_mitre_is_subtechnique: true` and a
`subtechnique-of` relationship to its parent (attack-stix-data README).

**ID to name**, every non-revoked technique as a lookup table:

```bash
jq -r '.objects[]
  | select(.type=="attack-pattern" and .revoked!=true and .x_mitre_deprecated!=true)
  | ((.external_references[]|select(.source_name=="mitre-attack")|.external_id)
     + "\t" + .name)' attack/enterprise-attack.json | sort > attack/techniques.tsv
grep -P '^T1053\.005\t' attack/techniques.tsv
```

**Name to ID**, which is the direction a question actually asks:

```bash
jq -r --arg n "clear windows event logs" '.objects[]
  | select(.type=="attack-pattern")
  | select((.name|ascii_downcase)==$n)
  | [(.external_references[]|select(.source_name=="mitre-attack")|.external_id),
     .name, (.x_mitre_is_subtechnique|tostring), (.revoked|tostring)]|@tsv' \
  attack/enterprise-attack.json
```

**Measured, and the reason `.revoked` is in that output:** that exact query returns
**two** rows - `T1070.001 Clear Windows Event Logs true true` and
`T1685.005 Clear Windows Event Logs true false`. A name lookup without the revoked
column silently hands back a retired ID.

**Sub-techniques of a parent.** The cheap way is a prefix filter on the TSV above:

```bash
grep -P '^T1547\.' attack/techniques.tsv
```

The correct way follows the relationship, which also survives a renumbering:

```bash
jq -r '
  (reduce (.objects[]|select(.type=="attack-pattern")) as $o ({};
     .[$o.id] = [($o.external_references[]|select(.source_name=="mitre-attack")|.external_id),
                 $o.name, ($o.revoked==true)])) as $ap
  | [.objects[]|select(.type=="relationship" and .relationship_type=="subtechnique-of")]
  | map(select($ap[.target_ref][0]=="T1053")
        | ($ap[.source_ref][0]+"\t"+$ap[.source_ref][1]+"\trevoked="+($ap[.source_ref][2]|tostring)))
  | sort | .[]' attack/enterprise-attack.json
```

Measured output for `T1053`: `T1053.002 At`, `T1053.003 Cron`, `T1053.004 Launchd`,
`T1053.005 Scheduled Task`, `T1053.006 Systemd Timers`,
`T1053.007 Container Orchestration Job`, all `revoked=false`.

**Old ID to new ID**, via the `revoked-by` relationship:

```bash
jq -r '
  (reduce (.objects[]|select(.type=="attack-pattern")) as $o ({};
     .[$o.id] = [($o.external_references[]|select(.source_name=="mitre-attack")|.external_id), $o.name])) as $ap
  | [.objects[]|select(.type=="relationship" and .relationship_type=="revoked-by")]
  | map(select($ap[.source_ref][0]=="T1070.001")
        | ($ap[.source_ref][0]+" -> "+$ap[.target_ref][0]+" "+$ap[.target_ref][1]))
  | .[]' attack/enterprise-attack.json
```

**Which tactic a technique belongs to**, from `kill_chain_phases`:

```bash
jq -r '.objects[] | select(.type=="attack-pattern" and .revoked!=true)
  | select((.external_references[]|select(.source_name=="mitre-attack")|.external_id)=="T1547.001")
  | [.kill_chain_phases[]|select(.kill_chain_name=="mitre-attack")|.phase_name]|join(",")' \
  attack/enterprise-attack.json
```

Measured: `T1547.001` returns `persistence,privilege-escalation` - a technique can
sit under more than one tactic, so "which tactic" can have two right answers and the
question's wording decides.

**The tactics**, measured from the `x-mitre-tactic` objects in v19.2:

```bash
jq -r '.objects[]|select(.type=="x-mitre-tactic")
  | [(.external_references[]|select(.source_name=="mitre-attack")|.external_id),
     .x_mitre_shortname, .name]|@tsv' attack/enterprise-attack.json | sort
```

| ID | shortname | name |
|---|---|---|
| TA0043 | reconnaissance | Reconnaissance |
| TA0042 | resource-development | Resource Development |
| TA0001 | initial-access | Initial Access |
| TA0002 | execution | Execution |
| TA0003 | persistence | Persistence |
| TA0004 | privilege-escalation | Privilege Escalation |
| TA0005 | stealth | Stealth |
| TA0006 | credential-access | Credential Access |
| TA0007 | discovery | Discovery |
| TA0008 | lateral-movement | Lateral Movement |
| TA0009 | collection | Collection |
| TA0011 | command-and-control | Command and Control |
| TA0010 | exfiltration | Exfiltration |
| TA0040 | impact | Impact |
| TA0112 | defense-impairment | Defense Impairment |

### The version trap, measured

ATT&CK renumbers. All of the following was measured against the v19.2 bundle and
against `attack.mitre.org` on 2026-09-28:

- `TA0005` is now named **Stealth**, shortname `stealth`. The name
  "Defense Evasion" is what every older writeup and every Sigma `attack.*` tag
  uses.
- `TA0112` **Defense Impairment** is new, and it did not exist in older versions.
- `T1562` **Impair Defenses** is revoked; `attack.mitre.org/techniques/T1562/`
  serves `<meta http-equiv="refresh" content="0; url=/techniques/T1685"/>`, and
  `T1685` is **Disable or Modify Tools**.
- `T1070.001` **Clear Windows Event Logs** is revoked in favour of **T1685.005**,
  same name, and `T1685.005`'s tactic is `defense-impairment`.
- `T1070` itself is still **Indicator Removal**, and `T1070.004 File Deletion` and
  `T1070.006 Timestomp` are still live. Only some children moved.

So a Sherlock question is answered in the ATT&CK version it was written against.
Answer with the current ID, and if it is rejected, submit the revoked one that the
`revoked-by` query above maps it to. Never guess which - the two queries cost
seconds.

### The recurring technique set, verified against v19.2

Every ID and name below was read out of the bundle with the ID-to-name query above,
not from memory. The artifact column is the evidence a Sherlock bundle actually
carries; the event-ID semantics are in `windows-event-logs.md` and
`registry-and-execution.md` in this directory.

| ID | Name (v19.2) | Artifact that evidences it |
|---|---|---|
| T1059.001 | PowerShell | PowerShell/Operational **4104** script block text; 4103 pipeline detail; classic 400/403/600 |
| T1059.003 | Windows Command Shell | Sysmon **1** or Security **4688** with `Image` ending `\cmd.exe` and a `/c` command line |
| T1053.005 | Scheduled Task | Security **4698** (task registered, full task XML inside the event), TaskScheduler/Operational **106** registration and **200** action start. 200 carries `ActionName`, the executable path, but **no command line** - so the arguments only exist in 4698's XML or on disk, plus the `TaskCache\Tree` registry key |
| T1136.001 | Local Account | Security **4720** (`TargetUserName`, and `SubjectUserName` for who created it), 4722 enabled, 4724 password reset, 4732 added to a local group; SAM key last-write time |
| T1685.005 | Clear Windows Event Logs | Security **1102**; `chainsaw analyse gaps` for a RecordID discontinuity when the 1102 itself is gone |
| T1547.001 | Registry Run Keys / Startup Folder | `SOFTWARE\Microsoft\Windows\CurrentVersion\Run` and `RunOnce`, the NTUSER.DAT equivalents, the Startup folder, and Sysmon **13** on that value |
| T1021.001 | Remote Desktop Protocol | Security **4624 LogonType 10** (Microsoft Learn calls type 10 `RemoteInteractive`), TerminalServices-LocalSessionManager **21** (session logon succeeded) / **25** (session reconnection succeeded), RemoteConnectionManager **1149**. 21 and 25 carry their own `Source Network Address`; a value of the literal string `LOCAL` there means a console session, **not** a remote one, and answering an "from which IP" question with a 25 whose address is `LOCAL` is the standard wrong answer |
| T1543.003 | Windows Service | System **7045** (service name, image path, start type) and Security **4697**; `SYSTEM\CurrentControlSet\Services` |
| T1110.003 | Password Spraying | many Security **4625** with `SubStatus 0xC000006A` across many distinct `TargetUserName` values from one `IpAddress` |
| T1003.001 | LSASS Memory | Sysmon **10** `ProcessAccess` with `TargetImage` ending `\lsass.exe` and a `GrantedAccess` including read-memory rights; Sysmon 11 for a dump file written |
| T1105 | Ingress Tool Transfer | Sysmon **3** and **22**; BITS-Client/Operational **59** transfer started / **60** completed - and **61** in place of 60 when the transfer was interrupted, which is the one people miss. The URL is the `RemoteName` field; `JobId`, `JobTitle` and the job owner are in the same record, and the **destination path is not** - pair it with Sysmon 11. Also the `Zone.Identifier` alternate data stream's host URL |
| T1027.010 | Command Obfuscation | PowerShell **4104** carrying `-enc` or `FromBase64String`, logged after deobfuscation |
| T1218.011 | Rundll32 | Sysmon **1** with `Image` ending `\rundll32.exe` and an export name in the command line (LOLBAS entry `Rundll32`) |
| T1112 | Modify Registry | Sysmon **12**/**13**/**14** with `TargetObject` and `Details` |
| T1070.006 | Timestomp | Sysmon **2** (file creation time changed), and an `$MFT` `$STANDARD_INFORMATION` created time earlier than the `$FILE_NAME` one |
| T1070.004 | File Deletion | `$J` USN journal delete reason flags, Sysmon **23** (FileDelete, *archived*) / **26** (FileDeleteDetected, logged only), `$Recycle.Bin` `$I` records. Sysmon 23 copies the deleted file into `ArchiveDirectory`, `C:\Sysmon` by default (Microsoft Learn, Sysmon) - if the bundle carries that directory, the deleted payload itself is in it |
| T1041 | Exfiltration Over C2 Channel | one capture conversation whose outbound byte count dominates, joined to Sysmon 3 by the 5-tuple |
| T1048.003 | Exfiltration Over Unencrypted Non-C2 Protocol | cleartext FTP or HTTP PUT in the capture, with the object extractable |
| T1567.002 | Exfiltration to Cloud Storage | Sysmon **22** `QueryName` for a storage provider, plus browser history |
| T1078.003 | Local Accounts | Security **4624** for an existing local account with no preceding 4720 |
| T1087.001 | Local Account Discovery | Sysmon **1** command lines running `net user`, `net localgroup`, `whoami /groups` |
| T1204.002 | Malicious File | Sysmon **1** whose `ParentImage` is an Office or archive application; `Zone.Identifier` on the child file |
| T1071.001 | Web Protocols | Sysmon **3** to 80/443 joined by `ProcessGuid` to a non-browser `Image`; capture User-Agent |

Directory-attack traces belong in this table by artifact identity, never by tool
name - for example event **4662** carrying the `DS-Replication-Get-Changes-All`
control access right requested by an account that is not a domain controller
computer account. `windows-event-logs.md` holds the rest of that list, and the scope
clause in `../../AGENTS.md` says why it is written that way.

## 6. Answering a technique-id question

Four steps, in this order, and never skip to step 3.

1. **Behaviour.** State in one sentence what happened, from an artifact you have
   already quoted. "A task named `\Updater` was registered at 02:14:09Z running
   `C:\Users\Public\svc.exe`." If you cannot write that sentence from a record,
   the question is not ready to answer.
2. **Artifact.** Name the record and field that proves it: Security 4698,
   `TaskName` and the `<Command>` inside the task XML. Right-hand column of the
   table in section 5, read right to left.
3. **Technique.** Resolve the name to an ID with the name-to-ID jq, with the
   `.revoked` column shown. Do not type an ID you did not resolve.
4. **Granularity.** Answer at the granularity the question asks for. "Which
   technique" usually wants the sub-technique, `T1053.005`. "Which parent
   technique" or a question with no dotted ID in the sample answer wants `T1053`.
   A question naming a tactic wants `TA0002`, or `execution`, and
   `answer-discipline.md` decides which spelling.

The two failure modes this replaces. Answering from the scenario prose - the
scenario says "the attacker created a persistence mechanism" and the answer becomes
`T1547.001` when the artifact actually shows a service, `T1543.003`. And answering
with a technique whose artifact is not in the bundle at all, which is a guess with
an ID attached to it.

Record it like any other answer:

```bash
python3 tools/hooks.py pre-flag <sherlock>-q7 --value 'T1136.001' \
  --source artifact --evidence '<verbatim 4720 record excerpt>'
```

The evidence is the **4720 record**, not the ATT&CK page. The mapping is
`hypothesizer` work; only the record is `reader` work.

## Falsifier

This file is the wrong one when:

- no query engine and no ATT&CK bundle are in play and the question wants a value
  out of one artifact - that is the artifact-family file, routed from
  `method.md` step 1;
- the question asks what an event ID or a field *means*, rather than how to express
  or classify it - `windows-event-logs.md` owns the event tables and
  `registry-and-execution.md` the hive paths;
- the answer is already in hand and only its format is in doubt -
  `answer-discipline.md`;
- a command here failed because its tool is absent - `toolchain.md`, and use the
  day-zero route at the end of section 2 rather than the next engine.

And the hard stop: a rule that fires is not a finding. A chainsaw or hayabusa hit is
a pointer to a record. Open the record, quote it, and answer from that.
