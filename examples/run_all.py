"""一键运行全部示例,并做最小自检(充当测试)。

用法:  python3 run_all.py
"""

import io
import contextlib

import ex01_factors
import ex02_index_enhance
import ex03_lookahead
import ex04_neutral


def run(name, mod):
    print("=" * 68)
    print(f"  {name}")
    print("=" * 68)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        mod.main()          # 各示例内部带 assert,出问题会直接抛
    print(buf.getvalue())


if __name__ == "__main__":
    run("示例 1 · 因子与分层回测(第 11 章)", ex01_factors)
    run("示例 2 · 指数增强完整回测(第 21 章)", ex02_index_enhance)
    run("示例 3 · 偷看未来 vs 不偷看(第 21/22 章)", ex03_lookahead)
    run("示例 4 · 市场中性对冲账本(第 14/20 章)", ex04_neutral)
    print("全部示例运行通过(含各自断言自检)。")
