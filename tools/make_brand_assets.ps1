<#
  Build the social-preview image from the official logo.
  (Browser / bookmark icons come from the owner's K favicon artwork: tools/make_favicon.ps1.)

      powershell -ExecutionPolicy Bypass -File tools\make_brand_assets.ps1

  Source : assets/brand/kotibhaskar-logo.png   (never modified)
  Writes : assets/brand/og-image.png (1200x630 social preview)
  The logo is always scaled uniformly (aspect ratio preserved) and centred on white.
  Re-run this if a higher-resolution logo replaces the source file.
#>
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$repo = Split-Path -Parent $PSScriptRoot
$src = [System.Drawing.Image]::FromFile((Join-Path $repo 'assets\brand\kotibhaskar-logo.png'))

function New-Canvas([int]$w, [int]$h, [double]$maxLogoWidthFraction, [string]$out) {
  $bmp = New-Object System.Drawing.Bitmap $w, $h
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.Clear([System.Drawing.Color]::White)
  $g.InterpolationMode = 'HighQualityBicubic'; $g.SmoothingMode = 'HighQuality'; $g.PixelOffsetMode = 'HighQuality'
  $scale = [Math]::Min(($w * $maxLogoWidthFraction) / $src.Width, ($h * 0.9) / $src.Height)
  $lw = [int][Math]::Round($src.Width * $scale); $lh = [int][Math]::Round($src.Height * $scale)
  $g.DrawImage($src, [int](($w - $lw) / 2), [int](($h - $lh) / 2), $lw, $lh)
  $bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $bmp.Dispose()
}
try {
  New-Canvas 1200 630 0.55 (Join-Path $repo 'assets\brand\og-image.png')
} finally { $src.Dispose() }

'Brand asset written: assets/brand/og-image.png'
