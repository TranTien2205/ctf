#!/usr/bin/env python3
"""Classify a bundle into DFIR artifact families and name the ONE file to open.

A Sherlock bundle is hundreds to thousands of files. The expensive mistake is
never a wrong parser flag, it is an hour spent inside the wrong artifact family,
and that choice gets made by eye in the first two minutes. This walks the tree
once, classifies every file by name, extension and the bytes actually on disk,
and hands back one route into the DFIR router's depth files plus what else is
present, before any parser runs.

It parses nothing and shells out to nothing. One stat and one short read per
file, so a 10k-file tree costs no memory and nothing is loaded; an unreadable
file is recorded as unreadable rather than raised.

Magic values are the part of a tool like this that rots into invented facts, so
every value carries its provenance in "magic_provenance": "verified_here" is true
only where the bytes were read off a real artifact produced on this box, or where
an independent signature database here names them. The prefetch signatures are
marked false on purpose - nothing on this box could confirm them - and for that
family the .pf extension is the deciding signal, not the magic.

The verdict is always "inconclusive" with evidence-kind "surface", and asking for
"confirms" cannot change that: fkit.downgrade() is called with parser_ok=False
because an inventory ran no parser. Knowing a file is a Security event log is not
knowing who logged in.

    python3 tools/forensics/artifact_inventory.py --path <bundle> \
        --challenge <sherlock>-q1 --class <hypothesis bug_class> \
        --hypothesis-id h1
    python3 tools/forensics/artifact_inventory.py --path <bundle> --hash --compact
"""
import argparse
import hashlib
import os
import re
import stat
import struct
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fkit  # noqa: E402

SKILL_DIR = "skills/dfir-sherlock-triage"

WEL = "windows-event-logs.md"
REG = "registry-and-execution.md"
FS = "filesystem-timeline.md"
NET = "network-and-cloud.md"
MAL = "memory-and-malware.md"
INTAKE = "intake-and-inventory.md"

# Which depth file owns each family. Taken from the routing table in
# skills/dfir-sherlock-triage/SKILL.md, not invented here.
FAMILY_OWNER = {
    "evtx-security": WEL,
    "evtx-sysmon": WEL,
    "evtx-powershell": WEL,
    "evtx-other": WEL,
    "registry-hive": REG,
    "registry-transaction-log": REG,
    "amcache": REG,
    "prefetch": REG,
    "sqlite-db": REG,
    "mft": FS,
    "usn-journal": FS,
    "ntfs-other": FS,
    "recycle-bin": FS,
    "capture": NET,
    "cloudtrail-json": NET,
    "linux-log": NET,
    "pe-binary": MAL,
    "office-doc": MAL,
    "archive": MAL,
    "memory-image": MAL,
    "kape-marker": INTAKE,
    "unknown": INTAKE,
}

EVTX_MAGIC = b"ElfFile\x00"
REGF_MAGIC = b"regf"
MFT_MAGIC = b"FILE"
MFT_BAAD = b"BAAD"
PCAP_LE = b"\xd4\xc3\xb2\xa1"
PCAP_BE = b"\xa1\xb2\xc3\xd4"
PCAPNG_MAGIC = b"\x0a\x0d\x0d\x0a"
SQLITE_MAGIC = b"SQLite format 3\x00"
MZ_MAGIC = b"MZ"
OLE_MAGIC = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
ZIP_MAGIC = b"PK\x03\x04"
SEVENZ_MAGIC = b"7z\xbc\xaf\x27\x1c"
GZIP_MAGIC = b"\x1f\x8b"
BZIP2_MAGIC = b"BZh"
XZ_MAGIC = b"\xfd7zXZ\x00"
RAR_MAGIC = b"Rar!\x1a\x07"
NTFS_OEM = b"NTFS    "
PREFETCH_SCCA = b"SCCA"
PREFETCH_MAM = b"MAM\x04"
EOCD_MAGIC = b"PK\x05\x06"

