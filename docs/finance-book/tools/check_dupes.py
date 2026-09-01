#!/usr/bin/env python3
"""检查 callout 是否与紧邻正文段重复。

背景:历史上有 callout 把正文整段复制过去重新讲一遍,读者“同一句话读两遍”;
从 2026-08-31 起设个 gate,相似度超过阈值即失败。
"""
from __future__ import annotations

import difflib
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MARKER_PREFIXES = (
    "划重点:",
    "一句话记住:",
    "常见误区:",
    "记住这一条:",
    "注意:",
    "注意,",
    "先记住一个反直觉的结论:",
    "这条记住:",
)
SIMILARITY_LIMIT = 0.85


def _clean(text: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", text)).strip()


def main() -> int:
    problems: list[str] = []
    for path in sorted(ROOT.glob("chapter-*.html")):
        raw = path.read_text(encoding="utf-8")
        raw = re.sub(r"<script.*?</script>", "", raw, flags=re.S)
        # 先把 callout 整块从“正文流”里抠走
        callouts = re.findall(
            r'<div class="callout[^"]* reveal"><span class="callout__title">([^<]*)</span><p>(.*?)</p></div>',
            raw,
            re.S,
        )
        body = re.sub(
            r'<div class="callout[^"]* reveal">.*?</div>',
            "",
            raw,
            flags=re.S,
        )
        paragraphs = [
            _clean(m.group(1))
            for m in re.finditer(r"<p>(.{60,2000}?)</p>", body, re.S)
        ]
        for title, body_html in callouts:
            b = _clean(body_html)
            for marker in MARKER_PREFIXES:
                if b.startswith(marker):
                    b = b[len(marker):].strip()
                    break
            best, best_p = 0.0, ""
            for p in paragraphs:
                r = difflib.SequenceMatcher(None, b[:500], p[:500]).ratio()
                if r > best:
                    best, best_p = r, p
            if best > SIMILARITY_LIMIT:
                problems.append(
                    f"{path.name}: callout“{title}”与正文相似度 {best:.2f}\n"
                    f"  开头:{b[:60]}\n  与正文:{best_p[:60]}"
                )
    if problems:
        print(f"callout 重复检查失败({len(problems)} 处):")
        for p in problems:
            print(" ", p)
        return 1
    print(f"callout 重复检查通过:无相似度超过 {SIMILARITY_LIMIT} 的 callout")
    return 0


if __name__ == "__main__":
    sys.exit(main())
