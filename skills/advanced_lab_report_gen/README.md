# Advanced Lab Report Generator — 近物实验报告自动生成器

## 当前工作区格式约定

生成的报告须遵循工作区根目录的 report.md：引言恰好两段；第2节“原理”下设“实验原理”“实验装置”“实验方法”，方法按实际步骤设子子标题；结果章节后以“实验总结”收尾；正文引用使用上角标，图表标题及图表引用只用中文；英文摘要和英文关键词放在参考文献之后；原始数据及完整实验记录另存本地，不列入报告附录。若本文件夹中的历史训练画像与该规范不同，以 report.md 和当前教师要求为准。

![Version](https://img.shields.io/badge/version-3.1-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Skill](https://img.shields.io/badge/Codex-Skill-purple)

[English](#english) | [中文](#中文)

---

## 中文

### 简介

Advanced Lab Report Generator 是一个基于 Codex/Harness 平台的专属 Skill，能够根据实验讲义和原始数据，自动生成符合正式期刊风格的近代物理实验报告。它内嵌了 17 份优秀报告的风格特征和 9 个实验的物理知识库，支持实验自动识别、数据处理、报告撰写、PDF 编译一条龙。

### 适用场景

- 近代物理实验（原子物理、光学、凝聚态、非线性动力学）
- 需要标准化、高效率生成实验报告的教学/科研场景
- 希望继承优秀报告风格、避免常见写作缺陷的写作者

### 核心特性

- **实验自动识别**：基于关键词和公式匹配，自动识别 9 个典型近物实验
- **数据处理自动化**：自动完成线性/非线性拟合、误差传递、信噪比计算
- **风格锚定**：基于 17 份有效样本（学生A、学生B、学生C），生成符合当前项目规范及教师明确要求的报告
- **反面案例过滤**：自动检测并重写“要点式 / 无图注 / 摘要无数值”等常见缺陷
- **正式输出**：自包含的 `lab_report.tex` + PDF；Markdown 可作为额外阅读稿，正式编译采用用户所选六种模板之一 + XeLaTeX
- **样本不足警告**：对样本少的实验（激光模式分析、干涉滤光片）自动提示人工复核
- **含修订的 v3.1 口径**：顶层章节对齐老师小论文格式（“结果与分析讨论”为**合并章节**）、摘要 100–200 字、参考文献 3–6 条；相对误差为硬性要求，R²/残差与不确定度为「使用则须给出」的条件项；附录仅按需保留程序或推导，原始实验数据独立保存；数据溯源声明**双落点**（正文灰框 + `data/README.md`）
- **配套工作流（推荐）**：与 `Lab_Workflow_Generator` 配合可工程化「讲义 → 脚手架 → 图表/正文 → PDF」。该工作流提供 `run_lab_workflow.py`（目录/绘图/按需文献处理/XeLaTeX 编译）、`make_data_tables.py`（由 `data/*.csv` 生成本地三线表片段，正文按需选用）与 `check_report_tex.py`（图/表题注、引用可解析、章节完整性校验）

### 当前模板与编译

制作新实验报告前，先检查本份报告已有源稿和 `template_selection.json`：已有则继续沿用，换版须用户明确要求并保留正文、数据和手动修改。用户已经针对本份报告明确选定模板，或明确要求沿用上一份样式时，不重复询问；其他实验曾选过模板不能自动套用。新实验没有本次选择时，先列出以下六种，请用户明确选择后再部署和撰写，不擅自默认任一模板。

| 编号 | 模板 | 版式特点 |
| --- | --- | --- |
| 01 | 清华课程双栏 | 居中题头、传统双栏 |
| 02 | Physical Review 风格 | 紧凑双栏、栏间细线 |
| 03 | Nature 风格 | 大标题、浅色摘要；引言单栏，原理起同页双栏，附录单栏 |
| 04 | Applied Physics Letters 风格 | 浅色题头、无首行缩进、段落留白、单栏宽图表 |
| 05 | Journal of Physics 风格 | 题头与摘要独立页、大字号与行距、单栏宽图表 |
| 06 | He-Ne 原报告单栏 | 黑白、1.5倍行距、题目页眉与就地图表；宋黑字体由 Fandol 替代 |

六种模板共用已修复的 XeLaTeX、Fandol 与 Latin Modern 字体底座和自动章节编号，保留各自题头、字号、行距及单/双栏特点。部署后直接填写自包含的 `lab_report/lab_report.tex`，不要求拆成 metadata/body。辅助文件集中到 `build/`，无外部文献库时通常编译两遍；实际使用 `\bibliography` 时再执行相应文献流程。校徽、中文摘要和关键词、末尾英文摘要和关键词及全部实验内容要求继续按 `report.md` 执行。

独立 `assets/minimal_latex/build.ps1 -Verify` 用于引擎、字体和编号诊断，不取代六种模板选择。

### 适用实验（9个）

1. 光学多道与氢氘同位素光谱
2. 铷原子的光泵磁共振
3. 塞曼效应
4. 液晶物性
5. 光纤性质与应用
6. He-Ne 激光纵横模分析与模分裂
7. 高温超导材料的特性与表征
8. 非线性电路混沌及其同步控制
9. 干涉滤光片的镀制

### 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/yourname/advanced_lab_report_gen-skill.git

# 2. 复制到 Codex Skills 目录
cp -r advanced_lab_report_gen-skill ~/.codex/skills/advanced_lab_report_gen/

# 3. 重启 Codex，新开会话后输入
/gen_report
```

详细安装步骤请见 [docs/installation.md](docs/installation.md)。

### 依赖要求

- Codex/Harness 环境
- Python 3.11+（pandas、numpy、scipy、matplotlib、uncertainties）
- TeX Live / XeLaTeX、ctex、Fandol 和 Latin Modern（六种现行模板统一使用，不依赖系统中文字体）
- `Lab_Workflow_Generator`（推荐，用于六种模板部署、检查与编译）；lab-report-writer/lab-assist 仅为可选旧流程扩展

### 示例

- 完整示例报告：[examples/光泵磁共振实验_报告.md](examples/光泵磁共振实验_报告.md)
- 拟真数据与讲义摘要：[examples/sample_data/](examples/sample_data/)

### 许可证

[MIT License](LICENSE)

### 贡献

欢迎提交 Issue 和 Pull Request。如需新增实验或更换模板，请参考 [docs/customization.md](docs/customization.md)。

> ⚠️ **公开发布前请注意**：`training_output/` 内含真实作者与教师姓名等个人信息。推送到公开仓库前请先做匿名化处理（见 [PUBLISHING_CHECKLIST.md](PUBLISHING_CHECKLIST.md)）。

---

## English

### Introduction

The **Advanced Lab Report Generator** is a Codex/Harness Skill that automatically generates journal-style experimental reports from lecture notes and raw data. It incorporates style features from 17 excellent reports and a knowledge base of 9 physics experiments, supporting end-to-end automation: experiment identification → data processing → report writing → PDF compilation.

### Features

- Automatic identification of 9 typical modern-physics experiments by keyword/formula matching
- Built-in data processing: linear/nonlinear fitting, error propagation, SNR calculation
- Style anchoring from 17 validated reports (Wei Tianxiang, Zhang Ziyang, Li Renzhi)
- Counterexample filtering against bullet-point style, missing captions, and value-free abstracts
- Self-contained `lab_report.tex` + PDF output using the user's choice among the six report styles with XeLaTeX; Markdown is optional
- Sample-size warnings for low-coverage experiments

### Quick Start

```bash
git clone https://github.com/yourname/advanced_lab_report_gen-skill.git
cp -r advanced_lab_report_gen-skill ~/.codex/skills/advanced_lab_report_gen/
# Restart Codex, then type: /gen_report
```

See [docs/installation.md](docs/installation.md) and [docs/usage.md](docs/usage.md) for details.

### License

MIT License — see [LICENSE](LICENSE).

> ⚠️ Personal names inside `training_output/` must be anonymized before publishing to a public repository.
