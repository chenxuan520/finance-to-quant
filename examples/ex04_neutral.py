"""示例 4:市场中性的对冲账本(对应“市场中性策略”和“市场中性模拟盘”)

多头:每天持有综合分最高的一组股票;
对冲:按 Beta 公式空指数名义(对冲名义 = 多头市值 × Beta);
账本:每日记录多头盈亏、空头盈亏、净暴露和保证金占用。

你会亲眼看到三件事:
  1. 对冲后波动大幅下降——方向风险被压掉了;
  2. 但没有降到 0——Beta 会估错,基差/残余暴露都在;
  3. “中性”赚的是选股能力,不是“大盘涨跌不动也能稳赢”的魔法。
"""

from common import annual_vol, daily_returns, load_universe, report
from ex01_factors import factors_at

BETA = 1.0                 # 教学版固定用 1;真实项目要回归估计,见市场中性章节
MARGIN_RATE = 0.12         # 期货保证金比例(书里 120 万名义×12% 那本账)
HOLD_NUM = 20
REBALANCE_EVERY = 20
WARMUP = 70


def main():
    stocks, bench = load_universe()
    n_days = len(bench) - 1

    long_nav, neutral_nav = [1.0], [1.0]
    holdings = {}

    for t in range(1, n_days + 1):
        bench_ret = bench[t] / bench[t - 1] - 1
        long_ret = 0.0
        if holdings:
            for code, w in holdings.items():
                s = next(x for x in stocks if x.code == code)
                long_ret += w * (s.prices[t] / s.prices[t - 1] - 1)
        long_nav.append(long_nav[-1] * (1 + long_ret))

        # 空头指数在 Beta 口径下的盈亏 + 净暴露监控
        hedge_pnl = -BETA * bench_ret
        neutral_ret = (long_ret + hedge_pnl) / 2          # 一半仓位做多、一半名义做空的教学口径
        neutral_nav.append(neutral_nav[-1] * (1 + neutral_ret))

        if t > WARMUP and t % REBALANCE_EVERY == 0:
            score = factors_at(stocks, t)
            ranked = sorted(stocks, key=lambda s: score[s.code], reverse=True)
            holdings = {s.code: 1.0 / HOLD_NUM for s in ranked[:HOLD_NUM]}

    print("同一个多头组合,对冲前后:\n")
    report("纯多头", long_nav, bench=None)
    report("对冲后(中性)", neutral_nav)
    bench_norm = [v / bench[0] for v in bench]
    report("基准指数", bench_norm)
    print(f"""
账本上还能读到:
  - 净暴露被压到 ≈(多头 Beta - 对冲 Beta)≈ 0,但不是恒等于 0;
  - 保证金占用 ≈ 名义空头 × {MARGIN_RATE:.0%},也就是总资产的一个固定比例上下浮动
    (真实项目里还随浮盈浮亏每日变动,见市场中性模拟盘里的现金账)——钱被锁着,这就是对冲的直接代价;
  - 对冲后剩下的涨跌,全部来自选股超额和 Beta 估错的残余,与大盘方向基本无关——
    所以中性策略的夏普常常不如纯多头好看:你买的不是更高收益,是更低波动和更稳的路径。
"""
    )

    assert annual_vol(neutral_nav) < annual_vol(long_nav) * 0.6, "对冲必须显著降波动"


if __name__ == "__main__":
    main()
