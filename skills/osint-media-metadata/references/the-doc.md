# Document metadata — docProps + revisions

docx/xlsx/pptx are zips — docProps/core.xml (creator, modified,
lastModifiedBy) + app.xml. Revisions/comments carry the edit
history. meta_read.py reads them; unzip+grep is the manual route.