# How each magic value above was established. "verified_here" true means it was
# read off a real artifact on this box, or an independent signature database here
# names those bytes. False means documentation only, and the tool leans on the
# filename instead.
MAGIC_PROVENANCE = [
    {"family": "evtx-*", "magic": "ElfFile\\x00", "offset": 0, "verified_here": True,
     "how": "libmagic's compiled database here carries the same signature string, "
            "and it names a file starting with these bytes "
            "'MS Windows 10-11 Event Log'"},
    {"family": "registry-hive / registry-transaction-log / amcache",
     "magic": "regf", "offset": 0, "verified_here": True,
     "how": "libmagic here names a file starting with these bytes "
            "'MS Windows registry file, NT/2000 or above'. A hive transaction log "
            "carries the SAME signature, so the .LOG1/.LOG2 name must win over it"},
    {"family": "mft", "magic": "FILE (or BAAD) plus update-sequence-array offset "
                               "0x10..0x40 at offset 4", "offset": 0,
     "verified_here": True,
     "how": "read off the $MFT of an NTFS volume built with mkntfs and extracted "
            "with sleuthkit 'icat <img> 0': 46 49 4c 45 30 00 03 00, so the offset "
            "field reads 0x0030"},
    {"family": "ntfs-other", "magic": "NTFS    ", "offset": 3, "verified_here": True,
     "how": "read off the same volume's $Boot via 'icat <img> 7': "
            "eb 52 90 4e 54 46 53 20 20 20 20"},
    {"family": "capture", "magic": "d4c3b2a1 / a1b2c3d4", "offset": 0,
     "verified_here": True,
     "how": "d4c3b2a1 read off a file written by text2pcap -F pcap here; a1b2c3d4 "
            "is the same 32-bit value in the other byte order"},
    {"family": "capture", "magic": "0a0d0d0a", "offset": 0, "verified_here": True,
     "how": "read off a file written by text2pcap in its default format here"},
    {"family": "sqlite-db", "magic": "SQLite format 3\\x00", "offset": 0,
     "verified_here": True,
     "how": "read off a database created by the sqlite3 binary here"},
    {"family": "pe-binary", "magic": "MZ, plus PE\\x00\\x00 at the offset stored "
                                     "at 0x3c", "offset": 0, "verified_here": True,
     "how": "read off a real PE test binary present on this box"},
    {"family": "office-doc", "magic": "d0cf11e0a1b11ae1", "offset": 0,
     "verified_here": True,
     "how": "read off a real .xls shipped under /usr/share/doc here; note this is "
            "the OLE container, which other formats also use"},
    {"family": "archive", "magic": "PK\\x03\\x04 / 7z\\xbc\\xaf'\\x1c / \\x1f\\x8b "
                                   "/ BZh / \\xfd7zXZ\\x00", "offset": 0,
     "verified_here": True,
     "how": "each read off a file written by the matching packer on this box"},
    {"family": "archive", "magic": "Rar!\\x1a\\x07", "offset": 0,
     "verified_here": True,
     "how": "no rar file was written here; the byte sequence is present in "
            "libmagic's compiled database on this box, which is what confirms it"},
    {"family": "kape-marker", "magic": "PK\\x05\\x06, comment length at +20, "
                                       "comment at +22", "offset": -1,
     "verified_here": True,
     "how": "a zip written with an archive comment was parsed with this exact "
            "offset arithmetic and the result matched what 'unzip -z' printed"},
    {"family": "prefetch", "magic": "SCCA", "offset": 4, "verified_here": False,
     "how": "NOT verified on this box: no prefetch sample exists here, and neither "
            "libmagic's database nor binwalk's signatures contain 'SCCA'. The .pf "
            "extension is the deciding signal for this family; the magic is a "
            "secondary check carried on documentation alone"},
    {"family": "prefetch", "magic": "MAM\\x04", "offset": 0, "verified_here": False,
     "how": "NOT verified on this box, same reason. The four 'MAM' hits in "
            "libmagic's database here belong to MAME, not to prefetch"},
]

