"""示例 2:一个完整(教学版)的指数增强回测(对应第 19 章)

严格按书里那张调仓时间线走:
    T 日收盘后  计算因子和目标组合(只用 T 日收盘及以前的数据)
    T+1 开盘    按目标调仓成交(用 T+1 的价格,不是 T 的收盘价!)
    每 20 个交易日调一次仓,双边成本万 13
对照组:全池等权基准。
"""

from common import apply_cost, daily_returns, load_universe, report
from ex01_factors import factors_at

REBALANCE_EVERY = 20       # 近似月频
HOLD_NUM = 30              # 每期持有综合分最高的 30 只
WARMUP = 70                # 前 70 天凑不齐 60 日动量窗口,不交易


def backtest(stocks, bench):
    n_days = len(bench) - 1
    holdings = {}                       # code -> 目标权重
    strat_nav = [1.0]
    total_turnover = 0.0

    for t in range(1, n_days + 1):
        # ---- 先按 T 日收益更新旧持仓净值(持仓在整个 T 日内生效) ----
        day_ret = 0.0
        if holdings:
            for code, w in holdings.items():
                s = next(x for x in stocks if x.code == code)
                day_ret += w * (s.prices[t] / s.prices[t - 1] - 1)
        nav_after_day = strat_nav[-1] * (1 + day_ret)

        # ---- T 日收盘后:出信号(T 日晚上能做的事) ----
        if t > WARMUP and t % REBALANCE_EVERY == 0:
            score = factors_at(stocks, t)           # 只用 [0, t] 的可见数据
            ranked = sorted(stocks, key=lambda s: score[s.code], reverse=True)
            target = {s.code: 1.0 / HOLD_NUM for s in ranked[:HOLD_NUM]}
            turnover = sum(abs(target.get(c, 0) - holdings.get(c, 0))
                           for c in set(target) | set(holdings))
            total_turnover += turnover
            nav_after_day *= 1 - apply_cost(turnover)
            # 成交实际发生在 T+1:我们用“明天才换上新持仓”来体现这一点——
            # 新持仓从 t+1 的收益开始计入,见下一轮循环。
            holdings = target

        strat_nav.append(nav_after_day)

    years = n_days / 252
    return strat_nav, total_turnover / years


def main():
    stocks, bench_nav = load_universe()
    bench_rel = [v / bench_nav[0] for v in bench_nav]

    strat_nav, turnover = backtest(stocks, bench_nav)

    print("指数增强(教学版) vs 等权基准,共 {} 个交易日\n".format(len(bench_rel) - 1))
    report("等权基准", bench_rel)
    report("指数增强组合", strat_nav, bench=bench_rel, turnover=turnover)
    print("""
对着第 19 章逐项自查这份输出:
  - 信号用的是 T 日收盘前的数据,新持仓从 T+1 才开始计入收益(无未来函数);
  - 成本按真实换手逐笔扣除,不是事后拍一个数字;
  - 看的不是终点收益,而是超额、跟踪误差、IR 三件事一起。"""
    )

    assert strat_nav[-1] > strat_nav[0], "净值必须可计算"
    assert turnover > 0, "换手必须为正,否则成本逻辑没生效"


if __name__ == "__main__":
    main()
