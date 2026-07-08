$job = "chaboche_eps005_20cycles_dtmax_0p005_inc6000"
$wd = "D:\TUBAF\Master_Thesis\Abaqus_trial\runs\chaboche_umat"
Set-Location $wd
Out-File -FilePath "monitor_$job.log" -InputObject "Monitor started at $(Get-Date) for $job"
while ($true) {
    Start-Sleep -Seconds 30
    $msg = ""
    $dat = ""
    if (Test-Path "$job.msg") { $msg = Get-Content "$job.msg" -Tail 400 -Raw }
    if (Test-Path "$job.dat") { $dat = Get-Content "$job.dat" -Tail 400 -Raw }

    if ($msg -match "THE ANALYSIS HAS BEEN COMPLETED" -or $dat -match "THE ANALYSIS HAS BEEN COMPLETED") {
        Out-File -FilePath "monitor_$job.log" -InputObject "COMPLETED detected at $(Get-Date)" -Append
        & .\abaqus_env.bat python extract_increment_sensitivity_baseline.py $job 2>&1 | Out-File -FilePath "monitor_$job.log" -Append
        Out-File -FilePath "monitor_$job.log" -InputObject "Postprocess finished at $(Get-Date)" -Append
        exit 0
    }

    if ($msg -match "\*\*\*ERROR: TOO MANY INCREMENTS NEEDED TO COMPLETE THE STEP" -or $dat -match "\*\*\*ERROR: TOO MANY INCREMENTS NEEDED TO COMPLETE THE STEP") {
        Out-File -FilePath "monitor_$job.log" -InputObject "TOO MANY INCREMENTS detected at $(Get-Date)" -Append
        if (Test-Path "$job.sta") { Get-Content "$job.sta" -Tail 200 | Out-File -FilePath "monitor_${job}_sta_tail.log" -Append }
        if (Test-Path "$job.msg") { Get-Content "$job.msg" -Tail 400 | Out-File -FilePath "monitor_${job}_msg_tail.log" -Append }
        $odbExists = Test-Path "$job.odb"
        Out-File -FilePath "monitor_$job.log" -InputObject ("ODB exists: " + $odbExists) -Append
        # create inc9000 input by copying and replacing INC value
        $src = "increment_sensitivity_study\\chaboche_eps005_20cycles_dtmax_0p005_inc6000.inp"
        $dst = "increment_sensitivity_study\\chaboche_eps005_20cycles_dtmax_0p005_inc9000.inp"
        if (Test-Path $src) {
            (Get-Content $src) -replace 'INC=6000','INC=9000' | Set-Content $dst
            Out-File -FilePath "monitor_$job.log" -InputObject "Created $dst" -Append
            # run datacheck for inc9000 (job name with _check suffix)
            & .\abaqus_env.bat job=chaboche_eps005_20cycles_dtmax_0p005_inc9000_check input=$dst user=umat\chaboche_vp_v1_working.f interactive 2>&1 | Out-File -FilePath "monitor_$job.log" -Append
        } else {
            Out-File -FilePath "monitor_$job.log" -InputObject "Source inp not found: $src" -Append
        }
        exit 2
    }

    if ($msg -match "WARNING" -or $dat -match "WARNING") {
        Out-File -FilePath "monitor_$job.log" -InputObject "WARNING detected at $(Get-Date) -- saving tails" -Append
        if ($msg -match "WARNING") { Get-Content "$job.msg" -Tail 400 | Out-File -FilePath "monitor_${job}_warnings.log" -Append }
        if ($dat -match "WARNING") { Get-Content "$job.dat" -Tail 400 | Out-File -FilePath "monitor_${job}_warnings.log" -Append }
        # continue waiting for final completion or error
    }
}
