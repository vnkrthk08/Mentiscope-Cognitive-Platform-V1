$src = "c:\Users\venka\Desktop\trail iitm\mentiscope-capsule-main (friend-integrated)\mentiscope-capsule-main"
$destDir = "c:\Users\venka\Desktop\trail iitm\temp_build_zip_integrated"
$zipPath = "c:\Users\venka\Desktop\mentiscope-capsule-integrated.zip"

if (Test-Path $destDir) { 
    Remove-Item $destDir -Recurse -Force 
}
New-Item -ItemType Directory -Path $destDir -Force | Out-Null

Get-ChildItem -Path $src -Recurse | Where-Object { 
    $_.FullName -notmatch "node_modules" -and 
    $_.FullName -notmatch "dist" -and 
    $_.FullName -notmatch "\\\.git" -and 
    $_.FullName -notmatch "\\\.gemini" -and 
    $_.FullName -notmatch "scratch" -and 
    $_.FullName -notmatch "temp_build_zip_integrated" 
} | ForEach-Object {
    $targetPath = $_.FullName -replace [regex]::Escape($src), $destDir
    if ($_.PsIsContainer) {
        New-Item -ItemType Directory -Path $targetPath -Force | Out-Null
    } else {
        $parentDir = Split-Path $targetPath
        if (-not (Test-Path $parentDir)) { 
            New-Item -ItemType Directory -Path $parentDir -Force | Out-Null 
        }
        Copy-Item -Path $_.FullName -Destination $targetPath -Force
    }
}

if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}

Compress-Archive -Path "$destDir\*" -DestinationPath $zipPath -Force
Remove-Item $destDir -Recurse -Force
Write-Output "Zip file successfully created at: $zipPath"
