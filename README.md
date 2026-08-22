# self-skills · 自有技能包

> 自己实践中整理的 **agent skills**（DSH / Claude Code / Codex 等支持 SKILL.md 规范的工具可直接安装使用）。
> 每个技能 = 一个目录：`skills/<技能名>/SKILL.md`（+ 辅助脚本）。

## 📦 技能清单

| 技能 | 目录 | 用途 |
|------|------|------|
| **gh-summary** | `skills/gh-summary/` | 快速解读 GitHub 项目：输入仓库链接 → 抓 README + 元数据（star/语言/更新时间）→ 调用本机 LLM 生成通俗中文解读（一句话定位 / 解决什么问题 / 核心功能 / 怎么用 / 适不适合你）|

## 🛠 如何安装一个技能

把对应目录复制到你的 agent 技能目录即可，例如 DSH：

```powershell
# Windows
Copy-Item -Recurse skills\gh-summary "$env:USERPROFILE\.agents\skills\gh-summary"
```

> Claude Code: `~/.claude/skills/` · Codex: `~/.codex/skills/` · DSH: `~/.agents/skills/`

## 🤖 自动提交约定（重要）

**凡是自建的 skills，统一提交到本仓库（`self-skills`）。**

规则：
- 新技能创建后 → 复制到 `skills/<技能名>/` → 更新上方清单 → 提交推送
- 技能修改 → 同步更新本仓库
- 提交信息用 `feat(skills): <技能名> - 一句话说明` 的格式
- 本机工作副本：`E:\AI\dsh-workspace\self-skills\`（SSH 远程：`git@github.com:zkaizj/self-skills.git`）

### 一键同步工具：`tools/sync-skills.py`（本仓库自带）

以后**新建或修改自建技能后，直接跑这个脚本**即可自动完成「复制到仓库 → git commit → SSH push」：

```bash
python tools/sync-skills.py          # 同步全部自建技能并推送
python tools/sync-skills.py --dry-run   # 先看会同步哪些，不做改动
python tools/sync-skills.py --skip-push # 只复制+提交，不推送
```

工作原理：
- 扫描本机技能目录 `C:\Users\83690\.agents\skills\`，找出**自建技能**
- 自建判定：脚本内置 `SELF_BUILT` 列表，或技能 `SKILL.md` frontmatter 标记 `self-built: true`
- 把技能目录整体复制到 `skills/<名>/` → `git add/commit`（信息格式 `feat(skills): <名> - ...`）→ `git push`
- 需要新增自建技能时，往 `SELF_BUILT` 列表加名字即可（或给 SKILL.md 加 `self-built: true`）

## 📐 技能规范

- 目录命名：`skills/<小写英文技能名>/`
- 必须包含 `SKILL.md`，frontmatter 至少含 `name` 和 `description`
- 辅助脚本放在技能目录内，SKILL.md 中用相对本技能目录的路径引用
- description 里写明触发场景（当用户做什么/说什么时使用本技能），便于 agent 自动匹配
