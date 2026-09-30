# 近代物理实验报告工作区

实验报告现有6套可由AI按编号或名称调用的LaTeX模板：01清华课程双栏（默认）、02 Physical Review、03 Nature、04 Applied Physics Letters、05 Journal of Physics、06 He-Ne原报告单栏。可直接说“这份报告使用模板03”或“用 Physical Review 样板写报告”。内容仍按 [report.md](report.md)，预习报告仍按 [preview.md](preview.md)。

模板及选择/编译流程见 [模板库说明](skills/Lab_Workflow_Generator/assets/report_templates/README.md)，期刊参考来源见 [来源说明](skills/Lab_Workflow_Generator/assets/report_templates/SOURCES.md)。期刊风格版是中文课程适配，非官方投稿模板。AI按“读材料 → 选择并部署 → 写真实内容 → 编译 → 检查内容和PDF → 交付”完成报告；换样式保留正文与数据。通用模板可同步GitHub，实验实例全部留在本地。

本仓库保存北京师范大学近代物理实验报告的通用写作规范、参考模板和可选工作流。具体实验资料、预习报告、实验报告及原始数据只保存在本地工作区。

供其他Agent使用的独立副本位于源工作区的 `agent_report_bundle/`；复制整个文件夹后从包内 `START_HERE.md` 开始。该包集中保存五份Markdown规范、六套模板、必要依赖及选择/编译/检查工具；更新源规范或模板后运行 `python skills/Lab_Workflow_Generator/scripts/export_agent_bundle.py` 同步副本。

## 通用文件

- [agents.md](agents.md)：工作区目录、数据真实性、编译和协作规则。
- [AGENT.md](AGENT.md)：简要操作约定。
- [preview.md](preview.md)：预习报告要求。
- [report.md](report.md)：实验报告要求。
- `物理学报模板_Acta_Physica_Sinica_/`：排版参考模板。
- [skills/](skills/)：可选的目录脚手架、绘图与附录表生成、XeLaTeX 编译及 PDF 版面检查工作流。安装与使用方法见 [skills/README.md](skills/README.md)。

报告内容以根目录 `preview.md` 和 `report.md` 为准；工作流只提供生成与检查工具。

## 本地实验目录

每项实验在本地使用独立目录，按讲义标题命名。例如：

```text
<实验标题>/
├── <实验标题>.pdf
├── preview_report/       # 预习报告源文件和 PDF
├── lab_report/           # 实验报告、数据、图片和脚本
└── lab_report_previous/  # 如需保留历史版本
```

报告按相应规范编写，并使用支持中文的 LaTeX 引擎编译。编译后检查公式、图表、引用和 PDF 版面。原始数据与历史版本留在本地，修改时保留可复核的来源。

## GitHub 同步范围

只提交根目录的通用规范、`skills/` 工作流、参考模板及 `agent_report_bundle/` 通用副本。根目录的 `.gitignore` 默认忽略实验子文件夹；请勿强制加入其中的讲义、报告、个人信息、原始数据、照片或生成文件。提交前核对暂存列表。
