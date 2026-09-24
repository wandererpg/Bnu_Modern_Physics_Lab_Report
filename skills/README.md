# 实验报告工作流（Skill 套件）

本目录是「实验报告自动化工作流」的完整套件：两个 Codex Skill、安装与自检脚本、
文档与一个可直接跑通的示例工程。它把本仓库的 `report.md` / `preview.md` 规范
进一步工程化：目录驱动、图表程序化生成、编译与**成品 PDF 版式校验**一条龙。

## 组成

| 目录 / 文件 | 说明 |
| --- | --- |
| `Lab_Workflow_Generator/` | 编排层 v1.27：工作区脚手架、绘图脚本执行、附录三线表生成、XeLaTeX 编译、四项版式校验 |
| `advanced_lab_report_gen/` | 文本核心 v3.1：报告结构、写作与数据处理规则（脱敏版） |
| `docs/` | 工作流总览、数据与目录约定、校验与验收、故障排查、AI 一键安装提示词 |
| `install.ps1` / `install.sh` | 安装到用户级 Skill 目录 |
| `verify_install.py` | 环境自检，`--demo` 会端到端跑一遍示例工程 |

## 安装

```powershell
# Windows
python -m pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File .\install.ps1
python .\verify_install.py --demo
```

```bash
# macOS / Linux
python3 -m pip install -r requirements.txt
bash ./install.sh
python3 ./verify_install.py --demo
```

`--demo` 需要示例工程；本仓库版本**不含示例数据**，因此该步骤会被跳过并提示 WARN（其余 11 项自检照常执行）。需要端到端冒烟测试时，用随包分发的完整版套件。
安装后**新开一个会话**，Skill 才会被加载。详细说明见 `INSTALL.md` 与 `docs/`。

## 关于示例数据

本仓库版本**刻意不含任何实验数据**（含示例工程与拟真数据），只保留工作流、规范、模板与文档，避免与仓库内真实实验记录混淆。完整套件（含可跑 demo）见分发用压缩包。

## 与本仓库规范的关系

本工作流自带 `Lab_Workflow_Generator/references/` 下的规范副本（`report.md`、
`preview.md`、`agents.md`），以便脱离本仓库独立运行；仓库根目录的同名文件仍是
本仓库的权威规范。两者若有出入，以仓库根目录的版本为准，并欢迎把差异同步回
Skill 的 `references/`。

## 许可

套件自有部分为 MIT，模板类资产版权归各自作者，详见 `THIRD_PARTY.md`。
