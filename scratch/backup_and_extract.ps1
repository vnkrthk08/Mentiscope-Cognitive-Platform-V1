$src = "c:\Users\venka\Desktop\trail iitm\mentiscope-processing-speed-live-integration"
$dest = "c:\Users\venka\Desktop\trail iitm\mentiscope-processing-speed-live-integration (checkpoint-A-working-VINAY)"
$zipPath = "C:\Users\venka\Desktop\trail iitm\V3\mentiscope-capsule-main.zip"
$extractDest = "c:\Users\venka\Desktop\trail iitm\mentiscope-capsule-main (friend-integrated)"

# 1. Create backup of current workspace (excluding node_modules and dist)
if (Test-Path $dest) {
    Remove-Item $dest -Recurse -Force
}
New-Item -ItemType Directory -Path $dest -Force | Out-Null

Get-ChildItem -Path $src -Recurse | Where-Object { 
    $_.FullName -notmatch "node_modules" -and 
    $_.FullName -notmatch "dist" 
} | ForEach-Object {
    $targetPath = $_.FullName -replace [regex]::Escape($src), $dest
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
Write-Output "Backup created successfully at: $dest"

# 2. Extract the friend's zip file
if (Test-Path $extractDest) {
    Remove-Item $extractDest -Recurse -Force
}
New-Item -ItemType Directory -Path $extractDest -Force | Out-Null

Expand-Archive -Path $zipPath -DestinationPath $extractDest -Force
Write-Output "Friend's zip file extracted successfully to: $extractDest"
