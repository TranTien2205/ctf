# Tool Permission Audit Checklist

## Per-Tool Capability Inventory Template
```markdown
## Tool: [tool_name]
- **Purpose (as documented):** [what it claims to do]
- **Filesystem access:** [none / read-only path X / read-write path X / unrestricted]
- **Network access:** [none / specific domains / unrestricted outbound]
- **Shell/command execution:** [none / fixed allowlist / arbitrary]
- **Credential handling:** [none needed / API key via env var / hardcoded
  in config / requested at runtime]
- **Auto-executes without confirmation:** [yes/no]
- **Handles untrusted input:** [yes/no — e.g. web content, user files]
- **Risk rating:** [low/medium/high]
- **Justification for access level:** [does the actual permission match
  the stated purpose, or is it broader than needed?]
```

## Filesystem Access Review
```
[ ] Is access scoped to a specific project directory, or can the tool
    read/write anywhere on the filesystem (including outside the workspace)?
[ ] Can the tool read sensitive files by path if instructed (e.g. ~/.ssh/,
    .env, credential stores) even if that's not the intended use case?
[ ] Is there a denylist/allowlist enforced in code, or just a suggestion
    in documentation that the agent might not always respect?
```

## Network Access Review
```
[ ] Does the tool make outbound requests to a fixed, documented set of
    endpoints, or can it be directed to arbitrary URLs/IPs?
[ ] Could this tool be used to exfiltrate data to an attacker-controlled
    endpoint if the agent were manipulated (via prompt injection or a
    malicious task) into doing so?
[ ] Are there egress restrictions at the network level (firewall/proxy)
    as a defense-in-depth measure, independent of the tool's own logic?
```

## Shell/Command Execution Review
```
[ ] Fixed command allowlist vs. arbitrary shell string construction —
    arbitrary construction is high risk, especially if any part of the
    command incorporates untrusted input (files, web content, user text)
    without proper escaping
[ ] Does the tool use parameterized/array-based execution (safe) or string
    concatenation/interpolation into a shell command (injection risk)?
[ ] Are dangerous commands (rm -rf, format, credential dumping tools)
    reachable through this tool, even indirectly?
```

## Credential Handling Review
```
[ ] Are secrets passed via environment variables (better) or hardcoded/
    committed in config files (worse)?
[ ] Does the tool log credentials to stdout/files during normal operation?
[ ] Is there a least-privilege API key/token in use, or a broad admin-level
    credential where a scoped one would suffice?
```

## Confirmation/Approval Flow Review
```
[ ] Which specific actions run without any human-in-the-loop confirmation?
[ ] For an agent operating autonomously (no user watching every step), what
    is the worst-case action it could take unsupervised with this tool?
[ ] Is there a "dry run" or preview mode available for destructive actions?
```

## Aggregate Risk Scoring
```
Low risk:    Read-only, scoped filesystem access; no shell exec; no
             untrusted content handling; requires confirmation for any
             state-changing action
Medium risk: Scoped write access OR fixed-allowlist shell commands OR
             handles untrusted content with some sanitization
High risk:   Unrestricted filesystem/network/shell access, OR handles
             untrusted content with no sanitization and auto-executes
             without confirmation
```

## Recommendation Output
```markdown
## MCP Server Audit: [server_name]
- Overall risk: [low/medium/high]
- Tools reviewed: [count]
- High-risk tools: [list with brief reason]
- Recommendation: [approve / approve with restrictions (specify) / reject]
- Restrictions to apply if approved: [e.g. sandbox filesystem to project
  dir only, disable auto-execute for shell tool, require confirmation for
  network tool]
```
