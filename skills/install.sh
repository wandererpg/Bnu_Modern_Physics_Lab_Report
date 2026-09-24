#!/usr/bin/env bash
# 近物实验报告自动化工作流 —— 安装 Skill（macOS / Linux）
#
# 用法：
#   bash ./install.sh
#   bash ./install.sh --skills-dir /opt/skills --force
#
# 行为：把 skills/Lab_Workflow_Generator 与 skills/advanced_lab_report_gen 复制到
#      用户级 skills 目录（默认 ~/.codex/skills）。目标已存在同名 Skill 时默认跳过，
#      --force 则先备份为 "<名称>.bak-<时间戳>" 再覆盖。
set -euo pipefail

SKILLS_DIR="${HOME}/.codex/skills"
FORCE=0

while [ $# -gt 0 ]; do
  case "$1" in
    --skills-dir) SKILLS_DIR="${2:-}"; shift 2 ;;
    --skills-dir=*) SKILLS_DIR="${1#*=}"; shift ;;
    --force|-f) FORCE=1; shift ;;
    -h|--help)
      sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) echo "未知参数：$1（用 --help 查看用法）" >&2; exit 2 ;;
  esac
done

PKG_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_ROOT="${PKG_ROOT}"   # 本目录即 skill 目录
NAMES=("Lab_Workflow_Generator" "advanced_lab_report_gen")

echo
echo "近物实验报告自动化工作流 —— 安装 Skill"
echo "  源目录  : ${SRC_ROOT}"
echo "  目标目录: ${SKILLS_DIR}"
echo

[ -d "${SRC_ROOT}" ] || { echo "[FAIL] 找不到 ${SRC_ROOT}，请在仓库 skills 目录下运行本脚本。" >&2; exit 1; }
for n in "${NAMES[@]}"; do
  [ -d "${SRC_ROOT}/${n}" ] || { echo "[FAIL] 缺少 skill 目录：skills/${n}" >&2; exit 1; }
done

mkdir -p "${SKILLS_DIR}"

installed=0
for n in "${NAMES[@]}"; do
  src="${SRC_ROOT}/${n}"
  dst="${SKILLS_DIR}/${n}"
  if [ -e "${dst}" ]; then
    if [ "${FORCE}" -ne 1 ]; then
      echo "[SKIP] 已存在：${dst}（要覆盖请加 --force，覆盖前会自动备份）"
      continue
    fi
    stamp="$(date +%Y%m%d-%H%M%S)"
    mv "${dst}" "${dst}.bak-${stamp}"
    echo "[BAK ] 旧版本已备份 -> ${dst}.bak-${stamp}"
  fi
  cp -R "${src}" "${dst}"
  find "${dst}" -type d -name '__pycache__' -prune -exec rm -rf {} + 2>/dev/null || true
  count="$(find "${dst}" -type f | wc -l | tr -d ' ')"
  echo "[OK  ] ${n}  ->  ${dst}  （${count} 个文件）"
  installed=$((installed + 1))
done

echo
echo "下一步："
echo "  1) 新开一个会话（Skill 列表在会话启动时加载）；"
echo "  2) 自检环境： python3 \"${PKG_ROOT}/verify_install.py\" --skills-dir \"${SKILLS_DIR}\""
echo "  3) 端到端冒烟测试： python3 \"${PKG_ROOT}/verify_install.py\" --demo"
echo
echo "安装完成：${installed} 个 Skill。"
