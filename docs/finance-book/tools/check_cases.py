#!/usr/bin/env python3
"""检查新增金融案例与概念场景是否完整进入手稿与生成页。"""

import re
from pathlib import Path

import manual_manuscript


ROOT = Path(__file__).resolve().parents[1]
CASES = manual_manuscript.NARRATIVE_CASES
CONCEPTS = manual_manuscript.CONCEPT_SCENES


def fail(message: str, problems: list[str]) -> None:
    problems.append(message)


def main() -> int:
    problems: list[str] = []
    titles = []
    records = [
        (
            source_num,
            "金融现场",
            title.removeprefix("Case: "),
            body,
        )
        for source_num, (title, body) in CASES.items()
    ]
    records.extend(
        (source_num, "概念现场", title, body)
        for source_num, sections in CONCEPTS.items()
        for title, body in sections
    )

    if len(CASES) < 35:
        fail(f"新增案例数量不足: {len(CASES)}", problems)
    concept_count = sum(len(sections) for sections in CONCEPTS.values())
    if concept_count < 15:
        fail(f"新增概念场景数量不足: {concept_count}", problems)

    for source_num, label, title, body in records:
        titles.append(title)
        paragraphs = re.findall(r"<p>(.*?)</p>", body, flags=re.S)
        han = len(re.findall(r"[\u4e00-\u9fff]", body))
        if len(paragraphs) < 3:
            fail(f"源单元 {source_num} {label}不足三段: {title}", problems)
        if han < 180:
            fail(f"源单元 {source_num} {label}过短: {han} 汉字", problems)
        if not any(
            word in paragraphs[-1]
            for word in (
                "量化", "模型", "回测", "系统", "组合", "研究", "策略",
                "产品", "项目", "资金管理", "资产配置", "家庭配置",
            )
        ):
            fail(f"源单元 {source_num} {label}缺少方法连接: {title}", problems)

    source_nums = sorted(set(CASES) | set(CONCEPTS))
    for source_num in source_nums:
        expected = []
        if source_num in CASES:
            title, _ = CASES[source_num]
            expected.append(f"金融现场｜{title.removeprefix('Case: ')}")
        expected.extend(
            f"概念现场｜{title}"
            for title, _ in CONCEPTS.get(source_num, [])
        )
        actual = [
            title
            for title, _ in manual_manuscript.CHAPTERS[source_num]["sections"][
                :len(expected)
            ]
        ]
        if actual != expected:
            fail(f"源单元 {source_num} 开场案例顺序错误", problems)

    if len(titles) != len(set(titles)):
        fail("新增案例标题重复", problems)

    rendered = 0
    rendered_pages = 0
    for path in sorted(ROOT.glob("chapter-*.html")):
        count = path.read_text(encoding="utf-8").count('class="case-study reveal"')
        rendered += count
        rendered_pages += bool(count)
    if rendered != len(records):
        fail(f"生成页案例数量不一致: {rendered}/{len(records)}", problems)

    if problems:
        print("案例检查失败:")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    paragraph_count = sum(body.count("<p>") for _, _, _, body in records)
    print(
        f"案例检查通过: {len(CASES)} 个金融案例 + {concept_count} 个概念场景, "
        f"{paragraph_count} 个段落,覆盖 {rendered_pages} 个公开章"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
