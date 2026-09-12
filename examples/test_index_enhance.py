"""用可手算行情检查成交时点、持仓和成本,不以策略赚钱作为正确性标准。"""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

import ex02_index_enhance as example


def stock(code, closes, opens):
    return SimpleNamespace(code=code, prices=closes, opens=opens)


class IndexEnhanceTest(unittest.TestCase):
    def run_backtest(self, stocks, scores=None, cost=0, every=1, hold_num=1):
        if scores is None:
            scores = lambda stocks, t: {s.code: 1 for s in stocks}
        with patch.multiple(example, WARMUP=0, REBALANCE_EVERY=every,
                            HOLD_NUM=hold_num), \
                patch.object(example, "factors_at", side_effect=scores), \
                patch.object(example, "apply_cost", side_effect=lambda amount: amount * cost):
            return example.backtest(stocks, [1.0] * len(stocks[0].prices))

    def test_new_position_does_not_earn_overnight_gap(self):
        s = stock("A", [100, 100, 110], [100, 100, 110])
        nav, _ = self.run_backtest([s])
        self.assertEqual(nav, [1.0, 1.0, 1.0])

    def test_new_position_earns_only_open_to_close_return(self):
        s = stock("A", [100, 100, 121], [100, 100, 110])
        nav, _ = self.run_backtest([s])
        self.assertAlmostEqual(nav[-1], 1.1)

    def test_old_position_keeps_gap_until_next_open_sale(self):
        a = stock("A", [100, 100, 100, 120], [100, 100, 100, 120])
        b = stock("B", [100, 100, 100, 220], [100, 100, 100, 200])
        scores = lambda stocks, t: {"A": int(t == 1), "B": int(t != 1)}
        nav, _ = self.run_backtest([a, b], scores)
        # A 在卖出前赚 20%,B 从 200 买入后赚 10%。
        self.assertAlmostEqual(nav[-1], 1.2 * 1.1)

    def test_pending_order_has_no_fee_until_fill(self):
        s = stock("A", [100, 100], [100, 100])
        nav, turnover = self.run_backtest([s], cost=0.01)
        self.assertEqual(nav, [1.0, 1.0])
        self.assertEqual(turnover, 0)

    def test_buy_fee_fits_cash_and_turnover_counts_filled_amount(self):
        s = stock("A", [100, 100, 100], [100, 100, 100])
        nav, turnover = self.run_backtest([s], cost=0.01)
        # 1 元现金 = 买入金额 × (1 + 1% 费用)。
        self.assertEqual(nav[1], 1.0)
        self.assertAlmostEqual(nav[-1], 1 / 1.01)
        self.assertAlmostEqual(turnover, (1 / 1.01) * 252 / 2)

    def test_full_switch_charges_both_sell_and_buy(self):
        a = stock("A", [100] * 4, [100] * 4)
        b = stock("B", [100] * 4, [100] * 4)
        scores = lambda stocks, t: {"A": int(t == 1), "B": int(t != 1)}
        nav, turnover = self.run_backtest([a, b], scores, cost=0.01)
        self.assertAlmostEqual(nav[-1], (1 / 1.01) * 0.99 / 1.01)
        self.assertAlmostEqual(turnover, (1 / 1.01 + 1 + 0.99 / 1.01) * 252 / 3)

    def test_shares_do_not_rebalance_between_scheduled_trades(self):
        a = stock("A", [100, 100, 100, 200, 100], [100] * 5)
        b = stock("B", [100] * 5, [100] * 5)
        nav, turnover = self.run_backtest([a, b], every=2, hold_num=2)
        self.assertAlmostEqual(nav[3], 1.5)
        self.assertAlmostEqual(nav[4], 1.0)
        self.assertAlmostEqual(turnover, 252 / 4)


if __name__ == "__main__":
    unittest.main()
