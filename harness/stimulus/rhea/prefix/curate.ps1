# Rhea board curation -- wakes a headless Rhea (a mind, not a script) to curate
# the shared board: carry warm items forward, consolidate keepers into long-term
# memory, decay the stale, re-render board.md. This script only TRIGGERS; the
# judgment is the spawned Rhea's. Mirrors launch.ps1's claude.exe resolver.
#
#   curate.ps1        -> curates the LIVE memory.db
#
# The FIRST live run should be watched (run curate.bat in a visible window once)
# before it is ever trusted unattended.

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot   # Rhea project root -> the curator boots AS Rhea
. (Join-Path $PSScriptRoot "automation_common.ps1")

# --- resolve claude.exe (mirrors launch.ps1) ---
$realBase    = "$env:LOCALAPPDATA\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude-code"
$reparseBase = Join-Path $env:APPDATA "Claude\claude-code"
$candidates  = @((Join-Path $realBase "2.1.156\claude.exe"), (Join-Path $reparseBase "2.1.156\claude.exe"))
foreach ($base in @($realBase, $reparseBase)) {
    if (Test-Path -LiteralPath $base) {
        $candidates += Get-ChildItem -LiteralPath $base -Directory -ErrorAction SilentlyContinue |
            Sort-Object Name -Descending |
            ForEach-Object { Join-Path $_.FullName 'claude.exe' }
    }
}
$exe = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $exe) { Write-Host "ERROR: claude.exe not found."; exit 1 }

# --- the curation brief (a focused boot task, not a script doing the thinking) ---
$promptFile = Join-Path $PSScriptRoot "memory\curate_prompt.md"
$prompt     = Get-Content -LiteralPath $promptFile -Raw

$log    = Join-Path $PSScriptRoot "memory\curate_log.txt"     # MARKERS ONLY -- this script's own voice
$outLog = Join-Path $PSScriptRoot "memory\curate_output.txt"  # the headless curator's transcript

# 2026-08-20: the monitored process no longer writes into the monitor's log. Rotate any
# mixed-encoding predecessor once, so a marker here means the script actually wrote it.
Initialize-MarkerLog -Log $log
Write-Marker -Log $log -Text "=== curate run $(Get-Date -Format 'yyyy-MM-dd HH:mm') ==="

