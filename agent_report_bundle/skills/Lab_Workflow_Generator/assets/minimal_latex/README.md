# 最小 LaTeX 模板

用途：把编译器、字体、文档类和章节编号拆开检查，再把论文正文逐段迁入独立的 `main.tex`。这是一份诊断模板，不属于实验报告模板 01—06，也不替代报告内容要求。

## 使用

需要包含中文支持的 TeX Live 或 MiKTeX；本机验证使用 TeX Live 2025。字体包为 Fandol 和 Latin Modern，文档类为 ctexart，另需 iftex、geometry、amsmath。文件保存为 UTF-8。

将整个目录复制到可写位置，在 PowerShell 中运行：

```powershell
# 可从任意当前目录调用；路径含空格也可使用。
& "C:\完整路径\minimal_latex\build.ps1" -Verify
```

`-Verify` 依次检查 `01_engine.tex`（英文、编译器和 PDF 输出）、`02_fonts.tex`（中文类及字体）、`03_sections.tex`（编号与引用），最后编译 `main.tex`。每个文件编译两次。以后只编译正文时省略 `-Verify`。

最终文件为本目录下的 `main.pdf`；日志、辅助文件和诊断 PDF 位于 `build/run-<唯一标识>/`。每次使用新目录，任一编译失败立即停止，保留日志；只有全部步骤成功才更新 `main.pdf`。失败时旧的 `main.pdf` 可能仍在，应以脚本成功提示为准。脚本无需 Perl、latexmk、BibTeX 或外部图片。若本机禁止运行 PowerShell 脚本，可在本目录直接编译：

```powershell
New-Item -ItemType Directory -Path build -Force | Out-Null
xelatex -no-shell-escape -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=build main.tex
# 确认上一条退出码为 0 后再运行第二遍：
xelatex -no-shell-escape -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=build main.tex
```

手工方式的 PDF 位于 `build/main.pdf`。命令行输入文件使用 `main.tex` 或正斜线路径，避免将 Windows 反斜线路径误读为 TeX 命令。编辑器应选择 XeLaTeX，主文件应为 `main.tex`；文件首行的编辑器提示不能替代实际引擎选择。

## 修改与报错对应

| 修改 | 解决的症状或报错 | 验证方法 |
| --- | --- | --- |
| 明确使用 XeLaTeX，并通过 `iftex` 提前检查 | 用 pdfLaTeX 编译含 fontspec 的中文文档时出现 `fontspec requires either XeTeX or LuaTeX`；引擎不匹配 | 英文最小文件输出 PDF；误用 pdfLaTeX 时明确报引擎要求 |
| 使用 `ctexart[fontset=fandol]`，英文选用 Latin Modern | `The font "..." cannot be found`；系统缺少宋体、微软雅黑或 Times New Roman；中文缺字 | 检查字体可定位、中文/英文/粗斜体正常显示、日志无缺字或字体替换警告 |
| 用标准 ctexart 文档类，不加载 thuemp.cls 及旧排版文件 | 自定义类、共享输入、校徽、文献等依赖缺失时的 `File ... not found`；减少定位时的干扰 | `main.tex` 单独复制后也能编译 |
| 保留标准章节命令；使用无星号 section/subsection；设 `secnumdepth=2`、阿拉伯编号并清空中文前后缀 | `section*` 不编号、编号深度不足、中文编号/标点与期望不符；report/book 中无 chapter 时可能出现的 `0.1` | PDF 及 aux 中为 `1`、`1.1`、`2`，引用与标题一致 |
| 以脚本目录为工作目录，先创建输出目录，检查退出码与非空 PDF | 找不到主文件、无法写入输出目录、失败后误读旧 PDF，或成功后找错输出位置 | 从其他当前目录运行脚本，确认最终 PDF 的路径与本轮日志 |
| 连续编译两次，检查第二遍日志 | 初次编译出现 `Reference ... undefined`、引用显示 `??` | 第二遍没有未定义引用，公式引用显示 `(1)` |

表中的错误文本是对应问题的典型表现，不是对缺失历史日志的转述。当前源码可确认：`../thu_template/thuemp.cls` 指定 `Times New Roman` 并自定义章节命令；正式模板 06 使用 ctex 自动字体选择；正式模板通常还须连同共享文件部署。这些依赖在本模板中被移除，但不能仅凭它们断言旧项目的真实故障原因。

Fandol 是发行版字体，并非凭空内置；若 `kpsewhich FandolSong-Regular.otf` 无输出，应安装缺失包。只有一级、二级标题参与编号；三级标题默认不编号。不需要编号的摘要可单独使用 `section*`。

## 验证后迁回正文

先保持文档类、字体及章节设置不变，迁入纯文字并编译；再依次加入公式、图片、表格和文献，每步检查日志。不要整段复制旧导言区。本文中的公式与文字仅用于排版检查，不是实验数据或论文内容。

编译生成的 PDF、build 目录和临时检查文件仅供本地使用，不进入通用模板包。

## 本机验证

2026-11-05，TeX Live 2025 / XeLaTeX：三个分项文件和最终模板均编译两遍通过；最终 PDF 为一页 A4。已核对中文、英文、粗斜体、公式、字体嵌入及 1、1.1、2 的标题和引用；第二遍日志无缺字、字体替换、溢出或未定义引用。误用 pdfLaTeX 时明确提示需要 XeTeX，退出且不生成 PDF。已渲染并查看整页。项目自动版面检查为 FATAL 0、WARN 1：短文档的正文宽度估计误把右侧公式编号判为越界，人工确认该编号在页内且无重叠。
