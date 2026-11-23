<#
  Make web-ready copies of product photos and drawings.

      powershell -ExecutionPolicy Bypass -File tools\optimise_images.ps1 uhmw

  Reads data/products/wheels/<category>.json, opens each product's original
  photo and drawing from product-sources (never modified) and writes:
    <slug>-photo.jpg    900 px wide product photo
    <slug>-thumb.jpg    420 px wide photo for category grids
    <slug>-drawing.jpg  1100 px wide technical drawing (higher quality for line art)
  into the folder named in each product's "images" paths.
  Existing outputs are skipped unless the source is newer (use -Force to redo all).

  Other product families: pass the data file instead of a wheel category, e.g.
      powershell -ExecutionPolicy Bypass -File tools\optimise_images.ps1 -DataFile data\products\trolleys\trolleys.json
  (products without a drawing simply get photo + thumb)
#>
param(
  [string]$Category,
  [string]$DataFile,
  [switch]$Force
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$repo = Split-Path -Parent $PSScriptRoot
if (-not $DataFile) {
  if (-not $Category) { throw 'Pass a wheel category (e.g. uhmw) or -DataFile <path>' }
  $DataFile = "data\products\wheels\$Category.json"
}
$data = Get-Content -Raw -Encoding UTF8 (Join-Path $repo $DataFile) | ConvertFrom-Json
$jpeg = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/jpeg' }

function Save-Resized([string]$src, [string]$dest, [int]$width, [long]$quality) {
  if (-not $Force -and (Test-Path -LiteralPath $dest) -and ((Get-Item -LiteralPath $dest).LastWriteTime -ge (Get-Item -LiteralPath $src).LastWriteTime)) { return 'skip' }
  $img = [System.Drawing.Image]::FromFile($src)
  try {
    $w = [Math]::Min($width, $img.Width)
    $h = [int][Math]::Round($img.Height * $w / $img.Width)
    $bmp = New-Object System.Drawing.Bitmap $w, $h
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.Clear([System.Drawing.Color]::White)   # flatten any transparency onto white
    $g.InterpolationMode = 'HighQualityBicubic'; $g.SmoothingMode = 'HighQuality'; $g.PixelOffsetMode = 'HighQuality'
    $g.DrawImage($img, 0, 0, $w, $h)
    $p = New-Object System.Drawing.Imaging.EncoderParameters 1
    $p.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter ([System.Drawing.Imaging.Encoder]::Quality), $quality
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dest) | Out-Null
    $bmp.Save($dest, $jpeg, $p)
    $g.Dispose(); $bmp.Dispose()
  } finally { $img.Dispose() }
  return 'made'
}

$made = 0; $skipped = 0
foreach ($p in $data.products) {
  $jobs = @(
    @($p.source.photo,   $p.images.photo,   900,  82),
    @($p.source.photo,   $p.images.thumb,   420,  78)
  )
  if ($p.source.drawing) { $jobs += ,@($p.source.drawing, $p.images.drawing, 1100, 86) }
  foreach ($j in $jobs) {
    $src = Join-Path $repo ($j[0] -replace '/', '\')
    $dest = Join-Path $repo (($j[1].TrimStart('/')) -replace '/', '\')
    if (-not (Test-Path -LiteralPath $src)) { throw "Missing source image for $($p.code): $src" }
    if ((Save-Resized $src $dest $j[2] $j[3]) -eq 'made') { $made++ } else { $skipped++ }
  }
}
$outDir = Split-Path -Parent (Join-Path $repo (($data.products[0].images.photo.TrimStart('/')) -replace '/', '\'))
$total = (Get-ChildItem $outDir -File | Measure-Object Length -Sum)
"{0} images written, {1} up to date. Folder now holds {2} files, {3:N1} MB." -f $made, $skipped, $total.Count, ($total.Sum / 1MB)
