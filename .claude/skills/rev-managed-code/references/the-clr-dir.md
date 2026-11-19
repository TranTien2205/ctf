# The CLR data directory — the .NET tell

The PE optional header's data directory entry 14 (COM Descriptor)
is non-zero for a managed assembly — the CLR header pointer.

## The read

    rabin2 -I ./chal | grep -i clr
    # or parse the PE: directory[14].rva != 0 → managed

A non-zero CLR directory = .NET metadata present → decompile the
managed code, don't disassemble the native wrapper.
