param([string]$src, [string]$out, [string]$only = "")
New-Item -ItemType Directory -Force $out | Out-Null
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($src, $true, $false, $false)
$n = $pres.Slides.Count
$list = if ($only -ne "") { $only.Split(",") | ForEach-Object { [int]$_ } } else { 1..$n }
foreach ($i in $list) { $pres.Slides($i).Export("$out\s$('{0:D2}' -f $i).png", "PNG", 1600, 900) }
$pres.Close()
"exported $($list.Count) of $n"
