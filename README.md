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

- 第 0-5 章: 金融世界的底层结构和主要资产,包括货币、信用、银行、股票、债券、基金、期货、期权、外汇、商品、REITs 和结构化产品。
- 第 6-8 章: A 股市场、行情、指数、收益风险、资产配置和有效市场。
- 第 9-12 章: 量化研究生产线,包括因子、标签、数据切分、回测、机器学习、组合优化、交易执行和风控。
- 第 13-18 章: 量化行业、策略类型、产品阅读、监管合规、财务报表、宏观数据和多资产。
- 第 19-32 章: 项目骨架、公式速查、实战项目、常见错误、场景练习、最终清单和结语。
- 附录: 术语表与参考资料。

## 配套代码示例

[examples/](examples/) 目录里有四个零第三方依赖的 Python 教学脚本,对应第 9/14/19/20/21/22 章:
因子分层、指数增强完整回测、未来函数对照实验、市场中性对冲账本。

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
