# 实验报告工作流（Skill 套件）

本目录是「实验报告自动化工作流」的完整套件：两个 Codex Skill、安装与自检脚本、
文档与模板资源（当前仓库不含实验示例数据）。它把本仓库的 `report.md` / `preview.md` 规范
进一步工程化：目录驱动、图表程序化生成、编译与**成品 PDF 版式校验**一条龙。

## 当前模板与编译

新报告默认使用唯一注册的 `minimal` 模板，别名为 `default`、`默认`、`最小`；`--template minimal` 可省略，`--list-templates` 用于查看注册表。正式模板是 [template_minimal.tex](Lab_Workflow_Generator/assets/report_templates/template_minimal.tex)，部署后直接填写自包含的 `lab_report/lab_report.tex`，不再按 01—06 选样式或拆成 metadata/body 文件。已有报告及手改源文件保留，历史模板仅用于兼容旧报告。

编译固定使用 XeLaTeX、`ctexart[UTF8,fontset=fandol,scheme=plain]`、发行版自带的 Fandol 与 Latin Modern 字体；章节使用标准无星号命令和 `1`、`1.1` 编号。运行器将辅助文件集中到 `build/`，通常编译两遍；没有 BibTeX 文献库时不要求 BibTeX，有真实 `.bib` 文献库时再执行相应文献流程。校徽、首页中文摘要和关键词、参考文献后英文摘要和关键词及其余实验内容要求继续以 `report.md` 为准。

可用 [分项诊断模板](Lab_Workflow_Generator/assets/minimal_latex/README.md) 的 `build.ps1 -Verify` 分别验证引擎、字体和编号；诊断通过不代替正式实验内容及 PDF 版面的检查。

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
