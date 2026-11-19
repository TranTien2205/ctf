# Archives inside the image — the second layer

cpio/zip/tar/rar/7z/iso/git objects — each has a local reader:

- cpio/ar: cpio_read.py
- zip: zip_struct.py (local_only = hidden files)
- tar: tar_tail.py (post-EOT trailer hide)
- rar: rar_list.py; 7z: sevenz_list.py
- iso: iso_read.py (the `;1` name suffix)
- .git: git_obj.py dangling
- cab/msu: cab_list.py