# Families this tool classifies from the name alone, because the format has no
# signature at offset 0 that this tool is willing to claim it knows.
NAME_ONLY = ("usn-journal", "recycle-bin", "linux-log", "memory-image",
             "ntfs-other ($LogFile, $Secure and the rest of the metafiles)")

HIVE_STEMS = {"system", "software", "sam", "security", "default", "ntuser.dat",
              "usrclass.dat", "components", "drivers", "bcd", "bcd-template",
              "elam", "userdiff", "syscache.hve"}
NTFS_META = {"$boot", "$logfile", "$secure", "$bitmap", "$attrdef", "$upcase",
             "$volume", "$badclus", "$mftmirr", "$objid", "$reparse", "$quota",
             "$repair", "$extend", "$tops", "$config", "$deleted"}
LINUX_LOG_NAMES = {"wtmp", "btmp", "utmp", "lastlog", "faillog", "dmesg",
                   "boot.log", "sulog", "auth.log", "secure", "syslog",
                   "messages", "kern.log", "daemon.log", "cron.log", "audit.log"}
LINUX_LOG_ROTATED = re.compile(
    r"^(auth\.log|secure|syslog|messages|kern\.log|daemon\.log|cron\.log|"
    r"audit\.log)(\.\d+)?(\.gz|\.bz2|\.xz)?$")
CAPTURE_EXT = (".pcap", ".pcapng", ".cap", ".pcapng.gz", ".pcap.gz")
MEM_EXT = (".vmem", ".mem", ".dmp", ".lime", ".core", ".vmss", ".vmsn", ".sav",
           ".raw", ".bin", ".aff4")
MEM_NAMES = {"hiberfil.sys", "pagefile.sys", "swapfile.sys"}
OOXML_EXT = (".docx", ".docm", ".dotx", ".dotm", ".xlsx", ".xlsm", ".xltx",
             ".pptx", ".pptm", ".potx")
OFFICE_EXT = (".doc", ".xls", ".ppt", ".rtf", ".pub", ".msg", ".one")
ARCHIVE_EXT = (".zip", ".7z", ".gz", ".tgz", ".tar", ".bz2", ".xz", ".rar",
               ".cab", ".iso", ".wim")


def _u16(buf, off):
    if len(buf) < off + 2:
        return None
    return struct.unpack_from("<H", buf, off)[0]


def _u32(buf, off):
    if len(buf) < off + 4:
        return None
    return struct.unpack_from("<I", buf, off)[0]


def looks_like_mft_record(head):
    """FILE plus a plausible update-sequence-array offset.

    'FILE' on its own is four letters of English, so the offset field at 4 is
    what makes this a record rather than a text file. The real $MFT read on this
    box has 0x0030 there.
    """
    if head[:4] not in (MFT_MAGIC, MFT_BAAD):
        return False
    usa = _u16(head, 4)
    return usa is not None and 0x10 <= usa <= 0x40


def pe_header_offset(head):
    """-> the offset of PE\\x00\\x00, or None when it is not in what we read."""
    off = _u32(head, 0x3C)
    if off is None or off + 4 > len(head):
        return None
    return off if head[off:off + 4] == b"PE\x00\x00" else None


def looks_like_cloudtrail(head):
    return b'"eventVersion"' in head and (b'"eventSource"' in head or
                                          b'"Records"' in head)


