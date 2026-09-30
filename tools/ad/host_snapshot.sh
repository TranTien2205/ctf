#!/bin/sh
# Snapshot the surfaces an organiser plants a foothold in. Prints ONE JSON document.
#
# There is no `debsums`, no `aide`, no `rkhunter` and no host IDS on this box --
# measured. So this plus tools/ad/host_diff.py is the whole answer to "did anything
# change since I took the baseline", and the baseline is taken during the thirty
# minutes in skills/ad-planted-backdoor-hunt/SKILL.md. The surfaces below are that
# skill's sweep, in the same order, so the two cannot drift.
#
#   sh tools/ad/host_snapshot.sh > runs/<host>/survey/t0.json
#   sh tools/ad/host_snapshot.sh --expensive > runs/<host>/survey/t0-full.json
#
# THREE MEASURED HAZARDS shape every line of this file, because the first design
# of it was unrunnable:
#
#   * a /var/lib/dpkg/info/*.md5sums walk is 407,392 entries and about 41 MINUTES
#     on this box. So package verification is behind --expensive and says so.
#   * `find / -xdev -perm -4000 -type f` exceeded 120 seconds. Same treatment.
#   * a hung hard NFS mount makes `df` BLOCK FOREVER (`timeout 3 df` exits 124).
#     So this never calls df. Mount points come from /proc/mounts, and network
#     filesystems are pruned by type before any traversal.
#
# Every command is wrapped in `timeout`. A collector that times out records
# "timeout" rather than an empty list, because an empty list reads as "looked, and
# there is nothing there" -- which is the one wrong answer.
#
# Read-only. It never removes anything and never writes outside stdout.
set -u

EXPENSIVE=0
# 10s, not 5: `systemctl list-unit-files --state=enabled` was measured at 2.47s
# idle on this box and it timed out at 5s under concurrent load. A collector that
# times out records "timeout", which is honest but useless, and enabled units are
# the first surface the sweep looks at. Override with SNAPSHOT_TIMEOUT.
T=${SNAPSHOT_TIMEOUT:-10}
for arg in "$@"; do
    case "$arg" in
        --expensive) EXPENSIVE=1 ;;
        -h|--help)
            sed -n '2,32p' "$0" | sed 's/^# \{0,1\}//'
            printf '\n--expensive  also run the set-id sweep and package verification.\n'
            printf '             MEASURED COST: the set-id sweep exceeded 120s and the\n'
            printf '             package walk is about 41 minutes on this box.\n'
            exit 0 ;;
        *) printf 'unknown argument: %s\n' "$arg" >&2; exit 2 ;;
    esac
done

# JSON string escaping, in pure awk: no jq dependency for a tool the operator may
# run on a contest box that has nothing installed.
esc() {
    awk 'BEGIN{ORS=""} {
        gsub(/\\/,"\\\\"); gsub(/"/,"\\\""); gsub(/\t/,"\\t"); gsub(/\r/,"\\r")
        print (NR>1 ? "\\n" : "") $0
    }'
}

# Run a command with a hard timeout and emit a JSON member: either its lines as an
# array of strings, or the single string "timeout".
collect() {
    key=$1; shift
    printf '  "%s": ' "$key"
    out=$(timeout "$T" "$@" 2>/dev/null)
    rc=$?
    if [ "$rc" -eq 124 ]; then
        printf '{"status": "timeout", "seconds": %s}' "$T"
        return
    fi
    printf '{"status": "ok", "lines": ['
    first=1
    printf '%s\n' "$out" | while IFS= read -r line; do
        [ -z "$line" ] && continue
        if [ "$first" -eq 1 ]; then first=0; else printf ', '; fi
        printf '"%s"' "$(printf '%s' "$line" | esc)"
    done
    printf ']}'
}

# Local mount points only. /proc/mounts never blocks; df can block forever.
local_mounts() {
    awk '$3 !~ /^(nfs|nfs4|cifs|smb3|smbfs|fuse\.sshfs|afs|9p|ceph|glusterfs)$/ \
         && $2 ~ /^\// { print $2 }' /proc/mounts 2>/dev/null | sort -u
}

