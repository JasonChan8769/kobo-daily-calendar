# Copies a rendered calendar PNG to a USB-connected Kobo as its sleep-screen image.
# Usage: .\copy-to-kobo.ps1 [-Image out\mock-v3.png]
# It only adds/overwrites ONE file (calendar.png) and never deletes anything.
param([string]$Image = "out\mock-v3.png")

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$src = if ([System.IO.Path]::IsPathRooted($Image)) { $Image } else { Join-Path $here $Image }
if (-not (Test-Path -LiteralPath $src)) { throw "Image not found: $src" }

# A Kobo mounts as a drive with a hidden .kobo folder at its root.
$kobo = Get-PSDrive -PSProvider FileSystem | Where-Object {
  $_.Root -ne "C:\" -and (Test-Path -LiteralPath (Join-Path $_.Root ".kobo"))
} | Select-Object -First 1

if (-not $kobo) {
  Write-Host "No Kobo found. Plug it in with USB, tap 'Connect' on the Kobo screen, wait for the drive to appear, then run this again."
  exit 1
}

$dir = Join-Path $kobo.Root ".kobo\screensaver"
New-Item -ItemType Directory -Force -Path $dir | Out-Null
Copy-Item -LiteralPath $src -Destination (Join-Path $dir "calendar.png") -Force
Write-Host "Copied to $dir\calendar.png"

$others = Get-ChildItem -LiteralPath $dir -File | Where-Object { $_.Name -ne "calendar.png" }
if ($others) {
  Write-Host ""
  Write-Host "Note: the Kobo picks a RANDOM image from this folder. These other files are also there, so the calendar will only show some of the time:"
  $others | ForEach-Object { Write-Host "  $($_.Name)" }
  Write-Host "Move them out if you want the calendar to show every time."
}
Write-Host ""
Write-Host "Next: eject the Kobo from Windows, wait for it to reboot/import, then press the power button to put it to sleep."
