$pu = 'C:\Users\USER\OneDrive\Desktop\nawab_urduverse\static\css\premium-ui.css'
$pp = 'C:\Users\USER\OneDrive\Desktop\nawab_urduverse\static\css\poetry-premium.css'
$style = 'C:\Users\USER\OneDrive\Desktop\nawab_urduverse\static\css\style.css'

# Read contents
$puContent = Get-Content $pu -Raw
$ppContent = Get-Content $pp -Raw
$styleContent = Get-Content $style -Raw

# Step 1: Replace body.site-shell with body.dashboard-shell (scoping body to dashboard only)
$puContent = $puContent -replace 'body\.site-shell', 'body.dashboard-shell'

# Step 2: Prefix all dashboard-specific selectors with .dashboard-shell, skipping at-rules, keyframes, and global element selectors
$inKeyframes = $false
$lines = $puContent -split "`r?`n"
$newLines = @()
foreach ($line in $lines) {
    # Track @keyframes blocks to avoid prefixing keyframe selectors
    if ($inKeyframes) {
        $newLines += $line
        if ($line -match '^\s*\}') { $inKeyframes = $false }
        continue
    }
    if ($line -match '^\s*@keyframes') {
        $inKeyframes = $true
        $newLines += $line
        continue
    }
    # Lines without a '{' are not rule selectors (comments, properties, empty)
    if ($line -notmatch '\{') {
        $newLines += $line
        continue
    }
    # Skip at-rules (@media, @supports, etc.) and global selectors (:root, html, body) – they are handled separately
    if ($line -match '^\s*@' -or $line -match '^\s*(:root|html|body)\b') {
        $newLines += $line
        continue
    }
    # Split selector and after-brace
    $idx = $line.IndexOf('{')
    $selPart = $line.Substring(0, $idx).Trim()
    $afterPart = $line.Substring($idx)  # includes '{' and remainder
    if ([string]::IsNullOrWhiteSpace($selPart)) {
        $newLines += $line
        continue
    }
    # Split comma-separated selector groups
    $groups = $selPart -split ','
    $newGroups = @()
    foreach ($g in $groups) {
        $trim = $g.Trim()
        if ($trim -eq '') { continue }
        if ($trim -match '^body\.') {
            # body selectors (already adjusted)
            $newGroups += $trim
        } elseif ($trim.StartsWith('.dark-mode')) {
            # Combine dark-mode class into the .dashboard-shell selector (since both classes are on <body>)
            $rest = $trim.Substring('.dark-mode'.Length).TrimStart()
            if ($rest -ne '') {
                $newGroups += ".dashboard-shell.dark-mode $rest"
            } else {
                $newGroups += ".dashboard-shell.dark-mode"
            }
        } else {
            $newGroups += ".dashboard-shell $trim"
        }
    }
    $newSel = ($newGroups -join ', ')
    $newLine = "$newSel $afterPart"
    $newLines += $newLine
}
$processedPU = $newLines -join "`n"

# Merge order: original public style.css first, then processed premium-ui, then poetry-premium
$finalContent = $styleContent + "`n`n/* === merged premium-ui (scoped to .dashboard-shell) === */`n`n" + $processedPU + "`n`n/* === merged poetry-premium === === */`n`n" + $ppContent

# Write back to style.css (overwrite)
Set-Content -Path $style -Value $finalContent -Encoding UTF8

# Delete consolidated files
Remove-Item $pu -Force
Remove-Item 'C:\Users\USER\OneDrive\Desktop\nawab_urduverse\static\css\dark-mode.css' -Force -ErrorAction SilentlyContinue
Remove-Item $pp -Force

Write-Host "CSS consolidation complete. Final style.css line count:" ($finalContent -split "`n").Count
