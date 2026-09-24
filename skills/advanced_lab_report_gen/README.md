# Advanced Lab Report Generator — 近物实验报告自动生成器

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
- **风格锚定**：基于 17 份有效样本（学生A、学生B、学生C），生成符合老师 PPT 要求的报告
- **反面案例过滤**：自动检测并重写“要点式 / 无图注 / 摘要无数值”等常见缺陷
- **双格式输出**：Markdown + PDF（依赖 xelatex）
- **样本不足警告**：对样本少的实验（激光模式分析、干涉滤光片）自动提示人工复核
- **含修订的 v3.1 口径**：顶层章节对齐老师小论文格式（「四、结果与分析讨论」为**合并章节**）、摘要 100–200 字、参考文献 3–6 条；相对误差为硬性要求，R²/残差与不确定度为「使用则须给出」的条件项；附录统一为「附录 A 原始数据 + 程序附录」；数据溯源声明**双落点**（正文灰框 + `data/README.md`）
- **配套工作流（推荐）**：与 `Lab_Workflow_Generator` 配合可工程化「讲义 → 脚手架 → 图表/正文 → PDF」。该工作流提供 `run_lab_workflow.py`（目录/绘图/BibTeX/编译）、`make_data_tables.py`（由 `data/*.csv` 生成附录三线表）与 `check_report_tex.py`（图/表题注、引用可解析、章节完整性校验）

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
- TeX Live / xelatex（用于 PDF 编译）
- lab-report-writer 和 lab-assist 两个基础 Skill（安装方式见文档）

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
- Markdown + PDF output (xelatex)
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
