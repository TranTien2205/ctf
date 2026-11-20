# Office metadata — the zip innards

docx/xlsx/pptx = zip. docProps/core.xml + app.xml; comments.xml;
track-changes in document.xml. `unzip -p file.docx docProps/core.xml`
or meta_read.py — the author/editor fields are the identity.
