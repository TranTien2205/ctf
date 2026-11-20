# Timestamp shapes across formats

- access.log: [10/Oct/2000:13:55:36 -0700]
- auth/syslog: Oct 10 13:55:36
- ISO: 2000-10-10T13:55:36Z
- JSON: a "timestamp" field
Each parses differently — the timezone suffix matters.
