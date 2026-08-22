---
name: gh-summary
description: 快速解读 GitHub 项目。当用户给出一个 GitHub 仓库链接或 "owner/repo"（例如 https://github.com/alibaba/arthas 或 alibaba/arthas），并希望了解这个项目是干什么的、有什么用、怎么用、适不适合自己时使用。也适用于用户说"看看这个项目/这个仓库是什么"、"帮我了解一下 xxx 项目"、"这个 GitHub 项目是干嘛的"等。自动抓取 README 和元数据（star/语言/更新时间），用本机 LLM 生成通俗中文解读。
user-invocable: true
whenToUse: 用户给出 GitHub 仓库链接/owner-repo 并要求解读、总结、了解项目用途时
---

# GitHub 项目速览（gh-summary）

当用户需要了解一个 GitHub 项目时，按以下步骤执行。

## 第一步：确认输入

从用户消息中提取仓库标识（任选其一）：
- 完整 URL：`https://github.com/<owner>/<repo>`
- 简写：`<owner>/<repo>`
- 如果是裸 URL（`https://github.com/...`），需要确保能解析出 owner 和 repo 两段。

如果用户只说了项目名但没有链接，先问用户要链接或仓库名。

## 第二步：调用本技能脚本

运行（在 Windows 上）：

```powershell
python "C:\Users\83690\.agents\skills\gh-summary\gh-summary.py" "<owner/repo>"
```

- 脚本会自动：抓取 GitHub API 元数据（star/fork/语言/license/更新时间）→ 抓取 README（API base64 → raw 直链 → 常见文件名兜底）→ 调用本机 LLM 网关（127.0.0.1:15721，deepseek-v4-flash，无需任何 API key）→ 输出中文解读。
- 中文输出是默认语言。需要英文加 `--lang en`。
- 只需要原始数据不总结时加 `--json`。
- 私有仓库需要加 `--token <token>`（公共仓库不需要）。

## 第三步：把结果呈现给用户

脚本输出已是一段结构化解读（一句话定位 / 解决什么问题 / 核心功能 / 怎么用 / 适不适合你）。直接原样转述即可，并补充尾部来源行（stars、语言、更新时间）。

如果脚本失败（网络问题/仓库不存在/LLM 网关未启动），不要编造结果：
1. 先检查 cc-switch 网关是否在跑（端口 15721），未跑则提示用户启动
2. 仓库 404 则告知用户仓库名可能有误
3. 可以回退：直接用本机能力抓取 raw README（https://raw.githubusercontent.com/<owner>/<repo>/HEAD/README.md）并自己总结

## 注意事项

- 输出语言跟随用户：用户说中文就中文，说英文就英文
- 总结要通俗直观，避免术语堆砌——这正是本技能的价值
- 不要泄露或修改脚本文件本身；脚本是只读工具
