# -*- coding: utf-8 -*-
"""
gh-summary.py - GitHub 项目速览工具
输入仓库 URL（如 https://github.com/zkaizj/pm2-console 或 zkaizj/pm2-console），
自动抓取 README + 元数据（star/fork/语言/更新时间），调用本机 LLM 生成中文直观解读。

用法:
  python gh-summary.py zkaizj/pm2-console
  python gh-summary.py https://github.com/zkaizj/pm2-console
  python gh-summary.py zkaizj/pm2-console --lang en    # 英文输出
  python gh-summary.py zkaizj/pm2-console --json       # 只输出原始 JSON（不调 LLM）
"""
import argparse
import json
import re
import sys
import urllib.request

# Windows 控制台默认 GBK，强制 UTF-8 输出避免 emoji/中文报错
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

LLM_URL = "http://127.0.0.1:15721/v1/messages"
LLM_MODEL = "deepseek-v4-flash"
API = "https://api.github.com"

PROMPT_TEMPLATE = """你是 GitHub 项目解读助手。下面是一个 GitHub 仓库的元数据和 README 内容，请用{lang}输出一段直观、通俗的中文解读，让完全不懂这个项目的人也能明白。要求：

1. **一句话定位**：这个项目是干什么的（用一句话说清楚）
2. **解决什么问题**：它解决什么痛点/场景，什么时候用得上
3. **核心功能**：3-6 条要点式列出主要能力
4. **怎么用**：最简的使用方式（安装/启动/访问）
5. **适不适合你**：一句话判断这类用户是否值得用

风格：口语化、直观、避免堆砌专业术语；总字数 300 字以内。

===== 仓库元数据 =====
{meta}

===== README 内容 =====
{readme}
"""


def fetch(url, token=None):
    req = urllib.request.Request(url, headers={
        "User-Agent": "gh-summary-local",
        "Accept": "application/vnd.github+json",
    })
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_readme_text(repo_full):
    """依次尝试：API 的 readme 端点（base64）→ raw 直链 → 常见文件名"""
    attempts = [
        (f"{API}/repos/{repo_full}/readme", True),
        (f"https://raw.githubusercontent.com/{repo_full}/HEAD/README.md", False),
        (f"https://raw.githubusercontent.com/{repo_full}/HEAD/readme.md", False),
        (f"https://raw.githubusercontent.com/{repo_full}/HEAD/README.MD", False),
    ]
    for url, is_api in attempts:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "gh-summary-local"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                if is_api:
                    data = json.loads(resp.read().decode("utf-8"))
                    import base64
                    return base64.b64decode(data.get("content", "")).decode("utf-8", "replace")
                return resp.read().decode("utf-8", "replace")
        except Exception:
            continue
    return None


def call_llm(system_prompt, user_content):
    body = json.dumps({
        "model": LLM_MODEL,
        "max_tokens": 1024,
        "system": [{"type": "text", "text": system_prompt}],
        "messages": [{"role": "user", "content": user_content}],
    }).encode("utf-8")
    req = urllib.request.Request(LLM_URL, data=body, headers={
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    texts = [c.get("text", "") for c in data.get("content", []) if c.get("type") == "text"]
    return "".join(texts).strip()


def parse_repo(raw):
    m = re.search(r"github\.com/([^/\s]+)/([^/\s#?]+)", raw)
    if m:
        return f"{m.group(1)}/{m.group(2)}"
    raw = raw.strip().rstrip("/")
    if re.match(r"^[\w.-]+/[\w.-]+$", raw):
        return raw
    raise ValueError(f"无法解析仓库地址: {raw}")


def main():
    ap = argparse.ArgumentParser(description="GitHub 项目速览")
    ap.add_argument("repo", help="仓库地址，如 zkaizj/pm2-console 或完整 URL")
    ap.add_argument("--lang", default="中文", help="输出语言（默认中文）")
    ap.add_argument("--json", action="store_true", help="只输出原始元数据+README，不调 LLM")
    ap.add_argument("--token", default=None, help="GitHub token（可选，公共仓库不需要）")
    args = ap.parse_args()

    repo_full = parse_repo(args.repo)
    print(f"[1/3] 获取仓库元数据: {repo_full} ...")

    try:
        meta = fetch(f"{API}/repos/{repo_full}", args.token)
    except Exception as e:
        print(f"[ERROR] 仓库不存在或无法访问: {e}", file=sys.stderr)
        sys.exit(1)

    meta_lines = [
        f"名称: {meta.get('full_name')}",
        f"描述: {meta.get('description') or '（无）'}",
        f"语言: {meta.get('language')}",
        f"Star: {meta.get('stargazers_count')}",
        f"Fork: {meta.get('forks_count')}",
        f"License: {(meta.get('license') or {}).get('spdx_id') or '（无）'}",
        f"最近更新: {meta.get('updated_at')}",
        f"主页: {meta.get('homepage') or '（无）'}",
    ]
    print("[2/3] 抓取 README ...")
    readme = fetch_readme_text(repo_full)
    if readme is None:
        print("[WARN] 未找到 README，仅用元数据总结", file=sys.stderr)
        readme = "（此仓库没有 README）"

    # README 太长就截断（保留开头 8000 字符，README 通常开头最有信息量）
    if len(readme) > 8000:
        readme = readme[:8000] + "\n...（已截断）"

    if args.json:
        print(json.dumps({"meta": meta_lines, "readme": readme[:2000]}, ensure_ascii=False, indent=2))
        return

    print("[3/3] 调用本机 LLM 生成解读 ...")
    try:
        summary = call_llm(
            PROMPT_TEMPLATE.format(lang=args.lang, meta="\n".join(meta_lines), readme=readme),
            f"请解读这个 GitHub 项目：{repo_full}"
        )
    except Exception as e:
        print(f"[ERROR] LLM 调用失败: {e}", file=sys.stderr)
        print("原始数据如下，供人工查看：")
        print("\n".join(meta_lines))
        print("\n----- README 前 2000 字 -----")
        print(readme[:2000])
        sys.exit(1)

    print("\n" + "=" * 60)
    print("[项目] " + meta.get('full_name'))
    print("=" * 60)
    print(summary)
    print("=" * 60)
    print(f"（来源: https://github.com/{repo_full} · {meta.get('stargazers_count')} stars · {meta.get('language')} · 更新于 {meta.get('updated_at', '')[:10]}）")


if __name__ == "__main__":
    main()
