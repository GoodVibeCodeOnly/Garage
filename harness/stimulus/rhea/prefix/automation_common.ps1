# Shared plumbing for the nightly automations (curate.ps1, capture_pass.ps1,
# osint\osint_pass.ps1). Dot-source it:  . "$PSScriptRoot\automation_common.ps1"
#
# Built 2026-08-20. It exists because the three scripts kept failing IDENTICALLY
# and getting fixed three times -- the Aug 15 cap death took all three down at
# once, because none of them named a model. Two jobs live here and nothing else:
#
#   1. THE LOG SPLIT. Each script used to pipe the headless instance's whole
#      stdout into the SAME file it wrote its own liveness markers to
#      (`... | Tee-Object -FilePath $log -Append`) while writing its own lines
#      with Add-Content. PS 5.1 defaults those two to DIFFERENT encodings --
#      UTF-16 and the system ANSI codepage -- so the mojibake was designed
#      behaviour, not drift. Worse than unreadable: on Aug 19 the capture log
#      produced two completion lines for one run, 07:52 before 07:06, from a
#      script with exactly one writer. A liveness log that returns impossible
#      readings is not a liveness log.
#
#      The structural fault underneath: THE MONITORED PROCESS WAS WRITING INTO
#      THE MONITOR'S OWN LOG. A marker line in that file was not evidence the
#      script produced it. So now the script's markers go to <name>_log.txt and
#      the headless transcript goes to <name>_output.txt, both UTF-8 no-BOM,
#      and a marker means what it says.
#
#   2. CAPPED IS NOT DEAD. Every guard in this house distinguishes "did the
#      work" from "found no work"; none of them distinguished "the account is
#      out of capacity" from "the job is broken". One exhausted cap could still
#      take the whole layer down and the alert would read as a fault. Now the
#      run classifies its own failure, retries once on a named cheaper model,
#      and the alert says CAPPED when that is what happened.
#
# Everything here fails toward the caller: no exception escapes these functions
# in a way that would kill a pass that would otherwise have finished.

# --- UTF-8 without BOM. PS 5.1's -Encoding UTF8 writes a BOM; this doesn't. ---
$script:Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function Write-Marker {
    <#  One liveness line, appended as UTF-8 no-BOM. This is the ONLY thing that
        should ever write to a marker log -- the headless transcript goes
        elsewhere. #>
    param(
        [Parameter(Mandatory)][string]$Log,
        [Parameter(Mandatory)][string]$Text
    )
    try {
        [System.IO.File]::AppendAllText($Log, ($Text + "`r`n"), $script:Utf8NoBom)
    } catch {
        # A failure to log must never fail a pass.
        Write-Host "WARN: could not write marker to $Log -- $($_.Exception.Message)"
    }
}

function Initialize-MarkerLog {
    <#  Assert the marker log decodes as UTF-8 before appending to it. The old
        logs are mixed-encoding and mostly mojibake; rather than tolerate that
        forever in the reader, rotate the bad file out ONCE and start clean.
        Nothing is deleted -- the old file keeps its history under a new name. #>
    param([Parameter(Mandatory)][string]$Log)
    if (-not (Test-Path -LiteralPath $Log)) { return }
    try {
        $bytes = [System.IO.File]::ReadAllBytes($Log)
        if ($bytes.Length -eq 0) { return }
        # Strict decode: throws on any byte sequence that isn't valid UTF-8.
        $strict = New-Object System.Text.UTF8Encoding($false, $true)
        [void]$strict.GetString($bytes)
        # Valid UTF-8, but a UTF-16 file can decode as... nothing; catch the
        # obvious BOM case explicitly so it also gets rotated.
        if ($bytes.Length -ge 2 -and $bytes[0] -eq 0xFF -and $bytes[1] -eq 0xFE) { throw "utf-16 BOM" }
    } catch {
        $stamp   = Get-Date -Format 'yyyyMMdd'
        $dir     = Split-Path -Parent $Log
        $base    = [System.IO.Path]::GetFileNameWithoutExtension($Log)
        $rotated = Join-Path $dir "${base}_legacy_$stamp.txt"
        try {
            Move-Item -LiteralPath $Log -Destination $rotated -Force
            Write-Marker -Log $Log -Text "[$(Get-Date -Format 'yyyy-MM-dd HH:mm')] Rotated a non-UTF-8 predecessor to $(Split-Path -Leaf $rotated). This file is UTF-8 no-BOM from here on."
        } catch {
            Write-Host "WARN: could not rotate $Log -- $($_.Exception.Message)"
        }
    }
}

function Get-RunFailureKind {
    <#  Classify a headless run's output. Returns one of:
          ok      -- nothing that looks like a platform failure
          capped  -- out of capacity for the model that was asked for
          auth    -- credentials, not capacity (the Aug 3 death, eight days invisible)
          error   -- something else went wrong loudly
        Deliberately conservative: an unrecognised failure is 'error', never 'ok'. #>
    param([string]$Output, [int]$ExitCode)
    $o = "$Output"
    if ($o -match '(?i)(reached your .{0,40}limit|usage limit|rate limit|limit reached|out of (credits?|capacity)|quota (exceeded|exhausted))') { return 'capped' }
    if ($o -match '(?i)(failed to authenticate|oauth session expired|not logged in|invalid api key|authentication_error)')                     { return 'auth'   }
    if ($ExitCode -ne 0)                                                                                                                       { return 'error'  }
    return 'ok'
}

