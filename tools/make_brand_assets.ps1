<#
  Build favicons and the social-preview image from the official logo.

      powershell -ExecutionPolicy Bypass -File tools\make_brand_assets.ps1

  Source : assets/brand/kotibhaskar-logo.png   (never modified)
  Writes : favicon-16x16.png, favicon-32x32.png, favicon-48x48.png (temp for .ico),
           apple-touch-icon.png (180x180), favicon.ico (16/32/48),
           assets/brand/og-image.png (1200x630 social preview)
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
  New-Canvas 16 16 1.0 (Join-Path $repo 'favicon-16x16.png')
  New-Canvas 32 32 1.0 (Join-Path $repo 'favicon-32x32.png')
  New-Canvas 48 48 0.96 (Join-Path $repo 'favicon-48x48.png')
  New-Canvas 180 180 0.9 (Join-Path $repo 'apple-touch-icon.png')
  New-Canvas 1200 630 0.55 (Join-Path $repo 'assets\brand\og-image.png')
} finally { $src.Dispose() }

# favicon.ico with embedded PNG images (supported by all current browsers)
$sizes = 16, 32, 48
$pngs = $sizes | ForEach-Object { [IO.File]::ReadAllBytes((Join-Path $repo "favicon-${_}x${_}.png")) }
$ms = New-Object IO.MemoryStream; $bw = New-Object IO.BinaryWriter $ms
$bw.Write([UInt16]0); $bw.Write([UInt16]1); $bw.Write([UInt16]$sizes.Count)
$offset = 6 + 16 * $sizes.Count
for ($k = 0; $k -lt $sizes.Count; $k++) {
  $bw.Write([byte]$sizes[$k]); $bw.Write([byte]$sizes[$k]); $bw.Write([byte]0); $bw.Write([byte]0)
  $bw.Write([UInt16]1); $bw.Write([UInt16]32); $bw.Write([UInt32]$pngs[$k].Length); $bw.Write([UInt32]$offset)
  $offset += $pngs[$k].Length
}
foreach ($p in $pngs) { $bw.Write($p) }
[IO.File]::WriteAllBytes((Join-Path $repo 'favicon.ico'), $ms.ToArray())
$bw.Dispose()
Remove-Item (Join-Path $repo 'favicon-48x48.png')
'Brand assets written: favicon.ico, favicon-16x16.png, favicon-32x32.png, apple-touch-icon.png, assets/brand/og-image.png'
