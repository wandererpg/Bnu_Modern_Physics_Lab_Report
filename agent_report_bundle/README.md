# 近代物理实验报告工作区

## 使用入口

接到任务后先按[运行规范](运行规范.md)整理任务、上下文、约束和完成条件，并识别需要向用户确认的关键信息。

| 文件 | 用途 |
| --- | --- |
| [agents.md](agents.md) | 工作区级路由、自主权、验证、实验资料和 Git 规则 |
| [AGENT.md](AGENT.md) | Agent 快速入口 |
| [preview.md](preview.md) | 预习报告要求与检查清单 |
| [report.md](report.md) | 实验报告要求、六套模板及其选择流程 |
| [运行规范.md](运行规范.md) | 人类提示词拆解、缺失信息处理和完成检查 |
| [skills/](skills/) | 可复用的工作流、模板和辅助工具 |
| Agent 通用包 | 原工作区入口为 agent_report_bundle/START_HERE.md；包内入口为 START_HERE.md |
| 物理学报模板目录 | 本地版式参考 |

实验报告模板编号、别名和设计说明以 report.md 及模板注册表为准。期刊风格是中文课程适配，不是官方投稿模板。内容规范更新后，应同步流程包的 references/ 并用导出脚本更新 agent_report_bundle/。

## 实验资料目录

每项实验独立存放，至少包含预习报告和实验报告目录：

    <实验标题>/
    ├── <实验标题>.pdf
    ├── preview_report/
    └── lab_report/

图示仅用于说明目录结构；实验资料的具体组织和存储边界见 agents.md，报告内容与检查要求见 preview.md 和 report.md。