def classify(rel_path, name, head, size):
    """-> (family, why). Name and extension first, magic as the tie-breaker.

    Order matters twice over. A hive transaction log has the hive's own 'regf'
    signature, so .LOG1/.LOG2 is tested before the magic. And $Reparse and
    $Repair start with the same two characters as a Recycle Bin $R file, so the
    NTFS metafile names are tested before the Recycle Bin shape.
    """
    lname = name.lower()
    lpath = rel_path.replace("\\", "/").lower()
    stem, ext = os.path.splitext(lname)

    if lname.endswith("copylog.csv") or lname.endswith("skiplog.csv"):
        return "kape-marker", "KAPE copy-log filename"

    if head[:8] == EVTX_MAGIC or ext == ".evtx":
        how = "ElfFile magic" if head[:8] == EVTX_MAGIC else ".evtx extension"
        if "security" in lname:
            return "evtx-security", how + "; name carries Security"
        if "sysmon" in lname:
            return "evtx-sysmon", how + "; name carries Sysmon"
        if "powershell" in lname:
            return "evtx-powershell", how + "; name carries PowerShell"
        return "evtx-other", how
    if ext == ".etl":
        return "evtx-other", ".etl trace, an event log family this tool does not parse"

    if ext == ".pf":
        extra = ""
        if head[4:8] == PREFETCH_SCCA:
            extra = "; SCCA at offset 4 agrees"
        elif head[:4] == PREFETCH_MAM:
            extra = "; MAM compressed header agrees"
        return "prefetch", ".pf extension (the deciding signal)" + extra
    if head[4:8] == PREFETCH_SCCA or head[:4] == PREFETCH_MAM:
        return "prefetch", ("prefetch magic without a .pf name; this magic value "
                            "is unverified on this box, see magic_provenance")

    if "amcache" in lname:
        if ext in (".log1", ".log2"):
            return "registry-transaction-log", "Amcache transaction log by name"
        return "amcache", "Amcache by name"
    if ext in (".log1", ".log2"):
        return "registry-transaction-log", "%s transaction log by name" % ext
    if ext == ".log" and stem in HIVE_STEMS:
        return "registry-transaction-log", "hive-named .log beside a hive"

    if head[:4] == REGF_MAGIC:
        return "registry-hive", "regf magic"
    if lname in HIVE_STEMS or ext == ".hve" or ext == ".dat" and stem in ("ntuser", "usrclass"):
        return "registry-hive", "hive filename"

    if lname == "$mft":
        return "mft", "$MFT by name"
    if lname in ("$j", "$usnjrnl", "$usnjrnl.$j") or "usnjrnl" in lname:
        return "usn-journal", "USN journal by name"
    if lname in NTFS_META or lname.startswith("$mftmirr"):
        return "ntfs-other", "NTFS metafile name"
    if looks_like_mft_record(head):
        return "mft", ("FILE record header with a plausible "
                       "update-sequence-array offset")
    if head[3:11] == NTFS_OEM:
        return "ntfs-other", ("NTFS volume boot record at offset 3; this may be a "
                              "whole volume image rather than $Boot alone")

    if "$recycle.bin" in lpath or (len(lname) > 2 and lname[0] == "$" and
                                   lname[1] in "ir"):
        return "recycle-bin", "Recycle Bin path or $I/$R filename"

    if head[:4] in (PCAP_LE, PCAP_BE):
        return "capture", "libpcap magic"
    if head[:4] == PCAPNG_MAGIC:
        return "capture", "pcapng section header block magic"
    if lname.endswith(CAPTURE_EXT):
        return "capture", "capture extension"

    if "cloudtrail" in lpath:
        return "cloudtrail-json", "CloudTrail in the path"
    if looks_like_cloudtrail(head):
        return "cloudtrail-json", "eventVersion and eventSource keys in the head"

    if head[:16] == SQLITE_MAGIC:
        return "sqlite-db", "SQLite header"

    if lname in LINUX_LOG_NAMES or LINUX_LOG_ROTATED.match(lname) or \
            ext == ".journal" or "/var/log/" in "/" + lpath:
        return "linux-log", "Linux log name or /var/log path"

    if head[:2] == MZ_MAGIC:
        off = pe_header_offset(head)
        if off is not None:
            return "pe-binary", "MZ with PE header at 0x%x" % off
        return "pe-binary", ("MZ only; the PE header sits beyond --max-bytes or "
                             "is absent")

    if head[:8] == OLE_MAGIC:
        return "office-doc", ("OLE container; .msi and .msg use the same "
                              "container, so confirm by extension")
    if head[:4] == ZIP_MAGIC and lname.endswith(OOXML_EXT):
        return "office-doc", "zip magic with an OOXML extension"
    if lname.endswith(OFFICE_EXT):
        return "office-doc", "Office extension"

    if head[:4] == ZIP_MAGIC or head[:6] == SEVENZ_MAGIC or \
            head[:2] == GZIP_MAGIC or head[:3] == BZIP2_MAGIC or \
            head[:6] == XZ_MAGIC or head[:7] == RAR_MAGIC:
        return "archive", "archive magic"
    if lname.endswith(ARCHIVE_EXT):
        return "archive", "archive extension"

    if lname in MEM_NAMES or lname.endswith(MEM_EXT):
        return "memory-image", ("name only; a .raw or .bin may equally be a disk "
                                "image, and nothing here reads a memory image")

    return "unknown", "no name, extension or magic signal matched"


