# Copies the calendar "Update" add-on onto a USB-connected Kobo that already has NickelMenu.
# Usage: .\install-kobo-addon.ps1 -Url https://raw.githubusercontent.com/OWNER/REPO/output/today.png
# Adds only: .adds\calendar\update.sh and .adds\nm\calendar. Nothing is deleted or overwritten elsewhere.
param([Parameter(Mandatory = $true)][string]$Url)

if ($Url -notmatch '^https://[A-Za-z0-9._~/%?=&:@+-]+$') {
  throw "URL must start with https:// and contain only plain URL characters."
}
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

$kobo = Get-PSDrive -PSProvider FileSystem | Where-Object {
  $_.Root -ne "C:\" -and (Test-Path -LiteralPath (Join-Path $_.Root ".kobo"))
} | Select-Object -First 1
if (-not $kobo) { throw "No Kobo found. Plug it in, tap Connect, and try again." }

$nm = Join-Path $kobo.Root ".adds\nm"
if (-not (Test-Path -LiteralPath $nm)) {
  throw "NickelMenu is not installed on this Kobo yet (no .adds\nm folder). Install it first, then rerun."
}

# The Kobo shell needs LF line endings, so write both files with LF and no BOM.
$utf8 = New-Object System.Text.UTF8Encoding($false)
function Write-Lf($path, $text) { [System.IO.File]::WriteAllText($path, ($text -replace "`r`n", "`n"), $utf8) }

$addon = Join-Path $kobo.Root ".adds\calendar"
New-Item -ItemType Directory -Force -Path $addon | Out-Null
$sh = (Get-Content -LiteralPath (Join-Path $here "kobo\update.sh") -Raw).Replace("@@CALENDAR_URL@@", $Url)
Write-Lf (Join-Path $addon "update.sh") $sh
Write-Lf (Join-Path $nm "calendar") (Get-Content -LiteralPath (Join-Path $here "kobo\calendar.nm") -Raw)

Write-Host "Installed:"
Write-Host "  $addon\update.sh   (downloads $Url)"
Write-Host "  $nm\calendar   (adds 'Update calendar' and 'Calendar status' to the NickelMenu main menu)"
Write-Host "Eject the Kobo, then look for those entries in the NickelMenu menu."
