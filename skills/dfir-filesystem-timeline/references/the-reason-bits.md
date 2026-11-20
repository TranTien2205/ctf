# The $J reason table — read the bits

0x100 FILE_CREATE is first existence and survives log clearing;
0x200 FILE_DELETE regardless of the bin; repeated 0x2 DATA_EXTEND
dates each append; 0x8000 BASIC_INFO_CHANGE is the backdating
fingerprint; 0x1000/0x2000 is the rename pair on one FileReferenceNumber.
