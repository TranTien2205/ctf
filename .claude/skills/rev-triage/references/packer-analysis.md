# Packer/Obfuscation Analysis

## Detecting Packed Binaries
```bash
# High entropy sections indicate packing/encryption
binwalk -E ./binary

# DIE (Detect It Easy) - GUI/CLI packer signature detection
diec ./binary

# PEiD-style signatures (Windows PE)
# Check for UPX, ASPack, Themida, VMProtect signatures
```

## UPX Detection & Unpacking
```bash
# Detection: strings often show "UPX!" magic bytes
strings ./binary | grep -i upx

# Unpack
upx -d ./binary -o ./binary_unpacked
```

## Generic Manual Unpacking Approach
```
1. Load in debugger (x64dbg/GDB/IDA)
2. Set breakpoint at OEP (Original Entry Point) - often found via:
   - Single-step until jump to unusual memory region (freshly decompressed code)
   - Look for large jump/call after decompression stub
3. Dump memory at OEP to a fresh file
4. Fix imports (for PE files, use Scylla/ImpREC to rebuild import table)
```

## Detecting Anti-Debug Techniques
```
IsDebuggerPresent()          Windows API check
ptrace(PTRACE_TRACEME)       Linux self-tracing to detect debugger attach
Timing checks (rdtsc)        Detect single-stepping via elapsed time
INT3 scanning                Check own code for breakpoint bytes (0xCC)
Parent process checks        Verify not launched from known debugger
```

## Bypassing Anti-Debug (Common Patches)
```bash
# Patch conditional jump after anti-debug check (NOP or invert)
# In GDB: catch syscall ptrace, then modify return value

# In x64dbg: TitanHide plugin, ScyllaHide plugin for stealth
```

## VM-Based Obfuscation (VMProtect, Themida)
```
- Very time-intensive to reverse manually
- Look for VM dispatcher loop (large switch-case-like structure)
- Consider dynamic analysis (trace execution) over static disassembly
- Tools: VMProtect devirtualization tools (community scripts), or focus on
  side-channel approach (patch checks, trace syscalls, memory dumps at
  decision points) rather than full devirtualization
```

## String/Constant Obfuscation
```
- XOR-encoded strings: look for decode loops before comparisons
- Stack strings (built char-by-char on stack): trace in debugger, dump at use point
- Control flow flattening: use decompiler (Ghidra/IDA) rather than raw disassembly
```

## Dynamic Analysis Shortcut (Instead of Full Unpacking)
```bash
# Run and dump memory after unpacking completes
gdb ./binary
(gdb) run
(gdb) [wait for unpack, ctrl+C]
(gdb) dump memory dumped.bin 0x<start> 0x<end>

# Or use LD_PRELOAD hooks to intercept function calls without full unpack
```

## Tools Summary
```
UPX               # Common packer, easily unpacked
DIE               # Detect packer/compiler signatures
x64dbg / OllyDbg  # Windows dynamic analysis + unpacking
Scylla/ImpREC     # PE import table reconstruction after dump
Ghidra/IDA        # Decompilation for obfuscated logic understanding
```
