# cmov — the branchless select


cmov selects by flags without a jump — the "branch" is a data move;
the compare still exists, the select is its use.
