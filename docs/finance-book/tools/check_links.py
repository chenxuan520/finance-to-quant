#!/usr/bin/env python3
"""Check local links in the generated ebook."""

import glob
import os
import re
import sys


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def explicit_ids(html):
    return set(re.findall(r'\bid="([^"]+)"', html))


def main():
    os.chdir(BASE_DIR)
    files = sorted(glob.glob("chapter-*.html")) + ["index.html", "glossary.html"]
    files = [f for f in files if os.path.exists(f)]
    ids_by_file = {path: explicit_ids(open(path, encoding="utf-8").read()) for path in files}
    bad = []
    total = 0
    for path in files:
        html = open(path, encoding="utf-8").read()
        for href in re.findall(r'href="([^"]+)"', html):
            if href.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target, _, anchor = href.partition("#")
            if not target:
                target = path
            if target.endswith(".html"):
                total += 1
                if target not in ids_by_file and not os.path.exists(target):
                    bad.append((path, href, "file-missing"))
                elif anchor and anchor not in ids_by_file.get(target, set()):
                    bad.append((path, href, "anchor-missing"))
            elif target.startswith("assets/"):
                total += 1
                if not os.path.exists(target):
                    bad.append((path, href, "asset-missing"))
    print(f"本地链接: {total}")
    print(f"失效: {len(bad)}")
    for src, href, why in bad:
        print(f"  {src} -> {href} [{why}]")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
