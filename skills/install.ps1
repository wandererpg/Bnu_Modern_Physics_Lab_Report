<#
.SYNOPSIS
    把「近物实验报告自动化工作流」的两个 Skill 安装到用户级 skills 目录。

.DESCRIPTION
    复制 skills/Lab_Workflow_Generator 与 skills/advanced_lab_report_gen 到
    ~/.codex/skills/（Windows: %USERPROFILE%\.codex\skills\）。
    目标已存在同名 Skill 时：默认跳过（不覆盖），加 -Force 则先备份为
    "<名称>.bak-<时间戳>" 再覆盖。

.PARAMETER SkillsDir
    目标 skills 目录，默认 "$HOME\.codex\skills"。

.PARAMETER Force
    覆盖已存在的同名 Skill（覆盖前自动备份）。

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\install.ps1

.EXAMPLE
    .\install.ps1 -SkillsDir D:\my\skills -Force
#>
[CmdletBinding()]
param(
    [string]$SkillsDir = (Join-Path $HOME ".codex\skills"),
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# —— 控制台编码：脚本与提示含中文，避免乱码 ——
try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
} catch { }

$pkgRoot = $PSScriptRoot
$srcRoot = $pkgRoot   # 本目录即 skill 目录
$names = @("Lab_Workflow_Generator", "advanced_lab_report_gen")

Write-Host ""
Write-Host "近物实验报告自动化工作流 —— 安装 Skill" -ForegroundColor Cyan
Write-Host "  源目录  : $srcRoot"
Write-Host "  目标目录: $SkillsDir"
Write-Host ""

if (-not (Test-Path -LiteralPath $srcRoot)) {
    Write-Host "[FAIL] 找不到 $srcRoot —— 请在仓库的 skills 目录下运行本脚本。" -ForegroundColor Red
    exit 1
}

foreach ($n in $names) {
    if (-not (Test-Path -LiteralPath (Join-Path $srcRoot $n))) {
        Write-Host "[FAIL] 缺少 skill 目录：skills\$n" -ForegroundColor Red
        exit 1
    }
}

if (-not (Test-Path -LiteralPath $SkillsDir)) {
    New-Item -ItemType Directory -Force -Path $SkillsDir | Out-Null
    Write-Host "[NEW ] 已创建 $SkillsDir"
}

$installed = @()
$skipped = @()

foreach ($n in $names) {
    $src = Join-Path $srcRoot $n
    $dst = Join-Path $SkillsDir $n
    if (Test-Path -LiteralPath $dst) {
        if (-not $Force) {
            Write-Host "[SKIP] 已存在：$dst（要覆盖请加 -Force，覆盖前会自动备份）" -ForegroundColor Yellow
            $skipped += $n
            continue
        }
        $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
        $bak = "$dst.bak-$stamp"
        Move-Item -LiteralPath $dst -Destination $bak
        Write-Host "[BAK ] 旧版本已备份 -> $bak" -ForegroundColor DarkGray
    }
    Copy-Item -LiteralPath $src -Destination $dst -Recurse -Force

    # 清掉 Python 缓存，避免跨机器/跨版本复用
    Get-ChildItem -LiteralPath $dst -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue |
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

    $count = (Get-ChildItem -LiteralPath $dst -Recurse -File | Measure-Object).Count
    Write-Host ("[OK  ] {0}  ->  {1}  （{2} 个文件）" -f $n, $dst, $count) -ForegroundColor Green
    $installed += $n
}

Write-Host ""
Write-Host "下一步：" -ForegroundColor Cyan
Write-Host "  1) 新开一个会话（Skill 列表在会话启动时加载，不重启看不到）；"
Write-Host "  2) 自检环境： python `"$pkgRoot\verify_install.py`" --skills-dir `"$SkillsDir`""
Write-Host "  3) 端到端冒烟测试： python `"$pkgRoot\verify_install.py`" --demo"
Write-Host ""
if ($skipped.Count -gt 0) {
    Write-Host ("注意：{0} 未安装（已存在同名目录）。" -f ($skipped -join "、")) -ForegroundColor Yellow
}
Write-Host "安装完成：$($installed.Count) 个 Skill。" -ForegroundColor Green
exit 0
