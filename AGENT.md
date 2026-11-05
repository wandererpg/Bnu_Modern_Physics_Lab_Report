# Agent 快速入口

实验报告的文字起草与润色按 [report.md 的协作规范](report.md#文字写作与润色协作)：可调用时交给 `codex-antigravity` 的 Gemini 3.8 Flash，Codex 核实资料并审核合入；不可调用时跳过插件，由 Codex 完成。模板选择、计算与编译仍按原流程执行。

处理用户请求前，按[运行规范.md](运行规范.md)识别任务、上下文、约束和完成条件，并检查是否缺少会影响正确性或权限边界的信息。

本工作区的任务路由、自主权、验证、实验资料与版本管理要求见 [agents.md](agents.md)。预习报告按 [preview.md](preview.md)，实验报告按 [report.md](report.md)；两者是对应报告的内容规范与检查清单。

实验报告写作与润色前，读取 [report.md 的写作风格](report.md#写作风格)，按该节完成表达检查。

工作区文件索引与实验目录说明见 [README.md](README.md)。


制作新实验报告前，先按 [report.md](report.md#六种-latex-模板与选择流程) 展示 01—06 六种模板并询问选择。已有明确选择或维护既有报告时沿用；选择后编辑 `lab_report/lab_report.tex`。六种版式共用稳定编译基础，旧稿与手工修改须保留。
