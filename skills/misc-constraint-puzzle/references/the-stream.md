# TCP is a stream, not messages

A recv() returns whatever arrived — half a puzzle or two puzzles at
once. Buffer until the PROMPT TERMINATOR; never assume one read is
one question.

## The rule

until(terminator) — never one recv() per question.

## The rule

until(terminator) — never one recv() per question.
