# 安装指南

面向 Windows / macOS / Linux 的分步安装。装完全部约 5 分钟（不含 LaTeX 发行版下载）。

## 0. 前置检查

```bash
python -V                     # 需 3.11 或更高
xelatex --version             # 需 TeX Live 2023+ 或 MiKTeX
kpsewhich gbt7714-numerical.bst   # 国标参考文献样式（texlive-lang-chinese 自带）
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

## 2. LaTeX（XeLaTeX + 中文 + 参考文献）

| 平台 | 安装方式 |
| --- | --- |
| Windows | 安装 [TeX Live](https://tug.org/texlive/)（推荐，勾选安装 `ctex`），或 MiKTeX |
| macOS | `brew install --cask mactex` |
| Debian/Ubuntu | `sudo apt install texlive-xetex texlive-lang-chinese texlive-fonts-recommended texlive-latex-extra` |

需要的中文支持：`ctex`、`xeCJK`；参考文献：`gbt7714-numerical.bst`。
`thuemp.cls` **随包提供**（`skills/Lab_Workflow_Generator/assets/thu_template/`），无需另外下载。

字体：Windows 自带微软雅黑即可出图；Linux 若缺中文字体，装 `fonts-noto-cjk`。

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

逐项检查：Python 版本、五个库、`xelatex`、中文字体、`gbt7714` 样式、两个 Skill 的关键文件是否齐全。
输出形如：

```text
[PASS] Python 3.11.9
[PASS] numpy 1.26.4 / scipy / matplotlib / pandas / PyMuPDF
[PASS] xelatex 在 PATH 中
[PASS] 中文字体可用（Microsoft YaHei）
[PASS] Lab_Workflow_Generator 关键文件齐全（8 个脚本 + 模板资产）
[PASS] advanced_lab_report_gen SKILL.md 存在
==> ALL PASS（可运行 --demo 做端到端冒烟测试）
```

想直接验证"能不能产出 PDF"，跑示例工程：

```powershell
python verify_install.py --demo
```

它会在临时目录复制 demo 工程并执行完整流水线，期望得到 3 页 PDF 且四项校验全绿。

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
