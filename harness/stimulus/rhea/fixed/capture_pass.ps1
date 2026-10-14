# Rhea transcript capture -- wakes a headless Rhea to sweep extracted session
# transcripts that no /capture ever caught, and board-add the keepers. The
# upstream twin of curate.ps1 (which files the board downstream).
#
# Built 2026-08-11 at Damon's ask, after the record pass recovered three months
# of dropped keepers. Zero-cost when there is nothing new: capture_scan.py picks
# candidates first, and if the list is empty no model is spawned at all.
#
# Pipeline order (all daily): extract 6:30 -> THIS 7:00 -> curate files it next night.

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot   # Rhea project root -> boots AS Rhea
. (Join-Path $PSScriptRoot "automation_common.ps1")

$py     = "C:\Users\<user>\AppData\Local\Programs\Python\Python313\python.exe"
$log    = Join-Path $PSScriptRoot "memory\capture_log.txt"     # MARKERS ONLY -- this script's own voice
$outLog = Join-Path $PSScriptRoot "memory\capture_output.txt"  # the headless instance's transcript

# The monitored process no longer writes into the monitor's log (2026-08-20). Rotate any
# mixed-encoding predecessor once, so a marker in this file actually means the script wrote it.
Initialize-MarkerLog -Log $log

Write-Marker -Log $log -Text "=== capture run $(Get-Date -Format 'yyyy-MM-dd HH:mm') ==="

# --- zero-token pre-scan: anything to sweep? ---
$cand = & $py -X utf8 (Join-Path $PSScriptRoot "memory\capture_scan.py")
$cand = ($cand | Out-String).Trim()
if ([string]::IsNullOrWhiteSpace($cand)) {
    Write-Marker -Log $log -Text "nothing to sweep."
    exit 0
}
Write-Marker -Log $log -Text "candidates:`r`n$cand"

# --- resolve claude.exe (mirrors curate.ps1) ---
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
if (-not $exe) { Write-Marker -Log $log -Text "ERROR: claude.exe not found."; exit 1 }

# --- spawn headless Rhea with the brief + today's file list ---
$prompt = (Get-Content -LiteralPath (Join-Path $PSScriptRoot "memory\capture_prompt.md") -Raw -Encoding utf8)
$prompt += "`n`n## FILES TO SWEEP TODAY`n`n$cand`n"

# Arrival gate skipped BY DESIGN: this brief says "do not run your full boot
# sequence" — seed + brief is the intended footing for the sweep.
$env:RHEA_SKIP_ARRIVAL = "1"
# --model PINNED, not inherited -- see the note in curate.ps1 (Aug 15 2026: one spent
# Fable cap took down all three nightly jobs, because none of them named a model).
# The run now classifies its own failure and retries once on a cheaper model when the
# cause is capacity rather than a fault; the transcript goes to capture_output.txt.
$run = Invoke-HeadlessRhea -Exe $exe -Prompt $prompt `
    -Model "claude-sonnet-5[1m]" `
    -MarkerLog $log -OutputLog $outLog `
    -AddDir "$PSScriptRoot\memory"

# --- verify the effect, not the exit code (lesson of the Aug 3 curator death) ---
$left = & $py -X utf8 (Join-Path $PSScriptRoot "memory\capture_scan.py")
$left = ($left | Out-String).Trim()
if ([string]::IsNullOrWhiteSpace($left)) {
    Write-Marker -Log $log -Text "verify: all candidates marked swept (ran on $($run.ModelUsed))."
} else {
    Write-Marker -Log $log -Text "verify: UNSWEPT candidates remain -- pass did not finish (status: $($run.Status)). Writing Inbox alert."
    $alert = Join-Path $PSScriptRoot ("Inbox\ALERT_capture_failed_" + (Get-Date -Format 'yyyy-MM-dd') + ".md")
    $tail = (Get-Content -LiteralPath $log -Tail 40) -join "`n"
    $note = Get-StatusNote -Status $run.Status -ModelUsed $run.ModelUsed -Retried $run.Retried
    @"
# Transcript capture pass failed ($(Get-Date -Format 'yyyy-MM-dd HH:mm'))

$note

These extracted sessions were due a capture sweep and did not get marked:

``````
$left
``````

Re-run by double-clicking ``capture_pass.bat``, or let the next Rhea session
investigate. Last 40 lines of capture_log.txt:

``````
$tail
``````
"@ | Set-Content -LiteralPath $alert -Encoding utf8
    try { & (Join-Path $PSScriptRoot 'paddock\notify.ps1') -Title 'Rhea' -Message 'The transcript capture pass failed. Note left in my Inbox.' } catch {}
}

Write-Marker -Log $log -Text "=== capture done $(Get-Date -Format 'yyyy-MM-dd HH:mm') ==="
exit 0