def zip_comment(path, tail=66000):
    """The archive comment, parsed from the end-of-central-directory record.

    Reads the tail only; the central directory is never walked and nothing is
    decompressed, so this stays cheap on a multi-gigabyte collection zip.
    """
    try:
        if not os.path.isfile(path):
            return None
        size = os.path.getsize(path)
        with open(path, "rb") as fh:
            fh.seek(max(0, size - tail))
            blob = fh.read(min(size, tail))
    except OSError:
        return None
    index = blob.rfind(EOCD_MAGIC)
    if index < 0:
        return None
    length = _u16(blob, index + 20)
    if not length:
        return None
    return blob[index + 22:index + 22 + length].decode("ascii", "replace")


def kape_shape(records):
    """True only on a real KAPE marker. An encoded drive path is not one.

    A triage collection often carries paths like C%3A%5CWindows, and that says
    the collector url-encoded a drive letter, nothing about which collector it
    was. Recording it as a rejected signal is the point: it is the plausible
    wrong answer this function exists to refuse.
    """
    markers = []
    rejected = []
    for rec in records:
        lname = rec["name"].lower()
        if lname.endswith("copylog.csv") or lname.endswith("skiplog.csv"):
            markers.append({"path": rec["path"], "marker": "KAPE copy-log filename"})
    for rec in records:
        if rec["name"].lower().endswith(".zip"):
            comment = zip_comment(rec["abs"])
            if comment and "kape" in comment.lower():
                markers.append({"path": rec["path"],
                                "marker": "zip comment: %s" % comment})
    encoded = [rec["path"] for rec in records
               if "c%3a" in rec["path"].lower() or "%5c" in rec["path"].lower()]
    if encoded:
        rejected.append({
            "signal": "url-encoded drive path in %d path(s), e.g. %s"
                      % (len(encoded), encoded[0]),
            "why_not_a_marker": "an encoded drive letter says the collector "
                                "escaped a path; it does not name the collector. "
                                "Only CopyLog.csv, SkipLog.csv or a zip comment "
                                "naming KAPE is a marker here"})
    return {"is_kape": bool(markers), "markers": markers[:5],
            "rejected_signals": rejected}


def collect(target):
    """-> (items, dirs, symlinks, walk_errors). One stat per file, no reads."""
    items, errors = [], []
    dirs = symlinks = 0
    if os.path.isdir(target):
        root = os.path.abspath(target)
        for dirpath, dirnames, filenames in os.walk(root, onerror=errors.append,
                                                   followlinks=False):
            dirs += len(dirnames)
            for fname in filenames:
                full = os.path.join(dirpath, fname)
                if os.path.islink(full):
                    symlinks += 1
                    continue
                items.append((full, os.path.relpath(full, root)))
    else:
        items.append((os.path.abspath(target), os.path.basename(target)))
    return items, dirs, symlinks, [str(err) for err in errors]


def sha256(path, cap):
    size = os.path.getsize(path)
    if size > cap:
        return None, "larger than --hash-max-bytes (%d)" % cap
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(1 << 20)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest(), None


