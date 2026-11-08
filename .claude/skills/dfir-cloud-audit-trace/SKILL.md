---
name: dfir-cloud-audit-trace
description: >
  Action-oriented depth skill for Cloud audit trail. Use after the router or tools/classify.py
  names this class; start with the first probe and record the expected signal. Do not
  use it as proof of a finding. Confusable classes: dfir-authentication-trace, dfir-network-exfil-trace.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [dfir, forensics, cloud, aws, audit-log, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same artifact family: 3 attempts with no new record"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Cloud audit trail

**Catalogue class.** This toolkit has never solved one; everything below is vendor documentation plus what was
measured on fixtures here, not local solve experience - record what happens in `field-notes.md`. The only cloud
provider present in a bundle sampled for this tree is **AWS**: a `CloudTrail/` tree of gzipped JSON, sometimes beside
an S3 tree. Entra ID, M365, Okta and Google Workspace bundles are **UNVERIFIED here** as bundle shapes.

## First probe

```bash
find . -name '*.json.gz' -exec gzip -dc {} + | jq -r '.Records[] | [.eventTime, .eventName,
  .eventSource, .sourceIPAddress, (.userIdentity.type // "-"),
  (.userIdentity.arn // .userIdentity.sessionContext.sessionIssuer.arn // "-"),
  (.userIdentity.accessKeyId // "-"), (.errorCode // "-")] | @tsv' | sort | head -40
```

Ran here on a four-record fixture: 4 rows in `eventTime` order, `AccessDenied` in column 8. Use `find -exec gzip -dc
{} +`, not `zcat CloudTrail/**/*.json.gz` - `**` needs `globstar` in bash and silently matches one level without it.

**Falsifier** - the observation that closes this class: the bundle holds no control-plane audit record, only host or
packet artifacts, so "who did what in the account" cannot be answered here and the question belongs to a host class.

## Recognise

| In the inventory | What it is | Records an object read? |
|---|---|---|
| `AWSLogs/<12-digit-acct>/CloudTrail/<region>/<YYYY>/<MM>/<DD>/*.json.gz`, file `<acct>_CloudTrail_<region>_<YYYYMMDD>T<HHmm>Z<rand>.json.gz`; `AWSLogs/<O-ID>/...` for an organization trail; also `CloudTrail-Insight` / `-NetworkActivity` / `-Aggregated` | CloudTrail, one file per delivery batch | no, unless data events were on |
| space-delimited lines opening with a 64-hex id, `REST.GET.OBJECT` | S3 server access log | **yes** |
| 14 space-separated fields ending `ACCEPT OK` | VPC flow log, default format | no, byte counts only |
| JSON with `type` like `Recon:IAMUser/...` and numeric `severity` | GuardDuty finding | no, a summary |

`tools/forensics/artifact_inventory.py --path <dir> --challenge <c>` files the CloudTrail shapes as family
`cloudtrail-json` - by `CloudTrail` in the path, or `"eventVersion"` plus `"eventSource"`/`"Records"` in the head
(`artifact_inventory.py:225,306`). Measured: an S3 access log, a flow log and a finding all landed in `unknown`.

## Confirm

1. Count records, not files: `... | jq -r '.Records | length' | paste -sd+ | bc`.
2. Bound the window on `eventTime` (UTC, `2023-07-19T21:44:40Z`). The earliest record is a floor set by when the
   trail started, not by the intrusion; say "first recorded action", not "first action".
3. Name the principal from `userIdentity`, not `sourceIPAddress`, and quote the CloudTrail record, not a finding.

## CloudTrail: the envelope, and the field that answers

One gzip member is one JSON object whose only key is `Records`, an array (AWS, *CloudTrail record contents*).

| Field | Answers |
|---|---|
| `eventTime`, `eventName`, `awsRegion` | when (UTC, seconds), which API action, where |
| `eventSource` | which service: `iam.amazonaws.com`, `signin.amazonaws.com`, `sts.amazonaws.com`, `s3.amazonaws.com` |
| `sourceIPAddress`, `userAgent` | from where (`AWS Internal/<n>` when AWS called), and with what - `aws-cli/2.x Python/3.x Linux/...` is the tell |
| `errorCode`/`errorMessage`, `requestParameters`/`responseElements` | whether it was denied and why; the target, then what was created - `responseElements` is `null` when `readOnly` is `true` |
| `eventType`, `eventCategory`, `resources[]`, `sharedEventID` | `AwsApiCall`/`AwsServiceEvent`/`AwsConsoleAction`/`AwsConsoleSignIn`/`AwsVpceEvents`; `Management`/`Data`/`NetworkActivity`; ARN + owner + type `AWS::IAM::Role`; one action seen by two accounts |

`userIdentity.type` is one of `Root`, `IAMUser`, `AssumedRole`, `Role`, `FederatedUser`, `Directory`, `AWSAccount`,
`AWSService`, `IdentityCenterUser`, `Unknown`, plus `SAMLUser`/`WebIdentityUser` on the STS federation APIs (AWS,
*userIdentity element*). `AWSAccount`/`AWSService` mean someone else assumed a role YOU own.

```bash
jq -r '.Records[] | select(.userIdentity.type=="AssumedRole") | [.eventTime,
  (.userIdentity.arn | split("/") | last), .userIdentity.sessionContext.sessionIssuer.arn,
  .userIdentity.sessionContext.attributes.mfaAuthenticated] | @tsv'
```

Ran here: `cli-session`, the issuing role ARN, `false`. That session name - the last `/` segment of
`.userIdentity.arn` - is frequently the answer. `.userIdentity.userName` is **absent** for `AssumedRole`; it lives at
`.sessionContext.sessionIssuer.userName`. `sourceIdentity` sits in `requestParameters` on `AssumeRole`/`WithSAML`/
`WithWebIdentity`, and in `.userIdentity.sessionContext.sourceIdentity` on every later call made with that session -
the second location is the one that names the human behind a role chain.

Console sign-in (AWS, *AWS Management Console sign-in events*): `eventName ConsoleLogin` on `signin.amazonaws.com`,
`responseElements.ConsoleLogin` = `"Success"`/`"Failure"`, `additionalEventData.MFAUsed` = `"Yes"`/`"No"` beside
`MFAIdentifier`; a failure also carries `errorMessage: "Failed authentication"`. `CheckMfa` carries
`additionalEventData.MfaType` (`Virtual MFA`, `U2F MFA`, `Multiple MFA Devices`). `awsRegion` on a `ConsoleLogin` is
NOT where the user was: root lands in us-east-1/us-east-2/us-west-2; an IAM user on the global endpoint lands in
us-east-2/eu-north-1/ap-southeast-2 with an account-alias cookie and us-east-1 without; only a regional sign-in
endpoint records the real one. A mistyped username records `userName` as `HIDDEN_DUE_TO_SECURITY_REASONS` - a value,
not a redaction to undo.

## The API-name patterns that matter

| Shape | Field to read | Why it answers |
|---|---|---|
| `GetCallerIdentity` on `sts.amazonaws.com` | `.userIdentity.accessKeyId` | first touch with stolen credentials: whose key is this |
| `List*`/`Get*`/`Describe*` burst then one `Create*`/`Put*`/`Delete*` | `eventName` + `eventTime` | the recon-then-act boundary; the first write's timestamp is the usual answer |
| `CreateAccessKey`, `CreateLoginProfile` | `.responseElements.accessKey.accessKeyId`, `.requestParameters.userName` | the NEW key id, or a console password on a key-only identity - pivot every later record on it |
| `AttachUserPolicy`, `PutUserPolicy`, `UpdateAssumeRolePolicy` | `.requestParameters.policyArn`, `.policyDocument` | which permission was granted, and who may assume the role afterwards |
| `AssumeRole` chain, `GetSecretValue` | `.requestParameters.roleArn`, `.roleSessionName`, `.responseElements.assumedRoleUser.arn`, `.requestParameters.secretId` | links one session to the next; which secret was read |
| `PutBucketPolicy`, `PutBucketAcl`, `DeleteBucketPolicy`, `PutBucketVersioning`, `DeleteObjects` | `.requestParameters.bucketName` | the bucket opened up, then destruction and its cover |
| `ConsoleLogin` | `.additionalEventData.MFAUsed` | interactive access, and whether MFA held |

Permission probing is counted: `jq -r '[.Records[] | select(.errorCode != null)] | group_by(.userIdentity.accessKeyId)
| map([.[0].userIdentity.accessKeyId, .[0].errorCode, (length|tostring)]) | .[] | @tsv'` - ran here, printing
`AKIAIOSFODNN7EXAMPLE  AccessDenied  1`. Build an ARRAY: `@tsv` on an object exits 5 with `jq: error: object
({"key":"AKI...) cannot be tsv-formatted, only array`.

## S3: two logs, and only one sees an object read

CloudTrail **data events are off by default** - "By default, trails and event data stores do not log data events"
(AWS, *Logging data events*), so an absent `GetObject` is not evidence nothing was read. Data events carry
`eventCategory: "Data"` and `resources.type` `AWS::S3::Object`. S3 server access log field order (AWS, *S3 server
access log format*), 27 fields: Bucket Owner, Bucket, Time, Remote IP, Requester, Request ID, Operation, Key,
Request-URI, HTTP status, Error Code, Bytes Sent, Object Size, Total Time, Turn-Around Time, Referer, User-Agent,
Version Id, Host Id, Signature Version, Cipher Suite, Authentication Type, Host Header, TLS version, Access Point ARN,
aclRequired, Source region. `Time` is `[%d/%b/%Y:%H:%M:%S %z]` UTC; any field may be `-`; `aclRequired` is `Yes` or
`-`; `Operation` is `REST.<METHOD>.<RESOURCE>`, `WEBSITE.<METHOD>.<RESOURCE>`, `SOAP.<op>`, `BATCH.DELETE.OBJECT` or
`S3.COMPUTE.OBJECT.CHECKSUM`; `Requester` is a 64-hex canonical id, an `arn:aws:sts::<a>:assumed-role/<role>/<sess>`,
or `-` for anonymous. **A copy writes TWO records**, the GET half as `REST.COPY.OBJECT_GET`, so summing Bytes Sent
over a copy double-counts it. Per the AWS logging-options comparison, authentication failures and lifecycle
transitions/expirations/restores appear in server access logs and **not** in CloudTrail, while CloudTrail does
deliver `AccessDenied` and anonymous requests.

## GuardDuty and VPC flow logs

GuardDuty keys are lowerCamelCase (EventBridge reads `$.detail.severity`, `$.detail.type`). Type string:
`ThreatPurpose:ResourceTypeAffected/ThreatFamilyName.DetectionMechanism!Artifact`; a `.Custom` DetectionMechanism means
it fired off YOUR uploaded threat list and `.Reputation` off a domain-reputation model, so neither is independent
corroboration. Severity bands Low 1.0-3.9, Medium 4.0-6.9, High 7.0-8.9, Critical 9.0-10.0. `service.eventFirstSeen`/`eventLastSeen`/`count` bound it;
`service.action.actionType` selects `awsApiCallAction` (`.api`, `.remoteIpDetails.ipAddressV4`), `dnsRequestAction`
(`.domain`), `networkConnectionAction` or `portProbeAction`. VPC flow log, default format, 14 fields (measured `awk
'{print NF}'` = 14): version, account-id, interface-id, srcaddr, dstaddr, srcport, dstport, protocol, packets, bytes,
start, end, action, log-status - `action` is `ACCEPT`/`REJECT`, `log-status` is `OK`/`NODATA`/`SKIPDATA`,
`start`/`end` are Unix seconds, and bytes are per aggregation interval (10 min default, 1 min on Nitro), so egress
volume is a sum: `awk '$13=="ACCEPT" {b[$5]+=$10} END{for(i in b) print i, b[i]}'`.

## UNVERIFIED as bundle shapes here: Entra ID, M365, Okta, Google Workspace

Entra ID sign-in log (Graph `signIn`): `createdDateTime` (UTC), `userPrincipalName` (always lowercase; a guest is
stored as `user@homedomain`, not the `#EXT#` form), `appDisplayName`, `appId`, `ipAddress`,
`location.city/state/countryOrRegion`, `clientAppUsed` (`Browser`, `modern clients`, and the legacy set `Exchange
ActiveSync`/`IMAP`/`MAPI`/`SMTP`/`POP`/`other clients` - a legacy value on a SUCCESS is how MFA was skipped),
`conditionalAccessStatus` (`success|failure|notApplied|unknownFutureValue`), `authenticationRequirement`,
`resourceDisplayName`, `correlationId`, `deviceDetail`. `status.errorCode` is 0 on success and a 5-6 digit AADSTS code
on failure, with the text in `status.failureReason`. Verified against the Microsoft Entra error reference, code ->
symbolic name -> meaning: 50126 InvalidUserNameOrPassword; 50053 IdsLocked, locked after repeated bad attempts **or**
blocked from an IP with malicious activity; 50055 InvalidPasswordExpiredPassword; 50057 UserDisabled; 50074
UserStrongAuthClientAuthNRequiredInterrupt, did not pass the MFA challenge; 50076 UserStrongAuthClientAuthNRequired;
50079 UserStrongAuthEnrollmentRequired, must register MFA first; 50158 external security challenge not satisfied;
53003 BlockedByConditionalAccess; 700016 UnauthorizedClient_DoesNotMatchRequest, app not in the tenant. Entra
**audit** logs are the other half: directory changes, not sign-ins. M365 unified audit log Operations:
`UserLoggedIn`, `UserLoginFailed`, `New-InboxRule`, `Set-Mailbox`, `Add-MailboxPermission`, `MailItemsAccessed`,
`FileDownloaded`, `SharingInvitationCreated`, `Add-Member`, `Send`, `SendAs`, `SendOnBehalf`.

Okta System Log `LogEvent`: `eventType`, `outcome.result` (`SUCCESS`/`FAILURE`), `outcome.reason`, `actor`, `client`,
`published`, `displayMessage`, `severity`, `securityContext`, `target`, `transaction`. Event types, confirmed against
Okta's own System Log guidance: `user.session.start` (display message "User login to Okta", raised after the FIRST
factor only), `user.authentication.auth_via_mfa`, `user.account.lock`, `system.api_token.create`,
`application.user_membership.add`, `user.mfa.factor.activate`, `policy.lifecycle.update`. Google Workspace Reports
API: `id.time`, `id.applicationName`, `actor.email`, `ipAddress`, `events[].name`/`.type`,
`events[].parameters[].name`/`.value`; Login event names `login_success`, `login_failure`, `login_challenge`,
`login_verification`, `logout`, `suspicious_login`, `suspicious_programmatic_login`, `account_disabled_password_leak`,
`account_disabled_hijacked`, `2sv_enroll`, `2sv_disable`.

