# Attack cell: transfer on segmentation

Depth module for `ctf-ai-ml`. Open `../SKILL.md` for the quick-reference
index first; this file is one named piece of the corpus - never a
finding by itself.

How `transfer` applies to a `segmentation` target.

## Applicability

Whether this attack family reaches this model type and what the
perturbation space looks like (pixel, token, feature, waveform).

## Constraints

The norm the challenge's checker measures and the output granularity
the model exposes - which decides whether the attack is white-box,
score-based, or decision-only.

## Pivot

Cell read -> `../adversarial-ml.md` for the attack playbook or
`meth-fgsm.md` for the base method.