# --- spawn a headless Rhea to do the curation (proven -p form; cf OSR web_ui) ---
# The spawned claude's shutdown hooks write to stderr, so the abort preference is
# softened inside Invoke-HeadlessRhea rather than here.
# (Olórin fixed a dead form of this line 2026-06-25 — which is why curate never ran.)
# The arrival gate is skipped here BY DESIGN: this brief deliberately says
# "do not run your full boot sequence" (seed + brief is enough for filing).
$env:RHEA_SKIP_ARRIVAL = "1"
# --model is PINNED, not inherited (2026-08-15). Inheriting the account default is
# what killed all three nightly jobs on the morning of Aug 15: the default was Fable,
# the Fable cap was spent, and curation + the world-check + the transcript sweep all
# died on one line within an hour. Damon's split: the expensive model is for thinking
# WITH him, not for filing. Pinning also means his default can move without silently
# re-aiming this job at a different model.
#
# 2026-08-20: pinning stopped ONE cap from being inherited by three jobs; it did not stop
# a cap on the pinned model from reading as a fault. The run now classifies itself and
# retries once on a cheaper model when the cause is capacity.
#
# NOTE FOR A FALLBACK RUN: this pass writes PERMANENT memory. A cheaper model filing the
# board is better than a night unfiled -- and the coverage guard below still catches a
# partial pass -- but the alert says which model ran, and a fallback night is worth a
# warm look rather than being trusted silently.
$run = Invoke-HeadlessRhea -Exe $exe -Prompt $prompt `
    -Model "claude-sonnet-5[1m]" `
    -MarkerLog $log -OutputLog $outLog `
    -AddDir "$PSScriptRoot\memory"

Write-Marker -Log $log -Text "=== curate done $(Get-Date -Format 'yyyy-MM-dd HH:mm') (model: $($run.ModelUsed), status: $($run.Status)) ==="

# --- verify the pass actually landed (added 2026-08-11; the Aug 3 OAuth death was
#     invisible because we trusted the exit path, not the effect). A real pass always
#     logs a board row with author='curator'; check one exists from the last 12h. ---
$py = "C:\Users\<user>\AppData\Local\Programs\Python\Python313\python.exe"
$dbCheck = & $py -X utf8 (Join-Path $PSScriptRoot "memory\curator_check.py") 2>$null
if ("$dbCheck".Trim() -ne "0" -and "$dbCheck".Trim() -match '^\d+$') {
    Write-Marker -Log $log -Text "verify: curator row found, pass landed (ran on $($run.ModelUsed))."

    # --- second verify: DID IT ACTUALLY FILE EVERYTHING? (added 2026-08-15)
    #     A curator row proves a pass ran, not that it finished. On 8-15 a pass
    #     filed 19 rows, reported "board fully consolidated, 50/50", and left 37
    #     unfiled -- because get_board() silently caps at 50 and a truncated view
    #     of a full board looks exactly like a finished job. The row-exists guard
    #     went green on it. Coverage needs its own check. ---
    #     Lives in its own .py (like curator_check.py) rather than an inline -c: PS 5.1
    #     parses COUNT(*) out of a nested-quoted string and the check dies silently,
    #     which is the very failure this guard exists to prevent. It prints -1, never a
    #     count, when it cannot run -- so "broken" can't be mistaken for "clean".
    $unfiled = & $py -X utf8 (Join-Path $PSScriptRoot "memory\coverage_check.py") 2>$null
    $unfiled = "$unfiled".Trim()
    if ($unfiled -match '^\d+$' -and [int]$unfiled -gt 0) {
        Write-Marker -Log $log -Text "verify: PARTIAL PASS -- $unfiled board rows still unfiled. Writing Inbox alert."
        $palert = Join-Path $PSScriptRoot ("Inbox\ALERT_curator_partial_" + (Get-Date -Format 'yyyy-MM-dd') + ".md")
        @"
# Curator ran but did not finish ($(Get-Date -Format 'yyyy-MM-dd HH:mm'))

Ran on ``$($run.ModelUsed)``$(if ($run.Retried) { " -- a CAP FALLBACK, so thinner output is expected" }).

The pass landed -- there is a curator row -- but **$unfiled board rows are still
unfiled**. That is a partial pass reporting itself as a complete one.

The known cause: ``get_board()`` and ``python memory.py board`` silently cap at 50
rows. A curator working from that view sees a truncated board, files what it can
see, and honestly reports success. **Use ``python memory.py board-unfiled``** --
uncapped, and the curator brief now says so in step 0.

Re-run by double-clicking ``curate.bat``. To see what is outstanding:

``````
python memory.py board-unfiled
``````
"@ | Set-Content -LiteralPath $palert -Encoding utf8
        try { & (Join-Path $PSScriptRoot 'paddock\notify.ps1') -Title 'Rhea' -Message "Curator ran but left $unfiled rows unfiled. Note in my Inbox." } catch {}
    } elseif ($unfiled -eq "0") {
        Write-Marker -Log $log -Text "verify: coverage clean -- zero unfiled rows."

        # --- PRUNE (wired 2026-09-08, at his instruction) ---------------------------
        # The board is the WARM tier and had never been trimmed: consolidation COPIES a
        # row into long-term, it does not remove it, and nothing ever called board-decay.
        # 358 rows spanning two months were sitting in a tier whose job is "recent".
        # Criterion is EXPIRY, not warmth: --max-warmth defaults to 2 and only 13 of 358
        # rows are warmth 2, because the real filter runs at whether-to-record. The
        # file-everything guard still applies -- decay_board() refuses anything not yet
        # consolidated -- so nothing can be lost, only moved from warm to searchable.
        $decayed = (& $py (Join-Path $PSScriptRoot 'memory\memory.py') board-decay --max-warmth 5) 2>&1
        Write-Marker -Log $log -Text "prune: $decayed"
        & $py (Join-Path $PSScriptRoot 'memory\memory.py') board-render --out (Join-Path $PSScriptRoot 'memory\board.md') | Out-Null
        Write-Marker -Log $log -Text "prune: board.md re-rendered."
    } else {
        # -1, empty, or anything non-numeric. A check that cannot run is NOT a pass.
        Write-Marker -Log $log -Text "verify: COVERAGE CHECK BROKEN (got '$unfiled') -- coverage is UNKNOWN, not clean."
    }
} else {
    Write-Marker -Log $log -Text "verify: NO curator row in last 12h -- pass DID NOT LAND (status: $($run.Status)). Writing Inbox alert."
    $alert = Join-Path $PSScriptRoot ("Inbox\ALERT_curator_failed_" + (Get-Date -Format 'yyyy-MM-dd') + ".md")
    $tail = (Get-Content -LiteralPath $log -Tail 40) -join "`n"
    $note = Get-StatusNote -Status $run.Status -ModelUsed $run.ModelUsed -Retried $run.Retried
    @"
# Curator failed last night ($(Get-Date -Format 'yyyy-MM-dd HH:mm'))

$note

The nightly board-curation pass ran but left no curator row in the DB -- the same
signature as the Aug 3 OAuth death. The board was NOT filed. Re-run by
double-clicking ``curate.bat``, or let the next Rhea session investigate.

Last 40 lines of curate_log.txt:

``````
$tail
``````
"@ | Set-Content -LiteralPath $alert -Encoding utf8
    try { & (Join-Path $PSScriptRoot 'paddock\notify.ps1') -Title 'Rhea' -Message 'The nightly memory curator failed last night. Note left in my Inbox.' } catch {}
}
exit 0
