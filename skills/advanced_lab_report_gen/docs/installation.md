# 安装指南（Installation Guide）

## 1. 环境准备

### 1.1 Python 环境（3.11+）

```bash
python -m pip install pandas numpy scipy matplotlib uncertainties
```

Windows 上若 `python` 指向 Microsoft Store 占位符，请改用启动器：

```powershell
py -m pip install pandas numpy scipy matplotlib uncertainties
```

### 1.2 TeX Live / xelatex

PDF 编译依赖 xelatex。macOS 可用 `brew install --cask mactex`，Linux 可用 `sudo apt install texlive-xetex texlive-lang-chinese`，Windows 推荐安装 TeX Live 2025 并确认 `xelatex` 在 PATH 中。

```bash
xelatex --version
```

### 1.3 安装两个基础 Skill

本项目运行时依赖 `lab-report-writer` 与 `lab-assist`：

```bash
npx skills add https://github.com/mingchen666/Reviva --skill lab-report-writer
npx skills add https://github.com/Daigui233/lab-assist --skill lab-assist
```

若 `npx` 不可用，可用 skill-installer 脚本（来自 Codex 内置技能）或按 lab-assist 仓库 README 手动安装到 `~/.codex/skills/`。

### 1.4 配套工作流 Skill（推荐）

如需**目录驱动**、一次产出预习报告 + 实验报告 + PDF，请一并安装 `Lab_Workflow_Generator`（提供 `/build_lab`、工作区脚手架、`run_lab_workflow.py`、`make_data_tables.py`、`check_report_tex.py`，并携带物理学报模板与校徽资产）。

注意：该工作流的 `run_lab_workflow.py` 请用**真实 Python 解释器**运行（如 `C:\Users\<你>\AppData\Local\Programs\Python\Python311\python.exe`）。在本机实测中，Windows `py` 启动器对含中文的脚本路径/参数可能直接返回 **9009**（命令未找到），用完整解释器路径即可。

## 2. 安装 advanced_lab_report_gen

### 方式A：Git 克隆 + 复制（推荐）

```bash
git clone https://github.com/yourname/advanced_lab_report_gen-skill.git
cp -r advanced_lab_report_gen-skill ~/.codex/skills/advanced_lab_report_gen/
```

Windows PowerShell 对应：

```powershell
Copy-Item -Recurse -Force .\advanced_lab_report_gen-skill $HOME\.codex\skills\advanced_lab_report_gen
```

`SKILL.md` 必须位于 `~/.codex/skills/advanced_lab_report_gen/SKILL.md`。

### 方式B：会话内直接粘贴

将仓库根目录的 `SKILL.md` 全文粘贴到支持 System Prompt / 自定义指令的会话中，然后输入 `/gen_report`。

### 注意

- 安装完成后需要**重启 Codex / 新开会话**，技能列表才会重新加载；
- 若本机已存在同名旧版，先备份再覆盖：

```bash
cp -r ~/.codex/skills/advanced_lab_report_gen ~/.codex/skills/advanced_lab_report_gen.bak
```

## 3. 依赖检查清单

```bash
# Codex Skills
ls ~/.codex/skills/advanced_lab_report_gen/SKILL.md
ls ~/.codex/skills/lab-report-writer/SKILL.md
ls ~/.codex/skills/lab-assist/SKILL.md

# Python 库
py -c "import pandas,numpy,scipy,matplotlib,uncertainties; print('ok')"

# LaTeX
xelatex --version
```

全部通过后，新开会话输入 `/gen_report` 即可使用。

## 4. 常见问题（FAQ）

| 问题 | 解决方法 |
| --- | --- |
| `python` 命令找不到 | Windows 使用 `py` 启动器 |
| 技能列表里看不到本 Skill | 重启 Codex / 新开会话；确认 SKILL.md 在用户级 skills 目录且 frontmatter 含 `name` 与 `description` |
| PDF 编译失败 | 检查 xelatex 是否安装、中文支持（ctex/zh 字体）是否完整；可先使用 Markdown 输出 |
| OCR 不可用 | `py -m pip install rapidocr-onnxruntime` |
| 识别不到实验 | 手动输入实验名称；检查关键词与 `experiment_library.json` 是否一致 |
| 目录含旧版本 | 先备份再覆盖（见上方注意） |
