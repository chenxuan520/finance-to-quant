#!/usr/bin/env python3
"""Check generated ebook HTML for basic structural issues."""

import glob
import os
import re
import sys
from html.parser import HTMLParser


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr", "path", "rect", "circle",
    "line", "polyline", "polygon",
}


class Balancer(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
            return
        if tag in self.stack:
            self.errors.append(f"错位 </{tag}>")
            while self.stack and self.stack[-1] != tag:
                self.stack.pop()
            if self.stack:
                self.stack.pop()
            return
        self.errors.append(f"多余 </{tag}>")


def check_file(path):
    html = open(path, encoding="utf-8").read()
    parser = Balancer()
    parser.feed(html)
    problems = []
    leftovers = [tag for tag in parser.stack if tag not in ("html", "body", "main")]
    if parser.errors:
        problems.append("标签错位: " + "; ".join(parser.errors[:8]))
    if leftovers:
        problems.append("未闭合残留: " + ", ".join(leftovers[:8]))
    nums = [int(x) for x in re.findall(r"<h2>(\d+)\.", html)]
    if nums and nums != list(range(1, len(nums) + 1)):
        problems.append(f"h2 编号不连续: {nums}")
    return problems


def main():
    os.chdir(BASE_DIR)
    files = sorted(glob.glob("chapter-*.html")) + ["index.html", "glossary.html"]
    files = [f for f in files if os.path.exists(f)]
    bad = 0
    for path in files:
        problems = check_file(path)
        if problems:
            bad += 1
            print(path + ":")
            for problem in problems:
                print("  - " + problem)
    if bad:
        print(f"结构校验失败: {bad} 个文件有问题")
        return 1
    print(f"结构校验通过: {len(files)} 个文件")
    return 0


if __name__ == "__main__":
    sys.exit(main())
