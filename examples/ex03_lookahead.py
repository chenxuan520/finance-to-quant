"""示例 3:同一个策略,偷看未来 vs 不偷看(对应“回测”和“识别回测幻觉”)

跑两条净值曲线:
  - 诚实版:每天只能看到今天收盘前的数据,用过去 20 日动量选股;
  - 作弊版:每天直接看“明天”的收益,专挑明天会涨的买。
两条曲线的差距,就是未来函数白送你的那一部分——实盘里一分都拿不到。
"""

from common import load_universe, report

HOLD_NUM = 20
REBALANCE_EVERY = 20
WARMUP = 25


def _nav(honest, stocks):
    holdings = {}
    nav = [1.0]
    n_days = len(stocks[0].prices) - 1
    for t in range(1, n_days + 1):
        day_ret = 0.0
        if holdings:
            for code, w in holdings.items():
                s = next(x for x in stocks if x.code == code)
                day_ret += w * (s.prices[t] / s.prices[t - 1] - 1)
        nav.append(nav[-1] * (1 + day_ret))

        if t > WARMUP and t % REBALANCE_EVERY == 0 and t + 1 <= n_days:
            if honest:
                # 只用到 t 为止的动量
                key = lambda s: s.prices[t] / s.prices[t - 20] - 1
            else:
                # 作弊:直接用“明天”的收益排名——回测里最常见的惨剧之一
                key = lambda s: s.prices[t + 1] / s.prices[t] - 1
            ranked = sorted(stocks, key=key, reverse=True)
            holdings = {s.code: 1.0 / HOLD_NUM for s in ranked[:HOLD_NUM]}
    return nav


def main():
    stocks, _ = load_universe()
    honest = _nav(True, stocks)
    cheat = _nav(False, stocks)

    print("同样的月频动量策略,唯一区别是选股那一下看不看“明天”:\n")
    report("诚实版", honest)
    report("偷看未来版", cheat)
    print(f"""
终点净值:诚实 {honest[-1]:.3f} vs 作弊 {cheat[-1]:.3f} —— 差出来的部分,就是未来函数
制造的幻觉。书中的回测拆解案例,拆的正是这种幻觉上又长出来的“漂亮曲线”。
排查方法永远只有一个:确认每一个决策时刻,代码碰不到那一刻之后的数据。"""
    )

    assert cheat[-1] > honest[-1], "偷看未来必须显著更好,否则示例没构造对"


if __name__ == "__main__":
    main()
