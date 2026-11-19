# Container images — flatten first

qcow2/vhd/vmdk/dmg/E01 are container formats over a flat image —
dump to flat, then part_table + the fs readers:

    qcow2_read.py disk.qcow2 dump guest.img
    vhd_read.py / vhdx_read.py / vmdk_info.py
    dmg_udif.py a.dmg --extract flat.img
    e01_read.py disk.E01 dump guest.img
