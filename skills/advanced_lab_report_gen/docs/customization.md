# 定制化指南（Customization Guide）

## 1. 更新章节模板

修改 `training_output/style_profile.json` 中的 `recommended_chapters`（顺序、`required`、`word_count`），然后把对应内容同步到 `SKILL.md` §2.1 的表格。强制章节缺失会导致报告被判不合格，请保留 PPT 要求的核心章节。

示例：把“结论和建议”字数要求调高：

```json
{"name": "结论和建议（总结）", "required": true, "word_count": "200-300字", "note": "总结+建议"}
```

## 2. 新增实验

两步：

1. 在 `experiment_library.json` 顶层新增条目：`domain`、`formulas`（LaTeX + 编号）、`data_methods`、`constants`、`variables`、`fit_model`、`error_propagation`；
2. 在 `style_profile.json` 的 `experiment_mapping` 新增同名字段：`keywords`、`formulas`、`fit_model`、`error_rules`，并同步到 SKILL.md §2.4 表格。

关键词应覆盖讲义中的实验名、仪器名、谱线/波长、测量对象等；关键词越多，自动识别越可靠。

## 3. 更换训练数据

1. 更新 `require/`（PPT 要求）、`report/`（优秀报告+反面案例）、`refer/`（讲义）；
2. 重新执行阶段2（风格分析与知识抽取），生成新的 `training_output/*.json`；
3. 检查新风格画像（尤其是摘要字数、图注格式、样本状态矩阵）；
4. 将关键字段回填到 `SKILL.md`（§2.1–§2.6 与附录）；
5. 重新验证：`py quick_validate.py <skill目录>`（如有 skill-creator）。

## 4. 调整反例过滤规则

反面案例登记位于 `report_style_analysis.json` 的 `excluded_counterexamples`，过滤特征表位于 SKILL.md §2.6：

- 增加禁止特征：在表格新增一行（特征名、检测信号、处理方式）；
- 更换反例样本：更新 `files` 列表并说明缺陷；
- 收紧/放宽阈值：调整 §2.2 摘要字数检查、§步骤5 的自检清单。

## 5. 修改输出格式

默认输出 Markdown + PDF：

- **Markdown**：由 SKILL.md §3 步骤4 直接生成；
- **PDF**：通过 lab-assist 接口（00_info / 01_lab_record / 02_summary + main.tex）调用 xelatex 两遍编译；
- **DOCX**：OfficeCLI 可用时由 lab-report-writer 生成 docx 副本；也可用 `python-docx` 编写转换脚本；
- **纯 LaTeX**：跳过 Markdown 中间层，直接写 main.tex（需额外维护模板宏与目录结构）。

修改位置：SKILL.md §6“编译逻辑”与 lab-assist 的 `assets/experiment-template/main.tex`。修改后建议用一份真实/拟真数据跑通全流程再发布。

## 6. 工作流层定制（配合 Lab_Workflow_Generator）

若同时使用 `Lab_Workflow_Generator`，除本 Skill 的写作规则外还可定制：

| 想改什么 | 修改位置 |
| --- | --- |
| 报告版式（页边距/行距/中文标题编号/校徽 overlay/双语图题/siunitx） | `assets/scaffold_template/report_preamble.tex` |
| 附录数据表生成（列对齐、转义、行数截断、汇总） | `scripts/make_data_tables.py` |
| 报告源校验（题注、悬空/孤儿引用、必需章节、摘要长度） | `scripts/check_report_tex.py` |
| 工作区目录约定与执行流程 | 该 Skill `SKILL.md` §3/§5 |
| 数据溯源声明模板 | `assets/scaffold_template/data_README.md` |

修改后请用一次真实/拟真数据跑通：脚手架 → 表生成 → 源校验 → XeLaTeX 编译。