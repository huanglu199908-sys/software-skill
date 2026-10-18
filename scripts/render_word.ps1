param(
    [Parameter(Mandatory=$true)][string]$Document,
    [Parameter(Mandatory=$true)][string]$OutDir
)
# Refresh and paginate copies only. Never attach to or kill the user's Word.
$ErrorActionPreference = 'Stop'
$outputPath = [IO.Path]::GetFullPath($OutDir)
if (Test-Path -LiteralPath $outputPath) { throw 'OutDir must not exist; preserve previous evidence.' }
$resolvedDocs = @((Resolve-Path -LiteralPath $Document).Path)
$names = @($resolvedDocs | ForEach-Object { [IO.Path]::GetFileName($_) })
if (($names | Select-Object -Unique).Count -ne $names.Count) { throw 'Duplicate document filenames.' }
New-Item -ItemType Directory -Path $outputPath | Out-Null
$word = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.AutomationSecurity = 3
    $engineVersion = $word.Version
    foreach ($sourcePath in $resolvedDocs) {
        if ([IO.Path]::GetExtension($sourcePath) -ne '.docx') { throw 'Only explicit DOCX inputs are supported.' }
        $sourceHash = (Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash.ToLowerInvariant()
        $targetPath = Join-Path $outputPath ([IO.Path]::GetFileName($sourcePath))
        Copy-Item -LiteralPath $sourcePath -Destination $targetPath
        $doc = $null
        try {
            $doc = $word.Documents.Open($targetPath, $false, $false, $false)
            $doc.Fields.Update() | Out-Null
            foreach ($story in $doc.StoryRanges) { $story.Fields.Update() | Out-Null }
            foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
            $doc.Repaginate()
            $doc.Fields.Update() | Out-Null
            foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
            $doc.Repaginate()
            $doc.Saved = $false
            $doc.Save()
            $pageCount = $doc.ComputeStatistics(2)
            $pages = @()
            for ($i = 1; $i -le $pageCount; $i++) {
                $startRange = $doc.GoTo(1, 1, $i)
                $pageStart = $startRange.Start
                if ($i -lt $pageCount) { $pageEnd = $doc.GoTo(1, 1, ($i+1)).Start } else { $pageEnd = $doc.Content.End }
                $range = $doc.Range($pageStart, $pageEnd)
                $pages += [ordered]@{page=$i; visual_lines=$range.ComputeStatistics(1); inline_images=$range.InlineShapes.Count}
            }
            $headings = @()
            $codeRows = @()
            foreach ($para in $doc.Paragraphs) {
                $paraText = $para.Range.Text.TrimEnd([char]13, [char]7)
                $probe = $doc.Range($para.Range.Start, [Math]::Min($para.Range.Start+1, $doc.Content.End))
                $page = $probe.Information(3)
                if ($para.OutlineLevel -le 2) { $headings += [ordered]@{title=$paraText; page=$page} }
                if ($paraText -match '^(\d{2}) (.*)$') {
                    $codeRows += [ordered]@{page=$page; number=[int]$Matches[1]; nonblank=([bool]$Matches[2].Trim()); visual_lines=$para.Range.ComputeStatistics(1)}
                }
            }
            $pdfPath = [IO.Path]::ChangeExtension($targetPath, '.pdf')
            $doc.ExportAsFixedFormat($pdfPath, 17)
            $doc.Close(0)
            $doc = $null
            $record = [ordered]@{
                engine='Microsoft Word'; engine_version=$engineVersion; source_sha256=$sourceHash
                refreshed_docx_sha256=(Get-FileHash -LiteralPath $targetPath -Algorithm SHA256).Hash.ToLowerInvariant()
                pdf_sha256=(Get-FileHash -LiteralPath $pdfPath -Algorithm SHA256).Hash.ToLowerInvariant()
                actual_pages=$pageCount; pages=$pages; headings=$headings; code_rows=$codeRows
                limits='Visual-line statistics require per-page classification and full-page review; they do not establish legal compliance.'
            }
            $record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath ([IO.Path]::ChangeExtension($targetPath, '.layout.json')) -Encoding UTF8
            Write-Output ([PSCustomObject]@{document=[IO.Path]::GetFileName($targetPath); actual_pages=$pageCount; output=$outputPath} | ConvertTo-Json -Compress)
        } finally {
            if ($null -ne $doc) { $doc.Close(0) }
        }
    }
} finally {
    if ($null -ne $word) {
        try { $word.Quit() } catch {
            if ($_.Exception.HResult -ne -2147023174) { Write-Warning 'Word cleanup was unavailable; no existing user process was terminated.' }
        }
        [Runtime.InteropServices.Marshal]::FinalReleaseComObject($word) | Out-Null
    }
}
