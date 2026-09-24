# 开源发布检查清单 / Publishing Checklist

## 代码与文档 / Code & Docs

- [ ] README.md（中英双语，含徽章）
- [ ] LICENSE（MIT）
- [ ] SKILL.md（自包含；当前约 23 KB）
- [ ] docs/installation.md
- [ ] docs/usage.md
- [ ] docs/training_data.md
- [ ] docs/customization.md

## 示例 / Examples

- [ ] examples/光泵磁共振实验_报告.md
- [ ] examples/光泵磁共振实验_报告.pdf（若有；当前测试未编译 PDF，暂缺）
- [ ] examples/sample_data/光泵磁共振_拟真数据.csv
- [ ] examples/sample_data/光泵磁共振_讲义摘要.txt

## 训练数据 / Training Data

- [ ] training_output/require_spec.json
- [ ] training_output/report_style_analysis.json
- [ ] training_output/experiment_library.json
- [ ] training_output/style_profile.json
- [ ] training_output/training_summary.md

## 清理 / Cleanup

- [ ] 移除所有“待补充”占位符（或改写为通用说明）
- [ ] **检查敏感信息**：将真实姓名/学号/教师姓名替换为化名或占位符（示例：学生A、学生B、学生C、反例D、[指导教师姓名]）
- [ ] 移除绝对路径，全部改用相对路径或 `~/.codex/skills/` 占位符
- [ ] 复核 examples 示例数据确为拟真数据，不包含他人真实实验记录

## 发布 / Release

- [ ] 推送到 GitHub 公开仓库
- [ ] 添加仓库描述与主题标签：`lab-report`、`physics`、`codex-skill`
- [ ] 发布 Release（v1.0.0）
- [ ] README 添加演示截图/录屏
- [ ] 若包含真实课程材料（讲义摘要），确认版权与引用许可

- ✅ 敏感信息已匿名化（学号掩码、姓名化名、路径占位）
