# Olórin board curation -- wakes a headless Olórin (a mind, not a script) to curate
# the shared board: carry warm items forward, consolidate keepers into long-term
# memory, decay the stale, re-render board.md. This script only TRIGGERS; the
# judgment is the spawned Olórin's. Mirrors Rhea's curate.ps1 / the launch resolver.
#
#   curate.ps1        -> curates the LIVE memory.db
#
# The FIRST live run should be watched (run curate.bat in a visible window once)
# before it is ever trusted unattended.

param([switch]$Force)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot   # Olorin project root -> the curator boots AS Olórin

# --- resolve claude.exe (mirrors Rhea's resolver / launch.ps1) ---
$realBase    = "$env:LOCALAPPDATA\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude-code"
$reparseBase = Join-Path $env:APPDATA "Claude\claude-code"
$candidates  = @()
foreach ($base in @($realBase, $reparseBase)) {
    if (Test-Path -LiteralPath $base) {
        $candidates += Get-ChildItem -LiteralPath $base -Directory -ErrorAction SilentlyContinue |
            Sort-Object Name -Descending |
            ForEach-Object { Join-Path $_.FullName 'claude.exe'; Get-ChildItem -LiteralPath $_.FullName -Directory -ErrorAction SilentlyContinue | ForEach-Object { Join-Path $_.FullName 'claude.exe' } }
    }
}
$exe = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $exe) { Write-Host "ERROR: claude.exe not found."; exit 1 }

# --- the curation brief (a focused boot task, not a script doing the thinking) ---
$promptFile = Join-Path $PSScriptRoot "memory\curate_prompt.md"
$prompt     = Get-Content -LiteralPath $promptFile -Raw -Encoding utf8

$log = Join-Path $PSScriptRoot "memory\curate_log.txt"
# --- QUIET-NIGHT GATE ------------------------------------------------------------
# memory\board_pending.py prints one integer: rows on the board that a curator has
# not yet seen, plus expiries that have lapsed since the last pass. 0: skip, spawn
# nothing. Any positive number: run. -1 means the check could not run; run anyway,
# a broken gate never reads as "nothing to do". -Force runs regardless; curate.bat
# passes it, so a double-click always runs a pass.
$py = "C:\Users\<user>\AppData\Local\Programs\Python\Python313\python.exe"
$pending = "-1"
try {
    $v = (& $py -X utf8 (Join-Path $PSScriptRoot "memory\board_pending.py") 2>$null | Select-Object -First 1)
    if ("$v".Trim() -match '^-?\d+$') { $pending = "$v".Trim() }
} catch { $pending = "-1" }
if (-not $Force -and $pending -eq "0") {
    "=== curate $(Get-Date -Format 'yyyy-MM-dd HH:mm') -- quiet night: nothing on the board since the last pass; skipped, no model spawned ===" | Add-Content -LiteralPath $log -Encoding utf8
    exit 0
}
if ($pending -notmatch '^\d+$') {
    "=== curate $(Get-Date -Format 'yyyy-MM-dd HH:mm') -- PENDING CHECK BROKEN (got '$pending'); running anyway ===" | Add-Content -LiteralPath $log -Encoding utf8
} elseif ($Force) {
    "=== curate $(Get-Date -Format 'yyyy-MM-dd HH:mm') -- forced by hand ($pending row(s) pending) ===" | Add-Content -LiteralPath $log -Encoding utf8
} else {
    "=== curate $(Get-Date -Format 'yyyy-MM-dd HH:mm') -- $pending row(s) pending since the last pass; waking the curator ===" | Add-Content -LiteralPath $log -Encoding utf8
}

"=== curate run $(Get-Date -Format 'yyyy-MM-dd HH:mm') ===" | Add-Content -LiteralPath $log

# --- spawn a headless Olórin to do the curation (proven -p form) ---
# Tee-Object in PS 5.1 rejects -LiteralPath with -Append; use -FilePath. The
# spawned claude's shutdown hooks write stderr, so soften the abort first.
# --- the model is PINNED, not inherited --------------------------------------
# Damon's decision, in his own hand, 2026-09-10:
#     "Sonnet with Haiku last resort is my decision."
#
# WHY PINNED AT ALL. Inheriting the account default is what killed all three
# nightly jobs on the morning of 2026-08-15: the default was Fable, the Fable cap
# was spent, and curation, the world-check and the transcript sweep all died on
# one line within an hour. Damon's split is that the expensive model is for
# thinking WITH him, not for filing. Pinning also means his default can move
# without silently re-aiming this job.
#
# WHY HAIKU AND NOT OPUS, since Haiku was being purged the night this was written.
# The fallback fires on exactly one condition: the primary is capped. On a spent
# evening the Opus cap is spent too - same account, same night - so falling back
# to a more expensive model in the same family is the one direction that cannot
# help. A cheaper model filing the board beats a night unfiled. The marker says
# which model ran, so a fallback night gets a warm look rather than silent trust.
$Model         = "claude-sonnet-5[1m]"
$FallbackModel = "claude-haiku-4-5"

