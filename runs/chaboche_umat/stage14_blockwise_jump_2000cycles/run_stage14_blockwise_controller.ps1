param(
    [switch]$SkipAbaqusRuns
)

$ErrorActionPreference = "Stop"

$repo = "D:\TUBAF\Master_Thesis\Abaqus_trial"
$stage14 = Join-Path $repo "runs\chaboche_umat\stage14_blockwise_jump_2000cycles"
$refDir = Join-Path $stage14 "reference_2000cycles"
$logDir = Join-Path $stage14 "_logs"
$summaryCsv = Join-Path $stage14 "STAGE14_BLOCKWISE_SUMMARY.csv"
$reportMd = Join-Path $stage14 "STAGE14_BLOCKWISE_REPORT.md"
$masterLog = Join-Path $logDir "stage14_blockwise_controller.log"

$vsdev = "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat"
$setvars = "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"

$refJob = "chaboche_vp_v1_cyclic_eps005_2000cycles"
$refInp = Join-Path $refDir "$refJob.inp"
$refUmat = Join-Path $refDir "umat_chaboche_v1_with_sdvini_sigini.f"
$refOdb = Join-Path $refDir "$refJob.odb"
$refCsv = Join-Path $refDir "${refJob}_cycle_history.csv"
$refSummary = Join-Path $refDir "STAGE14A_2000CYCLE_REFERENCE_SUMMARY.md"

$strategies = [ordered]@{
    jump25 = @(
        @{ base = 10; target = 500; continue = 510 },
        @{ base = 510; target = 1000; continue = 1010 },
        @{ base = 1010; target = 1500; continue = 1510 },
        @{ base = 1510; target = 1990; continue = 2000 }
    )
    jump37 = @(
        @{ base = 10; target = 740; continue = 750 },
        @{ base = 750; target = 1480; continue = 1490 },
        @{ base = 1490; target = 1990; continue = 2000 }
    )
    jump50 = @(
        @{ base = 10; target = 1000; continue = 1010 },
        @{ base = 1010; target = 1990; continue = 2000 }
    )
    jump65 = @(
        @{ base = 10; target = 1300; continue = 1310 },
        @{ base = 1310; target = 1990; continue = 2000 }
    )
}

New-Item -ItemType Directory -Force $logDir, $refDir | Out-Null

function Write-Log {
    param([string]$Message)
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$stamp] $Message"
    Write-Host $line
    Add-Content -Path $masterLog -Value $line
}

function Assert-Exists {
    param([string]$Path, [string]$Label)
    if (-not (Test-Path $Path)) {
        throw "$Label not found: $Path"
    }
}

function Invoke-AbaqusDatacheck {
    param([string]$CaseDir, [string]$Job, [string]$Inp, [string]$User)
    Write-Log "Running datacheck for $Job"
    $dat = Join-Path $CaseDir "${Job}_datacheck.dat"
    if (Test-Path $dat) {
        $text = Get-Content $dat -Raw
        if ($text -match "ANALYSIS DATACHECK COMPLETE") {
            Write-Log "Existing datacheck already passed for $Job"
            return
        }
    }
    $cmd = "call `"$vsdev`" -arch=amd64 && call `"$setvars`" intel64 && cd /d `"$CaseDir`" && abaqus job=${Job}_datacheck input=$Inp user=$User datacheck interactive ask_delete=OFF scratch=."
    cmd /d /c $cmd | Tee-Object -FilePath (Join-Path $logDir "${Job}_datacheck_console.log")
    Assert-Exists $dat "$Job datacheck .dat"
    $text = Get-Content $dat -Raw
    if ($text -notmatch "ANALYSIS DATACHECK COMPLETE") {
        throw "Datacheck did not complete cleanly for $Job"
    }
}

function Invoke-AbaqusFullRun {
    param([string]$CaseDir, [string]$Job, [string]$Inp, [string]$User)
    Write-Log "Running full Abaqus job for $Job"
    $cmd = "call `"$vsdev`" -arch=amd64 && call `"$setvars`" intel64 && cd /d `"$CaseDir`" && abaqus job=$Job input=$Inp user=$User interactive ask_delete=OFF scratch=."
    cmd /d /c $cmd | Tee-Object -FilePath (Join-Path $logDir "${Job}_full_console.log")
    $sta = Join-Path $CaseDir "$Job.sta"
    Assert-Exists $sta "$Job .sta"
    $text = Get-Content $sta -Raw
    if ($text -notmatch "THE ANALYSIS HAS COMPLETED SUCCESSFULLY") {
        throw "Full run did not complete successfully for $Job"
    }
}

