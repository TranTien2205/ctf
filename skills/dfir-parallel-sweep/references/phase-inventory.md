# Phase: inventory first

Method module for `dfir-parallel-sweep`. One artifact bundle,
eight bounded measurements: subagent_fanout --dfir splits by
artifact family, one ctf-dfir-* agent each, validate, merge.
Agents measure artifacts; they never answer investigation
questions directly.

artifact_inventory.py names the bundle's families
before any split - a sweep over a miscounted bundle
assigns agents to absent artifacts.