def inventory(target, max_bytes, want_hash, hash_cap):
    items, dirs, symlinks, walk_errors = collect(target)
    records, unreadable = [], []
    for abs_path, rel in items:
        try:
            info = os.stat(abs_path)
        except OSError as exc:
            unreadable.append({"path": rel, "stage": "stat",
                               "error": "%s: %s" % (type(exc).__name__, exc)})
            continue
        size = info.st_size
        head = b""
        read_error = None
        # Only a regular file is ever opened. A fifo blocks in open() until a
        # writer appears, which hangs the whole walk with no output at all, and a
        # device file reports st_size 0 so no byte cap can bound a read of it.
        # A bundle recovered from a unix filesystem can carry both.
        regular = stat.S_ISREG(info.st_mode)
        if not regular:
            read_error = ("not a regular file (st_mode 0o%o); not opened"
                          % info.st_mode)
            unreadable.append({"path": rel, "stage": "open", "error": read_error,
                               "note": "a fifo, socket or device file is never "
                                       "opened here: the read could block or "
                                       "never reach an end. Classified from the "
                                       "name alone"})
        else:
            try:
                with open(abs_path, "rb") as fh:
                    head = fh.read(max_bytes)
            except OSError as exc:
                read_error = "%s: %s" % (type(exc).__name__, exc)
                unreadable.append({"path": rel, "stage": "read",
                                   "error": read_error,
                                   "note": "classified from the name alone"})
        family, why = classify(rel, os.path.basename(rel), head, size)
        rec = {"path": rel, "abs": abs_path, "name": os.path.basename(rel),
               "bytes": size, "family": family, "why": why,
               "head_hex": head[:8].hex()}
        if read_error:
            rec["read_error"] = read_error
        if want_hash and not regular:
            rec["sha256"] = None
            rec["sha256_skipped"] = ("not a regular file; hashing it could never "
                                     "reach an end of file")
        elif want_hash:
            try:
                digest, skipped = sha256(abs_path, hash_cap)
            except OSError as exc:
                digest, skipped = None, "%s: %s" % (type(exc).__name__, exc)
            rec["sha256"] = digest
            if skipped:
                rec["sha256_skipped"] = skipped
        records.append(rec)
    return records, {"directories": dirs, "symlinks_skipped": symlinks,
                     "walk_errors": walk_errors, "unreadable": unreadable}


def families_of(records, examples):
    out = {}
    for rec in records:
        fam = out.setdefault(rec["family"], {
            "count": 0, "bytes": 0,
            "depth_file": "%s/%s" % (SKILL_DIR, FAMILY_OWNER[rec["family"]]),
            "examples": []})
        fam["count"] += 1
        fam["bytes"] += rec["bytes"]
        if len(fam["examples"]) < examples:
            example = {"path": rec["path"], "bytes": rec["bytes"],
                       "head_hex": rec["head_hex"], "why": rec["why"]}
            if "sha256" in rec:
                example["sha256"] = rec["sha256"]
            if "sha256_skipped" in rec:
                example["sha256_skipped"] = rec["sha256_skipped"]
            if "read_error" in rec:
                example["read_error"] = rec["read_error"]
            fam["examples"].append(example)
    ordered = sorted(out.items(),
                     key=lambda kv: (-kv[1]["count"], -kv[1]["bytes"], kv[0]))
    return dict(ordered), [name for name, _ in ordered]


