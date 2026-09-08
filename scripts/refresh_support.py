#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
refresh_support.py — nevermind.skill 宿主清单联网刷新器（C3 节奏的后端）

职责
----
本 skill 的「宿主门禁」依赖一份权威清单 data/supported-hosts.txt（R3 内置）。
清单每约 3 天应联网与 tokens.ci 官方核对一次是否有增删（见 SKILL.md「宿主门禁
第 3 节 C3」）。本脚本就是那一步的真实执行后端：

  1. 抓 https://tokens.ci/docs 的 Supported clients 段（官方权威源，HTML）。
  2. 解析出全部官方客户端名。
  3. 与 data/supported-hosts.txt 比对；有差异 → 以官方为准回写内置清单。
  4. 写 support_cache.json（last_checked + source + hosts 快照 + changed），
     供「每次新会话首次接触」判断是否已过 3 天刷新点。

用法
----
  python3 scripts/refresh_support.py            # 联网刷新（写 cache，必要时回写清单）
  python3 scripts/refresh_support.py --dry-run  # 只比对打印，不写任何文件

设计约定
--------
- 仅用 Python 标准库（urllib / re / json / os / sys / datetime），零第三方依赖，
  任何装了 Python 3.8+ 的环境都能跑，无需 pip install。
- 联网失败/解析异常时【不写假成功】：
    * support_cache.json 保持原状（不伪造 last_checked）。
    * data/supported-hosts.txt 不被动。
    * 返回退出码 1，并在 stderr 给出可读提示。
  这与 SKILL.md「离线/联网失败时不要假称查过」一致。

FALLBACK（非必要不用）
-----------------------
主路径是用上面 Python 的 urllib 直接抓取。若在极特殊网络/代理环境里 Python
HTTPS 出栈走不通，可用系统 curl 抓 HTML 存临时文件，再让脚本只做本地解析：

  # 1) 先用 curl 抓到本地（手动执行，仅当 Python 直连失败才需要）：
  curl -fsSL -A "Mozilla/5.0" https://tokens.ci/docs -o /tmp/tokens_docs.html

  # 2) 再让本脚本只解析本地文件、不回写网络（同 --dry-run 精神，仅比对）：
  python3 scripts/refresh_support.py --from-file /tmp/tokens_docs.html

  # 3) 确认解析无误、想要真正回写时，可再正常跑一次（网络通时）。
这是“fallback 方案”：默认【不要】用它——优先让脚本自己联网。只有 Python
直连被网络层挡住时才考虑 curl 这条降级路。

目录/文件
---------
  data/supported-hosts.txt  内置权威清单（R3），本脚本可能回写它。
  support_cache.json        联网快照 + 上次核对时间（gitignored，不入仓库）。
