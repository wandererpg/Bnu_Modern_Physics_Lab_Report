# 第三方资产与出处

本包的**自有部分**（工作流 Skill、文档、安装与自检脚本）以 MIT 发布。
以下随包分发的第三方资产**版权归各自作者/机构**，此处列明出处与许可，便于合规分享与二次分发。

## 1. 清华近代物理实验报告模板（`thuemp`）

| 项 | 内容 |
| --- | --- |
| 位置 | `skills/Lab_Workflow_Generator/assets/thu_template/`（`thuemp.cls`、`TempExample.tex/.bib`、`image/`） |
| 出处 | THU_emp —— 清华大学近代物理实验报告 LaTeX 模板（**非官方**） |
| 许可 | 上游未附明确许可证；上游 README 自述为"非官方模板" |
| 使用建议 | 课程内部使用无碍；**公开分发/发表前请自行确认授权**，或改用学校下发的官方模板 |
| 注意 | `TempExample.tex` 内自带示例学号 `2018123236` 与示例邮箱 `lmytime@hotmail.com`，均为上游占位符，**使用前必须替换** |

## 2. 物理学报（Acta Physica Sinica）模板

| 项 | 内容 |
| --- | --- |
| 位置 | `skills/Lab_Workflow_Generator/assets/aps_template/`（`physics_report.sty`、`acta_physica_sinica.bst/.dbj`、`template.tex/.pdf` 等） |
| 出处 | "LaTeX Template for ActaPhysicaSinica"，作者 Ddddavid（见该目录 `README.md`） |
| 许可 | **MIT License**，Copyright (c) 2022 Ddddavid（见 `assets/aps_template/LICENSE`） |
| 说明 | 本包中作为**备选**模板；默认模板是清华 `thuemp` |

## 3. 校徽图片

| 项 | 内容 |
| --- | --- |
| 位置 | `skills/Lab_Workflow_Generator/assets/branding/`（`bnu_logo.png`、`校徽.webp`） |
| 版权 | 归学校所有，仅作报告首页排版素材 |
| 使用建议 | 非本校使用时请替换为自己学校的标识，或删除这两个文件（模板不引用它们也能编译） |

## 4. 可选（**未随包分发**）的第三方 Skill

本流水线**不依赖**它们的代码，仅在其 SKILL.md 中被引为"约定/思维"参考。按需自行安装：

| Skill | 出处 | 安装 |
| --- | --- | --- |
| `lab-assist` | GitHub `Daigui233/lab-assist` | `npx skills add https://github.com/Daigui233/lab-assist --skill lab-assist` |
| `lab-report-writer` | GitHub `mingchen666/Reviva` | `npx skills add https://github.com/mingchen666/Reviva --skill lab-report-writer` |

## 5. 关于个人信息

- 随包的文本核心 `advanced_lab_report_gen` 是**脱敏版**：语料与训练摘要中的姓名/学号
  已化名为「学生 A / 学生 B / 学生 C」、教师姓名写成 `[指导教师姓名]`、本机绝对路径
  （`C:\Users\<用户名>\...`）已改写为 `~/.codex/skills/...`。
- 随包的 `training_output/*.json` 同为脱敏版，**不含真实姓名、学号或联系方式**。
- 本包**不含**任何真实实验记录、讲义原件或课程材料。

## 6. 二次分发前检查清单

- [ ] 替换 `TempExample.tex` / `template.tex` 中的示例学号与邮箱
- [ ] 确认 `thuemp` 模板的授权情况（或替换为自己学校的模板）
- [ ] 若删改校徽素材，确认模板仍能编译（`bnu_logo.png` 未被模板引用）
- [ ] 不要把自己的实验工作区（含真实姓名/学号/数据）一起打进分享包
- [ ] 保留本文件与各目录下的 `LICENSE`/`README.md`
