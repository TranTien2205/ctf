# Aggregator: eventName index

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

sts: GetCallerIdentity, AssumeRole(+SAML/WebIdentity), GetSessionToken. signin: ConsoleLogin, CheckMfa. iam: CreateUser/CreateAccessKey/DeleteAccessKey/UpdateAccessKey/CreateLoginProfile/UpdateLoginProfile/AttachUserPolicy/PutUserPolicy/AttachRolePolicy/PutRolePolicy/UpdateAssumeRolePolicy/CreateRole/CreatePolicyVersion/AddUserToGroup. s3: ListBuckets, PutBucketPolicy/Acl, DeleteBucketPolicy, PutBucketVersioning, PutBucketPublicAccessBlock, DeleteBucket, GetObject/PutObject (data). ec2: RunInstances, AuthorizeSecurityGroupIngress, CreateSecurityGroup, CreateSnapshot, ModifyInstanceAttribute. lambda: CreateFunction, AddPermission, InvokeFunction. kms: PutKeyPolicy, ScheduleKeyDeletion, Decrypt, DisableKey. cloudtrail: DeleteTrail, StopLogging, UpdateTrail, PutEventSelectors. cloudwatchlogs: DeleteLogGroup, DeleteLogStream.

## Use

An index - open the named family module for the detail; this file
only decides which one.

## Pivot

Index consulted -> the module it names.