def route_of(families, order, kape, threshold):
    """One depth file. Breadth beats a single count, because the skill says so.

    SKILL.md routes a bundle that carries the whole Windows surface to
    intake-and-inventory.md and lets the QUESTION pick the family, rather than
    letting a 200-file prefetch directory outvote one Security.evtx. Everything
    narrower routes to the owner of the family with the most files, ties broken
    by total bytes and then by name so the answer is deterministic.
    """
    artifact_files = sorted({fam["depth_file"] for name, fam in families.items()
                             if name not in ("unknown", "kape-marker")})
    dominant = order[0] if order else None
    if kape["is_kape"]:
        chosen = "%s/%s" % (SKILL_DIR, INTAKE)
        reason = ("a real KAPE marker is present, so the whole Windows surface "
                  "was collected; open intake first and let the question pick the "
                  "family")
        basis = "kape-marker"
    elif len(artifact_files) >= threshold:
        chosen = "%s/%s" % (SKILL_DIR, INTAKE)
        reason = ("%d artifact families across %d depth files: a broad triage "
                  "surface, so the question routes, not the file listing"
                  % (len(families), len(artifact_files)))
        basis = "breadth (>= --breadth-threshold %d depth files)" % threshold
    elif dominant is None:
        chosen = "%s/%s" % (SKILL_DIR, INTAKE)
        reason = "nothing was classified"
        basis = "empty"
    else:
        chosen = families[dominant]["depth_file"]
        reason = ("%s dominates with %d file(s) and %d byte(s)"
                  % (dominant, families[dominant]["count"],
                     families[dominant]["bytes"]))
        basis = "largest family by file count"
    also = []
    for name in order:
        path = families[name]["depth_file"]
        if path == chosen:
            continue
        entry = next((item for item in also if item["depth_file"] == path), None)
        if entry is None:
            entry = {"depth_file": path, "families": [], "files": 0, "bytes": 0}
            also.append(entry)
        entry["families"].append(name)
        entry["files"] += families[name]["count"]
        entry["bytes"] += families[name]["bytes"]
    also.sort(key=lambda item: (-item["files"], item["depth_file"]))
    runner_up = None
    for name in order:
        if families[name]["depth_file"] != chosen:
            runner_up = {"family": name, "depth_file": families[name]["depth_file"],
                         "files": families[name]["count"]}
            break
    return {"open_first": chosen,
            "exists": os.path.isfile(os.path.join(fkit.ROOT, chosen)),
            "dominant_family_by_count": dominant, "reason": reason,
            "basis": basis,
            "runner_up": runner_up}, also


