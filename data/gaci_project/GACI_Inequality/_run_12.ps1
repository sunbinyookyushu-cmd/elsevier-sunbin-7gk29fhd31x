$D = "C:\Users\sunbi\managi-lab Dropbox\Sunbin Yoo\Research Box ^-^\2026\GACI\GACI_Inequality"
$p = Start-Process -FilePath "C:\Program Files\StataNow19\StataSE-64.exe" -ArgumentList @("/e","do","12_gic_dose.do") -WorkingDirectory $D -Wait -PassThru
"rc=$($p.ExitCode)"
