# PDF metadata — /Info + XMP + embedded

The /Info dict (Title, Author, Creator, Producer, dates) + the
XMP stream + embedded files (/EmbeddedFiles). meta_read.py reads
/Info + XMP; the embedded files need a structural parse.
