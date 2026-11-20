# The 4+4 divergence — the timestomp answer

`$STANDARD_INFORMATION` (0x10) and `$FILE_NAME` (0x30) each carry
Created/Modified/MFT-Modified/Accessed. Backdating tools patch only
0x10 — the divergence between the plain row and the `($FILE_NAME)`
row in one bodyfile is the timestomp proof.
