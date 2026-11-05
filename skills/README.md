# 实验报告工作流（Skill 套件）

本目录是「实验报告自动化工作流」的完整套件：两个 Codex Skill、安装与自检脚本、
文档与模板资源（当前仓库不含实验示例数据）。它把本仓库的 `report.md` / `preview.md` 规范
进一步工程化：目录驱动、图表程序化生成、编译与**成品 PDF 版式校验**一条龙。

## 模板选择与编译

模板选择仅针对本份/本次报告；其他实验曾选过的样式不得自动套用。用户明确要求沿用上一份样式时可沿用；新实验没有本次选择则重新列六种供用户选择。

制作新实验报告前，先检查已有报告和 `template_selection.json`：已有报告或选择记录继续沿用，换版须有用户明确要求并保留正文、数据和手动修改。用户本轮或此前已明确选定模板时沿用，不重复询问；否则先列出以下六种模板，请用户明确选择后再部署和撰写，不擅自默认任一模板。

| 编号 | 模板 | 版式特点 |
| --- | --- | --- |
| 01 | 清华课程双栏 | 居中题头、传统双栏 |
| 02 | Physical Review 风格 | 紧凑双栏、栏间细线 |
| 03 | Nature 风格 | 大标题、浅色摘要；引言单栏，原理起同页双栏，附录单栏 |
| 04 | Applied Physics Letters 风格 | 浅色题头、无首行缩进、段落留白、单栏宽图表 |
| 05 | Journal of Physics 风格 | 题头与摘要独立页、大字号与行距、单栏宽图表 |
| 06 | He-Ne 原报告单栏 | 黑白、1.5倍行距、题目页眉与就地图表；宋黑字体由 Fandol 替代 |

用 `--list-templates` 查看注册表；选定后显式传入编号，例如用户选择01时使用 `--template 01`。编号01只是调用示例，不是默认选项。

六种模板共用已修复的 XeLaTeX、Fandol 与 Latin Modern 字体底座和自动章节编号，保留各自题头、页边距、行距及单/双栏特点。部署后直接填写自包含的 `lab_report/lab_report.tex`，不要求拆成 metadata/body。辅助文件集中到 `build/`，无外部文献库时通常编译两遍；实际使用 `\bibliography` 时再执行 BibTeX 等相应文献流程。校徽、中文摘要和关键词、末尾英文摘要和关键词及全部实验内容要求继续按 `report.md` 执行。

[独立分项诊断模板](Lab_Workflow_Generator/assets/minimal_latex/README.md) 保留用于 `build.ps1 -Verify` 检查引擎、字体和编号；它不替代用户所选的六种报告模板，也不代替正式内容和 PDF 检查。

## 文字写作与润色协作

按根目录 [report.md 的文字写作与润色协作](../report.md#文字写作与润色协作)执行：Codex 负责资料核验、数据处理、写作任务组织与最终验收；`codex-antigravity` 可用且 Gemini 3.8 Flash 实际可调用时，由它起草或润色指定正文、摘要及英文表达。它只返回候选文字，不直接修改报告文件、数据、公式、文献键或模板。

调用使用 `gemini-3.8-flash-medium`、`task_type: simple`、`effort: medium`、`mode: analysis`、`fallback: false`；每次由 Codex 自动填写当前项目绝对工作目录。工具缺失、桥接离线、模型不可选、调用或鉴权等错误、超时、任务失败或需要人工处理时，跳过插件，由 Codex 继续原流程，不换模型、不反复重试，也不要求用户修复环境。它是可选协作环节，不是安装、写作或编译的必备依赖；六种模板选择流程保持原样。

## 组成

| 目录 / 文件 | 说明 |
| --- | --- |
| `Lab_Workflow_Generator/` | 编排层 v1.27：工作区脚手架、绘图脚本执行、三线表片段生成（本地留存、正文按需选用）、XeLaTeX 编译、四项版式校验 |
| `advanced_lab_report_gen/` | 文本核心 v3.1：报告结构、写作与数据处理规则（脱敏版） |
| `docs/` | 工作流总览、数据与目录约定、校验与验收、故障排查、AI 一键安装提示词 |
| `install.ps1` / `install.sh` | 安装到用户级 Skill 目录 |
| `verify_install.py` | 环境自检；可选 `--demo` 需要额外提供示例工程 |

## 安装

```powershell
# Windows
python -m pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File .\install.ps1
python .\verify_install.py
```

```bash
# macOS / Linux
python3 -m pip install -r requirements.txt
bash ./install.sh
python3 ./verify_install.py
```

`--demo` 需要示例工程；本仓库版本**不含示例数据**，因此该步骤会被跳过并提示 WARN（其余 11 项自检照常执行）。端到端验收需另行提供有权使用的讲义和实验数据。
安装后**新开一个会话**，Skill 才会被加载。详细说明见 `INSTALL.md` 与 `docs/`。

## 关于示例数据

本仓库版本**刻意不含任何实验数据**（含示例工程与拟真数据），只保留工作流、规范、模板与文档，避免与仓库内真实实验记录混淆。对外分享的内容、安装依赖和许可限制见 [DISTRIBUTION.md](DISTRIBUTION.md)。

## 与本仓库规范的关系

本工作流自带 `Lab_Workflow_Generator/references/` 下的规范副本（`report.md`、
`preview.md`、`agents.md`），以便**脱离本仓库独立运行**（安装到 `~/.codex/skills` 后无需本仓库）。

仓库根目录的同名文件是本仓库的**权威规范**，且已经把本工作流的全部规则并入
（图表规范、浮动体距离、按版心宽度就地图表、行文不得出现括号、数据双落点声明、提交前检查等），
因此外层文件的规则是本 Skill `references/` 的**超集**。修改规范时请改仓库根目录的文件，
再把改动同步回 `references/`，避免两处漂移。

## 许可

套件自有部分为 MIT，模板类资产版权归各自作者，详见 `THIRD_PARTY.md`。