def build_evidence(target, records, families, order, route):
    """A rendered inventory line, plus the real first bytes of one example.

    The head_hex is bytes actually read off disk. The sentence around it is this
    tool's own rendering, which is exactly why the kind is surface.
    """
    if not order:
        return "0 files classified under %s" % target
    top = order[0]
    example = families[top]["examples"][0]
    return ("%d file(s), %d family(ies) under %s; %s leads with %d file(s); "
            "example %s bytes=%d head=%s; route %s"
            % (len(records), len(families), target, top, families[top]["count"],
               example["path"], example["bytes"], example["head_hex"] or "(empty)",
               route["open_first"]))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    parser.add_argument("--path", required=True,
                        help="the bundle directory, or a single file")
    parser.add_argument("--max-bytes", type=int, default=4096,
                        help="cap on the magic read per file (default 4096; the "
                             "PE header offset and a CloudTrail key need a few "
                             "hundred)")
    parser.add_argument("--examples", type=int, default=5,
                        help="example paths kept per family (default 5)")
    parser.add_argument("--hash", action="store_true",
                        help="add sha256 for every file at or under "
                             "--hash-max-bytes")
    parser.add_argument("--hash-max-bytes", type=int, default=16 << 20,
                        help="size cap for --hash (default 16777216)")
    parser.add_argument("--breadth-threshold", type=int, default=3,
                        help="depth files present before the route goes to intake "
                             "instead of the biggest family (default 3)")

    gate = parser.add_argument_group("hooks.py post-probe fields")
    gate.add_argument("--challenge", required=True,
                      help="challenge name, as tools/state.py knows it")
    gate.add_argument("--class", dest="probe_class",
                      help="bug class; the gate refuses post-probe without it, "
                           "and it must equal the hypothesis bug_class")
    gate.add_argument("--hypothesis-id", dest="hypothesis_id",
                      help="the gate refuses post-probe without it")
    gate.add_argument("--chain-card")
    gate.add_argument("--verdict", default="inconclusive", choices=fkit.VERDICTS,
                      help="asking for confirms cannot produce one here: no "
                           "parser ran, so fkit.downgrade() forces inconclusive")

    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    if args.max_bytes < 16:
        parser.error("--max-bytes must be at least 16 to reach a magic value")
    if args.examples < 1:
        parser.error("--examples must be at least 1")
    if not os.path.exists(args.path):
        parser.error("no such path: %s" % args.path)

    started = time.monotonic()
    records, walk_stats = inventory(args.path, args.max_bytes, args.hash,
                                    args.hash_max_bytes)
    families, order = families_of(records, args.examples)
    kape = kape_shape(records)
    route, also = route_of(families, order, kape, args.breadth_threshold)
    elapsed = round(time.monotonic() - started, 4)

    classified = sum(1 for rec in records if rec["family"] != "unknown")
    # No parser ran: that is the whole design, and it is why this can never
    # confirm. fkit.downgrade() is the rule, not a comment about the rule.
    verdict, forced_kind, reasons = fkit.downgrade(args.verdict,
                                                   matched=bool(classified),
                                                   parser_ok=False)
    downgrades = list(reasons)
    if verdict != "inconclusive":
        # fkit.downgrade() guards "confirms" only. An inventory ran no parser, so
        # it can no more falsify a hypothesis than confirm one: file shapes are
        # not evidence about what happened.
        verdict = "inconclusive"
    if args.verdict != verdict:
        downgrades.insert(0, "--verdict %s was downgraded to %s"
                          % (args.verdict, verdict))
    downgrades.append("an inventory classifies file shapes; it is never a "
                      "confirmation of anything about the investigation")
    kind = "surface"
    if forced_kind and forced_kind != "surface":
        downgrades.append(
            "fkit.downgrade offered evidence-kind %s because no parser ran; the "
            "kind stays surface, because a file listing is a real observation of "
            "file shapes and not a transport failure" % forced_kind)

    evidence = fkit.excerpt(build_evidence(args.path, records, families, order,
                                           route), 400)
    request = ("artifact_inventory --path %s --max-bytes %d%s"
               % (args.path, args.max_bytes, " --hash" if args.hash else ""))
    result = ("%d file(s), %d byte(s), %d family(ies), %d unreadable, %.3fs"
              % (len(records), sum(rec["bytes"] for rec in records),
                 len(families), len(walk_stats["unreadable"]), elapsed))
    post_argv = fkit.post_probe_argv(args.challenge, verdict, evidence, kind,
                                     request, result,
                                     bug_class=args.probe_class,
                                     hypothesis_id=args.hypothesis_id,
                                     chain_card=args.chain_card)
    missing = [flag for flag, value in (("--class", args.probe_class),
                                        ("--hypothesis-id", args.hypothesis_id))
               if not value]

    report = fkit.envelope(
        "artifact-inventory", ok=True, target=args.path,
        target_kind="directory" if os.path.isdir(args.path) else "file",
        scanned={"files": len(records), "classified": classified,
                 "bytes": sum(rec["bytes"] for rec in records),
                 "directories": walk_stats["directories"],
                 "symlinks_skipped": walk_stats["symlinks_skipped"],
                 "max_bytes_read_per_file": args.max_bytes,
                 "elapsed_s": elapsed},
        families=families, route=route, also_present=also, kape_shape=kape,
        unreadable=walk_stats["unreadable"], walk_errors=walk_stats["walk_errors"],
        magic_provenance=MAGIC_PROVENANCE,
        name_only_families=list(NAME_ONLY),
        verdict=verdict,
        verdict_downgrades=downgrades,
        evidence={"excerpt": evidence, "kind": kind,
                  "source": "this tool's own rendering of the file listing; the "
                            "head_hex inside it is bytes read off disk, the "
                            "sentence around it is not quoted from any artifact"},
        post_probe_command=fkit.as_command(post_argv),
        post_probe_argv=post_argv,
        gate="tools/hooks.py post-probe is the only write path for this verdict",
        next_action=("open %s; the gate refuses post-probe without %s"
                     % (route["open_first"], " and ".join(missing))
                     if missing else "open %s, then run post_probe_command"
                     % route["open_first"]))
    fkit.jprint(report, args.compact)
    return 0


if __name__ == "__main__":
    sys.exit(main())
