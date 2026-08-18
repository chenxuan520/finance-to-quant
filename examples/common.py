"""共享工具:合成行情数据 + 收益风险指标 + 组合记账。

为什么用合成数据而不是真实数据?
- 任何机器上 `python3 ex01_factors.py` 都能跑,不依赖网络和第三方库;
- 数据生成过程是公开的,我们可以精确控制"哪种股票真的好",
  从而能精确检验因子和回测是否发现了这些规律;
- 学完这套代码骨架,换成真实数据源时,只需要替换 load_universe() 一个函数。

本文件只依赖 Python 标准库。
"""

import math
import random

TRADING_DAYS = 252  # 一年按 252 个交易日年化,与全书口径一致


# ---------------------------------------------------------------- 合成数据

class Stock:
    """一只股票的完整信息。factor_score 是“上帝视角”的真实质地,
    市场数据(价格、波动)由它驱动但带噪声——这正是因子研究要对抗的东西。"""

    def __init__(self, code, quality, drift, base_vol, price0=20.0):
        self.code = code
        self.quality = quality        # 真实质地: 越高,长期漂移越大(选股因子的“答案”)
        self.drift = drift            # 每日真实期望收益
        self.base_vol = base_vol      # 日波动率
        self.prices = [price0]


def load_universe(n_stocks=120, n_days=760, seed=42):
    """生成一个有真实规律可挖的股票池。

    结构与本书第 11 章一致:
    - 每只股票有一条由真实质地决定的“底子线”: 底子按自身 drift 每天增长;
    - 每天的价格 = 底子 × 大盘共同项 × 个股噪声项;
    - 因此价格会偏离底子又回归底子——价值因子(底子/价格)挖的是这个偏差,
      质量/低波/动量因子挖的是底子本身的斜率差异。
    四条规律都真实存在,但每一条都埋在噪声里,这正是因子研究的日常。
    """
    rng = random.Random(seed)
    stocks = []
    for i in range(n_stocks):
        quality = rng.uniform(-1.0, 1.0)
        drift = quality * 0.0008                    # 底子的年化斜率差(教学用的明显差异)
        base_vol = 0.020 - quality * 0.004          # 好公司噪声略小
        stocks.append(Stock(f"S{i:04d}", quality, drift, max(0.010, base_vol)))

    market = 1.0
    for t in range(1, n_days + 1):
        market *= 1 + rng.gauss(0.0002, 0.010)      # 大盘共同涨落(年化约 +5%)
        for s in stocks:
            fundamental = s.prices[0] * math.exp(s.drift * t)
            noise = rng.gauss(0, s.base_vol)
            s.prices.append(fundamental * market * math.exp(noise))

    # 基准指数 = 全池等权平均,归一到 1000 点
    bench = [1000.0]
    for t in range(1, n_days + 1):
        day_ret = sum(s.prices[t] / s.prices[t - 1] - 1 for s in stocks) / n_stocks
        bench.append(bench[-1] * (1 + day_ret))
    return stocks, bench


# ---------------------------------------------------------------- 指标

def daily_returns(nav):
    return [nav[t] / nav[t - 1] - 1 for t in range(1, len(nav))]


def annual_return(nav):
    years = (len(nav) - 1) / TRADING_DAYS
    return (nav[-1] / nav[0]) ** (1 / years) - 1 if years > 0 else 0.0


def annual_vol(nav):
    rets = daily_returns(nav)
    if len(rets) < 2:
        return 0.0
    mu = sum(rets) / len(rets)
    var = sum((r - mu) ** 2 for r in rets) / (len(rets) - 1)
    return math.sqrt(var) * math.sqrt(TRADING_DAYS)


def max_drawdown(nav):
    peak, mdd = nav[0], 0.0
    for v in nav:
        peak = max(peak, v)
        mdd = min(mdd, v / peak - 1)
    return mdd


def sharpe(nav, rf=0.03):
    vol = annual_vol(nav)
    return (annual_return(nav) - rf) / vol if vol > 0 else 0.0


def report(name, nav, bench=None, turnover=None):
    """打印一份迷你报告。turnover 给出时用来说明成本口径。"""
    line = (f"{name:<14s} 年化 {annual_return(nav):+.1%}  波动 {annual_vol(nav):5.1%}  "
            f"最大回撤 {max_drawdown(nav):6.1%}  夏普 {sharpe(nav):5.2f}")
    if bench is not None:
        excess = annual_return(nav) - annual_return(bench)
        te = _tracking_error(nav, bench)
        ir = excess / te if te > 0 else 0.0
        line += f"  超额 {excess:+.1%}  跟踪误差 {te:4.1%}  IR {ir:4.2f}"
    if turnover is not None:
        line += f"  年均换手 {turnover:4.1f} 倍"
    print(line)


def _tracking_error(nav, bench):
    ra, rb = daily_returns(nav), daily_returns(bench)
    diff = [a - b for a, b in zip(ra, rb)]
    if len(diff) < 2:
        return 0.0
    mu = sum(diff) / len(diff)
    var = sum((d - mu) ** 2 for d in diff) / (len(diff) - 1)
    return math.sqrt(var) * math.sqrt(TRADING_DAYS)


# ---------------------------------------------------------------- 交易成本

def apply_cost(turnover_value, cost_bps=13):
    """双边成本,默认万 13(佣金+印花税+滑点的教学口径,见第 21 章)。

    turnover_value: 本次调仓买入+卖出的名义总额(相对净值 1.0 的比例)。
    返回应扣除的净值比例。
    """
    return turnover_value * cost_bps / 10000
