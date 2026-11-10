# Renders template.html to a 1264x1680 PNG using headless Edge (no extra installs).
# Usage: .\render.ps1 [-Template template-simple.html] [-Out out\mock.png]
param([string]$Template = "template-simple.html", [string]$Out = "out\mock.png")

$edge = @(
  "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
  "C:\Program Files\Microsoft\Edge\Application\msedge.exe",
  "C:\Program Files\Google\Chrome\Application\chrome.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $edge) { throw "No Edge/Chrome found" }

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$html = "file:///" + ((Join-Path $here $Template) -replace '\\','/')
$outPath = if ([System.IO.Path]::IsPathRooted($Out)) { $Out } else { Join-Path $here $Out }
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $outPath) | Out-Null

& $edge --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 `
  --window-size=1264,1680 --virtual-time-budget=4000 "--screenshot=$outPath" $html | Out-Null
Start-Sleep -Milliseconds 500
if (Test-Path $outPath) {
  Add-Type -AssemblyName System.Drawing
  $img = [System.Drawing.Image]::FromFile($outPath)
  "Rendered $outPath  ($($img.Width)x$($img.Height))"
  $img.Dispose()
} else { throw "Screenshot not created" }
