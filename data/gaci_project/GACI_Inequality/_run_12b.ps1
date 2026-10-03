$D = "C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_Inequality"
$S = "C:\Program Files\StataNow19\StataSE-64.exe"
Set-Location $D
$log = Join-Path $D "_run_12b_progress.txt"
"start $(Get-Date -Format s)" | Out-File $log -Encoding utf8
$p = Start-Process -FilePath $S -ArgumentList @("/e","do","12b_gic_stacked.do") -WorkingDirectory $D -Wait -PassThru
"end $(Get-Date -Format s) rc=$($p.ExitCode)" | Add-Content $log -Encoding utf8
