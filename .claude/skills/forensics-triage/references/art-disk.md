# Artifact: disk/fs image

Routing module for `forensics-triage`. Artifact -> family ->
tool -> depth skill, with a falsifier for every route. The router
identifies and routes; the depth skills do the analysis.

E01, raw dd image, or a filesystem file (ext, ntfs,
fat) - disk-forensics.md + forensics-disk-image.
Mount or parse; deleted-file recovery is the common
task.

## Pivot

Artifact identified -> its route-* module and depth skill.
