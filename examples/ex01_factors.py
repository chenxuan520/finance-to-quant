"""示例 1:因子与分层回测(对应“从问题到因子”和“数据、标签和样本切分”)

做四件事:
1. 计算四个教学因子——价值、动量、低波、质量(与书中的常见因子家族一致);
2. 截面标准化(z-score)并等权合成综合分;
3. 按综合分把股票分成 5 组,看未来 20 日收益是否单调(对应书中的因子分层图);
4. 顺手验证一个常识:单因子里谁更有用。
"""

from common import TRADING_DAYS, load_universe


def zscore(pairs):
    """pairs: list[(stock, factor_value)] -> dict code -> z 分数"""
    vals = [v for _, v in pairs]
    mu = sum(vals) / len(vals)
    var = sum((v - mu) ** 2 for v in vals) / (len(vals) - 1)
    sd = var ** 0.5 or 1.0
    return {s.code: (v - mu) / sd for s, v in pairs}


def factors_at(stocks, t):
    """只使用 [0, t] 范围内可见的数据计算四个因子——这是纪律,不是习惯。"""
    value, momentum, low_vol, quality = [], [], [], []
    for s in stocks:
        book_like = s.prices[0] * (1 + s.drift * t)     # 教学版“账面价值”:缓慢增长的真底子
        value.append((s, book_like / s.prices[t]))      # 便宜 = 底子/价格 高
        momentum.append((s, s.prices[t] / s.prices[t - 60] - 1))
        rets = [s.prices[k] / s.prices[k - 1] - 1 for k in range(t - 59, t + 1)]
        mu = sum(rets) / len(rets)
        vol = (sum((r - mu) ** 2 for r in rets) / (len(rets) - 1)) ** 0.5
        low_vol.append((s, -vol))                       # 波动越低分越高
        quality.append((s, s.quality))                  # 真实项目里来自财报,这里用合成真值
    zs = [zscore(x) for x in (value, momentum, low_vol, quality)]
    return {c: sum(z[c] for z in zs) / 4 for c in zs[0]}


def future_return(stock, t, horizon=20):
    return stock.prices[t + horizon] / stock.prices[t] - 1


def main():
    stocks, bench = load_universe()
    # 书里反复强调:单个截面靠运气,要看很多期才作数。这里取 5 个时点平均。
    ts = [300, 340, 380, 420, 460]
    group_size = len(stocks) // 5
    group_ret = [[], [], [], [], []]
    for t in ts:
        score = factors_at(stocks, t)
        ranked = sorted(stocks, key=lambda s: score[s.code])
        for g in range(5):
            group = ranked[g * group_size:(g + 1) * group_size]
            group_ret[g].append(sum(future_return(s, t) for s in group) / group_size)

    print(f"按综合分把 {len(stocks)} 只股票分成 5 组,在 {len(ts)} 个时点上各看未来 20 日,再取平均")
    print("(对应书里那张图:因子若真有用,从第 1 组到第 5 组应当大体单调)\n")
    for g in range(5):
        fut = sum(group_ret[g]) / len(group_ret[g])
        bar = "█" * max(1, int((fut + 0.02) * 100))
        print(f"  第{g+1}组(分数{'最低' if g == 0 else '最高' if g == 4 else '居中'})  "
              f"平均未来20日 {fut:+6.2%}  {bar}")

    # 单因子有效性:各因子与未来 20 日收益的秩相关(简化版 IC),同样在多个时点取平均
    print("\n单因子的简化 IC(因子排名与未来收益排名的相关性,多期平均):")
    raw = {
        "价值": [], "动量": [], "低波": [], "质量": [],
    }
    ics = {"价值": [], "动量": [], "低波": [], "质量": []}
    for t in ts:
        raw_day = {k: [] for k in raw}
        for s in stocks:
            rets = [s.prices[k] / s.prices[k - 1] - 1 for k in range(t - 59, t + 1)]
            mu = sum(rets) / len(rets)
            vol = (sum((r - mu) ** 2 for r in rets) / (len(rets) - 1)) ** 0.5
            raw_day["价值"].append((s, (s.prices[0] * (1 + s.drift * t)) / s.prices[t]))
            raw_day["动量"].append((s, s.prices[t] / s.prices[t - 60] - 1))
            raw_day["低波"].append((s, -vol))
            raw_day["质量"].append((s, s.quality))
        order_r = [s.code for s in sorted(stocks, key=lambda s: future_return(s, t))]
        rank_r = {c: i for i, c in enumerate(order_r)}
        n = len(stocks)
        for name, pairs in raw_day.items():
            rank_f = {s.code: i for i, (s, _) in enumerate(sorted(pairs, key=lambda x: x[1]))}
            d2 = sum((rank_f[c] - rank_r[c]) ** 2 for c in rank_f)
            ics[name].append(1 - 6 * d2 / (n * (n * n - 1)))   # Spearman 秩相关公式
    for name, series in ics.items():
        print(f"  {name}: 平均 IC {sum(series)/len(series):+.3f}  (各期: "
              + ", ".join(f"{x:+.2f}" for x in series) + ")")

    print("""
对照“从问题到因子”读这份输出:
  - 综合分五组大体单调:这是“因子组合可能有用”的最小证据;
  - 但这组数字不能照搬到真实市场——合成世界里价格回归底子又快又猛,所以价值类 IC
    高得不真实;真实市场里一个因子的 IC 能稳定在 +0.03,已经值得研究;
  - 动量在这个世界里时正时负:短窗口动量在真实 A 股月频上同样忽强忽弱。
    因子“失效”不是意外,是常态——所以书里才反复强调多期均值和稳定性。"""
    )


if __name__ == "__main__":
    main()
