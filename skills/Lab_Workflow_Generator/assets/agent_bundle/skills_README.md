# 报告包内工具

本包提供01—06六种模板的选择、脚手架、编译和检查工具。新报告先列六种请用户针对本份报告明确选择；本份已有报告/记录或用户明确要求沿用上一份样式时不重复询问，不能自动沿用其他实验的模板。换版须明确要求并保留内容。完整流程从包根目录 [START_HERE.md](../START_HERE.md) 开始；无需安装其他文本生成 Skill，Agent 直接按根目录规范撰写内容。

`Lab_Workflow_Generator/scripts/` 中：

| 工具 | 用途与依赖 |
| --- | --- |
| `select_report_template.py` | 列出01—06及别名，按用户明确选择部署依赖并维护记录；无选择不擅自部署；Python标准库 |
| `run_lab_workflow.py` | 脚手架、材料清单、表格、检查与编译；本地编译用XeLaTeX两遍，缓存集中build/；真实.bib库按需加文献流程 |
| `make_data_tables.py` | 将真实CSV记录转为宽度适配的LaTeX表格；不生成测量值 |
| `check_report_tex.py` | 递归读取正文，检查章节、图题、引用及表格结构 |
| `check_pdf_geometry.py` | 测量PDF边界、重叠及图片可读性；需PyMuPDF |
| `check_float_distance.py` | 检查图表与首次引用的距离；需PyMuPDF |
| `check_inline_distance.py` | 检查就地图表与引用的距离；需PyMuPDF |

`Lab_Workflow_Generator/references/` 保存规范副本，包根目录规范是阅读入口。`assets/report_templates/` 提供01—06六种正式模板，部署后直接填写自包含 `lab_report.tex`；校徽等通用依赖已包含。各模板共用 XeLaTeX、Fandol/Latin Modern 与自动编号，不依赖系统中文字体，保留各自字号、行距、题头和单/双栏。调用示例 `--template 01` 仅适用于本份报告已经选择01时；`--list-templates` 可查看选项。`assets/minimal_latex/build.ps1 -Verify` 可分项检查引擎、字体和编号。源仓库的完整安装、OCR、文本生成扩展及其他历史参考模板不属于此精简包的运行依赖。
