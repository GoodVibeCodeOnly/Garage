#!/usr/bin/env bash
# backup-agents.sh -- a bash port of backup-agents.ps1 as it stood on 2026-09-05, the
# night the fault ran. The original is beside this file (backup-agents.ps1.bak-20260905).
#
# WHAT IS PRESERVED, because it is the fault:
#   1. the compress step is wrapped so that a failure is LOGGED AND NOT TREATED AS FAILURE
#      (the PowerShell `catch { Log "ERROR..." }` with no exit);
#   2. a failed compress leaves a partial .zip in the snapshot folder, under the same
#      agents-*.zip glob the restore and the rotation use;
#   3. the rotation counts every file matching the glob -- partials included -- and deletes
#      the oldest to stay under KeepCount, so a corrupt fragment evicts a good snapshot;
#   4. the rate-limiter reads the newest file's mtime, so a fresh 4 KB fragment reads as
#      "a successful backup ran recently" and the next night is skipped.
#
# WHAT IS NOT: robocopy -> rsync, bsdtar -a -> zip -r, the named mutex -> a flock. None of
# those carried the fault. Rhea, 2026-10-13.

HomebaseRoot='__HOMEBASE_ROOT__'
ClaudeRoot='__CLAUDE_ROOT__'
BackupRoot='__BACKUP_ROOT__'
KeepCount=14

Stamp="$(date +%Y-%m-%d_%H%M%S)"
Staging="${TMPDIR:-/tmp}/agent-backup-$Stamp"
ZipPath="$BackupRoot/agents-$Stamp.zip"
LogPath="$BackupRoot/backup.log"

mkdir -p "$BackupRoot"

log() { printf '%s  %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >> "$LogPath"; }

# Rate-limit: skip if a successful backup ran in the last $MinHours hours.
# Pass -Force to bypass.
MinHours=__MIN_HOURS__
force=0; for a in "$@"; do [ "$a" = "-Force" ] && force=1; done
if [ "$force" -eq 0 ]; then
    recent="$(ls -t "$BackupRoot"/agents-*.zip 2>/dev/null | head -n 1)"
    if [ -n "$recent" ]; then
        age_h=$(( ( $(date +%s) - $(stat -c %Y "$recent") ) / 3600 ))
        if [ "$age_h" -lt "$MinHours" ]; then
            log "skipped ($Stamp): last backup ${age_h}h ago"
            exit 0
        fi
    fi
fi

# Single-instance guard.
exec 9>"$BackupRoot/.backup.lock"
if ! flock -n 9; then
    log "skipped ($Stamp): another backup already running"
    exit 0
fi

log "=== backup start: $Stamp ==="

# Sweep staging trees abandoned by earlier runs.
for d in "${TMPDIR:-/tmp}"/agent-backup-*; do
    [ -d "$d" ] && [ "$d" != "$Staging" ] && { rm -rf "$d"; log "swept stale staging: $(basename "$d")"; }
done

# Pre-flight: refuse to start below a free-space margin.
MinFreeGB=__MIN_FREE_GB__
freeGB=$(( $(df -Pk "$BackupRoot" | awk 'NR==2{print $4}') / 1048576 ))
if [ "$freeGB" -lt "$MinFreeGB" ]; then
    log "skipped ($Stamp): only $freeGB GB free (need $MinFreeGB GB)"
    exit 0
fi

# Exclusions: bulk re-downloadable assets and caches (same list as the .ps1).
EXCLUDES=(--exclude 'pdfs' --exclude 'match_history' --exclude 'league' --exclude 'Castle Whiterock'
          --exclude '__pycache__' --exclude 'node_modules' --exclude '.venv' --exclude 'venv'
          --exclude 'cache' --exclude 'shell-snapshots' --exclude 'file-history' --exclude 'plugins'
          --exclude 'Inbox' --exclude '*.pyc' --exclude '*.log' --exclude '*.tmp'
          --exclude 'scheduled_tasks.lock' --exclude 'D&D.zip' --exclude 'agents-*.zip')

StagingHomebase="$Staging/Homebase"
StagingClaude="$Staging/dot-claude"
mkdir -p "$StagingHomebase" "$StagingClaude"

log "copying Homebase -> staging"
rsync -a "${EXCLUDES[@]}" "$HomebaseRoot/" "$StagingHomebase/" >/dev/null 2>&1; rcHomebase=$?
log "copying .claude -> staging"
rsync -a "${EXCLUDES[@]}" "$ClaudeRoot/" "$StagingClaude/" >/dev/null 2>&1; rcClaude=$?
[ "$rcHomebase" -ne 0 ] && log "WARN: rsync Homebase exit $rcHomebase"
[ "$rcClaude" -ne 0 ] && log "WARN: rsync .claude exit $rcClaude"

# Compress staging tree into a dated zip.
log "compressing -> $ZipPath"
if ( cd "$Staging" && zip -r -q "$ZipPath" . ); then
    sizeMB=$(( $(stat -c %s "$ZipPath") / 1048576 ))
    log "wrote $ZipPath ($sizeMB MB)"
else
    # THE FAULT: logged, and the script carries on to the rotation below with
    # whatever partial zip is sitting in the folder under the restore glob.
    log "ERROR: compress failed: zip exited $?"
fi

# Clean up staging.
rm -rf "$Staging"

# Rotate: keep the most recent $KeepCount snapshots (newest first by mtime).
mapfile -t snapshots < <(ls -t "$BackupRoot"/agents-*.zip 2>/dev/null)
if [ "${#snapshots[@]}" -gt "$KeepCount" ]; then
    for f in "${snapshots[@]:$KeepCount}"; do
        if rm -f "$f"; then
            log "rotated out: $(basename "$f")"
        else
            log "WARN: could not delete $(basename "$f")"
        fi
    done
fi

log "=== backup end ==="