# This retry is COARSER than Hadrian's, and deliberately so rather than by
# oversight: his room classifies the failure and retries only on capacity. This
# retries on any non-zero exit. The cost is a wasted fallback run after a genuine
# fault; the benefit is that two rooms are not carrying a sixth hand-copied
# classifier. The verify block below is the real check either way - it asks
# whether the pass LANDED, which is the question that survives either design.
$ErrorActionPreference = "Continue"
$modelUsed = $Model
& $exe -p --model $Model $prompt `
    --permission-mode bypassPermissions `
    --add-dir "$PSScriptRoot\memory" 2>&1 | Tee-Object -FilePath $log -Append

if ($LASTEXITCODE -ne 0) {
    "--- primary FAILED on $Model (exit $LASTEXITCODE) -- retrying once on $FallbackModel ---" |
        Add-Content -LiteralPath $log
    $modelUsed = $FallbackModel
    & $exe -p --model $FallbackModel $prompt `
        --permission-mode bypassPermissions `
        --add-dir "$PSScriptRoot\memory" 2>&1 | Tee-Object -FilePath $log -Append
}

"=== curate done $(Get-Date -Format 'yyyy-MM-dd HH:mm') (model: $modelUsed) ===" | Add-Content -LiteralPath $log

# --- verify the pass actually landed -----------------------------------------
# Ported from Rhea's room 2026-09-10, her design. A guard inside a script cannot
# catch the script running wrong and quietly, so this asks about the EFFECT: a real
# pass always leaves a board row authored 'curator'. Then a second question, because
# a curator row proves a pass ran and not that it finished.
$py = "C:\Users\<user>\AppData\Local\Programs\Python\Python313\python.exe"
$dbCheck = & $py -X utf8 (Join-Path $PSScriptRoot "memory\curator_check.py") 2>$null
if ("$dbCheck".Trim() -ne "0" -and "$dbCheck".Trim() -match '^\d+$') {
    "verify: curator row found, pass landed." | Add-Content -LiteralPath $log -Encoding utf8

    $unfiled = & $py -X utf8 (Join-Path $PSScriptRoot "memory\coverage_check.py") 2>$null
    $unfiled = "$unfiled".Trim()
    if ($unfiled -match '^\d+$' -and [int]$unfiled -gt 0) {
        "verify: OVERDUE -- $unfiled board rows past expiry (or 30+ days with none) and still unfiled. Writing Inbox alert." | Add-Content -LiteralPath $log -Encoding utf8
        $palert = Join-Path $PSScriptRoot ("Inbox\ALERT_curator_partial_" + (Get-Date -Format 'yyyy-MM-dd') + ".md")
        @"
# Curator ran but rows fell through ($(Get-Date -Format 'yyyy-MM-dd HH:mm'))

The pass landed -- there is a curator row -- but **$unfiled board rows are overdue
and unfiled**: past their expiry, or 30+ days old with no expiry set. Open threads
inside their window are not counted; these are rows nobody filed or re-dated.

The cause to check first: the rendered board view caps silently, so a curator can
miss rows it never saw. ``python ..\tools\memory_db\memory.py --db memory\memory.db board-unfiled``
lists them uncapped (this room's own memory.py has no such command).
File each, or re-date it if the thread is genuinely still live.

Re-run by double-clicking ``curate.bat``.
"@ | Set-Content -LiteralPath $palert -Encoding utf8
    } elseif ($unfiled -eq "0") {
        "verify: coverage clean -- zero unfiled rows." | Add-Content -LiteralPath $log -Encoding utf8
    } else {
        # -1, empty, or anything non-numeric. A check that cannot run is NOT a pass.
        "verify: COVERAGE CHECK BROKEN (got '$unfiled') -- coverage is UNKNOWN, not clean." | Add-Content -LiteralPath $log -Encoding utf8
    }
} else {
    "verify: NO curator row in last 12h -- pass DID NOT LAND. Writing Inbox alert." | Add-Content -LiteralPath $log -Encoding utf8
    $alert = Join-Path $PSScriptRoot ("Inbox\ALERT_curator_failed_" + (Get-Date -Format 'yyyy-MM-dd') + ".md")
    $tail = (Get-Content -LiteralPath $log -Tail 40) -join "`n"
    @"
# Curator failed last night ($(Get-Date -Format 'yyyy-MM-dd HH:mm'))

The nightly board-curation pass ran but left no curator row in the DB. The board was
NOT filed. Re-run by double-clicking ``curate.bat``, or let the next session look.

Last 40 lines of curate_log.txt:

``````
$tail
``````
"@ | Set-Content -LiteralPath $alert -Encoding utf8
}

exit 0
