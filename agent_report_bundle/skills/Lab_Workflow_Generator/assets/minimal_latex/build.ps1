[CmdletBinding()]
param([switch]$Verify)

$ErrorActionPreference = 'Stop'
$compiler = Get-Command xelatex -ErrorAction SilentlyContinue
if (-not $compiler) {
    throw 'XeLaTeX was not found. Install TeX Live or MiKTeX and add its bin directory to PATH.'
}

Push-Location -LiteralPath $PSScriptRoot
try {
    # A fresh directory prevents an old PDF or auxiliary file from hiding a failure.
    $runId = 'run-' + [guid]::NewGuid().ToString('N')
    $runDir = Join-Path $PSScriptRoot ('build/' + $runId)
    New-Item -ItemType Directory -Path $runDir -Force | Out-Null
    $sources = @('main.tex')
    if ($Verify) {
        $sources = @('checks/01_engine.tex', 'checks/02_fonts.tex', 'checks/03_sections.tex', 'main.tex')
    }
    foreach ($source in $sources) {
        $name = [System.IO.Path]::GetFileNameWithoutExtension($source)
        $targetDir = Join-Path $runDir $name
        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        $compilerArgs = @('-no-shell-escape', '-interaction=nonstopmode', '-halt-on-error',
                          '-file-line-error', ('-output-directory=' + $targetDir), $source)
        for ($pass = 1; $pass -le 2; $pass++) {
            $consoleFile = Join-Path $targetDir ('pass-' + $pass + '.txt')
            & $compiler.Source @compilerArgs *> $consoleFile
            if ($LASTEXITCODE -ne 0) {
                Get-Content -LiteralPath $consoleFile -Tail 30 | Write-Host
                throw "XeLaTeX failed: $source, pass $pass. See $consoleFile"
            }
        }
        $pdf = Join-Path $targetDir ($name + '.pdf')
        if (-not (Test-Path -LiteralPath $pdf) -or (Get-Item -LiteralPath $pdf).Length -eq 0) {
            throw "XeLaTeX returned without a nonempty PDF: $pdf"
        }
        $log = Get-Content -LiteralPath (Join-Path $targetDir ($name + '.log')) -Raw
        if ($log -match '(?m)^!|Missing character:|LaTeX Font Warning:|Package fontspec Warning:|Overfull \\[hv]box|LaTeX Warning:.*(undefined|Rerun)|Label\(s\) may have changed') {
            throw "Compilation has unresolved warnings. See $targetDir/$name.log"
        }
        if ($source -eq 'checks/03_sections.tex') {
            $aux = Get-Content -LiteralPath (Join-Path $targetDir ($name + '.aux')) -Raw
            foreach ($expected in @('\newlabel{sec:first}{{1}', '\newlabel{sec:sub}{{1.1}', '\newlabel{sec:second}{{2}')) {
                if (-not $aux.Contains($expected)) { throw "Unexpected section numbering: $expected" }
            }
        }
        Write-Host "PASS: $source -> $pdf"
    }
    $finalPdf = Join-Path $PSScriptRoot 'main.pdf'
    Copy-Item -LiteralPath (Join-Path $runDir 'main/main.pdf') -Destination $finalPdf -Force
    Write-Host "PDF ready: $finalPdf"
    Write-Host "Logs: $runDir"
}
finally {
    Pop-Location
}