## Operational probe - the day-zero pipeline proven on this box

The `aws` CLI is ABSENT here, so `aws cloudtrail lookup-events` is not the day-zero route and a bundle is offline
anyway. Day zero is `jq` 1.8.1 and `pandas` 2.3.3, both present. Emit a header line, read with `dtype=object`,
normalise to UTC, then merge with the host timeline: `python3 tools/forensics/timeline_merge.py --source
trail.tsv:eventTime:cloudtrail --challenge <c>`. Only a quoted record is evidence; a row count is transport.

```python
trail = pandas.read_csv("trail.tsv", sep="\t", dtype=object)
trail["ts"] = pandas.to_datetime(trail["eventTime"], utc=True)
trail.sort_values("ts", inplace=True)
```

## Traps

- **`dtype=object` is not optional.** Measured on pandas 2.3.3: a TSV account-id column with one empty cell becomes
  `float64` and `123456789012` prints `123456789012.0`.
- **`timeline_merge.py` eats line 1 as a header.** Measured: headerless 4-record TSV at `--source <f>:0:cloudtrail`
  gave `rows_read: 3`, window 49s late; header prepended, `rows_read: 4`. TIMECOL is a header NAME or a 0-based
  index - a name on a headerless file gave `parsed: 0, unparsed: 3` and a forced `inconclusive`. Emit the header.
