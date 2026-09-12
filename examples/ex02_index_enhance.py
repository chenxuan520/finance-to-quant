"""示例 2:一个完整(教学版)的指数增强回测(对应“指数增强策略”和“实战项目一”)

严格按书里那张调仓时间线走:
    T 日收盘后  计算因子和目标组合(只用 T 日收盘及以前的数据)
    T+1 开盘    按目标调仓成交(用 T+1 的价格,不是 T 的收盘价!)
    每 20 个交易日调一次仓,买卖每边成本万 13
对照组:全池等权基准。
教学边界:允许碎股,假设开盘可全部成交;未模拟停牌、涨跌停和成交量限制。
"""

import math

from common import apply_cost, load_universe, report
from ex01_factors import factors_at

REBALANCE_EVERY = 20       # 近似月频
HOLD_NUM = 30              # 每期持有综合分最高的 30 只
WARMUP = 70                # 前 70 天凑不齐 60 日动量窗口,不交易


def backtest(stocks, bench):
    n_days = len(bench) - 1
    by_code = {s.code: s for s in stocks}
    holdings = {}                       # code -> 实际持股数,调仓之间不变
    cash = 1.0
    pending = None                      # 前一日收盘后生成的目标权重
    strat_nav = [1.0]
    total_turnover = 0.0

    for t in range(1, n_days + 1):
        # ---- T 日开盘:旧股先按开盘价估值,再执行 T-1 日的信号 ----
        if pending is not None:
            values = {c: qty * by_code[c].opens[t] for c, qty in holdings.items()}
            open_nav = cash + sum(values.values())
            orders = {c: pending.get(c, 0) * open_nav - values.get(c, 0)
                      for c in by_code if c in pending or c in holdings}
            traded = 0.0

            # 先卖再买;费用从现金支付,不足以覆盖买入和费用时同比缩单。
            for c, amount in orders.items():
                if amount < 0:
                    holdings[c] += amount / by_code[c].opens[t]
                    cash += -amount - apply_cost(-amount)
                    traded += -amount
            buy_total = sum(max(amount, 0) for amount in orders.values())
            scale = min(1.0, cash / (buy_total + apply_cost(buy_total))) if buy_total else 0
            for c, amount in orders.items():
                if amount > 0:
                    amount *= scale
                    holdings[c] = holdings.get(c, 0) + amount / by_code[c].opens[t]
                    cash -= amount + apply_cost(amount)
                    traded += amount
            total_turnover += traded / open_nav
            pending = None

        # ---- T 日收盘:现金 + 实际股数 × 收盘价,新股只赚成交后的涨跌 ----
        strat_nav.append(cash + sum(qty * by_code[c].prices[t]
                                    for c, qty in holdings.items()))

        # ---- T 日收盘后:出信号(T 日晚上能做的事) ----
        if t > WARMUP and t % REBALANCE_EVERY == 0 and t < n_days:
            score = factors_at(stocks, t)           # 只用 [0, t] 的可见数据
            ranked = sorted(stocks, key=lambda s: score[s.code], reverse=True)
            selected = ranked[:HOLD_NUM]
            pending = {s.code: 1.0 / len(selected) for s in selected}

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
对照指数增强实战章节逐项自查这份输出:
  - T 日收盘后出信号,T+1 开盘成交;新买入股票不计入成交前的隔夜收益;
  - 成本按实际买卖金额每边万 13 扣除,换手为买卖成交额之和相对净值的比例;
  - 看的不是终点收益,而是超额、跟踪误差、IR 三件事一起。"""
    )

    assert all(math.isfinite(v) and v > 0 for v in strat_nav), "净值必须有限且为正,不要求盈利"
    assert turnover > 0, "换手必须为正,否则成本逻辑没生效"


if __name__ == "__main__":
    main()
