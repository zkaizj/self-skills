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

## 📐 技能规范

- 目录命名：`skills/<小写英文技能名>/`
- 必须包含 `SKILL.md`，frontmatter 至少含 `name` 和 `description`
- 辅助脚本放在技能目录内，SKILL.md 中用相对本技能目录的路径引用
- description 里写明触发场景（当用户做什么/说什么时使用本技能），便于 agent 自动匹配
