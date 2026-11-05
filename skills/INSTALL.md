# 安装指南

面向 Windows / macOS / Linux 的分步安装。装完全部约 5 分钟（不含 LaTeX 发行版下载）。

## 0. 前置检查

```bash
python -V                     # 需 3.11 或更高
xelatex --version             # 需 TeX Live 2023+ 或 MiKTeX
kpsewhich FandolSong-Regular.otf # 中文正文使用发行版自带 Fandol
kpsewhich lmroman10-regular.otf  # 英文正文使用发行版自带 Latin Modern
```

任何一条失败，先按下面对应小节安装。

## 1. Python 与库

```bash
python -m pip install -r requirements.txt
```

`requirements.txt`：`numpy scipy matplotlib pandas PyMuPDF`。

Windows 若 `python` 指向 Microsoft Store 占位符（运行后弹出商店），改用启动器或全路径：

```powershell
py -m pip install -r requirements.txt
# 或
& "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe" -m pip install -r requirements.txt
```

> **中文路径警告**：本机实测，`py` 启动器在含中文的**脚本路径或参数**下可能直接返回
> `9009`（命令未找到）。因此文档里的示例统一使用解释器全路径。工作流本身完全支持中文路径
> （包括中文实验目录名、中文 CSV 文件名）。

## 2. LaTeX（XeLaTeX + 发行版字体）

| 平台 | 安装方式 |
| --- | --- |
| Windows | 安装 [TeX Live](https://tug.org/texlive/)（推荐，勾选安装 `ctex`），或 MiKTeX |
| macOS | `brew install --cask mactex` |
| Debian/Ubuntu | `sudo apt install texlive-xetex texlive-lang-chinese texlive-fonts-recommended texlive-latex-extra` |

新报告使用 `minimal` 模板：`ctexart[UTF8,fontset=fandol,scheme=plain]`，中文为 Fandol，英文为 Latin Modern。安装 `ctex`、`xeCJK`、`fontspec` 和对应字体包即可，不要求安装宋体、黑体或微软雅黑。`thuemp.cls` 与旧模板资产仅兼容已有报告。

无 `.bib` 文献库时，XeLaTeX 编译两遍即可，不要求 BibTeX。只有报告确实使用真实 `.bib` 库及 `gbt7714` 样式时，才检查并安装 BibTeX 和 `gbt7714-numerical.bst`。

绘图字体与 LaTeX 正文字体分别配置。Matplotlib 若选择微软雅黑、黑体或 Noto CJK，需确认相应字体存在；也可显式加载发行版中的 Fandol 字体文件，不能用绘图字体检查代替正文编译检查。

## 3. 安装 Skill

```powershell
# Windows（PowerShell）
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

```bash
# macOS / Linux
bash ./install.sh
```

脚本会把两个 Skill 复制到用户级目录：

```text
~/.codex/skills/Lab_Workflow_Generator/     # 编排层（脚本 + 模板 + 规范）
~/.codex/skills/advanced_lab_report_gen/    # 文本核心（写作规则）
```

Windows 对应 `%USERPROFILE%\.codex\skills\`。常用参数：

```powershell
.\install.ps1 -SkillsDir D:\my\skills      # 自定义目标目录
.\install.ps1 -Force                       # 覆盖同名 Skill（覆盖前自动备份为 *.bak-<时间戳>）
bash ./install.sh --skills-dir /opt/skills --force
```

安装后**必须新开会话**（Skill 列表在会话启动时加载）。

## 4. 自检

```powershell
python verify_install.py
```

环境自检覆盖 Python、绘图库、编译器和 Skill 资源。若检查器列出绘图用的系统中文字体或旧模板的参考文献样式，应结合实际使用场景判断；`minimal` 正文使用 Fandol 与 Latin Modern，无文献库时不依赖 BibTeX。

在本 `skills/` 目录内单独验证引擎、字体、章节编号及 PDF 输出：

```powershell
powershell -ExecutionPolicy Bypass -File .\Lab_Workflow_Generator\assets\minimal_latex\build.ps1 -Verify
```

该诊断使用自带样例，不需要实验数据。正式报告部署 `template_minimal.tex` 后，直接填写 `lab_report.tex`，由运行器用 XeLaTeX 两遍编译，辅助文件集中到 `build/`。仍须按 `report.md` 检查正文、数据和渲染后的 PDF。

`python verify_install.py --demo` 是可选的实验流程验收；本仓库不附实验示例数据，缺少示例时会提示 WARN 并跳过。真实报告的端到端验收需另行提供有权使用的讲义和数据。

## 5. 可选依赖

| 用途 | 安装 |
| --- | --- |
| 扫描件讲义 OCR | `python -m pip install rapidocr-onnxruntime` |
| 两个第三方基础 Skill（lab-assist / lab-report-writer，**非必需**） | `npx skills add https://github.com/Daigui233/lab-assist --skill lab-assist`<br>`npx skills add https://github.com/mingchen666/Reviva --skill lab-report-writer` |

## 6. 卸载

```bash
rm -rf ~/.codex/skills/Lab_Workflow_Generator ~/.codex/skills/advanced_lab_report_gen
```

（卸载 Skill 不会动你的实验工作区；工作区里的 `lab_report/` 与 `data/` 都是你自己的文件。）

## 7. 目录对照表

| 本包内路径 | 安装后位置 |
| --- | --- |
| `skills/Lab_Workflow_Generator/` | `~/.codex/skills/Lab_Workflow_Generator/` |
| `skills/advanced_lab_report_gen/` | `~/.codex/skills/advanced_lab_report_gen/` |
| `examples/demo-单摆法测重力加速度/` | 无需安装，直接在工作区里跑 |
