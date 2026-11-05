# 报告包内工具

本包提供 minimal 模板的选择、脚手架、编译和检查工具。完整流程从包根目录 [START_HERE.md](../START_HERE.md) 开始；无需安装其他文本生成 Skill，Agent 直接按根目录规范撰写内容。

`Lab_Workflow_Generator/scripts/` 中：

| 工具 | 用途与依赖 |
| --- | --- |
| `select_report_template.py` | 解析 minimal 及 default/默认/最小别名、部署依赖、维护选择记录；Python标准库 |
| `run_lab_workflow.py` | 脚手架、材料清单、表格、检查与编译；本地编译用XeLaTeX两遍，缓存集中build/；真实.bib库按需加文献流程 |
| `make_data_tables.py` | 将真实CSV记录转为宽度适配的LaTeX表格；不生成测量值 |
| `check_report_tex.py` | 递归读取正文，检查章节、图题、引用及表格结构 |
| `check_pdf_geometry.py` | 测量PDF边界、重叠及图片可读性；需PyMuPDF |
| `check_float_distance.py` | 检查图表与首次引用的距离；需PyMuPDF |
| `check_inline_distance.py` | 检查就地图表与引用的距离；需PyMuPDF |

`Lab_Workflow_Generator/references/` 保存规范副本，包根目录规范是阅读入口。`assets/report_templates/template_minimal.tex` 是正式模板，部署后直接填写自包含 `lab_report.tex`；校徽等通用依赖已包含。正文使用 ctexart、Fandol/Latin Modern 和标准1/1.1编号，不依赖系统中文字体；历史模板只兼容已有报告。`assets/minimal_latex/build.ps1 -Verify` 可分项检查引擎、字体和编号。源仓库的完整安装、OCR、文本生成扩展及其他历史参考模板不属于此精简包的运行依赖。
