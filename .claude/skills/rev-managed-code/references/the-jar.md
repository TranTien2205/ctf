# The .jar — a zip of classes

A .jar is a zip: `unzip -l` lists the classes — the check class
(Main/Check/Verify) surfaces by name; jclass_info or javap on it.

## The extract

    unzip -o app.jar -d out/
    python3 tools/jclass_info.py out/Check.class
