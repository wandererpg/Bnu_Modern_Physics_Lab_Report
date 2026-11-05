# 定制化指南（Customization Guide）

现行格式基准是工作区 report.md 和当前教师要求；training_output 中的画像只记录历史样本，不作为新报告结构的覆盖规则。

## 1. 更新章节模板

新报告以工作区 `report.md`、当前教师要求和 `assets/report_templates/template_minimal.tex` 为准；正文直接写入 `lab_report/lab_report.tex`。章节使用标准无星号命令与 `1`、`1.1` 编号，不再把历史训练画像的 `recommended_chapters` 当作当前结构模板。更新通用内容要求时同步规范副本，保留校徽、中文摘要和关键词、末尾英文摘要和关键词。

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

正式输出为自包含的 LaTeX 源文件 `lab_report.tex` 和编译成功的 PDF，Markdown 或 DOCX 仅为按需阅读副本。新报告默认部署 `assets/report_templates/template_minimal.tex`，不拆成 metadata/body 或 lab-assist 的信息、记录和总结文件。

最小模板采用 XeLaTeX、`ctexart[UTF8,fontset=fandol,scheme=plain]`、Fandol 和 Latin Modern。辅助文件集中在 `build/`，无文献库时编译两遍即可；使用真实 `.bib` 文献库时再执行相应文献编译流程。引擎、字体或编号问题用 `assets/minimal_latex/build.ps1 -Verify` 分项诊断，正式报告仍须另做内容和 PDF 检查。

修改已有报告前备份并保留手改内容，不用新模板空骨架覆盖旧稿；历史模板只兼容已有报告。

## 6. 工作流层定制（配合 Lab_Workflow_Generator）

若同时使用 `Lab_Workflow_Generator`，除本 Skill 的写作规则外还可定制：

| 想改什么 | 修改位置 |
| --- | --- |
| 报告版式（页边距、行距、1/1.1章节编号、校徽、上角标引用和中文图题） | `assets/report_templates/template_minimal.tex`；具体报告直接改 `lab_report.tex` |
| 本地数据表片段生成、正文按需选用（列对齐、转义、行数截断、汇总） | `scripts/make_data_tables.py` |
| 报告源校验（题注、悬空/孤儿引用、必需章节、摘要长度） | `scripts/check_report_tex.py` |
| 工作区目录约定与执行流程 | 该 Skill `SKILL.md` §3/§5 |
| 数据溯源声明模板 | `assets/scaffold_template/data_README.md` |

修改后请用一次真实/拟真数据跑通：脚手架 → 表生成 → 源校验 → XeLaTeX 编译。
