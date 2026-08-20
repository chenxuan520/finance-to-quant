# 从金融零基础到量化研究者

给计算机背景读者的金融与量化入门书。从货币、银行、股票、债券、基金、衍生品和 A 股交易制度讲起,一路走到因子、回测、机器学习、组合优化、交易执行、风控,以及量化行业现状和个人项目路线。全书用小岛经济学式的直觉起步,配真实历史案例(郁金香狂热、南海泡沫、雷曼、LTCM、西蒙斯、骑士资本)和手绘概念图,尽量做到通俗又不失专业。

## 在线阅读

- 📖 GitHub Pages: https://chenxuan520.github.io/finance-to-quant/
- ⚡ Cloudflare Pages: https://finance-to-quant.pages.dev/
- 📄 PDF 版: 见本仓库 [Releases](https://github.com/chenxuan520/finance-to-quant/releases)

## 本地预览

```bash
cd docs/finance-book
python3 -m http.server 8776 --bind 127.0.0.1
# 浏览器打开 http://127.0.0.1:8776/index.html
```

## 内容结构

全书只走一条主线:

`真实财富 -> 金融权利 -> 市场价格与数据 -> 研究假设 -> 回测验证 -> 组合交易 -> 项目复盘`

- 金融为什么存在:从真实财富、货币和信用走到银行、金融系统与证券市场。
- 资产如何承载现金流与风险:股票、债券、基金、期货、期权、另类资产与结构性产品。
- 市场如何形成价格与数据:账户、A 股制度、行情、指数、财务报表、收益风险与市场有效性。
- 宏观环境如何改变资产:增长、通胀、央行、美元、金融危机与影子银行。
- 量化研究如何产生可信结论:问题、因子、数据、回测、机器学习、组合、执行、风控与工程骨架。
- 策略如何变成产品:指数增强、市场中性、CTA、套利、高频、产品文件与合规。
- 把研究变成可运行项目:完整回测、模拟盘、小实盘、资金管理与正反案例。
- 职业、复盘与长期成长:岗位、作品集、学习路线、全书自检与结语。
- 专题和附录:个人金融安全底盘、术语、公式、最终检查表与参考资料。

## 配套代码示例

[examples/](examples/) 目录里有四个零第三方依赖的 Python 教学脚本,对应因子研究、
指数增强、回测偏差和市场中性四个主题。

```bash
cd examples && python3 run_all.py
```

## 从源码构建

书稿正文全部手写在 `docs/finance-book/tools/manual_manuscript.py`,静态站点由 `build_book.py` 生成。

```bash
python3 docs/finance-book/tools/build_book.py       # 生成全部 HTML
python3 docs/finance-book/tools/check_structure.py  # 结构校验
python3 docs/finance-book/tools/check_links.py      # 链接校验
```

推送到 `main` 后,GitHub Actions 会自动重建并部署到 GitHub Pages 和 Cloudflare Pages(见 `.github/workflows/deploy.yml`)。

## 说明

内容吸收《小岛经济学》的生产、储蓄、信用直觉,以及《漫步华尔街》的市场有效性、随机游走和指数投资思想;正文为原创整理。书中涉及的行业、机构和监管信息会随时间变化,实盘和引用前请以交易所、证监会、协会、券商和数据服务商的最新原文为准。本书仅用于学习,不构成任何投资建议。

## 许可

代码与文档以 MIT License 开源,见 [LICENSE](LICENSE)。
