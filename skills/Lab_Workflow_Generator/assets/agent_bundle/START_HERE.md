# 其他 Agent 使用入口

将整个 `agent_report_bundle/` 复制到目标工作区，保留内部路径。这个文件夹可作为新工作区根目录；也可存放在已有工作区内，运行脚本时用 `--workspace` 指定目标工作区。模板仅提供排版和待填写骨架，实验内容由 Agent 根据真实材料撰写。

## 阅读与执行顺序

1. 先读 [运行规范.md](运行规范.md) 拆解请求，再读 [agents.md](agents.md) 和 [AGENT.md](AGENT.md)，确认任务路由、自主权、目录、真实性和历史保留要求。包内涉及原工作区的 Git 提交/推送约定，在其他工作区应结合该用户的授权与远程配置执行。
2. 写预习报告时读 [preview.md](preview.md)；写实验报告时读 [report.md](report.md)、讲义、原始记录和已有报告。确认实验标题、教师要求及缺失信息后再写作。
3. 先检查本份报告已有源稿与 `template_selection.json` 并沿用；用户已针对本份明确选择或要求沿用上一份样式时不重复询问，其他实验的选择不能自动套用。其余新报告须先从 [模板注册表](skills/Lab_Workflow_Generator/assets/report_templates/registry.json) 列01清华课程双栏、02 Physical Review风格、03 Nature风格、04 Applied Physics Letters风格、05 Journal of Physics风格、06 He-Ne原报告单栏，请用户明确选择后再调用。换版须用户明确要求并保留正文、数据及手改。具体特点见 [模板说明](skills/Lab_Workflow_Generator/assets/report_templates/README.md)。
4. 用下面的选择命令部署到 `<实验标题>/lab_report/`。成功标准是自包含 `lab_report.tex`、校徽和规范依赖齐全，且选择记录与用户选定的01—06编号一致。已有手改主文件应先备份、迁移并核对内容，保留原始数据及历史版本。
5. 直接填写 `lab_report.tex` 中的作者信息、摘要、正文和真实参考文献，不拆成 metadata/body。文字按 [协作规范](report.md#文字写作与润色协作)由可调用的 `codex-antigravity` / Gemini 3.8 Flash 起草、润色，Codex 核实来源并审核合入；不可调用时由 Codex 继续，不额外安装插件。首页仅放中文摘要和中文关键词；正文按 `report.md` 的五个顶层章节撰写，引言恰好两段，第2节“原理”下设实验原理、实验装置和实验方法，实验方法按实际步骤设置子子标题；英文摘要和英文关键词放在参考文献之后。缺测内容标记“待补充”，并核对数据处理依据、单位、有效数字、图表和引用。
6. 保存 LaTeX 源文件，使用支持中文的引擎编译成 PDF；运行源文件与PDF检查，人工查看渲染页面。交付时提供源文件、PDF及缺失项。只有内容核对和编译、版面检查都完成，才称正式报告完成。

## 直接调用

Python 3.10+ 可直接选择模板，无需安装本包为 Codex Skill。从包根目录执行：

```powershell
python skills/Lab_Workflow_Generator/scripts/select_report_template.py --list-templates
python skills/Lab_Workflow_Generator/scripts/run_lab_workflow.py --workspace . --experiment "实验标题" --stage scaffold --template 01
# 上例仅适用于用户已选择01；01不是默认项。Agent根据真实材料填写内容后：
python skills/Lab_Workflow_Generator/scripts/run_lab_workflow.py --workspace . --experiment "实验标题" --stage check
python skills/Lab_Workflow_Generator/scripts/run_lab_workflow.py --workspace . --experiment "实验标题" --stage compile
```

已有工作区可从包根目录将 `--workspace .` 改为目标工作区的绝对路径。若只安装实验报告骨架，使用 `select_report_template.py --workspace <目标工作区> --experiment "实验标题" --template 01`；预习报告由 Agent 按 `preview.md` 单独撰写。

优先在宿主提供的 LaTeX 编辑器中打开、编译报告。正式模板为本份报告选定的01—06之一，保留对应字号、行距、题头与单/双栏，各版式共用修复后的 XeLaTeX、Fandol 和 Latin Modern；无须安装系统宋体、黑体或微软雅黑。章节使用标准无星号命令与 `1`、`1.1` 编号。运行器将缓存集中到 `build/`，无文献库时编译两遍，不要求 BibTeX；使用真实 `.bib` 库时再执行相应文献流程。

分项诊断见 [minimal_latex](skills/Lab_Workflow_Generator/assets/minimal_latex/README.md)，可运行其 `build.ps1 -Verify` 核验引擎、字体与编号。PDF 自动测量需要 PyMuPDF；缺少引擎、宏包或字体时保留源码并报告具体原因，缺少检查库时明确自动检查未执行并继续人工版面检查。分项诊断不能代替正式实验内容及 PDF 验收。

## 包内文件与维护

- 根目录五份 Markdown 是源工作区规范的当前副本，保留最新 `preview.md`；[README.md](README.md) 提供原工作区介绍。
- `skills/Lab_Workflow_Generator/assets/report_templates/` 保存01—06六种可调用正式模板、注册表和说明；各模板保留对应题头、字号、行距和单/双栏。
- `assets/branding/bnu_logo.png` 及 `assets/scaffold_template/` 提供校徽、预习报告与数据说明等依赖；这些路径相对于 `skills/Lab_Workflow_Generator/`。旧 `thuemp.cls` 仅兼容历史实现，现行六种模板使用修复后的字体与自动编号底座。
- [工具说明](skills/README.md) 列出选择、编译及内容/版面检查工具；工具负责确定性步骤，正文由 Agent 撰写。
- `manifest.json` 记录每个文件的源路径、大小和 SHA-256，可用于核对复制完整性。包中保留正式模板源码，设计样例、预览PDF和实验资料不随包分发。

源工作区更新规范或模板后，运行 `python skills/Lab_Workflow_Generator/scripts/export_agent_bundle.py` 重新同步。本包是可移植副本，导出工具由源工作区维护；若手工修改副本，先将需要保留的修改合并回来源，再导出。目标工作区后续新增的实验资料应保存于独立实验目录。
