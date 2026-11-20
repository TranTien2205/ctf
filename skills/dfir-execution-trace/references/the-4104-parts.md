# 4104 multi-part — reassemble before reading

Long scripts split across 4104 records — `ScriptBlockId` joins the
parts, `MessageNumber`/`MessageTotal` order them. Part 1 alone
truncates the script.

## Reassemble

ScriptBlockId joins, MessageNumber orders.

## The order

MessageNumber orders the parts.