network_mounts() {
    awk '$3 ~ /^(nfs|nfs4|cifs|smb3|smbfs|fuse\.sshfs|afs|9p|ceph|glusterfs)$/ \
         { print $2 " (" $3 ")" }' /proc/mounts 2>/dev/null | sort -u
}

printf '{\n'
printf '  "mode": "ad-host-snapshot",\n'
printf '  "host": "%s",\n' "$(hostname 2>/dev/null | esc)"
printf '  "taken_utc": "%s",\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
printf '  "expensive": %s,\n' "$([ "$EXPENSIVE" -eq 1 ] && echo true || echo false)"
printf '  "timeout_seconds": %s,\n' "$T"

printf '  "network_mounts_skipped": ['
first=1
network_mounts | while IFS= read -r m; do
    [ -z "$m" ] && continue
    if [ "$first" -eq 1 ]; then first=0; else printf ', '; fi
    printf '"%s"' "$(printf '%s' "$m" | esc)"
done
printf '],\n'

# 1. start-up: what runs without anyone asking
collect enabled_units systemctl list-unit-files --state=enabled --no-pager --no-legend
printf ',\n'
collect timers systemctl list-timers --all --no-pager --no-legend
printf ',\n'
collect cron_files sh -c 'ls -la /etc/cron.d /etc/cron.daily /etc/cron.hourly /etc/cron.weekly /var/spool/cron/crontabs 2>/dev/null'
printf ',\n'
collect root_crontab crontab -l
printf ',\n'

# 2. keys and accounts
collect authorized_keys sh -c 'for f in /root/.ssh/authorized_keys /home/*/.ssh/authorized_keys /etc/ssh/authorized_keys*; do [ -f "$f" ] && sed "s|^|$f: |" "$f"; done'
printf ',\n'
collect shell_accounts awk -F: '$7 !~ /(nologin|false|sync)$/ {print $1 " uid=" $3 " shell=" $7}' /etc/passwd
printf ',\n'
collect empty_passwords awk -F: '$2 == "" {print $1}' /etc/shadow
printf ',\n'
collect sudoers sh -c 'ls -la /etc/sudoers.d/ 2>/dev/null; grep -hvE "^\s*(#|$)" /etc/sudoers /etc/sudoers.d/* 2>/dev/null'
printf ',\n'

# 3. loader hooks -- a short, finite list, so it is checked completely
collect ld_preload sh -c 'cat /etc/ld.so.preload 2>/dev/null; env | grep -i preload'
printf ',\n'

# 4. listeners: every one must map to a service you can name
collect listeners ss -lntup
printf ',\n'

# 5. the local mount points, so a diff can tell a new filesystem from a new file
collect local_mounts sh -c 'awk "\$3 !~ /^(nfs|nfs4|cifs|smb3|smbfs|fuse.sshfs|afs|9p|ceph|glusterfs)\$/ && \$2 ~ /^\// { print \$2 }" /proc/mounts | sort -u'

if [ "$EXPENSIVE" -eq 1 ]; then
    printf ',\n'
    # Bounded to local mounts and given a much longer timeout, because the
    # unbounded form was measured past 120 seconds.
    printf '  "setid_binaries": '
    out=$(timeout 180 find $(local_mounts | tr '\n' ' ') -xdev -type f \
          \( -perm -4000 -o -perm -2000 \) -printf '%M %u %p\n' 2>/dev/null)
    if [ $? -eq 124 ]; then printf '{"status": "timeout", "seconds": 180}'
    else
        printf '{"status": "ok", "lines": ['
        first=1
        printf '%s\n' "$out" | while IFS= read -r line; do
            [ -z "$line" ] && continue
            if [ "$first" -eq 1 ]; then first=0; else printf ', '; fi
            printf '"%s"' "$(printf '%s' "$line" | esc)"
        done
        printf ']}'
    fi
    printf ',\n'
    # dpkg -V, not a md5sums walk: same question, and it does not take 41 minutes.
    collect package_integrity sh -c 'dpkg -V 2>/dev/null | head -200'
else
    printf ',\n'
    printf '  "setid_binaries": {"status": "skipped", "why": "measured past 120s unbounded; pass --expensive"},\n'
    printf '  "package_integrity": {"status": "skipped", "why": "a dpkg md5sums walk is ~41 minutes here; pass --expensive for dpkg -V"}'
fi

printf '\n}\n'
