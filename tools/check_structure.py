#!/usr/bin/env python3
"""Check generated ebook HTML for basic structural issues."""

import glob
import html
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

import build_book


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
    nums = [int(x) for x in re.findall(r'<h2[^>]*>(?:<span class="case-study__label">[^<]*</span>\s*)?(\d+)\.', html)]
    if nums and nums != list(range(1, len(nums) + 1)):
        problems.append(f"h2 编号不连续: {nums}")
    return problems


def check_book_model():
    problems = []
    chapters = build_book.CHAPTERS
    visible_nums = [ch["num"] for ch in chapters]
    if visible_nums != list(range(len(chapters))):
        problems.append(f"公开章号不连续: {visible_nums}")

    used = [num for ch in chapters for num in ch["source_nums"]]
    duplicates = sorted(num for num in set(used) if used.count(num) > 1)
    source_nums = {ch["num"] for ch in build_book.SOURCE_CHAPTERS}
    expected = source_nums - set(build_book.EXCLUDED_SOURCE_CHAPTERS)
    missing = sorted(expected - set(used))
    unexpected = sorted(set(used) - expected)
    if duplicates:
        problems.append(f"源单元重复映射: {duplicates}")
    if missing:
        problems.append(f"源单元未映射: {missing}")
    if unexpected:
        problems.append(f"排除单元仍被映射: {unexpected}")

    for ch in chapters:
        han = sum(build_book.html_han_count(body) for _, body in ch["sections"])
        section_count = sum(
            1
            for unit in ch["units"]
            for title, _ in unit["sections"]
            if build_book.split_case_section_title(title)[0] is None
        )
        if han < 1200 or han > 10000:
            problems.append(f"第 {ch['num']} 章体量异常: {han} 汉字")
        if section_count > 25:
            problems.append(f"第 {ch['num']} 章非案例小节过多: {section_count}")
        for key in ("part", "part_badge", "part_question", "part_outcome"):
            if not ch.get(key):
                problems.append(f"第 {ch['num']} 章缺少 {key}")

    figure_total = sum(len(build_book.figure_anchors_for_chapter(ch)) for ch in chapters)
    expected_figures = sum(len(items) for items in build_book.CONCEPT_FIGURES.values())
    if figure_total != expected_figures:
        problems.append(f"概念图迁移不完整: {figure_total}/{expected_figures}")

    by_num = {ch["num"]: ch for ch in build_book.SOURCE_CHAPTERS}
    for legacy_num, anchors in build_book.CONCEPT_FIGURES.items():
        legacy_sources = build_book.LEGACY_CHAPTER_GROUPS[legacy_num]
        for keyword, _ in anchors:
            owners = []
            for source_num in legacy_sources:
                titles = [
                    build_book.clean_section_title(title)
                    for title, _ in by_num[source_num]["sections"]
                ]
                if any(keyword in title for title in titles):
                    owners.append(source_num)
            override = build_book.FIGURE_SOURCE_OVERRIDES.get((legacy_num, keyword))
            if not owners:
                problems.append(f"概念图锚点未命中: 旧章 {legacy_num} / {keyword}")
            elif len(owners) > 1 and override is None:
                problems.append(f"概念图锚点归属不唯一: 旧章 {legacy_num} / {keyword} -> {owners}")
            elif override is not None and override not in owners:
                problems.append(f"概念图人工归属无效: 旧章 {legacy_num} / {keyword} -> {override}")

    scan_paths = [
        Path(build_book.MANUSCRIPT_PATH),
        Path(build_book.ROOT).parents[1] / "README.md",
        Path(build_book.ROOT).parents[1] / "examples" / "README.md",
        *sorted((Path(build_book.ROOT).parents[1] / "examples").glob("*.py")),
    ]
    stale_pattern = re.compile(
        r"第(?:\s*\d+(?:\s*/\s*\d+)*\s*|[零一二三四五六七八九十百]+)章"
    )
    for path in scan_paths:
        text = path.read_text(encoding="utf-8")
        if stale_pattern.search(text):
            problems.append(f"仍有易失效的硬编码章号: {path.relative_to(Path(build_book.ROOT).parents[1])}")

    return problems


def check_generated_book():
    problems = []
    root = Path(BASE_DIR)
    chapters = build_book.CHAPTERS
    expected_files = {build_book.chapter_file(ch["num"]) for ch in chapters}
    actual_files = {path.name for path in root.glob("chapter-*.html")}
    if actual_files != expected_files:
        missing = sorted(expected_files - actual_files)
        extra = sorted(actual_files - expected_files)
        problems.append(f"生成章节文件不一致: 缺少 {missing}, 多出 {extra}")

    index_text = (root / "index.html").read_text(encoding="utf-8")
    checks = [
        (index_text.count('class="toc-card reveal"'), len(chapters), "首页章节卡"),
        (index_text.count('class="toc-part-block '), len(build_book.BOOK_STRUCTURE), "首页分部"),
        (
            index_text.count('class="roadmap-card"'),
            sum(part["kind"] == "main" for part in build_book.BOOK_STRUCTURE),
            "首页主线路线卡",
        ),
    ]
    for actual, expected, label in checks:
        if actual != expected:
            problems.append(f"{label}数量错误: {actual}/{expected}")

    for ch in chapters:
        path = root / build_book.chapter_file(ch["num"])
        if not path.exists():
            continue
        page = path.read_text(encoding="utf-8")
        expected_title = f"<h1>{html.escape(ch['title'], quote=True)}</h1>"
        if expected_title not in page:
            problems.append(f"第 {ch['num']} 章标题与模型不一致")
        if page.count('class="chapter-context ') != 1:
            problems.append(f"第 {ch['num']} 章路线定位缺失或重复")
        if page.count('<section class="chapter-handoff') != 1:
            problems.append(f"第 {ch['num']} 章承接说明缺失或重复")

    return problems


def main():
    os.chdir(BASE_DIR)
    files = sorted(glob.glob("chapter-*.html")) + ["index.html", "glossary.html"]
    files = [f for f in files if os.path.exists(f)]
    bad = 0
    model_problems = check_book_model() + check_generated_book()
    if model_problems:
        bad += 1
        print("整书叙事结构:")
        for problem in model_problems:
            print("  - " + problem)
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
    print(
        f"结构校验通过: {len(files)} 个文件, {len(build_book.CHAPTERS)} 个公开章, "
        f"{len({num for ch in build_book.CHAPTERS for num in ch['source_nums']})} 个源单元"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