function Invoke-HeadlessRhea {
    <#  Run a headless pass, keep its transcript out of the marker log, and
        retry ONCE on a cheaper model if the first attempt was capped.

        Returns a hashtable: Status (ok|capped|auth|error), ModelUsed, Retried,
        Output. The caller still verifies its own EFFECT-MARKER afterwards --
        this function reports what the platform did, never whether the work
        landed. Those are different questions and conflating them is how the
        Aug 3 curator death stayed invisible for eight days. #>
    param(
        [Parameter(Mandatory)][string]$Exe,
        [Parameter(Mandatory)][string]$Prompt,
        [Parameter(Mandatory)][string]$Model,
        [string]$FallbackModel = 'claude-haiku-4-5',   # verified live 2026-08-20; 200K window, no [1m] variant exists
        [Parameter(Mandatory)][string]$MarkerLog,
        [Parameter(Mandatory)][string]$OutputLog,
        [string]$AddDir
    )

    $result = @{ Status = 'error'; ModelUsed = $Model; Retried = $false; Output = '' }

    # Nested so it disappears with the call, and so it picks up $Exe/$Prompt/$AddDir
    # from the enclosing scope. NOT named $args -- that's an automatic variable.
    function RunOnce([string]$m) {
        $cliArgs = @('-p', $Prompt, '--model', $m, '--permission-mode', 'bypassPermissions')
        if ($AddDir) { $cliArgs += @('--add-dir', $AddDir) }
        $prevEAP = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        # [Console]::OutputEncoding governs how PS DECODES the child's stdout; pinned here
        # so the transcript's encoding does not depend on the machine's ambient codepage.
        # ($OutputEncoding is the other direction and is not the one that matters.)
        #
        # HONEST PROVENANCE: I added this believing I had caught real mangling in the first
        # run's output file. I hadn't -- the replacement characters were my own terminal
        # failing to print an em-dash, and the file was correct both before and after.
        # Kept anyway, on its own merit: a script whose correctness rides on the ambient
        # console codepage is the same fragility the rest of this file exists to remove.
        # Recorded because a fix with a false reason attached teaches the next reader a
        # bug that never existed.
        $prevEnc = [Console]::OutputEncoding
        try {
            [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
            $out  = (& $Exe @cliArgs 2>&1 | Out-String)
            $code = $LASTEXITCODE
        } finally {
            try { [Console]::OutputEncoding = $prevEnc } catch {}
            $ErrorActionPreference = $prevEAP
        }
        return @{ Out = $out; Code = $code }
    }

    # The transcript is appended to its OWN file, stamped, so two runs in a day
    # are still separable and nothing the model says can impersonate a marker.
    $stampHeader = "`r`n===== $Model @ $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') =====`r`n"

    $r = RunOnce $Model
    try { [System.IO.File]::AppendAllText($OutputLog, $stampHeader + $r.Out, $script:Utf8NoBom) } catch {}
    $kind = Get-RunFailureKind -Output $r.Out -ExitCode $r.Code
    $result.Output = $r.Out

    if ($kind -eq 'capped' -and $FallbackModel) {
        Write-Marker -Log $MarkerLog -Text "CAPPED on $Model -- retrying once on $FallbackModel. This is capacity, not a fault."
        $r2 = RunOnce $FallbackModel
        $hdr2 = "`r`n===== $FallbackModel (cap fallback) @ $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') =====`r`n"
        try { [System.IO.File]::AppendAllText($OutputLog, $hdr2 + $r2.Out, $script:Utf8NoBom) } catch {}
        $kind2 = Get-RunFailureKind -Output $r2.Out -ExitCode $r2.Code
        $result.Retried   = $true
        $result.ModelUsed = $FallbackModel
        $result.Output    = $r2.Out
        $result.Status    = $kind2
        if ($kind2 -eq 'ok') {
            Write-Marker -Log $MarkerLog -Text "fallback ran clean on $FallbackModel. Output may be thinner than a full pass -- worth a warm look."
        } else {
            Write-Marker -Log $MarkerLog -Text "fallback ALSO failed ($kind2) on $FallbackModel."
            $result.Status = 'capped'   # the originating condition is what the alert should name
        }
        return $result
    }

    $result.Status = $kind
    if ($kind -ne 'ok') { Write-Marker -Log $MarkerLog -Text "run classified as: $kind (exit $($r.Code))" }
    return $result
}

function Get-StatusNote {
    <#  One human sentence for an alert, so a person reading the Inbox note knows
        which of the three things happened without opening a log. #>
    param([string]$Status, [string]$ModelUsed, [bool]$Retried)
    switch ($Status) {
        'capped' { return "**CAPPED, not broken.** The account was out of capacity" + $(if ($Retried) { " and the retry on ``$ModelUsed`` did not clear it" } else { "" }) + ". Nothing is wrong with the script -- it will run normally after the cap resets." }
        'auth'   { return "**AUTHENTICATION, not capacity.** The headless session could not log in. This is the Aug 3 failure shape; double-click ``Reauthorize Rhea.bat`` on the desktop." }
        'ok'     { return "The run completed without a platform error, so the failure is in the work itself rather than in the plumbing." }
        default  { return "The run failed for a reason that isn't capacity or credentials. The transcript is in the matching ``*_output.txt``." }
    }
}