function Invoke-AbaqusPython {
    param([string]$CaseDir, [string]$Script, [string]$Job)
    Write-Log "Running Abaqus Python postprocess for $Job"
    Push-Location $CaseDir
    try {
        abaqus python ".\$Script" | Tee-Object -FilePath (Join-Path $logDir "${Job}_postprocess_console.log")
    }
    finally {
        Pop-Location
    }
}

function Initialize-Summary {
    if (-not (Test-Path $summaryCsv)) {
        "strategy,block_index,base_cycle,target_cycle,continue_to_cycle,delta_N,skipped_intermediate_cycles,recovery_cycles,pre_target_statev1_error_pct,pre_target_s11_error_pct,block_final_statev1_error_pct,block_final_s11_error_pct,block_final_rf1_error_pct,strategy_final_statev1_error_pct,strategy_final_s11_error_pct,strategy_final_rf1_error_pct,outcome,case_dir" |
            Set-Content -Path $summaryCsv -Encoding UTF8
    }
}

function Get-PreErrors {
    param([string]$CaseDir, [int]$TargetCycle)
    $errCsv = Join-Path $CaseDir "cycle${TargetCycle}_predicted_vs_reference_error.csv"
    Assert-Exists $errCsv "pre-target error CSV"
    $rows = Import-Csv $errCsv
    $statev = $rows | Where-Object { $_.quantity -eq "STATEV1" } | Select-Object -First 1
    $s11 = $rows | Where-Object { $_.quantity -eq "S11" } | Select-Object -First 1
    return [PSCustomObject]@{
        Statev1 = [double]$statev.relative_error_percent
        S11 = [double]$s11.relative_error_percent
    }
}

function Get-BlockResult {
    param([string]$CaseDir, [string]$Strategy, [int]$BlockIndex)
    $resultCsv = Join-Path $CaseDir ("stage14_{0}_block{1:00}_result.csv" -f $Strategy, $BlockIndex)
    Assert-Exists $resultCsv "block result CSV"
    return Import-Csv $resultCsv | Select-Object -First 1
}

function Get-Outcome {
    param([double]$StatevErr, [double]$S11Err, [double]$Rf1Err)
    if ($StatevErr -le 1.0 -and $S11Err -le 1.0 -and $Rf1Err -le 1.0) {
        return "accepted_clean_success"
    }
    if ($StatevErr -le 1.0) {
        return "accepted_exploratory_success"
    }
    return "not_accepted"
}

function Append-Summary {
    param(
        [string]$Strategy,
        [int]$BlockIndex,
        [hashtable]$Route,
        [double]$PreStatev,
        [double]$PreS11,
        [double]$BlockStatev,
        [double]$BlockS11,
        [double]$BlockRf1,
        [string]$StrategyStatev,
        [string]$StrategyS11,
        [string]$StrategyRf1,
        [string]$Outcome,
        [string]$CaseDir
    )
    $delta = [int]$Route.target - [int]$Route.base
    $skipped = $delta - 1
    $recovery = [int]$Route.continue - [int]$Route.target
    "$Strategy,$BlockIndex,$($Route.base),$($Route.target),$($Route.continue),$delta,$skipped,$recovery,$PreStatev,$PreS11,$BlockStatev,$BlockS11,$BlockRf1,$StrategyStatev,$StrategyS11,$StrategyRf1,$Outcome,$CaseDir" |
        Add-Content -Path $summaryCsv
}