"""

import os
import re
import sys
import json
import datetime
import urllib.request

# ---------------------------------------------------------------------------
# 常量（脚本被调用时，以本文件所在位置的上级目录为仓库根，保证从任何 cwd 都能跑）
# ---------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)  # scripts/ 的上一级 = 仓库根
HOSTS_FILE = os.path.join(REPO, "data", "supported-hosts.txt")
CACHE_FILE = os.path.join(REPO, "support_cache.json")
DOCS_URL = "https://tokens.ci/docs"
SOURCE_LABEL = DOCS_URL + "#supported-clients"

# 解析正则：官网 Supported clients 段每项形如
#   <li ...><img src="/clients/client-amp.png" .../><span class="...truncate...">Amp</span></li>
# 命中 img 的 /clients/client-* 后紧跟的 truncate span 内文本 = 客户端名。
# 大小写不敏感、允许 img 自闭合写法差异。
NAME_RE = re.compile(
    r'<img\s+src="/clients/client-[^"]+"[^>]*/>'
    r'<span\s+class="[^"]*truncate[^"]*">([^<]+)</span>',
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------
def log(msg: str) -> None:
    print(msg, file=sys.stderr)  # 常规进度走 stderr，stdout 只留干净结果供管道用


def fetch_html() -> str:
    """主路径：Python urllib 直连官网，返回 HTML 文本。失败抛异常。"""
    req = urllib.request.Request(
        DOCS_URL,
        headers={"User-Agent": "Mozilla/5.0 nevermind-refresh/0.1"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw = resp.read()
    return raw.decode("utf-8", "replace")


def parse_hosts(html: str):
    """从官网 HTML 提取官方客户端名清单，保序去重。"""
    seen = []
    for name in NAME_RE.findall(html):
        n = name.strip()
        if n and n not in seen:
            seen.append(n)
    return seen


def read_current_hosts():
    """读内置清单 data/supported-hosts.txt。文件不存在视为空清单。"""
    if not os.path.exists(HOSTS_FILE):
        return []
    with open(HOSTS_FILE, encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip()]


def write_hosts(names) -> bool:
    """以官方清单回写内置清单。返回是否发生了写文件。"""
    body = "\n".join(names) + "\n"
    with open(HOSTS_FILE, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)
    return True


def read_cache():
    """读 support_cache.json；不存在或损坏返回 None。"""
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def write_cache(names, changed: bool) -> None:
    """写 support_cache.json：last_checked(UTC now) + source + hosts 快照 + changed。"""
    payload = {
        "last_checked": datetime.datetime.now(datetime.timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
        "source": SOURCE_LABEL,
        "hosts": names,
        "changed": changed,
    }
    with open(CACHE_FILE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    from_file = None
    if "--from-file" in args:
        i = args.index("--from-file")
        if i + 1 < len(args):
            from_file = args[i + 1]

    if from_file:
        # FALLBACK 路径：不联网，只解析已抓好的本地 HTML 文件做比对（见文件头注释）。
        log(f"[fallback] 从本地文件解析（不联网）: {from_file}")
        try:
            with open(from_file, encoding="utf-8") as f:
                html = f.read()
        except OSError as e:
            log(f"无法读取本地文件: {e}")
            return 1
    else:
        # 主路径：联网抓取。
        log(f"[main] 联网抓取官网: {DOCS_URL}")
        try:
            html = fetch_html()
        except Exception as e:  # urllib 各类网络/HTTP 错误都走这里
            log(f"[main] Python 联网失败: {type(e).__name__}: {e}")
            log("主路径不可用。如需降级，参照本脚本头部注释的 FALLBACK(curl) 方案"
                "抓 HTML 到本地后再用 --from-file 解析。")
            return 1  # 不写假成功，保持 cache/内置清单原状

    official = parse_hosts(html)
    if not official:
        log("解析到 0 个客户端名 —— 官网结构可能变动，拒绝覆盖，返回错误。")
        return 1

    current = read_current_hosts()
    added = [n for n in official if n not in current]
    removed = [n for n in current if n not in official]
    changed = bool(added or removed)

    log(f"官方清单 {len(official)} 项；内置清单 {len(current)} 项。")
    if changed:
        log(f"  新增 {len(added)}: {added if added else '(无)'}")
        log(f"  移除 {len(removed)}: {removed if removed else '(无)'}")
    else:
        log("  无差异，内置清单已是最新。")

    if dry_run or from_file:
        # --dry-run：只报告不写。--from-file 属降级比对，同样不擅自回写网络清单。
        log("dry-run/本地比对模式：未写 support_cache.json、未改内置清单。")
        print(json.dumps({"official": len(official), "current": len(current),
                          "added": added, "removed": removed, "changed": changed},
                         ensure_ascii=False, indent=2))
        return 0

    # 正常模式：以官方为准回写（若有差异），并写缓存。
    if changed:
        write_hosts(official)
        log(f"已按官方回写内置清单 data/supported-hosts.txt（{len(official)} 项）。")
    write_cache(official, changed)
    log(f"已写 support_cache.json（last_checked 更新，changed={changed}）。")
    print(json.dumps({"official": len(official), "current": len(current),
                      "added": added, "removed": removed, "changed": changed,
                      "cache_written": True}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
