<#
  Build the browser / bookmark / home-screen icons from the official favicon artwork
  (white "K" on navy, owner-supplied 26 Nov 2026).

      powershell -ExecutionPolicy Bypass -File tools\make_favicon.ps1

  Source : product-sources/00 Company Assets/Kotibhaskar Favicon.png(.png)   (local only, never modified)
  Writes : favicon-16x16.png, favicon-32x32.png, favicon-48x48.png,
           apple-touch-icon.png (180x180), android-chrome-192x192.png, android-chrome-512x512.png,
           favicon.ico (16 / 32 / 48), site.webmanifest
  The artwork is square and full-bleed, so every size is a uniform high-quality scale of it:
  nothing is cropped, padded, recoloured or redrawn. Then run tools/build_site.py, which stamps
  the icon links on every page with a content hash so browsers pick up a new icon.
  The main website logo (assets/brand/kotibhaskar-logo.png) is not used or changed here.
#>
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$repo = Split-Path -Parent $PSScriptRoot
$dir = Join-Path $repo 'product-sources\00 Company Assets'
$srcPath = @('Kotibhaskar Favicon.png', 'Kotibhaskar Favicon.png.png') | ForEach-Object { Join-Path $dir $_ } | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $srcPath) { throw "Favicon artwork not found in $dir" }
$src = [System.Drawing.Image]::FromFile($srcPath)
if ($src.Width -ne $src.Height) { $src.Dispose(); throw "Favicon artwork must be square (is $($src.Width)x$($src.Height))" }

function Save-Icon([int]$size, [string]$name) {
  $bmp = New-Object System.Drawing.Bitmap $size, $size, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.InterpolationMode = 'HighQualityBicubic'; $g.SmoothingMode = 'HighQuality'
  $g.PixelOffsetMode = 'HighQuality'; $g.CompositingQuality = 'HighQuality'
  $attr = New-Object System.Drawing.Imaging.ImageAttributes
  $attr.SetWrapMode([System.Drawing.Drawing2D.WrapMode]::TileFlipXY)       # no faded edge pixels when scaling
  $g.DrawImage($src, (New-Object System.Drawing.Rectangle 0, 0, $size, $size), 0, 0, $src.Width, $src.Height, 'Pixel', $attr)
  $bmp.Save((Join-Path $repo $name), [System.Drawing.Imaging.ImageFormat]::Png)
  $attr.Dispose(); $g.Dispose(); $bmp.Dispose()
}
try {
  Save-Icon 16 'favicon-16x16.png'
  Save-Icon 32 'favicon-32x32.png'
  Save-Icon 48 'favicon-48x48.png'
  Save-Icon 180 'apple-touch-icon.png'
  Save-Icon 192 'android-chrome-192x192.png'
  Save-Icon 512 'android-chrome-512x512.png'
} finally { $src.Dispose() }

# favicon.ico with embedded PNG images (16, 32, 48), supported by all current browsers
$sizes = 16, 32, 48
$pngs = New-Object 'System.Collections.Generic.List[byte[]]'     # a typed list: the pipeline would flatten the byte arrays
foreach ($s in $sizes) { $pngs.Add([IO.File]::ReadAllBytes((Join-Path $repo "favicon-${s}x${s}.png"))) }
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

# web app manifest (Android home screen / installed icon); colours from the artwork's navy
$manifest = @'
{
  "name": "Kotibhaskar Industries",
  "short_name": "Kotibhaskar",
  "icons": [
    {"src": "/android-chrome-192x192.png", "sizes": "192x192", "type": "image/png"},
    {"src": "/android-chrome-512x512.png", "sizes": "512x512", "type": "image/png"}
  ],
  "start_url": "/",
  "display": "browser",
  "background_color": "#000A31",
  "theme_color": "#000A31"
}
'@
[IO.File]::WriteAllText((Join-Path $repo 'site.webmanifest'), $manifest.Replace("`r`n", "`n") + "`n", (New-Object System.Text.UTF8Encoding $false))
'Favicons written: favicon.ico (16/32/48), favicon-16x16/32x32/48x48.png, apple-touch-icon.png, android-chrome-192x192/512x512.png, site.webmanifest'