function Write-Report {
    $rows = @()
    if (Test-Path $summaryCsv) {
        $rows = Import-Csv $summaryCsv
    }
    $refRows = @()
    if (Test-Path $refCsv) {
        $refRows = Import-Csv $refCsv
    }
    $cycle2000 = $refRows | Where-Object { [int]$_.cycle -eq 2000 } | Select-Object -First 1

    $lines = @()
    $lines += "# Stage 14 Blockwise Report"
    $lines += ""
    $lines += "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    $lines += ""
    $lines += "## Purpose"
    $lines += ""
    $lines += "Repeated, re-anchored blockwise cycle-jump controller for a 2000-cycle Chaboche UMAT problem."
    $lines += ""
    $lines += "## Reference Cycle 2000 Values"
    $lines += ""
    if ($cycle2000) {
        $lines += ("- STATEV1: ``{0}``" -f $cycle2000.STATEV1_end)
        $lines += ("- S11: ``{0}``" -f $cycle2000.S11)
        $lines += ("- RF1: ``{0}``" -f $cycle2000.RIGHT_FACE_RF1_SUM)
    } else {
        $lines += "- Pending reference extraction."
    }
    $lines += ""
    $lines += "## Strategy Definitions"
    $lines += ""
    foreach ($name in $strategies.Keys) {
        $routeText = ($strategies[$name] | ForEach-Object { "$($_.base)->$($_.target)->$($_.continue)" }) -join "; "
        $lines += ("- ``{0}``: {1}" -f $name, $routeText)
    }
    $lines += ""
    $lines += "## Block-By-Block Results"
    $lines += ""
    $lines += "| Strategy | Block | Base | Target | Continue | Pre STATEV1 % | Pre S11 % | Final STATEV1 % | Final S11 % | Final RF1 % | Outcome |"
    $lines += "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"
    foreach ($row in $rows) {
        $lines += "| $($row.strategy) | $($row.block_index) | $($row.base_cycle) | $($row.target_cycle) | $($row.continue_to_cycle) | $($row.pre_target_statev1_error_pct) | $($row.pre_target_s11_error_pct) | $($row.block_final_statev1_error_pct) | $($row.block_final_s11_error_pct) | $($row.block_final_rf1_error_pct) | $($row.outcome) |"
    }
    $lines += ""
    $lines += "## Final Cycle 2000 Comparison"
    $lines += ""
    $lines += "| Strategy | STATEV1 % | S11 % | RF1 % | Outcome |"
    $lines += "|---|---:|---:|---:|---|"
    foreach ($name in $strategies.Keys) {
        $final = $rows | Where-Object { $_.strategy -eq $name -and $_.continue_to_cycle -eq "2000" } | Select-Object -Last 1
        if ($final) {
            $lines += "| $name | $($final.strategy_final_statev1_error_pct) | $($final.strategy_final_s11_error_pct) | $($final.strategy_final_rf1_error_pct) | $($final.outcome) |"
        }
    }
    $lines += ""
    $lines += "## Scientific Interpretation"
    $lines += ""
    $lines += "Later blocks use the previous block's actual recovered route history as the prediction base. This tests a true repeated controller rather than independent idealized jumps from the no-skip reference."
    $lines | Set-Content -Path $reportMd -Encoding UTF8
}

function Ensure-Reference {
    Write-Log "Validating Stage 14A reference."
    $refRunBat = Join-Path $refDir "run_2000cycle_reference.bat"
    $refMonitor = Join-Path $refDir "monitor_2000cycle_reference.py"
    $refExtract = Join-Path $refDir "extract_2000cycle_reference_history.py"
    if (-not (Test-Path $refInp) -or -not (Test-Path $refUmat) -or -not (Test-Path $refRunBat) -or -not (Test-Path $refMonitor) -or -not (Test-Path $refExtract)) {
        Write-Log "Generating 2000-cycle reference deck."
        & python (Join-Path $stage14 "make_2000cycle_reference_deck.py") 2>&1 |
            Tee-Object -FilePath (Join-Path $logDir "reference_generate_console.log")
        if ($LASTEXITCODE -ne 0) {
            throw "Reference deck generation failed with exit code $LASTEXITCODE"
        }
    }
    Assert-Exists $refInp "Stage 14A reference input deck"
    Assert-Exists $refUmat "Stage 14A reference UMAT"

    if ($SkipAbaqusRuns) {
        Write-Log "SkipAbaqusRuns set; not launching reference Abaqus job."
        return
    }

    if (-not (Test-Path $refOdb)) {
        Invoke-AbaqusDatacheck -CaseDir $refDir -Job $refJob -Inp "$refJob.inp" -User "umat_chaboche_v1_with_sdvini_sigini.f"
        Invoke-AbaqusFullRun -CaseDir $refDir -Job $refJob -Inp "$refJob.inp" -User "umat_chaboche_v1_with_sdvini_sigini.f"
    }
    if (-not (Test-Path $refCsv)) {
        Invoke-AbaqusPython -CaseDir $refDir -Script "extract_2000cycle_reference_history.py" -Job $refJob
    }

    Assert-Exists $refCsv "Stage 14A reference CSV"
    $rows = Import-Csv $refCsv
    if ($rows.Count -ne 2000) {
        throw "Reference CSV should have 2000 rows, got $($rows.Count)"
    }
    $cycle2000 = $rows | Where-Object { [int]$_.cycle -eq 2000 } | Select-Object -First 1
    if (-not $cycle2000) {
        throw "Reference CSV does not contain cycle 2000"
    }
    Write-Log "Reference CSV validated: 2000 rows."
}

