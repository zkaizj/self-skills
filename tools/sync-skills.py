# -*- coding: utf-8 -*-
"""
sync-skills.py - 自建技能自动同步到 self-skills 仓库

约定（README 已固化）：
  凡是自建的 skills 统一提交到 https://github.com/zkaizj/self-skills.git
  本机工作副本: E:/AI/dsh-workspace/self-skills/

用法:
  python sync-skills.py                          # 同步全部技能（复制 -> 提交 -> 推送）
  python sync-skills.py --skip-push              # 只复制+提交，不推送
  python sync-skills.py --dry-run                # 只显示会复制哪些技能，不做任何改动

流程:
  1. 扫描本机技能目录 C:/Users/83690/.agents/skills/ 下所有自建技能
     （以 SKILL.md 里 frontmatter 存在标记 self-built: true 为准，或手工指定列表）
  2. 复制到 self-skills/skills/<name>/（更新 SKILL.md 与辅助脚本）
  3. git add + commit（feat(skills): <name> - ...）
  4. git push（SSH）
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

# ---------- 配置 ----------
SKILLS_HOME = r"C:\Users\83690\.agents\skills"        # 本机技能目录
REPO_ROOT = r"E:\AI\dsh-workspace\self-skills"        # 仓库工作副本
SKILLS_DIR_IN_REPO = os.path.join(REPO_ROOT, "skills")

# 显式认定的"自建技能"（本会话/本人创建，纳入自动同步）
# 也可以给 SKILL.md 加 frontmatter 字段 self-built: true 自动识别
SELF_BUILT = [
    "gh-summary",
    # 2026-08-22 挑选安装：superpowers 3 个 + mattpocock 2 个（适合当前 Windows+DSH 环境）
    "verification-before-completion",
    "writing-skills",
    "subagent-driven-development",
    "handoff",
    "code-review",
]

GIT_IDENTITY = ["-c", "user.name=Mr.zk", "-c", "user.email=836901721@qq.com"]


def run_git(repo, *args, check=True):
    cmd = ["git", "-C", repo, *args]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r


def skill_is_self_built(name):
    """SKILL.md frontmatter 里有 self-built: true 也算自建；否则看显式列表"""
    if name in SELF_BUILT:
        return True
    md = os.path.join(SKILLS_HOME, name, "SKILL.md")
    if os.path.exists(md):
        with open(md, encoding="utf-8", errors="replace") as f:
            head = f.read(3000)
        m = re.search(r"self-built:\s*(true|yes|1)", head)
        return bool(m)
    return False


def main():
    ap = argparse.ArgumentParser(description="自建技能同步到 self-skills 仓库")
    ap.add_argument("--skip-push", action="store_true", help="只复制+提交，不推送")
    ap.add_argument("--dry-run", action="store_true", help="只显示计划，不做改动")
    args = ap.parse_args()

    if not os.path.isdir(SKILLS_HOME):
        print(f"[ERROR] 技能目录不存在: {SKILLS_HOME}")
        sys.exit(1)

    # 1. 扫描自建技能
    candidates = [d for d in os.listdir(SKILLS_HOME) if os.path.isdir(os.path.join(SKILLS_HOME, d))]
    built = [n for n in candidates if skill_is_self_built(n)]
    if not built:
        print("[INFO] 没有发现自建技能（SELF_BUILT 列表为空且无 self-built: true 标记）")
        return

    print(f"[1/4] 发现自建技能: {', '.join(built)}")
    if args.dry_run:
        print("[DRY-RUN] 将复制以下技能到仓库:")
        for n in built:
            print(f"  - skills/{n}/")
        return

    # 2. 复制到仓库
    os.makedirs(SKILLS_DIR_IN_REPO, exist_ok=True)
    changed = []
    for name in built:
        src = os.path.join(SKILLS_HOME, name)
        dst = os.path.join(SKILLS_DIR_IN_REPO, name)
        shutil.rmtree(dst, ignore_errors=True)
        shutil.copytree(src, dst)
        changed.append(name)
        print(f"  [复制] skills/{name}/ <- {src}")

    # 3. 提交
    run_git(REPO_ROOT, *GIT_IDENTITY, "add", "-A")
    r = run_git(REPO_ROOT, *GIT_IDENTITY, "status", "--porcelain", check=False)
    if not r.stdout.strip():
        print("[3/4] 无变更，跳过提交")
    else:
        msg = "feat(skills): " + ", ".join(changed) + " - 同步自建技能"
        run_git(REPO_ROOT, *GIT_IDENTITY, "commit", "-m", msg)
        print(f"[3/4] 已提交: {msg}")

    # 4. 推送
    if args.skip_push:
        print("[4/4] 跳过推送（--skip-push）")
    else:
        run_git(REPO_ROOT, "push")
        print("[4/4] 已推送到 https://github.com/zkaizj/self-skills.git")

    print("\n完成 ✅")


if __name__ == "__main__":
    main()