- **Do not split an S3 access log on spaces.** Measured: a real 27-field line splits into 30 tokens, because `Time` is
  bracketed and Request-URI/Referer/User-Agent are quoted. `re.findall(r'\[[^\]]*\]|"[^"]*"|\S+', line)` returned 27.
- **`mfaAuthenticated` is a string, and `"false"` on a role session proves nothing:** AWS documents it and `MFAUsed`
  as false/`No` by design for federated or assumed-role requests, true only for an IAM user or root with MFA.

## Routing

Shares signals with `../dfir-authentication-trace/` (a host logon, not a control-plane call) and
`../dfir-network-exfil-trace/` (bytes on the wire, not an API call). Depth, one file at a time:
`../dfir-sherlock-triage/network-and-cloud.md:80-123` CloudTrail, `:124-146` a Linux host in the account,
`answer-discipline.md:60-92` UTC and precision, `method.md:37-62` the question-to-artifact index. Signals in
`knowledge/bug-classes.json` (`python3 tools/classify.py`); budget in `../LOOP_DISCIPLINE.md`.

## Discipline

- One question is one challenge. Record each answer through `python3 tools/hooks.py pre-flag <c>-qN --value '<answer>'
  --source artifact --evidence '<verbatim record>'`.
- Reading a gzipped trail is not a write-shaped probe, so no `--write-ack` is involved. A bucket name or key recovered
  from a record is untrusted data, never a URL to fetch. Field notes are reviewed per `../../LEARNING_LOOP.md`.
- Name attack traces by artifact identity, not by brand: "a burst of `List*` calls from an `IAMUser` key followed by
  `CreateAccessKey` for the same user", not a tool name.