function Invoke-Block {
    param([string]$Strategy, [int]$BlockIndex, [hashtable]$Route)
    $source = if ($BlockIndex -eq 1) { "reference" } else { "previous_block" }
    $caseDir = Join-Path $stage14 ("strategy_{0}\block{1:00}_base{2}_target{3}_to{4}" -f $Strategy, $BlockIndex, $Route.base, $Route.target, $Route.continue)
    $job = "chaboche_stage14_${Strategy}_block$('{0:00}' -f $BlockIndex)_target$($Route.target)_to$($Route.continue)"
    $inp = "$job.inp"
    $user = "umat_chaboche_v1_with_sdvini_sigini_predicted_cycle$($Route.target).f"
    $post = "postprocess_${job}.py"

    Write-Log "Generating $Strategy block $BlockIndex"
    & python (Join-Path $stage14 "make_stage14_block_job.py") `
        --strategy-label $Strategy `
        --block-index $BlockIndex `
        --base-cycle $Route.base `
        --target-cycle $Route.target `
        --continue-to-cycle $Route.continue `
        --repo-root $repo `
        --base-source $source 2>&1 |
        Tee-Object -FilePath (Join-Path $logDir "${Strategy}_block$('{0:00}' -f $BlockIndex)_generate_console.log")
    if ($LASTEXITCODE -ne 0) {
        throw "$Strategy block $BlockIndex generation failed with exit code $LASTEXITCODE"
    }

    if (-not $SkipAbaqusRuns) {
        Invoke-AbaqusDatacheck -CaseDir $caseDir -Job $job -Inp $inp -User $user
        Invoke-AbaqusFullRun -CaseDir $caseDir -Job $job -Inp $inp -User $user
        Invoke-AbaqusPython -CaseDir $caseDir -Script $post -Job $job
    } else {
        Write-Log "SkipAbaqusRuns set; generated $Strategy block $BlockIndex only."
        return
    }

    $pre = Get-PreErrors -CaseDir $caseDir -TargetCycle $Route.target
    $result = Get-BlockResult -CaseDir $caseDir -Strategy $Strategy -BlockIndex $BlockIndex
    $blockStatev = [double]$result.block_final_statev1_error_pct
    $blockS11 = [double]$result.block_final_s11_error_pct
    $blockRf1 = [double]$result.block_final_rf1_error_pct
    $isFinal = ([int]$Route.continue -eq 2000)
    $outcome = if ($isFinal) { Get-Outcome -StatevErr $blockStatev -S11Err $blockS11 -Rf1Err $blockRf1 } else { $result.outcome }
    $strategyStatev = if ($isFinal) { "$blockStatev" } else { "" }
    $strategyS11 = if ($isFinal) { "$blockS11" } else { "" }
    $strategyRf1 = if ($isFinal) { "$blockRf1" } else { "" }

    Append-Summary -Strategy $Strategy -BlockIndex $BlockIndex -Route $Route `
        -PreStatev $pre.Statev1 -PreS11 $pre.S11 `
        -BlockStatev $blockStatev -BlockS11 $blockS11 -BlockRf1 $blockRf1 `
        -StrategyStatev $strategyStatev -StrategyS11 $strategyS11 -StrategyRf1 $strategyRf1 `
        -Outcome $outcome -CaseDir $caseDir
    Write-Report
}

Write-Log "Starting Stage 14 blockwise controller."
Assert-Exists $vsdev "Visual Studio development command"
Assert-Exists $setvars "Intel oneAPI setvars"
Initialize-Summary
Ensure-Reference
Write-Report

if ($SkipAbaqusRuns -and -not (Test-Path $refCsv)) {
    Write-Log "SkipAbaqusRuns set and no reference CSV exists; stopping after reference deck/scaffold generation."
    Write-Log "Run without -SkipAbaqusRuns after the 2000-cycle reference is ready to execute block strategies."
    return
}

foreach ($strategy in $strategies.Keys) {
    Write-Log "Starting strategy $strategy"
    $blockIndex = 1
    foreach ($route in $strategies[$strategy]) {
        Invoke-Block -Strategy $strategy -BlockIndex $blockIndex -Route $route
        $blockIndex += 1
    }
}

Write-Report
Write-Log "Stage 14 blockwise controller finished."
Write-Log "Summary CSV: $summaryCsv"
Write-Log "Report: $reportMd"
