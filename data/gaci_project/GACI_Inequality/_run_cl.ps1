$D = "C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_Inequality"
$S = "C:\Program Files\StataNow19\StataSE-64.exe"
Set-Location $D
$log = Join-Path $D "_run_cl_progress.txt"
"start $(Get-Date -Format s)" | Out-File $log -Encoding utf8
foreach ($f in @("01_main_cl","02_hetero_cl","03_conc_mech_cl","04_longdiff_cl","05_robust_cl","06_tails_cl","07_diag_cl","09_gdp_cl")) {
    "$f begin $(Get-Date -Format s)" | Add-Content $log -Encoding utf8
    $p = Start-Process -FilePath $S -ArgumentList @("/e","do","$f.do") -WorkingDirectory $D -Wait -PassThru
    "$f end $(Get-Date -Format s) rc=$($p.ExitCode)" | Add-Content $log -Encoding utf8
}
"done $(Get-Date -Format s)" | Add-Content $log -Encoding utf8
