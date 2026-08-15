#!/usr/bin/env python3
"""
Build the static HTML ebook.

The public prose is loaded from manual_manuscript.py. This file renders the
static site, navigation, diagrams and validation fixtures.
"""

import html
import importlib.util
import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


BOOK_TITLE = "从金融零基础到量化研究者"
BOOK_SUBTITLE = "给计算机背景读者的金融与量化入门书"
REPO_URL = "https://github.com/chenxuan520/finance-to-quant"


MANUSCRIPT_PATH = Path(__file__).with_name("manual_manuscript.py")
if not MANUSCRIPT_PATH.exists():
    raise FileNotFoundError(f"Manual manuscript not found: {MANUSCRIPT_PATH}")

_spec = importlib.util.spec_from_file_location("finance_manual_manuscript", MANUSCRIPT_PATH)
_manuscript = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_manuscript)
SOURCE_CHAPTERS = _manuscript.CHAPTERS
GLOSSARY = _manuscript.GLOSSARY
REFERENCES = _manuscript.REFERENCES


CHAPTER_GROUPS = [
    [0, 1], [2, 3], [4, 5], [6, 7], [8, 9], [10, 11, 12],
    [13, 14], [15, 16], [17, 18, 19],
    [20, 21], [22, 23], [24, 25, 26],
    [27, 28], [29, 30], [31, 32], [33, 34], [35, 36], [37, 38],
    [39, 40], [41], [42, 43], [44, 45], [46, 47], [48],
    [49, 50], [51, 52], [53, 54], [55, 56], [57], [58, 59],
    [60, 61], [62, 63], [64],
]


VISIBLE_PARTS = [
    "第一部分 · 金融世界的底层结构",
    "第一部分 · 金融世界的底层结构",
    "第一部分 · 金融世界的底层结构",
    "第一部分 · 金融世界的底层结构",
    "第一部分 · 金融世界的底层结构",
    "第一部分 · 金融世界的底层结构",
    "第二部分 · A 股市场与交易机器",
    "第二部分 · A 股市场与交易机器",
    "第三部分 · 收益、风险与投资评价",
    "第四部分 · 量化研究从因子开始",
    "第四部分 · 量化研究从因子开始",
    "第四部分 · 量化研究从因子开始",
    "第五部分 · 量化行业与策略版图",
    "第五部分 · 量化行业与策略版图",
    "第五部分 · 量化行业与策略版图",
    "第五部分 · 量化行业与策略版图",
    "第五部分 · 量化行业与策略版图",
    "第五部分 · 量化行业与策略版图",
    "第六部分 · 项目实战与工程化",
    "第六部分 · 项目实战与工程化",
    "第六部分 · 项目实战与工程化",
    "第六部分 · 项目实战与工程化",
    "第六部分 · 项目实战与工程化",
    "第六部分 · 项目实战与工程化",
    "第七部分 · 路线、复盘与检查清单",
    "第七部分 · 路线、复盘与检查清单",
    "第七部分 · 路线、复盘与检查清单",
    "第七部分 · 路线、复盘与检查清单",
    "第七部分 · 路线、复盘与检查清单",
    "第七部分 · 路线、复盘与检查清单",
    "第七部分 · 路线、复盘与检查清单",
    "第七部分 · 路线、复盘与检查清单",
    "第七部分 · 路线、复盘与检查清单",
]


# 每个可见章的整章标题与统领导语,由人手写,取代把子主题机械拼成
# "X 与 Y" 的标题、以及"只讲第一个子主题 + 开发说明"的导语。
# key = 可见章号(0..32)。
CHAPTER_OVERRIDES = {
    0: {
        "title": "货币与通胀:财富到底是什么",
        "lead": "在讲股票、债券和量化之前,先把最容易被忽略的地基打牢:钱本身不是财富,真正的财富是能吃、能用、能生产的真实东西。这一章借一座只有鱼的小岛,把货币、储蓄、资本、信用讲成一条线,再顺势解释价格为什么会涨、通胀为什么让钱缩水,以及名义收益和实际收益的区别。地基稳了,后面所有术语才不会变成一团雾。",
    },
    1: {
        "title": "信用、利率与银行体系",
        "lead": "上一章的小岛出现了\u201c借一条鱼\u201d的行为,这一章从这里继续。有人今天有多余资源,有人有能提高未来产出的计划,把两者接起来就是信用;只要有等待和风险,就会出现利率。理解了这一点,再看银行怎么把存款变成贷款、央行为什么能影响整个经济的钱是松还是紧,就不再是背名词,而是看清一套环环相扣的机制。",
    },
    2: {
        "title": "金融系统地图:钱和风险怎么流动",
        "lead": "现代金融不是一条直线,而是一张网络:有人有钱,有人缺钱;有人要确定性,有人愿担风险;还有人负责撮合、托管和监管。这一章先把这张地图画出来,弄清钱和风险到底怎么在其中流动;再区分公司第一次拿钱的一级市场,和投资者互相换手的二级市场。看懂地图,后面的股票、债券、基金、量化机构才不会散成一堆孤立名词。",
    },
    3: {
        "title": "股票:你买的到底是什么",
        "lead": "很多人第一次接触股票,看到的只是一串代码、一个价格和红绿涨跌。但股票的本质是公司所有权的一小份,你买的是未来分享公司剩余收益的权利。这一章先讲清\u201c买股票到底买了什么\u201d,再解释分红、送股、回购这些公司行为如何影响你手里的股份,以及为什么股价不是只看当期利润,而是看市场对未来的整体判断。",
    },
    4: {
        "title": "债券与基金:把钱借出去或交给别人管",
        "lead": "股票讲的是公司剩余收益,债券讲的是白纸黑字的合同现金流:什么时候付息、什么时候还本都写得清清楚楚。但确定性更强不等于没有风险,利率、信用和流动性都会让债券价格波动。这一章先把债券从一张借条讲到利率和信用风险,再转向另一条路径\u2014\u2014基金、ETF、指数和私募,看清\u201c把钱交给别人管理\u201d到底意味着什么。",
    },
    5: {
        "title": "衍生品与其他资产:把未来和风险变成合约",
        "lead": "衍生品这个词听起来吓人,其实核心只有一句:它的价值来自另一个东西。这一章先讲期货、远期和互换如何把未来的价格、利率或现金流提前写进合约,再讲期权如何把\u201c不对称的收益结构\u201d变成可以买卖的产品,最后把视野扩展到外汇、商品、REITs 和结构化产品。它们都能用来管理风险,也都能被用来放大风险。",
    },
    6: {
        "title": "A 股的交易机器:从下单到成交",
        "lead": "你在手机上点一次买入,看似一秒钟的事,背后却串起账户、券商、交易所、登记结算、托管、清算和风控一整套机器。这一章先讲清这套机器里每个角色在做什么,再落到 A 股具体的交易规则:交易时间、涨跌幅限制、T+1、各项费用。量化系统如果不懂这些,就会把交易写成一个想当然的简单函数,最后在实盘里出错。",
    },
    7: {
        "title": "看懂行情:屏幕上的数字和基准",
        "lead": "第一次打开行情软件,满屏的最新价、涨跌幅、成交量、换手率、买一卖一、K 线、均线、复权很容易把人吓住。这一章先不急着学指标,而是讲清这些数字从哪里来、表示什么、又不能说明什么;再讲指数、ETF 和基准,回答一个常被忽略的问题:你的收益到底在和谁比较?看懂行情,才谈得上理解交易和量化数据。",
    },
    8: {
        "title": "收益、风险与市场为什么难赢",
        "lead": "一条收益曲线好不好,不能只看最后赚了多少。这一章先讲怎么量化收益和风险:年化、波动、最大回撤、夏普比率,让\u201c赚钱的体验发生在时间里\u201d这件事变得可测量;再讲资产配置和分散化,为什么不该把判断全押在一处;最后借有效市场、随机游走和行为偏差,解释一个残酷的现实\u2014\u2014赚超额收益为什么这么难。",
    },
    9: {
        "title": "量化的起点:因子和数据",
        "lead": "实习时听到的\u201c找因子\u201d,不是什么玄学密码。最朴素地说,因子就是一列能描述资产特征、风险暴露或预测信息的数字,量化研究的第一步就是把一句投资判断写成可检验的数据列。这一章先讲因子是什么、从哪里来、怎么检验有没有用,再讲更容易被忽略却更致命的一环:数据从哪里来、标签怎么定义、样本又该怎么切分。",
    },
    10: {
        "title": "回测与机器学习:在历史里排练",
        "lead": "回测是量化研究的实验室:把策略规则放进历史市场里跑一遍,看当时这么做会发生什么。但它是排练,不是时光机,更不是赚钱证明\u2014\u2014偷看未来、忽略成本、假设无限成交,结果就会变成幻觉。这一章先讲怎么做一次可信的回测,再讲量化里的机器学习:模型为什么不是越复杂越好,以及金融数据和图像文本有什么根本不同。",
    },
    11: {
        "title": "从预测到交易:组合、执行与风控",
        "lead": "量化研究员常常先得到一列预测分数,但真实投资从不是把最高分的股票全部买满。这一章讲预测之后的三件事:组合优化怎么在收益、风险和各种约束之间做权衡;交易执行怎么把理想仓位真的下到市场里,又不被成本和冲击吃掉;风控和监控怎么盯住边界,决定什么时候该减仓、停用和复盘。预测告诉你想要什么,这三步决定你能付出什么代价去实现它。",
    },
    12: {
        "title": "量化行业和个人的路线",
        "lead": "从外面看,量化像一群人关在办公室里写神秘算法;真实工作更像一条生产线,研究、工程、交易、风控、合规各司其职,算法只是其中一环。这一章先讲行业里不同角色到底在做什么,帮你看清自己适合站在哪个位置;再给计算机背景的个人一条能真正走通的学习路线:从零起步,该学什么、该做什么、又该避开哪些一开始就注定失败的方向。",
    },
    13: {
        "title": "量化策略版图与指数增强",
        "lead": "量化不是一种策略,而是一大类用数据、模型和规则做投资的方法:有人做指数增强,有人做市场中性,有人做商品趋势,有人做套利和高频。这一章先把整张策略地图铺开,让你看清它们在数据、频率、收益来源和风险上的根本差异;再深入第一种最容易理解的路径\u2014\u2014指数增强,看它如何在紧贴基准的同时,争取那一点点稳定的超额收益。",
    },
    14: {
        "title": "市场中性与 CTA 趋势",
        "lead": "市场中性听起来很诱人:不管大盘涨跌,只赚自己的选股能力。但\u201c中性\u201d到底中和了什么值得先讲清楚\u2014\u2014对冲能降低方向风险,却消灭不了基差、融券、成本和极端行情里的相关性失效。这一章先拆解市场中性对冲之后到底还剩什么风险,再转向 CTA 和期货趋势,看另一类完全不同的思路:用规则去交易商品、股指和利率的趋势。",
    },
    15: {
        "title": "套利与高频:更快更精细的战场",
        "lead": "\u201c套利\u201d这个词容易让人误会成白捡钱。严格意义上的无风险套利很少,一旦出现就会被速度快、成本低、资金大的参与者迅速挤掉;普通人说的套利,多数是\u201c赌价差回归\u201d的相对价值交易,能赚钱但绝不是没有风险。这一章先讲套利和相对价值的真实面貌,再进入高频交易和市场微观结构,看清毫秒之间价格、排队和风险是怎么运作的。",
    },
    16: {
        "title": "量化产品、监管与合规",
        "lead": "很多人理解了策略,却不会看产品。一个量化产品不是一段回测代码,而是有管理人、托管人、合同、费用、封闭期和净值披露的金融产品,投资者真正买到的是扣费后、受约束、会波动的一条净值曲线。这一章先讲怎么看懂一个量化产品:净值、费用、封闭期和业绩归因;再讲监管、合规和伦理\u2014\u2014技术能力再强,也不能越过市场规则的边界。",
    },
    17: {
        "title": "基本面与宏观:数字背后的公司和经济",
        "lead": "股票背后是公司,公司背后是生意。量化可以只用价格和成交量,也可以用财务报表做基本面因子。这一章先讲清收入、利润、资产、负债和现金流分别在说什么,以及为什么\u201c利润好看但现金流很差\u201d会让投资者警惕;再把视野拉到宏观,看利率、通胀、汇率和商品这些大变量如何彼此牵动,又如何一层层传导到你持有的资产上。",
    },
    18: {
        "title": "量化项目的工程骨架与速查",
        "lead": "计算机背景的读者最容易把量化项目写成一个越拉越长的 notebook,几周后连自己都理不清哪个单元格先跑、哪个文件才是最终结果。这一章先讲怎么像正经工程项目那样组织一个量化项目:数据来源清楚、配置可重复、实验有记录、回测可复现、报告能自动生成;再给一份公式和指标速查,帮你在\u201c别死背公式,要知道它在问什么\u201d之间找到平衡。",
    },
    19: {
        "title": "实战一:从零做一个指数增强回测",
        "lead": "前面讲了很多概念,这一章带你真正走一遍完整的研究流程。目标很具体:选一个指数作为基准,在它的成分股里构造几个简单因子,每月调仓,扣除成本,再和基准比较。做完你会发现,量化项目真正难的地方不是写出买卖信号,而是让数据、时间、交易规则、风险和报告全都对得上\u2014\u2014这也是把\u201c懂概念\u201d变成\u201c能动手\u201d的第一道坎。",
    },
    20: {
        "title": "实战二:市场中性模拟盘与上线检查",
        "lead": "市场中性比指数增强更复杂,因为它不只买股票,还要处理对冲。这一章带你做一个市场中性的模拟盘,重点不是收益,而是看清多头为什么赚或亏、对冲工具贡献多少、基差带来什么影响、保证金和现金怎么变化。做完之后,再给你一份从回测走到模拟盘、再走向实盘前必须逐条确认的检查清单,把\u201c手刹\u201d拉在真正下真金白银之前。",
    },
    21: {
        "title": "避坑:常见错误和如何读研究",
        "lead": "量化新手亏钱,常常不是因为不懂高深理论,而是掉进了几个反复出现的坑:看起来赚钱,其实在偷看未来的答案。这一章先把这些最常见的错误一个个摆出来,让你在自己的项目里能认出它们;再讲一项同样重要的能力\u2014\u2014如何读量化研究报告和论文:先找它的假设和数据口径,再看结论,别被漂亮的曲线和术语牵着走。",
    },
    22: {
        "title": "心理、资金管理与一次复盘",
        "lead": "技术之外,能不能活下来,往往取决于心理和资金管理。这一章先讲为什么\u201c活下来比一次赚快钱更重要\u201d:仓位怎么定、亏损怎么扛、情绪怎么不被行情牵着走;再用一个复盘案例,完整拆开一条看起来很漂亮的回测曲线,看它是怎么在偷看未来、幸存者偏差和成本假设上一步步被拆穿的。纸面收益和真实收益之间,隔着的正是这些。",
    },
    23: {
        "title": "全书复盘:从一条鱼到一个量化系统",
        "lead": "学到这里,名词已经很多:货币、信用、股票、债券、基金、期货、期权、指数、因子、回测、机器学习、组合优化、交易执行、风控。这一章把它们重新收束成一条链\u2014\u2014真实财富产生现金流,金融工具分配现金流和风险,市场给这些权利定价,数据记录市场状态,策略试图从数据里找到优势,实盘系统再把优势变成可控的交易。金融不是一堆孤立术语,量化也不是孤立算法。",
    },
    24: {
        "title": "职业路线与长期学习",
        "lead": "如果你想把兴趣变成职业,这一章讲两件事。一是计算机背景的人怎样进入量化:该积累什么能力、怎么攒一个能证明自己的作品集、面试和岗位大致看什么;二是一条能长期走下去的学习路线\u2014\u2014读什么、做什么、又怎么定期复盘。量化是一条需要耐心的路,走得远比一开始跑得快更重要。",
    },
    25: {
        "title": "术语复盘:用人话再讲一遍",
        "lead": "全书出现了大量术语,这一章把它们集中起来,用最朴素的人话再讲一遍,方便你随时回来查。前半部分复盘金融基础词汇:货币、信用、股票、债券、基金这些概念到底在说什么;后半部分复盘量化词汇:因子、回测、夏普、中性、滑点又分别指什么。不追求严谨定义,只求你一看就想起它对应的那件真实的事。",
    },
    26: {
        "title": "场景练习:开户软件和基金月报",
        "lead": "概念懂了,真正上手时还是会被界面和文件里的术语绊住。这一章用两个真实场景带你练一遍:第一次开户后,交易软件里每一个数字、每一个按钮到底在说什么;第一次拿到基金月报和产品报告,又该重点看哪些栏目、警惕哪些说法。把抽象概念落到你真会遇到的屏幕和纸面上,才算真的学会。",
    },
    27: {
        "title": "场景练习:回测报告和模拟盘",
        "lead": "这一章继续用场景带你练手。第一个场景:第一次看到一份回测报告,你该按什么顺序读、哪些指标最容易骗人、哪些细节能暴露它是否偷看了未来;第二个场景:第一次跑模拟盘的一周,每天该关注什么、会遇到哪些和回测不一样的意外。这些练习的目的,是让你在面对真实材料时有一套可靠的检查动作,而不是凭感觉。",
    },
    28: {
        "title": "场景练习:第一次小资金实盘",
        "lead": "小资金实盘不是为了证明自己能很快赚钱,而是为了验证真实的交易链路。这一章带你走一遍第一次小实盘:先把资金上限定在\u201c全亏掉也不影响生活\u201d的水平,再观察订单、成交、费用、滑点、持仓、对账和自己的情绪反应。这一步最重要的从来不是收益,而是知道真实市场会怎样改变你的系统和你的心态。",
    },
    29: {
        "title": "最终清单:动手前必须真正懂的事",
        "lead": "在真正动手做量化之前,有些事必须先真正弄懂,而不是\u201c好像知道\u201d。这一章给你两份清单:第一份是从金融小白走到量化之前,必须真正理解的金融常识;第二份是着手做量化项目之前,必须真正做到的准备。把这两份清单当成过关检查,任何一条答不上来,就说明前面某一章还需要回去补。",
    },
    30: {
        "title": "自检判断题与一个反面案例",
        "lead": "这一章用两种方式帮你检验自己是不是真的理解了。先是十个判断题,每一个都对应书里的一个关键直觉,答错说明那块地基还没打牢;再是一个反面案例,完整讲一个程序员是怎样凭着扎实的编程能力,却在量化里一步步亏钱的。别人踩过的坑,是最便宜的学费。",
    },
    31: {
        "title": "一个稳妥的项目与结语",
        "lead": "这一章先讲一个正面案例:一个稳妥的个人量化项目,是怎样从一个很小的问题出发,一点点长成能长期运行的东西的\u2014\u2014它和那些追求一夜暴富的做法,区别到底在哪里。最后是全书的结语,回答一个问题:读完这本书,你现在真正应该带走的是什么。不是某个策略,而是一套看待金融和量化的方式。",
    },
    32: {
        "title": "附录:每次研究前先读这张纸",
        "lead": "最后给你一张可以反复看的纸。每次你想做一个策略、买一个产品、写一个模型、跑一次回测,或者把模拟盘推向实盘之前,先把这一章读一遍。它不提供新概念,只帮你把手刹拉住几分钟\u2014\u2014很多亏损不是因为不懂高深理论,而是因为忘了最基本的问题:问题是否足够小、数据是否可信、成本是否算够、风险是否扛得住。",
    },
}


def strip_num_prefix(title: str) -> str:
    return re.sub(r"^[0-9一二三四五六七八九十]+[.、．]\s*", "", str(title)).strip()


def merge_title(new_num: int, parts: list) -> str:
    if new_num in CHAPTER_OVERRIDES:
        return CHAPTER_OVERRIDES[new_num]["title"]
    titles = [strip_num_prefix(ch["title"]) for ch in parts]
    if len(titles) == 1:
        return titles[0]
    first = titles[0].split(":")[0]
    last = titles[-1].split(":")[0]
    title = f"{first} 与 {last}"
    return title if len(title) <= 34 else f"{first} 等"


def merge_desc(parts: list) -> str:
    if len(parts) == 1:
        return parts[0]["desc"]
    return " / ".join(ch["desc"] for ch in parts[:2])


def merge_lead(new_num: int, parts: list) -> str:
    if new_num in CHAPTER_OVERRIDES:
        return CHAPTER_OVERRIDES[new_num]["lead"]
    return parts[0]["lead"]


def clean_section_title(title: str) -> str:
    """把原始子章标题压成简洁小节标题:去掉编号、取冒号主干、丢弃斜杠后半。"""
    t = strip_num_prefix(title)
    # "钱、价格和通胀: 鱼票为什么会缩水" -> 取冒号后的具体说法(通常更像小节)
    if ":" in t or "：" in t:
        parts_ct = re.split(r"[:：]", t, maxsplit=1)
        head = parts_ct[0].strip()
        tail = parts_ct[1].strip() if len(parts_ct) > 1 else ""
        t = tail if tail else head
    # "鱼票为什么会缩水 / 为什么小岛需要鱼票" -> 只留第一段
    t = re.split(r"\s*/\s*", t)[0].strip()
    return t


def merged_sections(parts: list) -> list:
    if len(parts) == 1:
        return [(clean_section_title(t), b) for t, b in parts[0]["sections"]]
    out = []
    for pi, part in enumerate(parts):
        # 第一个子主题的开场话已经被章导语(手写)覆盖,不再重复前置它的 lead,
        # 否则导语和正文第 1 段会高度重复,显得很机械。
        # 后续子主题保留 lead 作为"进入下一个主题"的过渡段。
        if pi > 0:
            out.append((clean_section_title(part["title"]), f"<p>{html.escape(part['lead'], quote=True)}</p>"))
        for title, body in part["sections"]:
            out.append((clean_section_title(title), body))
    return out


def build_visible_chapters(source: list) -> list:
    by_num = {ch["num"]: ch for ch in source}
    visible = []
    for new_num, nums in enumerate(CHAPTER_GROUPS):
        parts = [by_num[n] for n in nums]
        first = parts[0]
        visible.append({
            "num": new_num,
            "source_nums": nums,
            "part": VISIBLE_PARTS[new_num],
            "title": merge_title(new_num, parts),
            "desc": merge_desc(parts),
            "lead": merge_lead(new_num, parts),
            "sections": merged_sections(parts),
            # 单元分组:双单元章渲染为 h2(单元) + h3(小节)两层,避免二十多个平级小节
            "units": [
                {"title": clean_section_title(p["title"]), "lead": p["lead"] if i else None,
                 "sections": p["sections"]}
                for i, p in enumerate(parts)
            ],
            "summary": [item for ch in parts for item in ch["summary"][:2]][:5],
            "quiz": [item for ch in parts for item in ch["quiz"][:2]][:6],
        })
    return visible


CHAPTERS = build_visible_chapters(SOURCE_CHAPTERS)


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def slugify(text: str) -> str:
    s = text.lower().replace(":", " ").replace("：", " ").strip()
    s = re.sub(r"\s+", "-", s)
    return "".join(ch for ch in s if ch == "-" or ch.isalnum() or "\u4e00" <= ch <= "\u9fff")


def chapter_file(num: int) -> str:
    return f"chapter-{num:02d}.html"


def html_han_count(s: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", re.sub(r"<[^>]+>", "", str(s))))


def merge_section_title(titles: list) -> str:
    clean = [clean_section_title(t) for t in titles]
    if len(clean) == 1:
        return clean[0]
    # 相邻短小节被合并时,取第一个作为小节标题最干净;
    # 避免"标题A、标题B"这种机械拼接读起来像目录。
    return clean[0]


def prepare_sections(sections: list, min_han: int = 190) -> list:
    """Merge adjacent short manuscript sections into reading-sized rendered sections."""
    prepared = []
    bucket_titles = []
    bucket_bodies = []
    bucket_han = 0

    def flush():
        nonlocal bucket_titles, bucket_bodies, bucket_han
        if not bucket_titles:
            return
        prepared.append((merge_section_title(bucket_titles), "\n".join(bucket_bodies)))
        bucket_titles = []
        bucket_bodies = []
        bucket_han = 0

    for title, body in sections:
        h = html_han_count(body)
        if not bucket_titles:
            bucket_titles = [title]
            bucket_bodies = [body]
            bucket_han = h
        elif bucket_han < min_han and len(bucket_titles) < 3:
            bucket_titles.append(title)
            bucket_bodies.append(body)
            bucket_han += h
        else:
            flush()
            bucket_titles = [title]
            bucket_bodies = [body]
            bucket_han = h
        if bucket_han >= min_han:
            flush()
    flush()
    return prepared


def svg_lines(text: str, max_chars: int = 11, max_lines: int = 4) -> list:
    text = re.sub(r"\s+", "", str(text))
    text = re.sub(r"^[0-9一二三四五六七八九十]+[.、．]\s*", "", text)
    lines = [text[i:i + max_chars] for i in range(0, len(text), max_chars)]
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][:max_chars]
    return lines or [""]


def svg_text(text: str, x: int, y: int, width: int, *, size: int = 17, color: str = "#eef4f8",
             weight: int = 760, max_chars: int = 11, max_lines: int = 4) -> str:
    line_height = int(size * 1.35)
    lines = svg_lines(text, max_chars=max_chars, max_lines=max_lines)
    start_y = y - int((len(lines) - 1) * line_height / 2)
    tspans = []
    for i, line in enumerate(lines):
        tspans.append(
            f'<tspan x="{x}" y="{start_y + i * line_height}">{esc(line)}</tspan>'
        )
    return (
        f'<text x="{x}" y="{y}" text-anchor="middle" fill="{color}" '
        f'font-size="{size}" font-weight="{weight}">'
        + "".join(tspans)
        + "</text>"
    )


def concept_figure(svg_body: str, viewbox: str, aria: str, cap: str) -> str:
    """把一段手画 SVG 包成和章首图一致的 figure 结构。"""
    return f"""
        <div class="figure figure--reading reveal">
          <svg class="chapter-diagram" viewBox="{viewbox}" role="img" aria-label="{esc(aria)}">
{svg_body}
          </svg>
          <p class="figure__cap">{esc(cap)}</p>
        </div>"""


# 每个重点章手画的"真概念图":用坐标轴、曲线、时间轴、结构块解释一个具体概念,
# 取代原来纯装饰的"本章留下三件事"卡片图。key = 可见章号。
def _fig_inflation():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">多印鱼票,鱼没变多:每张票能换到的鱼变少</text>
            <!-- 左:发票前 -->
            <text x="230" y="74" text-anchor="middle" fill="#7aa7f0" font-size="16" font-weight="800">发票前</text>
            <text x="230" y="98" text-anchor="middle" fill="#c9d4e8" font-size="13">仓库 100 条鱼 · 流通 100 张票</text>
            <g fill="#f0c96a"><circle cx="150" cy="150" r="13"/><circle cx="190" cy="150" r="13"/><circle cx="230" cy="150" r="13"/><circle cx="270" cy="150" r="13"/><circle cx="310" cy="150" r="13"/></g>
            <text x="230" y="196" text-anchor="middle" fill="#a8c6ff" font-size="17" font-weight="800">1 张票 → 1 条鱼</text>
            <!-- 右:多印一倍票 -->
            <text x="670" y="74" text-anchor="middle" fill="#e88" font-size="16" font-weight="800">多印一倍票后</text>
            <text x="670" y="98" text-anchor="middle" fill="#c9d4e8" font-size="13">仓库仍 100 条鱼 · 流通 200 张票</text>
            <g fill="#f0c96a"><circle cx="590" cy="150" r="13"/><circle cx="630" cy="150" r="13"/><circle cx="670" cy="150" r="13"/><circle cx="710" cy="150" r="13"/><circle cx="750" cy="150" r="13"/></g>
            <text x="670" y="196" text-anchor="middle" fill="#ffb4b4" font-size="17" font-weight="800">2 张票 → 1 条鱼</text>
            <line x1="450" y1="60" x2="450" y2="210" stroke="#46587a" stroke-width="1.5" stroke-dasharray="6 6"/>
            <text x="450" y="246" text-anchor="middle" fill="#eef4f8" font-size="15">票变多,鱼没变多 → 同一条鱼要更多票 → 这就是通胀:购买力下降</text>"""
    return concept_figure(body, "0 0 900 270",
        "通胀示意:鱼票翻倍但鱼不变,每张票能换的鱼减半",
        "鱼票从 100 张翻到 200 张,仓库还是 100 条鱼,于是换一条鱼需要的票翻倍。通胀不是某样东西偶尔涨价,而是整体购买力下降。")


def _fig_bank_balance():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">银行资产负债表:钱不是躺在保险柜里</text>
            <!-- 资产侧 -->
            <rect x="70" y="70" width="330" height="200" rx="14" fill="rgba(122,167,240,0.10)" stroke="#7aa7f0" stroke-width="2"/>
            <text x="235" y="98" text-anchor="middle" fill="#a8c6ff" font-size="16" font-weight="800">资产(钱用到哪去了)</text>
            <rect x="92" y="116" width="286" height="52" rx="8" fill="rgba(122,167,240,0.18)"/>
            <text x="104" y="148" fill="#eef4ff" font-size="15">发放的贷款(最大一块,不在柜里)</text>
            <rect x="92" y="176" width="286" height="34" rx="8" fill="rgba(122,167,240,0.14)"/>
            <text x="104" y="198" fill="#eef4ff" font-size="14">债券等投资</text>
            <rect x="92" y="218" width="286" height="34" rx="8" fill="rgba(122,167,240,0.14)"/>
            <text x="104" y="240" fill="#eef4ff" font-size="14">准备金/现金(只留一小部分)</text>
            <!-- 负债侧 -->
            <rect x="500" y="70" width="330" height="200" rx="14" fill="rgba(240,201,106,0.10)" stroke="#f0c96a" stroke-width="2"/>
            <text x="665" y="98" text-anchor="middle" fill="#f0c96a" font-size="16" font-weight="800">负债+资本(钱从哪来的)</text>
            <rect x="522" y="116" width="286" height="76" rx="8" fill="rgba(240,201,106,0.16)"/>
            <text x="534" y="150" fill="#eef4ff" font-size="15">储户存款(你以为随时能全取)</text>
            <text x="534" y="174" fill="#c9d4e8" font-size="13">这其实是银行欠你的钱</text>
            <rect x="522" y="200" width="286" height="52" rx="8" fill="rgba(240,201,106,0.12)"/>
            <text x="534" y="232" fill="#eef4ff" font-size="14">银行自有资本(缓冲垫)</text>
            <text x="450" y="70" text-anchor="middle" fill="#c9d4e8" font-size="13">左右恒等</text>"""
    return concept_figure(body, "0 0 900 290",
        "银行资产负债表:左边资产以贷款为主,右边负债以存款为主,两侧金额相等",
        "银行把大部分存款放成了贷款和投资,柜里只留一小部分准备金。存款是银行欠储户的钱,所以\u201c钱躺在保险柜里\u201d是错觉。")


def _fig_bank_run():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">挤兑:为什么信心一崩,好银行也会倒</text>
            <text x="230" y="72" text-anchor="middle" fill="#a8c6ff" font-size="16" font-weight="800">正常时</text>
            <rect x="120" y="90" width="220" height="120" rx="12" fill="rgba(122,167,240,0.12)" stroke="#7aa7f0" stroke-width="2"/>
            <text x="230" y="120" text-anchor="middle" fill="#eef4ff" font-size="14">少数人来取钱</text>
            <text x="230" y="150" text-anchor="middle" fill="#eef4ff" font-size="14">准备金够付</text>
            <text x="230" y="184" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">银行照常运转</text>
            <text x="670" y="72" text-anchor="middle" fill="#ffb4b4" font-size="16" font-weight="800">恐慌时</text>
            <rect x="560" y="90" width="220" height="120" rx="12" fill="rgba(232,120,120,0.12)" stroke="#e88" stroke-width="2"/>
            <text x="670" y="118" text-anchor="middle" fill="#eef4ff" font-size="14">所有人同时来取钱</text>
            <text x="670" y="146" text-anchor="middle" fill="#eef4ff" font-size="14">贷款一时收不回</text>
            <text x="670" y="180" text-anchor="middle" fill="#ffb4b4" font-size="15" font-weight="800">准备金瞬间见底</text>
            <path d="M 355 150 L 545 150" fill="none" stroke="#f0c96a" stroke-width="2.5" marker-end="url(#runarrow)"/>
            <defs><marker id="runarrow" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#f0c96a"/></marker></defs>
            <text x="450" y="140" text-anchor="middle" fill="#c9d4e8" font-size="13">信心消失</text>
            <text x="450" y="250" text-anchor="middle" fill="#eef4f8" font-size="15">部分准备金制度下,银行本就没留够全额现金;挤兑是信心问题,不只是资产问题</text>"""
    return concept_figure(body, "0 0 900 275",
        "挤兑示意:正常时准备金够付,所有人同时取钱时准备金瞬间见底",
        "银行只留部分准备金,平时够用;一旦所有人同时来取,贷款收不回、准备金见底,连经营正常的银行也可能倒下。这就是存款保险和央行存在的原因之一。")


def _fig_bond_cashflow():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">一张 3 年期债券的现金流(面值 100,票息 5%)</text>
            <line x1="70" y1="180" x2="830" y2="180" stroke="#46587a" stroke-width="2" marker-end="url(#tarrow)"/>
            <defs><marker id="tarrow" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#46587a"/></marker></defs>
            <text x="828" y="205" text-anchor="end" fill="#8499bd" font-size="13">时间</text>
            <!-- 买入:现金流出 -->
            <line x1="130" y1="180" x2="130" y2="250" stroke="#e88" stroke-width="3"/>
            <path d="M 130 250 L 124 238 M 130 250 L 136 238" stroke="#e88" stroke-width="3" fill="none"/>
            <text x="130" y="272" text-anchor="middle" fill="#ffb4b4" font-size="14" font-weight="800">-100</text>
            <text x="130" y="150" text-anchor="middle" fill="#c9d4e8" font-size="13">买入</text>
            <!-- 每年票息:现金流入 -->
            <line x1="320" y1="180" x2="320" y2="130" stroke="#a8c6ff" stroke-width="3"/>
            <path d="M 320 130 L 314 142 M 320 130 L 326 142" stroke="#a8c6ff" stroke-width="3" fill="none"/>
            <text x="320" y="118" text-anchor="middle" fill="#a8c6ff" font-size="14" font-weight="800">+5</text>
            <text x="320" y="205" text-anchor="middle" fill="#8499bd" font-size="13">第1年</text>
            <line x1="510" y1="180" x2="510" y2="130" stroke="#a8c6ff" stroke-width="3"/>
            <path d="M 510 130 L 504 142 M 510 130 L 516 142" stroke="#a8c6ff" stroke-width="3" fill="none"/>
            <text x="510" y="118" text-anchor="middle" fill="#a8c6ff" font-size="14" font-weight="800">+5</text>
            <text x="510" y="205" text-anchor="middle" fill="#8499bd" font-size="13">第2年</text>
            <!-- 到期:票息+本金 -->
            <line x1="700" y1="180" x2="700" y2="88" stroke="#f0c96a" stroke-width="3"/>
            <path d="M 700 88 L 694 100 M 700 88 L 706 100" stroke="#f0c96a" stroke-width="3" fill="none"/>
            <text x="700" y="76" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">+105</text>
            <text x="700" y="205" text-anchor="middle" fill="#8499bd" font-size="13">第3年到期</text>
            <text x="450" y="252" text-anchor="middle" fill="#c9d4e8" font-size="13">先付出本金,之后按期收票息,到期收回本金+最后一期票息</text>"""
    return concept_figure(body, "0 0 900 290",
        "债券现金流时间轴:买入时付出100,每年收5,到期收回105",
        "债券的现金流写在合同里:今天付出本金,之后每年收固定票息,到期收回本金。把这些未来现金流按利率折算到今天,就是债券的价格。")


def _fig_option_payoff():
    body = """            <text x="450" y="30" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">期权到期收益:亏损有底,盈利放大</text>
            <!-- 看涨期权 -->
            <text x="230" y="60" text-anchor="middle" fill="#a8c6ff" font-size="16" font-weight="800">买入看涨期权</text>
            <line x1="80" y1="240" x2="400" y2="240" stroke="#46587a" stroke-width="1.5"/>
            <line x1="240" y1="90" x2="240" y2="250" stroke="#46587a" stroke-width="1.5"/>
            <text x="398" y="262" text-anchor="end" fill="#8499bd" font-size="12">到期股价</text>
            <text x="150" y="256" text-anchor="middle" fill="#8499bd" font-size="12">行权价 K</text>
            <path d="M 100 210 L 240 210 L 380 110" fill="none" stroke="#a8c6ff" stroke-width="3"/>
            <line x1="100" y1="210" x2="240" y2="210" stroke="#ffb4b4" stroke-width="3"/>
            <text x="150" y="200" text-anchor="middle" fill="#ffb4b4" font-size="12">亏损=权利金(有底)</text>
            <text x="350" y="98" text-anchor="middle" fill="#a8c6ff" font-size="12">涨越多赚越多</text>
            <!-- 看跌期权 -->
            <text x="670" y="60" text-anchor="middle" fill="#f0c96a" font-size="16" font-weight="800">买入看跌期权</text>
            <line x1="520" y1="240" x2="840" y2="240" stroke="#46587a" stroke-width="1.5"/>
            <line x1="680" y1="90" x2="680" y2="250" stroke="#46587a" stroke-width="1.5"/>
            <text x="838" y="262" text-anchor="end" fill="#8499bd" font-size="12">到期股价</text>
            <text x="700" y="256" text-anchor="middle" fill="#8499bd" font-size="12">行权价 K</text>
            <path d="M 540 110 L 680 210 L 820 210" fill="none" stroke="#f0c96a" stroke-width="3"/>
            <line x1="680" y1="210" x2="820" y2="210" stroke="#ffb4b4" stroke-width="3"/>
            <text x="760" y="200" text-anchor="middle" fill="#ffb4b4" font-size="12">亏损=权利金(有底)</text>
            <text x="575" y="98" text-anchor="middle" fill="#f0c96a" font-size="12">跌越多赚越多</text>"""
    return concept_figure(body, "0 0 900 285",
        "期权到期收益图:看涨和看跌期权买方的最大亏损都是权利金,收益随价格朝有利方向放大",
        "期权买方最多亏掉权利金(收益曲线下方有一条水平底),但价格朝有利方向走时收益会放大。这种不对称结构,是期权和直接买卖股票最大的不同。")


def _fig_drawdown_sharpe():
    body = """            <text x="450" y="30" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">同样终点,体验完全不同:回撤决定能不能拿得住</text>
            <line x1="70" y1="250" x2="850" y2="250" stroke="#46587a" stroke-width="1.5"/>
            <line x1="70" y1="60" x2="70" y2="250" stroke="#46587a" stroke-width="1.5"/>
            <text x="848" y="272" text-anchor="end" fill="#8499bd" font-size="13">时间</text>
            <text x="52" y="70" fill="#8499bd" font-size="13">净值</text>
            <!-- 平稳曲线 A -->
            <path d="M 70 230 Q 300 190 500 150 T 830 90" fill="none" stroke="#a8c6ff" stroke-width="3"/>
            <text x="700" y="110" fill="#a8c6ff" font-size="14" font-weight="800">A:平稳上行(夏普高)</text>
            <!-- 大起大落曲线 B,同终点 -->
            <path d="M 70 230 C 180 120 240 300 340 250 C 440 200 520 300 600 180 C 680 90 760 160 830 90" fill="none" stroke="#f0c96a" stroke-width="3"/>
            <text x="150" y="300" fill="#f0c96a" font-size="14" font-weight="800">B:先跌一半再涨回(夏普低)</text>
            <!-- 回撤标注 -->
            <line x1="340" y1="150" x2="340" y2="250" stroke="#e88" stroke-width="1.5" stroke-dasharray="5 4"/>
            <text x="360" y="215" fill="#ffb4b4" font-size="13">最大回撤:从高点跌下来的最深幅度</text>
            <circle cx="830" cy="90" r="6" fill="#eef4ff"/>
            <text x="812" y="78" text-anchor="end" fill="#eef4ff" font-size="12">终点相同</text>"""
    return concept_figure(body, "0 0 900 315",
        "两条净值曲线终点相同,A平稳上行,B先深跌再涨回,B的最大回撤更大、夏普更低",
        "两条曲线赚的钱一样多,但 B 中途跌掉一半,多数人拿不住会在低点割肉。最大回撤和夏普比率,衡量的正是这种\u201c时间里的体验\u201d,不是只看终点。")


def _fig_factor_quantile():
    body = """            <text x="450" y="30" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">分层回测:把股票按因子值分成5组,看收益是否单调</text>
            <line x1="90" y1="250" x2="850" y2="250" stroke="#46587a" stroke-width="1.5"/>
            <line x1="90" y1="60" x2="90" y2="250" stroke="#46587a" stroke-width="1.5"/>
            <text x="60" y="70" fill="#8499bd" font-size="13">未来收益</text>
            <!-- 5根柱子,单调递增 -->
            <rect x="150" y="200" width="90" height="50" fill="#e88" opacity="0.75"/>
            <text x="195" y="270" text-anchor="middle" fill="#8499bd" font-size="12">第1组(因子最低)</text>
            <rect x="290" y="175" width="90" height="75" fill="#c98b6a" opacity="0.8"/>
            <text x="335" y="270" text-anchor="middle" fill="#8499bd" font-size="12">第2组</text>
            <rect x="430" y="150" width="90" height="100" fill="#b0a06a" opacity="0.8"/>
            <text x="475" y="270" text-anchor="middle" fill="#8499bd" font-size="12">第3组</text>
            <rect x="570" y="120" width="90" height="130" fill="#8fb37a" opacity="0.85"/>
            <text x="615" y="270" text-anchor="middle" fill="#8499bd" font-size="12">第4组</text>
            <rect x="710" y="90" width="90" height="160" fill="#a8c6ff" opacity="0.9"/>
            <text x="755" y="270" text-anchor="middle" fill="#8499bd" font-size="12">第5组(因子最高)</text>
            <path d="M 195 195 L 335 170 L 475 145 L 615 115 L 755 85" fill="none" stroke="#eef4f8" stroke-width="2" stroke-dasharray="6 5"/>
            <text x="600" y="70" fill="#eef4ff" font-size="13">收益随分组单调上升 → 因子可能有效</text>"""
    return concept_figure(body, "0 0 900 290",
        "因子分层回测柱状图:按因子值把股票分成5组,从第1组到第5组未来收益单调递增",
        "把股票按因子值排序、平均分成几组,再看每组之后的平均收益。如果从低到高单调递增(或递减),说明这个因子可能真的携带信息,而不是随机噪声。")


def _fig_lookahead():
    body = """            <text x="450" y="30" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">回测最致命的错:偷看了未来</text>
            <line x1="70" y1="150" x2="830" y2="150" stroke="#46587a" stroke-width="2" marker-end="url(#la)"/>
            <defs><marker id="la" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#46587a"/></marker></defs>
            <line x1="450" y1="80" x2="450" y2="220" stroke="#f0c96a" stroke-width="2" stroke-dasharray="6 5"/>
            <text x="450" y="70" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">决策时点(此刻)</text>
            <rect x="110" y="112" width="320" height="40" rx="8" fill="rgba(122,167,240,0.2)" stroke="#7aa7f0"/>
            <text x="270" y="138" text-anchor="middle" fill="#a8c6ff" font-size="14" font-weight="800">已知:历史数据(能用)</text>
            <rect x="470" y="112" width="320" height="40" rx="8" fill="rgba(232,120,120,0.18)" stroke="#e88"/>
            <text x="630" y="138" text-anchor="middle" fill="#ffb4b4" font-size="14" font-weight="800">未知:未来数据(不能用)</text>
            <path d="M 630 112 C 620 60 480 60 458 104" fill="none" stroke="#e88" stroke-width="2.5" marker-end="url(#la)"/>
            <text x="560" y="55" text-anchor="middle" fill="#ffb4b4" font-size="13">用未来信息做当下决策 = 未来函数</text>
            <text x="450" y="250" text-anchor="middle" fill="#c9d4e8" font-size="14">回测里一旦用到决策时点还不知道的信息,收益就是假的</text>
            <text x="450" y="276" text-anchor="middle" fill="#8499bd" font-size="13">常见来源:用收盘价当天下单、复权/财报数据提前、标签泄漏</text>"""
    return concept_figure(body, "0 0 900 295",
        "未来函数示意:决策时点左边是可用的历史,右边是不可用的未来,用到未来信息就是偷看答案",
        "回测在某个时点做决策时,只能用那一刻已经公开的信息。一旦用到当时还不知道的未来数据(未来函数),回测收益就是幻觉,实盘一定复现不了。")


# 可见章号 -> 该章要插入的手画概念图列表(按顺序渲染)。
# 这些图取代原本纯装饰的"本章留下三件事"卡片图。
def _fig_money_flow():
    body = """            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">钱和风险怎么在金融系统里流动</text>
            <!-- 左:资金盈余方 -->
            <rect x="40" y="90" width="170" height="130" rx="14" fill="rgba(122,167,240,0.12)" stroke="#7aa7f0" stroke-width="2"/>
            <text x="125" y="128" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">有钱的人</text>
            <text x="125" y="156" text-anchor="middle" fill="#c9d4e8" font-size="13">储户、投资者</text>
            <text x="125" y="182" text-anchor="middle" fill="#c9d4e8" font-size="13">想让钱增值</text>
            <!-- 中:金融中介 -->
            <rect x="330" y="72" width="240" height="166" rx="16" fill="rgba(240,201,106,0.12)" stroke="#f0c96a" stroke-width="2"/>
            <text x="450" y="104" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">金融中介与市场</text>
            <text x="450" y="132" text-anchor="middle" fill="#c9d4e8" font-size="12.5">银行 · 券商 · 基金</text>
            <text x="450" y="156" text-anchor="middle" fill="#c9d4e8" font-size="12.5">交易所 · 托管</text>
            <text x="450" y="180" text-anchor="middle" fill="#c9d4e8" font-size="12.5">撮合 · 定价 · 监管</text>
            <text x="450" y="212" text-anchor="middle" fill="#8499bd" font-size="12">把钱和风险重新分配</text>
            <!-- 右:资金需求方 -->
            <rect x="690" y="90" width="170" height="130" rx="14" fill="rgba(122,167,240,0.12)" stroke="#7aa7f0" stroke-width="2"/>
            <text x="775" y="128" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">缺钱的人</text>
            <text x="775" y="156" text-anchor="middle" fill="#c9d4e8" font-size="13">企业、政府</text>
            <text x="775" y="182" text-anchor="middle" fill="#c9d4e8" font-size="13">想融资办事</text>
            <!-- 箭头:资金右流,收益权左流 -->
            <path d="M 214 130 L 326 130" fill="none" stroke="#a8c6ff" stroke-width="3" marker-end="url(#mfa)"/>
            <text x="270" y="120" text-anchor="middle" fill="#a8c6ff" font-size="12">资金</text>
            <path d="M 570 130 L 686 130" fill="none" stroke="#a8c6ff" stroke-width="3" marker-end="url(#mfa)"/>
            <text x="628" y="120" text-anchor="middle" fill="#a8c6ff" font-size="12">资金</text>
            <path d="M 686 200 L 570 200" fill="none" stroke="#f0c96a" stroke-width="3" marker-end="url(#mfb)"/>
            <path d="M 326 200 L 214 200" fill="none" stroke="#f0c96a" stroke-width="3" marker-end="url(#mfb)"/>
            <text x="450" y="272" text-anchor="middle" fill="#c9d4e8" font-size="13">钱从盈余方流向需求方;股权、债权和利息等\u201c收益和风险\u201d反向流回</text>
            <defs>
              <marker id="mfa" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#a8c6ff"/></marker>
              <marker id="mfb" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#f0c96a"/></marker>
            </defs>"""
    return concept_figure(body, "0 0 900 290",
        "金融系统资金流示意:资金从盈余方经中介流向需求方,收益和风险反向流回",
        "金融系统的核心就是这张图:把有钱但暂时不用的人,和缺钱但能创造价值的人对接起来。中间的银行、券商、基金、交易所负责撮合、定价、托管和分配风险。")


def _fig_stock_ownership():
    body = """            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">买一股,就是把公司切成很多份、你拿其中一份</text>
            <!-- 公司大饼 -->
            <circle cx="230" cy="160" r="95" fill="rgba(18,29,49,0.6)" stroke="#f0c96a" stroke-width="2"/>
            <path d="M 230 160 L 230 65 A 95 95 0 0 1 315 200 Z" fill="rgba(240,201,106,0.28)" stroke="#f0c96a"/>
            <path d="M 230 160 L 315 200 A 95 95 0 0 1 175 249 Z" fill="rgba(122,167,240,0.22)" stroke="#7aa7f0"/>
            <path d="M 230 160 L 175 249 A 95 95 0 0 1 149 100 Z" fill="rgba(122,167,240,0.14)" stroke="#7aa7f0"/>
            <path d="M 230 160 L 149 100 A 95 95 0 0 1 230 65 Z" fill="rgba(122,167,240,0.14)" stroke="#7aa7f0"/>
            <text x="230" y="285" text-anchor="middle" fill="#c9d4e8" font-size="13">一家公司 = 总股本</text>
            <text x="272" y="130" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">你的1股</text>
            <!-- 右:你这一份意味着什么 -->
            <text x="600" y="86" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">持有这一份,你就有</text>
            <rect x="440" y="104" width="410" height="40" rx="8" fill="rgba(122,167,240,0.12)"/>
            <text x="460" y="130" fill="#eef4ff" font-size="14">· 分红权:公司赚钱后按份额分你一部分</text>
            <rect x="440" y="152" width="410" height="40" rx="8" fill="rgba(122,167,240,0.12)"/>
            <text x="460" y="178" fill="#eef4ff" font-size="14">· 投票权:重大事项按份额投票</text>
            <rect x="440" y="200" width="410" height="40" rx="8" fill="rgba(122,167,240,0.12)"/>
            <text x="460" y="226" fill="#eef4ff" font-size="14">· 剩余索取权:还完债、剩下的才归股东</text>
            <text x="645" y="270" text-anchor="middle" fill="#ffb4b4" font-size="13">上不封顶,但也可能归零</text>"""
    return concept_figure(body, "0 0 900 300",
        "股票所有权示意:公司被切成很多股,持有一股即拥有对应比例的分红权、投票权和剩余索取权",
        "买股票不是买一个会涨的数字,而是买下公司的一小片所有权。公司做大,你这一份跟着变值钱;公司倒了,你排在债主后面,可能血本无归。")


def _fig_orderbook():
    body = """            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">订单簿:买卖双方在这里排队,价格优先、时间优先</text>
            <!-- 卖盘(上,红) -->
            <text x="250" y="70" text-anchor="middle" fill="#ffb4b4" font-size="14" font-weight="800">卖盘(想卖的人)</text>
            <rect x="150" y="80" width="200" height="26" rx="4" fill="rgba(232,120,120,0.28)"/><text x="160" y="99" fill="#eef4ff" font-size="13">卖三  10.03  ×  800</text>
            <rect x="150" y="110" width="200" height="26" rx="4" fill="rgba(232,120,120,0.22)"/><text x="160" y="129" fill="#eef4ff" font-size="13">卖二  10.02  ×  500</text>
            <rect x="150" y="140" width="200" height="26" rx="4" fill="rgba(232,120,120,0.16)"/><text x="160" y="159" fill="#eef4ff" font-size="13">卖一  10.01  ×  300</text>
            <!-- 价差 -->
            <line x1="150" y1="176" x2="350" y2="176" stroke="#f0c96a" stroke-width="1.5" stroke-dasharray="5 4"/>
            <text x="370" y="181" fill="#f0c96a" font-size="12">← 买一卖一之间是价差</text>
            <!-- 买盘(下,绿) -->
            <rect x="150" y="186" width="200" height="26" rx="4" fill="rgba(122,167,240,0.16)"/><text x="160" y="205" fill="#eef4ff" font-size="13">买一  10.00  ×  400</text>
            <rect x="150" y="216" width="200" height="26" rx="4" fill="rgba(122,167,240,0.22)"/><text x="160" y="235" fill="#eef4ff" font-size="13">买二   9.99  ×  600</text>
            <rect x="150" y="246" width="200" height="26" rx="4" fill="rgba(122,167,240,0.28)"/><text x="160" y="265" fill="#eef4ff" font-size="13">买三   9.98  ×  900</text>
            <text x="250" y="292" text-anchor="middle" fill="#a8c6ff" font-size="14" font-weight="800">买盘(想买的人)</text>
            <!-- 右侧说明 -->
            <text x="470" y="110" fill="#eef4ff" font-size="14" font-weight="800">成交怎么发生?</text>
            <text x="470" y="140" fill="#c9d4e8" font-size="13">你出 10.01 买 → 立刻和卖一成交</text>
            <text x="470" y="168" fill="#c9d4e8" font-size="13">你出 10.00 买 → 排进买一等着</text>
            <text x="470" y="196" fill="#c9d4e8" font-size="13">同价看谁先挂,先到先成交</text>
            <text x="470" y="230" fill="#8499bd" font-size="12.5">挂涨停价也未必买到:卖盘太少</text>
            <text x="470" y="254" fill="#8499bd" font-size="12.5">时,后面排队的人只能干等</text>"""
    return concept_figure(body, "0 0 900 305",
        "订单簿示意:卖盘从卖一到卖三价格递增,买盘从买一到买三价格递减,中间是买卖价差",
        "屏幕上的\u201c买一卖一\u201d来自订单簿。所有人的买卖意愿在这里按价格和时间排队,成交价就是买卖力量碰在一起的结果。只用收盘价回测,会忽略排队和盘口深度。")


def _fig_candlestick():
    body = """            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">一根 K 线,记录一段时间里的四个价格</text>
            <!-- 阳线 -->
            <text x="250" y="76" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">阳线(收盘 &gt; 开盘)</text>
            <line x1="250" y1="96" x2="250" y2="130" stroke="#a8c6ff" stroke-width="2"/>
            <line x1="250" y1="230" x2="250" y2="262" stroke="#a8c6ff" stroke-width="2"/>
            <rect x="222" y="130" width="56" height="100" rx="3" fill="rgba(122,167,240,0.30)" stroke="#a8c6ff" stroke-width="2"/>
            <text x="300" y="104" fill="#c9d4e8" font-size="12.5">最高价</text>
            <text x="300" y="140" fill="#c9d4e8" font-size="12.5">收盘价(上沿)</text>
            <text x="300" y="228" fill="#c9d4e8" font-size="12.5">开盘价(下沿)</text>
            <text x="300" y="262" fill="#c9d4e8" font-size="12.5">最低价</text>
            <!-- 阴线 -->
            <text x="620" y="76" text-anchor="middle" fill="#ffb4b4" font-size="15" font-weight="800">阴线(收盘 &lt; 开盘)</text>
            <line x1="620" y1="96" x2="620" y2="130" stroke="#ffb4b4" stroke-width="2"/>
            <line x1="620" y1="230" x2="620" y2="262" stroke="#ffb4b4" stroke-width="2"/>
            <rect x="592" y="130" width="56" height="100" rx="3" fill="rgba(232,120,120,0.28)" stroke="#ffb4b4" stroke-width="2"/>
            <text x="670" y="104" fill="#c9d4e8" font-size="12.5">最高价</text>
            <text x="670" y="140" fill="#c9d4e8" font-size="12.5">开盘价(上沿)</text>
            <text x="670" y="228" fill="#c9d4e8" font-size="12.5">收盘价(下沿)</text>
            <text x="670" y="262" fill="#c9d4e8" font-size="12.5">最低价</text>
            <text x="450" y="292" text-anchor="middle" fill="#8499bd" font-size="13">实体是开盘和收盘,上下影线是这段时间摸到的最高和最低</text>"""
    return concept_figure(body, "0 0 900 305",
        "K线构成示意:阳线收盘高于开盘,阴线收盘低于开盘,上下影线是最高价和最低价",
        "一根 K 线把一段时间压缩成四个数:开盘、收盘、最高、最低。实体两端是开盘和收盘,细细的影线是期间摸到过的最高和最低价。")


def _fig_quant_pipeline():
    body = """            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">量化是一条流水线,算法只是其中一环</text>
            <!-- 5 个流程块 -->
            <rect x="30" y="90" width="150" height="90" rx="12" fill="rgba(122,167,240,0.14)" stroke="#7aa7f0" stroke-width="2"/>
            <text x="105" y="126" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">数据</text>
            <text x="105" y="150" text-anchor="middle" fill="#c9d4e8" font-size="12">采集·清洗·对齐</text>
            <rect x="205" y="90" width="150" height="90" rx="12" fill="rgba(122,167,240,0.14)" stroke="#7aa7f0" stroke-width="2"/>
            <text x="280" y="126" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">信号/因子</text>
            <text x="280" y="150" text-anchor="middle" fill="#c9d4e8" font-size="12">研究员建模</text>
            <rect x="380" y="90" width="150" height="90" rx="12" fill="rgba(240,201,106,0.16)" stroke="#f0c96a" stroke-width="2"/>
            <text x="455" y="126" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">组合</text>
            <text x="455" y="150" text-anchor="middle" fill="#c9d4e8" font-size="12">优化·约束</text>
            <rect x="555" y="90" width="150" height="90" rx="12" fill="rgba(240,201,106,0.16)" stroke="#f0c96a" stroke-width="2"/>
            <text x="630" y="126" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">交易执行</text>
            <text x="630" y="150" text-anchor="middle" fill="#c9d4e8" font-size="12">下单·成交</text>
            <rect x="730" y="90" width="140" height="90" rx="12" fill="rgba(232,120,120,0.14)" stroke="#e88" stroke-width="2"/>
            <text x="800" y="126" text-anchor="middle" fill="#ffb4b4" font-size="15" font-weight="800">风控</text>
            <text x="800" y="150" text-anchor="middle" fill="#c9d4e8" font-size="12">盯边界·止损</text>
            <!-- 箭头 -->
            <g stroke="#8499bd" stroke-width="2.5" fill="none">
              <path d="M 180 135 L 203 135" marker-end="url(#qp)"/>
              <path d="M 355 135 L 378 135" marker-end="url(#qp)"/>
              <path d="M 530 135 L 553 135" marker-end="url(#qp)"/>
              <path d="M 705 135 L 728 135" marker-end="url(#qp)"/>
            </g>
            <!-- 风控反馈回路 -->
            <path d="M 800 180 C 800 240 105 240 105 182" fill="none" stroke="#e88" stroke-width="2" stroke-dasharray="6 5" marker-end="url(#qpr)"/>
            <text x="450" y="235" text-anchor="middle" fill="#ffb4b4" font-size="12.5">风控和监控持续反馈,发现问题就减仓、停用、回炉</text>
            <text x="450" y="278" text-anchor="middle" fill="#8499bd" font-size="13">任何一环出错,再强的模型也赚不到钱</text>
            <defs>
              <marker id="qp" markerWidth="9" markerHeight="9" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#8499bd"/></marker>
              <marker id="qpr" markerWidth="9" markerHeight="9" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#e88"/></marker>
            </defs>"""
    return concept_figure(body, "0 0 900 295",
        "量化流水线示意:数据到信号到组合到执行到风控,风控持续反馈回整条链路",
        "量化不是\u201c写个模型就赚钱\u201d,而是一条流水线:数据、因子、组合、执行、风控环环相扣。任何一环掉链子,前面做得再好也白搭。")


def _fig_index_enhance():
    body = """            <text x="450" y="30" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">指数增强:紧贴指数,再想办法多赚一点点</text>
            <line x1="70" y1="250" x2="850" y2="250" stroke="#46587a" stroke-width="1.5"/>
            <line x1="70" y1="60" x2="70" y2="250" stroke="#46587a" stroke-width="1.5"/>
            <text x="848" y="272" text-anchor="end" fill="#8499bd" font-size="13">时间</text>
            <text x="52" y="70" fill="#8499bd" font-size="13">净值</text>
            <!-- 指数基准线 -->
            <path d="M 70 235 Q 300 195 520 165 T 830 120" fill="none" stroke="#8499bd" stroke-width="2.5" stroke-dasharray="7 5"/>
            <text x="700" y="150" fill="#8499bd" font-size="14" font-weight="800">指数基准</text>
            <!-- 增强线,略高于基准 -->
            <path d="M 70 235 Q 300 182 520 145 T 830 92" fill="none" stroke="#a8c6ff" stroke-width="3"/>
            <text x="600" y="96" fill="#a8c6ff" font-size="14" font-weight="800">指数增强</text>
            <!-- 超额区间标注 -->
            <line x1="830" y1="92" x2="830" y2="120" stroke="#f0c96a" stroke-width="2"/>
            <path d="M 830 92 L 825 102 M 830 92 L 835 102" stroke="#f0c96a" stroke-width="2" fill="none"/>
            <text x="815" y="80" text-anchor="end" fill="#f0c96a" font-size="13">超额收益(Alpha)</text>
            <text x="450" y="292" text-anchor="middle" fill="#c9d4e8" font-size="13">大方向跟着指数走(Beta),再靠选股在上面抠出一层薄薄的超额</text>"""
    return concept_figure(body, "0 0 900 305",
        "指数增强示意:增强曲线贴着指数基准走,并持续高出一小截超额收益",
        "指数增强不追求暴利。它先老老实实跟住指数(拿到市场平均的 Beta),再用量化选股在基准之上多挤出一点超额收益(Alpha)。日积月累,这一点点也很可观。")


def _fig_market_neutral():
    body = """            <text x="450" y="30" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">市场中性:买一篮子、卖空等额,抵掉大盘涨跌</text>
            <!-- 多头柱 -->
            <text x="200" y="76" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">多头:买入看好的股票</text>
            <rect x="130" y="90" width="140" height="70" rx="6" fill="rgba(122,167,240,0.25)" stroke="#a8c6ff" stroke-width="2"/>
            <text x="200" y="132" text-anchor="middle" fill="#eef4ff" font-size="14">+100 万</text>
            <!-- 空头柱 -->
            <text x="200" y="196" text-anchor="middle" fill="#ffb4b4" font-size="15" font-weight="800">空头:卖空指数/看淡的股票</text>
            <rect x="130" y="206" width="140" height="70" rx="6" fill="rgba(232,120,120,0.22)" stroke="#ffb4b4" stroke-width="2"/>
            <text x="200" y="248" text-anchor="middle" fill="#eef4ff" font-size="14">-100 万</text>
            <!-- 等号与结果 -->
            <text x="330" y="185" text-anchor="middle" fill="#f0c96a" font-size="30" font-weight="800">=</text>
            <rect x="380" y="95" width="470" height="180" rx="14" fill="rgba(18,29,49,0.5)" stroke="rgba(240,201,106,0.3)"/>
            <text x="615" y="128" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">大盘涨跌被抵消</text>
            <text x="410" y="162" fill="#c9d4e8" font-size="13.5">· 大盘涨 5%:多头 +5%、空头 -5%,方向对冲掉</text>
            <text x="410" y="192" fill="#c9d4e8" font-size="13.5">· 剩下的,是你选股比指数强的那部分</text>
            <text x="410" y="222" fill="#a8c6ff" font-size="13.5">· 赚的是\u201c选股能力\u201d,不赌大盘方向</text>
            <text x="410" y="252" fill="#ffb4b4" font-size="12.5">· 但对冲有成本,基差、融券、极端行情仍是风险</text>"""
    return concept_figure(body, "0 0 900 300",
        "市场中性示意:多头买入等额、空头卖空,大盘方向被对冲,只留下选股超额",
        "市场中性用一手买、一手卖空,把\u201c大盘涨不涨\u201d这个最大的不确定性对冲掉,只留下你选股比别人强的那一小块收益。代价是对冲本身要花钱,也有失效的时候。")


def _fig_income_statement():
    body = """            <text x="450" y="30" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">利润表:收入一层层减下去,才剩净利润</text>
            <!-- 漏斗式递减条 -->
            <rect x="250" y="60" width="400" height="40" rx="4" fill="rgba(122,167,240,0.30)" stroke="#a8c6ff"/>
            <text x="450" y="86" text-anchor="middle" fill="#eef4ff" font-size="14" font-weight="800">营业收入(卖东西收到的钱)</text>
            <text x="672" y="86" fill="#8499bd" font-size="12">100</text>
            <rect x="285" y="108" width="330" height="36" rx="4" fill="rgba(122,167,240,0.24)"/>
            <text x="450" y="132" text-anchor="middle" fill="#eef4ff" font-size="13.5">− 成本 → 毛利</text>
            <text x="637" y="131" fill="#8499bd" font-size="12">60</text>
            <rect x="320" y="152" width="260" height="36" rx="4" fill="rgba(122,167,240,0.18)"/>
            <text x="450" y="176" text-anchor="middle" fill="#eef4ff" font-size="13.5">− 费用 → 营业利润</text>
            <text x="602" y="175" fill="#8499bd" font-size="12">30</text>
            <rect x="355" y="196" width="190" height="36" rx="4" fill="rgba(240,201,106,0.22)"/>
            <text x="450" y="220" text-anchor="middle" fill="#eef4ff" font-size="13.5">− 税 → 净利润</text>
            <text x="567" y="219" fill="#f0c96a" font-size="12">20</text>
            <text x="450" y="266" text-anchor="middle" fill="#c9d4e8" font-size="13">收入不等于利润:中间要一层层扣掉成本、费用和税</text>
            <text x="450" y="290" text-anchor="middle" fill="#8499bd" font-size="12.5">另外两张表:资产负债表看\u201c有什么欠什么\u201d,现金流量表看\u201c钱真进真出\u201d</text>"""
    return concept_figure(body, "0 0 900 305",
        "利润表漏斗示意:营业收入依次减成本、费用、税,最后才是净利润",
        "利润表像一个漏斗:最上面是收入,往下每一层都要扣掉一块成本,最后漏出来的才是净利润。所以\u201c收入高\u201d不等于\u201c真赚钱\u201d,要看它一路扣完还剩多少。")


def _fig_project_layout():
    body = """            <text x="450" y="30" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">量化项目要分层,别塞进一个大 notebook</text>
            <!-- 分层结构 -->
            <rect x="120" y="60" width="660" height="40" rx="8" fill="rgba(122,167,240,0.20)" stroke="#a8c6ff" stroke-width="1.5"/>
            <text x="140" y="85" fill="#eef4ff" font-size="14">data/  原始与清洗后的数据,来源和口径清楚</text>
            <rect x="120" y="106" width="660" height="40" rx="8" fill="rgba(122,167,240,0.16)" stroke="#7aa7f0" stroke-width="1.5"/>
            <text x="140" y="131" fill="#eef4ff" font-size="14">factors/  因子计算,每个因子一个可复现脚本</text>
            <rect x="120" y="152" width="660" height="40" rx="8" fill="rgba(240,201,106,0.16)" stroke="#f0c96a" stroke-width="1.5"/>
            <text x="140" y="177" fill="#eef4ff" font-size="14">backtest/  回测引擎与成交、成本、约束假设</text>
            <rect x="120" y="198" width="660" height="40" rx="8" fill="rgba(240,201,106,0.16)" stroke="#f0c96a" stroke-width="1.5"/>
            <text x="140" y="223" fill="#eef4ff" font-size="14">config/  参数与实验配置,可重复、可追溯</text>
            <rect x="120" y="244" width="660" height="40" rx="8" fill="rgba(122,167,240,0.16)" stroke="#7aa7f0" stroke-width="1.5"/>
            <text x="140" y="269" fill="#eef4ff" font-size="14">reports/  自动生成的净值、指标和归因报告</text>
            <text x="450" y="300" text-anchor="middle" fill="#8499bd" font-size="12.5">每层职责单一,换人接手也能看懂,几周后自己也不会迷路</text>"""
    return concept_figure(body, "0 0 900 315",
        "量化项目分层结构示意:data、factors、backtest、config、reports 各司其职",
        "把项目按职责拆成清晰的几层,而不是全写进一个越拉越长的 notebook。数据、因子、回测、配置、报告各归各位,几周后你和接手的人都还能看懂。")


def _fig_arbitrage():
    body = """            <text x="450" y="30" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">相对价值套利:赌两个价格的价差会收敛回来</text>
            <line x1="70" y1="250" x2="850" y2="250" stroke="#46587a" stroke-width="1.5"/>
            <line x1="70" y1="55" x2="70" y2="250" stroke="#46587a" stroke-width="1.5"/>
            <text x="848" y="272" text-anchor="end" fill="#8499bd" font-size="13">时间</text>
            <text x="52" y="65" fill="#8499bd" font-size="13">价格</text>
            <!-- 两条本应同步的价格线,中间张开又收回 -->
            <path d="M 90 180 C 250 120 320 100 430 95 C 540 100 650 150 830 150" fill="none" stroke="#a8c6ff" stroke-width="2.5"/>
            <path d="M 90 190 C 250 185 320 190 430 175 C 540 165 650 155 830 152" fill="none" stroke="#f0c96a" stroke-width="2.5"/>
            <text x="250" y="95" fill="#a8c6ff" font-size="13">资产 A</text>
            <text x="250" y="205" fill="#f0c96a" font-size="13">资产 B</text>
            <!-- 价差最大处 -->
            <line x1="430" y1="95" x2="430" y2="175" stroke="#ffb4b4" stroke-width="1.5" stroke-dasharray="5 4"/>
            <text x="440" y="138" fill="#ffb4b4" font-size="12.5">价差拉大 → 此时下注:买低卖高</text>
            <!-- 收敛处 -->
            <circle cx="830" cy="151" r="5" fill="#eef4ff"/>
            <text x="815" y="138" text-anchor="end" fill="#eef4ff" font-size="12.5">价差收敛 → 平仓获利</text>
            <text x="450" y="292" text-anchor="middle" fill="#8499bd" font-size="12.5">赌的是\u201c价差回归\u201d;但如果价差不收敛反而继续扩大,加上杠杆就可能被拖垮(想想 LTCM)</text>"""
    return concept_figure(body, "0 0 900 305",
        "相对价值套利示意:两个资产价格张开价差后又收敛,价差最大时下注、收敛时获利",
        "多数\u201c套利\u201d不是白捡钱,而是赌两个本该同步的价格,在价差拉大后会重新收敛。赌对了赚价差,但价差也可能继续扩大\u2014\u2014这正是相对价值交易的真实风险。")


def _fig_fund_nav():
    body = """            <text x="450" y="30" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">你买到的不是模型,是扣费后的一条净值曲线</text>
            <line x1="70" y1="250" x2="850" y2="250" stroke="#46587a" stroke-width="1.5"/>
            <line x1="70" y1="55" x2="70" y2="250" stroke="#46587a" stroke-width="1.5"/>
            <text x="52" y="65" fill="#8499bd" font-size="13">净值</text>
            <!-- 毛收益线 -->
            <path d="M 70 225 Q 300 175 520 140 T 830 85" fill="none" stroke="#8499bd" stroke-width="2.5" stroke-dasharray="7 5"/>
            <text x="640" y="108" fill="#8499bd" font-size="13.5">策略毛收益(宣传里常展示这条)</text>
            <!-- 净收益线,被费用压低 -->
            <path d="M 70 225 Q 300 195 520 170 T 830 130" fill="none" stroke="#a8c6ff" stroke-width="3"/>
            <text x="610" y="150" fill="#a8c6ff" font-size="13.5">你到手的净值(扣费后)</text>
            <!-- 费用差 -->
            <line x1="830" y1="85" x2="830" y2="130" stroke="#ffb4b4" stroke-width="2"/>
            <text x="822" y="76" text-anchor="end" fill="#ffb4b4" font-size="12.5">管理费+业绩报酬+申赎</text>
            <text x="450" y="288" text-anchor="middle" fill="#c9d4e8" font-size="13">还要看封闭期能不能赎、净值多久披露一次、回撤时能不能扛得住</text>"""
    return concept_figure(body, "0 0 900 300",
        "基金净值示意:毛收益曲线在上,扣掉各项费用后的净值曲线在下,差额是费用",
        "买量化产品,真正到你手里的是\u201c扣费后\u201d那条净值曲线,不是宣传页上的毛收益。管理费、业绩报酬、申赎费、封闭期,每一项都在你和策略收益之间。")


def _fig_backtest_loop():
    body = """            <text x="450" y="30" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">回测就是在历史里,一天天重放这个循环</text>
            <!-- 环形流程 6 步 -->
            <rect x="360" y="60" width="180" height="46" rx="10" fill="rgba(122,167,240,0.16)" stroke="#7aa7f0" stroke-width="1.5"/>
            <text x="450" y="88" text-anchor="middle" fill="#eef4ff" font-size="13.5">① 读取当时可见数据</text>
            <rect x="640" y="120" width="180" height="46" rx="10" fill="rgba(122,167,240,0.16)" stroke="#7aa7f0" stroke-width="1.5"/>
            <text x="730" y="148" text-anchor="middle" fill="#eef4ff" font-size="13.5">② 计算信号</text>
            <rect x="640" y="210" width="180" height="46" rx="10" fill="rgba(240,201,106,0.16)" stroke="#f0c96a" stroke-width="1.5"/>
            <text x="730" y="238" text-anchor="middle" fill="#eef4ff" font-size="13.5">③ 生成目标持仓</text>
            <rect x="360" y="270" width="180" height="46" rx="10" fill="rgba(240,201,106,0.16)" stroke="#f0c96a" stroke-width="1.5"/>
            <text x="450" y="298" text-anchor="middle" fill="#eef4ff" font-size="13.5">④ 模拟成交+扣成本</text>
            <rect x="80" y="210" width="180" height="46" rx="10" fill="rgba(122,167,240,0.16)" stroke="#7aa7f0" stroke-width="1.5"/>
            <text x="170" y="238" text-anchor="middle" fill="#eef4ff" font-size="13.5">⑤ 更新现金持仓</text>
            <rect x="80" y="120" width="180" height="46" rx="10" fill="rgba(122,167,240,0.16)" stroke="#7aa7f0" stroke-width="1.5"/>
            <text x="170" y="148" text-anchor="middle" fill="#eef4ff" font-size="13.5">⑥ 记录净值</text>
            <!-- 环形箭头 -->
            <g stroke="#8499bd" stroke-width="2" fill="none">
              <path d="M 540 84 C 610 92 630 105 660 118" marker-end="url(#bl)"/>
              <path d="M 730 166 L 730 208" marker-end="url(#bl)"/>
              <path d="M 640 240 C 600 258 570 262 542 268" marker-end="url(#bl)"/>
              <path d="M 360 296 C 300 300 265 285 250 258" marker-end="url(#bl)"/>
              <path d="M 170 210 L 170 168" marker-end="url(#bl)"/>
              <path d="M 240 118 C 270 100 300 92 358 85" marker-end="url(#bl)"/>
            </g>
            <text x="450" y="192" text-anchor="middle" fill="#f0c96a" font-size="13">下一天,重复</text>
            <defs><marker id="bl" markerWidth="9" markerHeight="9" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#8499bd"/></marker></defs>"""
    return concept_figure(body, "0 0 900 335",
        "回测循环示意:读取可见数据、算信号、生成持仓、模拟成交扣成本、更新持仓、记录净值,每天重复",
        "回测的本质就是这个每天重放的循环。每一步都可能藏坑:数据当时真可见吗?信号偷看未来了吗?成交价真实吗?成本扣了吗?循环里任何一环失真,收益就是假的。")


def _fig_overfitting():
    body = """            <text x="450" y="30" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">过拟合:样本内越漂亮,样本外可能越崩</text>
            <line x1="70" y1="250" x2="850" y2="250" stroke="#46587a" stroke-width="1.5"/>
            <line x1="70" y1="55" x2="70" y2="250" stroke="#46587a" stroke-width="1.5"/>
            <text x="52" y="65" fill="#8499bd" font-size="13">净值</text>
            <!-- 分界线:样本内/样本外 -->
            <line x1="470" y1="55" x2="470" y2="250" stroke="#f0c96a" stroke-width="1.5" stroke-dasharray="6 5"/>
            <text x="270" y="75" text-anchor="middle" fill="#8499bd" font-size="13">样本内(用来调参数)</text>
            <text x="660" y="75" text-anchor="middle" fill="#8499bd" font-size="13">样本外(没见过的新数据)</text>
            <!-- 过拟合线:样本内极好,样本外崩 -->
            <path d="M 90 240 Q 260 130 470 90" fill="none" stroke="#a8c6ff" stroke-width="3"/>
            <path d="M 470 90 Q 620 130 830 215" fill="none" stroke="#e88" stroke-width="3"/>
            <text x="250" y="120" fill="#a8c6ff" font-size="13">回测里美如画</text>
            <text x="660" y="200" fill="#ffb4b4" font-size="13" font-weight="800">实盘一上就崩</text>
            <text x="450" y="290" text-anchor="middle" fill="#c9d4e8" font-size="13">参数试得越多、模型越复杂,越容易\u201c背下\u201d历史噪声,而不是学到规律</text>"""
    return concept_figure(body, "0 0 900 305",
        "过拟合示意:样本内净值曲线极其漂亮,越过样本外分界线后急转直下",
        "过拟合是量化头号杀手:你在历史数据里反复调参,做出一条完美曲线,其实只是把当年的偶然噪声背了下来。换到没见过的新数据(样本外),立刻原形毕露。")


def _fig_loss_recovery():
    body = """            <text x="450" y="30" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">亏得越多,回本要涨得越狠(先活下来)</text>
            <line x1="110" y1="250" x2="850" y2="250" stroke="#46587a" stroke-width="1.5"/>
            <line x1="110" y1="55" x2="110" y2="250" stroke="#46587a" stroke-width="1.5"/>
            <text x="90" y="60" text-anchor="end" fill="#8499bd" font-size="12.5">回本涨幅</text>
            <text x="848" y="272" text-anchor="end" fill="#8499bd" font-size="13">亏损幅度</text>
            <!-- 柱子:亏损 vs 需要涨幅 -->
            <rect x="160" y="228" width="60" height="22" fill="rgba(122,167,240,0.5)"/><text x="190" y="222" text-anchor="middle" fill="#c9d4e8" font-size="12">亏10%→涨11%</text>
            <rect x="320" y="200" width="60" height="50" fill="rgba(240,201,106,0.5)"/><text x="350" y="194" text-anchor="middle" fill="#c9d4e8" font-size="12">亏30%→涨43%</text>
            <rect x="480" y="150" width="60" height="100" fill="rgba(240,150,90,0.6)"/><text x="510" y="144" text-anchor="middle" fill="#c9d4e8" font-size="12">亏50%→涨100%</text>
            <rect x="640" y="75" width="60" height="175" fill="rgba(232,120,120,0.6)"/><text x="670" y="69" text-anchor="middle" fill="#ffb4b4" font-size="12">亏80%→涨400%</text>
            <text x="450" y="290" text-anchor="middle" fill="#c9d4e8" font-size="13">亏损和回本不对称:亏 50% 要涨 100% 才回本,亏 80% 几乎回不来</text>"""
    return concept_figure(body, "0 0 900 305",
        "亏损回本非对称示意:亏损越大,回到本金需要的涨幅急剧变大",
        "这张图是\u201c活下来比赚快钱更重要\u201d的数学原因:亏 10% 涨 11% 就回本,但亏 50% 要涨整整 100%,亏 80% 得涨 400%。控制回撤,不是胆小,是保命。")


# 可见章号 -> [(锚点小节关键词, 图函数), ...]
# 概念图不再堆在章首,而是渲染在标题包含"锚点关键词"的那个小节正文之后,
# 让图紧挨着解释它的文字(和 deeplearning 一致)。
def _fig_b1_roadmap():
    body = """            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">七个学习阶段:每一级都有拿得出手的产出物</text>
            <!-- 7 级台阶,从左下到右上,宽 118,高 64+48i,底线 y=430 -->
            <rect x="36" y="366" width="118" height="64" rx="6" fill="rgba(122,167,240,0.09)" stroke="rgba(122,167,240,0.28)"/>
            <text x="95" y="388" text-anchor="middle" fill="#a8c6ff" font-size="14" font-weight="800">① 金融地图</text>
            <text x="95" y="408" text-anchor="middle" fill="#eef4f8" font-size="11">产出:行业全图笔记</text>
            <text x="95" y="426" text-anchor="middle" fill="#8499bd" font-size="11">讲清钱的流转</text>
            <rect x="156" y="318" width="118" height="112" rx="6" fill="rgba(122,167,240,0.12)" stroke="rgba(122,167,240,0.28)"/>
            <text x="215" y="340" text-anchor="middle" fill="#a8c6ff" font-size="14" font-weight="800">② 数据小仓</text>
            <text x="215" y="360" text-anchor="middle" fill="#eef4f8" font-size="11">产出:可复现行情库</text>
            <text x="215" y="378" text-anchor="middle" fill="#8499bd" font-size="11">重跑结果一致</text>
            <rect x="276" y="270" width="118" height="160" rx="6" fill="rgba(122,167,240,0.15)" stroke="rgba(122,167,240,0.28)"/>
            <text x="335" y="292" text-anchor="middle" fill="#a8c6ff" font-size="14" font-weight="800">③ 最小回测</text>
            <text x="335" y="312" text-anchor="middle" fill="#eef4f8" font-size="11">产出:能跑的框架</text>
            <text x="335" y="330" text-anchor="middle" fill="#8499bd" font-size="11">逐笔解释成本</text>
            <rect x="396" y="222" width="118" height="208" rx="6" fill="rgba(122,167,240,0.18)" stroke="rgba(122,167,240,0.28)"/>
            <text x="455" y="244" text-anchor="middle" fill="#a8c6ff" font-size="14" font-weight="800">④ 因子报告</text>
            <text x="455" y="264" text-anchor="middle" fill="#eef4f8" font-size="11">产出:IC/分层两表</text>
            <text x="455" y="282" text-anchor="middle" fill="#8499bd" font-size="11">敢说因子灵不灵</text>
            <rect x="516" y="174" width="118" height="256" rx="6" fill="rgba(122,167,240,0.21)" stroke="rgba(122,167,240,0.28)"/>
            <text x="575" y="196" text-anchor="middle" fill="#a8c6ff" font-size="14" font-weight="800">⑤ 多因子模型</text>
            <text x="575" y="216" text-anchor="middle" fill="#eef4f8" font-size="11">产出:组合化打分</text>
            <text x="575" y="234" text-anchor="middle" fill="#8499bd" font-size="11">权重都有理由</text>
            <rect x="636" y="126" width="118" height="304" rx="6" fill="rgba(122,167,240,0.24)" stroke="rgba(122,167,240,0.28)"/>
            <text x="695" y="148" text-anchor="middle" fill="#a8c6ff" font-size="14" font-weight="800">⑥ 模拟盘</text>
            <text x="695" y="168" text-anchor="middle" fill="#eef4f8" font-size="11">产出:一个月流水</text>
            <text x="695" y="186" text-anchor="middle" fill="#8499bd" font-size="11">每天对账不中断</text>
            <rect x="756" y="78" width="118" height="352" rx="6" fill="rgba(240,201,106,0.20)" stroke="rgba(240,201,106,0.42)"/>
            <text x="815" y="100" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">⑦ 小资金实盘</text>
            <text x="815" y="120" text-anchor="middle" fill="#eef4f8" font-size="11">产出:实盘差异笔记</text>
            <text x="815" y="138" text-anchor="middle" fill="#8499bd" font-size="11">差异都能找到因</text>
            <!-- 最后一级台阶上的小旗 -->
            <line x1="862" y1="78" x2="862" y2="36" stroke="#f0c96a" stroke-width="2.5"/>
            <path d="M 862 36 L 862 58 L 887 47 Z" fill="#f0c96a"/>
            <line x1="20" y1="430" x2="885" y2="430" stroke="#46587a" stroke-width="1.5"/>
            <text x="450" y="452" text-anchor="middle" fill="#c9d4e8" font-size="14">过关标准达不到就不上一级:先做出能跑的,再谈做大的</text>"""
    return concept_figure(body, "0 0 900 460",
        "七个学习阶段阶梯图:金融地图、数据小仓、最小回测、因子报告、多因子模型、模拟盘、小资金实盘,每级标注产出物和过关标准",
        "七个阶段像台阶一样,每一级都留下具体产出物:行业全图笔记、可复现行情库、能跑的回测框架、IC/分层两张表、组合化打分、一个月模拟盘流水、实盘与回测的差异笔记。过关标准达不到,就不上一级。")


def _fig_b1_neutral_ledger():
    body = """            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">市场中性组合的三本账:多头、空股指、保证金</text>
            <!-- 左:多头市值 -->
            <rect x="60" y="64" width="220" height="140" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>
            <text x="170" y="90" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">① 多头市值</text>
            <text x="170" y="116" text-anchor="middle" fill="#8499bd" font-size="12">一篮子股票的市值</text>
            <text x="170" y="144" text-anchor="middle" fill="#eef4f8" font-size="18" font-weight="800">100 万</text>
            <text x="170" y="168" text-anchor="middle" fill="#8499bd" font-size="12">赚的是选股 Alpha</text>
            <text x="170" y="190" text-anchor="middle" fill="#8499bd" font-size="12">市值每天随涨跌变</text>
            <!-- 中:空股指名义 -->
            <rect x="340" y="64" width="220" height="140" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(240,201,106,0.42)"/>
            <text x="450" y="90" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">② 空股指名义</text>
            <text x="450" y="116" text-anchor="middle" fill="#8499bd" font-size="12">对冲金额 = 市值 × Beta</text>
            <text x="450" y="144" text-anchor="middle" fill="#eef4f8" font-size="16" font-weight="800">100 万 × 1.2 = 120 万</text>
            <text x="450" y="168" text-anchor="middle" fill="#8499bd" font-size="12">把大盘的涨跌对冲掉</text>
            <text x="450" y="190" text-anchor="middle" fill="#8499bd" font-size="12">随多头市值每天重算</text>
            <!-- 右:保证金占用 -->
            <rect x="620" y="64" width="220" height="140" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>
            <text x="730" y="88" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">③ 保证金占用</text>
            <text x="730" y="110" text-anchor="middle" fill="#eef4f8" font-size="13" font-weight="800">120 万 × 12% = 14.4 万</text>
            <text x="648" y="138" text-anchor="end" fill="#8499bd" font-size="11">名义</text>
            <rect x="655" y="128" width="165" height="12" rx="3" fill="rgba(122,167,240,0.30)"/>
            <text x="648" y="160" text-anchor="end" fill="#8499bd" font-size="11">占用</text>
            <rect x="655" y="150" width="20" height="12" rx="3" fill="#f0c96a"/>
            <text x="648" y="182" text-anchor="end" fill="#8499bd" font-size="11">备用</text>
            <rect x="655" y="172" width="36" height="12" rx="3" fill="#8fb37a" opacity="0.6"/>
            <text x="730" y="199" text-anchor="middle" fill="#ffb4b4" font-size="11">指数涨 10% → 空仓多亏 12 万</text>
            <!-- 卡间连线 -->
            <line x1="280" y1="134" x2="336" y2="134" stroke="#7aa7f0" stroke-width="2.5" marker-end="url(#b1lg)"/>
            <text x="310" y="120" text-anchor="middle" fill="#c9d4e8" font-size="11">按 Beta 对冲</text>
            <line x1="560" y1="134" x2="616" y2="134" stroke="#f0c96a" stroke-width="2.5" marker-end="url(#b1lgg)"/>
            <text x="590" y="120" text-anchor="middle" fill="#c9d4e8" font-size="11">× 12% 占用</text>
            <defs>
              <marker id="b1lg" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#7aa7f0"/></marker>
              <marker id="b1lgg" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#f0c96a"/></marker>
            </defs>
            <text x="450" y="250" text-anchor="middle" fill="#eef4f8" font-size="14">三笔账每天对一遍,爆仓前它们会先说</text>"""
    return concept_figure(body, "0 0 900 285",
        "中性组合三本账:多头市值100万,按Beta1.2空股指名义120万,保证金占用120万乘12%等于14.4万,另留备用现金",
        "中性组合每天要对三本账:多头股票值多少钱、该空多少名义的股指(市值×Beta)、这些名义占用多少保证金(名义×12%)。占用只是名义的一小条,所以指数一涨空仓亏得很快——三笔账每天对一遍,爆仓前它们会先说。")


def _fig_b1_ten_layers():
    body = """            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">全书十层复盘:越往上,越依赖下层垫着</text>
            <!-- 十层金字塔,底层宽720,每层收60,层高32间距4,底 y=420 -->
            <rect x="360" y="64" width="180" height="32" rx="4" fill="rgba(122,167,240,0.08)" stroke="rgba(122,167,240,0.28)"/>
            <text x="450" y="85" text-anchor="middle" fill="#eef4f8" font-size="13" font-weight="800">L10 · 人和纪律</text>
            <rect x="330" y="100" width="240" height="32" rx="4" fill="rgba(122,167,240,0.10)" stroke="rgba(122,167,240,0.28)"/>
            <text x="450" y="121" text-anchor="middle" fill="#eef4f8" font-size="13" font-weight="800">L9 · 交易执行实盘</text>
            <rect x="300" y="136" width="300" height="32" rx="4" fill="rgba(122,167,240,0.12)" stroke="rgba(122,167,240,0.28)"/>
            <text x="450" y="157" text-anchor="middle" fill="#eef4f8" font-size="13" font-weight="800">L8 · 组合和风险</text>
            <rect x="270" y="172" width="360" height="32" rx="4" fill="rgba(122,167,240,0.14)" stroke="rgba(122,167,240,0.28)"/>
            <text x="450" y="193" text-anchor="middle" fill="#eef4f8" font-size="13" font-weight="800">L7 · 回测和验证</text>
            <rect x="240" y="208" width="420" height="32" rx="4" fill="rgba(122,167,240,0.16)" stroke="rgba(122,167,240,0.28)"/>
            <text x="450" y="229" text-anchor="middle" fill="#eef4f8" font-size="13" font-weight="800">L6 · 因子和模型</text>
            <rect x="210" y="244" width="480" height="32" rx="4" fill="rgba(122,167,240,0.18)" stroke="rgba(122,167,240,0.28)"/>
            <text x="450" y="265" text-anchor="middle" fill="#eef4f8" font-size="13" font-weight="800">L5 · 数据和可见性</text>
            <rect x="180" y="280" width="540" height="32" rx="4" fill="rgba(122,167,240,0.20)" stroke="rgba(122,167,240,0.28)"/>
            <text x="450" y="301" text-anchor="middle" fill="#eef4f8" font-size="13" font-weight="800">L4 · 市场与交易制度</text>
            <rect x="150" y="316" width="600" height="32" rx="4" fill="rgba(122,167,240,0.22)" stroke="rgba(122,167,240,0.28)"/>
            <text x="450" y="337" text-anchor="middle" fill="#eef4f8" font-size="13" font-weight="800">L3 · 权利和资产</text>
            <rect x="120" y="352" width="660" height="32" rx="4" fill="rgba(122,167,240,0.24)" stroke="rgba(122,167,240,0.28)"/>
            <text x="450" y="373" text-anchor="middle" fill="#eef4f8" font-size="13" font-weight="800">L2 · 信用和时间</text>
            <rect x="90" y="388" width="720" height="32" rx="4" fill="rgba(240,201,106,0.16)" stroke="rgba(240,201,106,0.42)"/>
            <text x="450" y="409" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">L1 · 真实财富和生产力(地基)</text>
            <!-- 右侧向上的依赖提示 -->
            <line x1="845" y1="412" x2="845" y2="80" stroke="#f0c96a" stroke-width="2" stroke-dasharray="6 5" marker-end="url(#b1ly)"/>
            <defs><marker id="b1ly" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#f0c96a"/></marker></defs>
            <text x="867" y="243" text-anchor="middle" transform="rotate(-90 867 243)" fill="#f0c96a" font-size="12.5" font-weight="800">越往上,越依赖下层垫着</text>
            <!-- 底部两条向内的支撑线,构成金字塔底 -->
            <line x1="90" y1="420" x2="450" y2="446" stroke="rgba(240,201,106,0.42)" stroke-width="2"/>
            <line x1="810" y1="420" x2="450" y2="446" stroke="rgba(240,201,106,0.42)" stroke-width="2"/>
            <circle cx="450" cy="446" r="4" fill="#f0c96a"/>"""
    return concept_figure(body, "0 0 900 460",
        "十层金字塔:自下而上依次是真实财富、信用时间、权利资产、市场制度、数据可见、因子模型、回测验证、组合风险、交易实盘、人纪律",
        "把全书压成十层:真实财富和生产力是地基,上面依次垫着信用、资产、市场制度、数据、因子、回测、组合、实盘,最上面是人和纪律。层越往上越窄——它能站住,全靠下面九层垫着;下层有问题,上层加倍还。")


def _fig_b1_portfolio():
    body = """            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">三个作品集:每个都打四个里程碑,打到头才算可展示</text>
            <!-- 作品集一 -->
            <text x="150" y="120" text-anchor="middle" fill="#eef4f8" font-size="15" font-weight="800">① 指数增强回测</text>
            <text x="150" y="140" text-anchor="middle" fill="#8499bd" font-size="11">对应小节 1.4</text>
            <rect x="270" y="111" width="540" height="10" rx="5" fill="rgba(122,167,240,0.14)"/>
            <circle cx="346" cy="116" r="5" fill="#7aa7f0"/><text x="346" y="98" text-anchor="middle" fill="#a8c6ff" font-size="12" font-weight="800">需求</text><text x="346" y="144" text-anchor="middle" fill="#8499bd" font-size="11">基准与目标写清</text>
            <circle cx="497" cy="116" r="5" fill="#7aa7f0"/><text x="497" y="98" text-anchor="middle" fill="#a8c6ff" font-size="12" font-weight="800">数据</text><text x="497" y="144" text-anchor="middle" fill="#8499bd" font-size="11">成分权重历史齐</text>
            <circle cx="648" cy="116" r="5" fill="#7aa7f0"/><text x="648" y="98" text-anchor="middle" fill="#a8c6ff" font-size="12" font-weight="800">验证</text><text x="648" y="144" text-anchor="middle" fill="#8499bd" font-size="11">跟踪误差算出来</text>
            <circle cx="767" cy="116" r="5" fill="#7aa7f0"/><text x="767" y="98" text-anchor="middle" fill="#a8c6ff" font-size="12" font-weight="800">交付</text><text x="767" y="144" text-anchor="middle" fill="#8499bd" font-size="11">可复现完整报告</text>
            <circle cx="832" cy="116" r="7" fill="#8fb37a"/><text x="832" y="98" text-anchor="middle" fill="#8fb37a" font-size="12" font-weight="800">可展示</text>
            <!-- 作品集二 -->
            <text x="150" y="200" text-anchor="middle" fill="#eef4f8" font-size="15" font-weight="800">② 数据质量与时点</text>
            <text x="150" y="220" text-anchor="middle" fill="#8499bd" font-size="11">对应小节 1.5</text>
            <rect x="270" y="191" width="540" height="10" rx="5" fill="rgba(122,167,240,0.14)"/>
            <circle cx="346" cy="196" r="5" fill="#7aa7f0"/><text x="346" y="178" text-anchor="middle" fill="#a8c6ff" font-size="12" font-weight="800">需求</text><text x="346" y="224" text-anchor="middle" fill="#8499bd" font-size="11">列出要修的脏数据</text>
            <circle cx="497" cy="196" r="5" fill="#7aa7f0"/><text x="497" y="178" text-anchor="middle" fill="#a8c6ff" font-size="12" font-weight="800">数据</text><text x="497" y="224" text-anchor="middle" fill="#8499bd" font-size="11">历史时点可还原</text>
            <circle cx="648" cy="196" r="5" fill="#7aa7f0"/><text x="648" y="178" text-anchor="middle" fill="#a8c6ff" font-size="12" font-weight="800">验证</text><text x="648" y="224" text-anchor="middle" fill="#8499bd" font-size="11">修复前后可比对</text>
            <circle cx="767" cy="196" r="5" fill="#7aa7f0"/><text x="767" y="178" text-anchor="middle" fill="#a8c6ff" font-size="12" font-weight="800">交付</text><text x="767" y="224" text-anchor="middle" fill="#8499bd" font-size="11">质检脚本进仓库</text>
            <circle cx="832" cy="196" r="7" fill="#8fb37a"/><text x="832" y="178" text-anchor="middle" fill="#8fb37a" font-size="12" font-weight="800">可展示</text>
            <!-- 作品集三 -->
            <text x="150" y="280" text-anchor="middle" fill="#eef4f8" font-size="15" font-weight="800">③ 模拟盘状态机</text>
            <text x="150" y="300" text-anchor="middle" fill="#8499bd" font-size="11">对应小节 1.6</text>
            <rect x="270" y="271" width="540" height="10" rx="5" fill="rgba(122,167,240,0.14)"/>
            <circle cx="346" cy="276" r="5" fill="#7aa7f0"/><text x="346" y="258" text-anchor="middle" fill="#a8c6ff" font-size="12" font-weight="800">需求</text><text x="346" y="304" text-anchor="middle" fill="#8499bd" font-size="11">状态机图先画全</text>
            <circle cx="497" cy="276" r="5" fill="#7aa7f0"/><text x="497" y="258" text-anchor="middle" fill="#a8c6ff" font-size="12" font-weight="800">数据</text><text x="497" y="304" text-anchor="middle" fill="#8499bd" font-size="11">逐笔委托都留痕</text>
            <circle cx="648" cy="276" r="5" fill="#7aa7f0"/><text x="648" y="258" text-anchor="middle" fill="#a8c6ff" font-size="12" font-weight="800">验证</text><text x="648" y="304" text-anchor="middle" fill="#8499bd" font-size="11">断线异常可恢复</text>
            <circle cx="767" cy="276" r="5" fill="#7aa7f0"/><text x="767" y="258" text-anchor="middle" fill="#a8c6ff" font-size="12" font-weight="800">交付</text><text x="767" y="304" text-anchor="middle" fill="#8499bd" font-size="11">连跑一个月不挂</text>
            <circle cx="832" cy="276" r="7" fill="#8fb37a"/><text x="832" y="258" text-anchor="middle" fill="#8fb37a" font-size="12" font-weight="800">可展示</text>
            <text x="450" y="338" text-anchor="middle" fill="#c9d4e8" font-size="13">三份作品集的共同标准:能跑、能讲、数据能复现</text>"""
    return concept_figure(body, "0 0 900 355",
        "三个作品集进度条:指数增强回测、数据质量与时点处理、模拟盘交易状态机,每件按需求、数据、验证、交付四个里程碑推进,末端为可展示",
        "作品集不是一条高收益曲线,而是四段可检查的里程碑:需求写清、数据齐备、验证通过、交付可复现。指数增强练流程,数据质量练点时还原,模拟盘状态机练工程稳定性——三件都打到绿点,简历才有得讲。")


def _fig_b1_glossary():
    body = """            <text x="450" y="30" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">二十个词速查:先用人话记住,再回去抠定义</text>
            <!-- 上卡:10 个金融词 -->
            <rect x="40" y="56" width="820" height="172" rx="14" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>
            <text x="450" y="84" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">金融词 · 先看懂市场在说什么</text>
            <rect x="57" y="100" width="148" height="50" rx="10" fill="rgba(122,167,240,0.08)" stroke="rgba(122,167,240,0.22)"/><text x="131" y="121" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">货币</text><text x="131" y="140" text-anchor="middle" fill="#bcc9dd" font-size="11">交换的通用筹码</text>
            <rect x="214" y="100" width="148" height="50" rx="10" fill="rgba(122,167,240,0.08)" stroke="rgba(122,167,240,0.22)"/><text x="288" y="121" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">信用</text><text x="288" y="140" text-anchor="middle" fill="#bcc9dd" font-size="11">先拿后还的凭证</text>
            <rect x="371" y="100" width="148" height="50" rx="10" fill="rgba(122,167,240,0.08)" stroke="rgba(122,167,240,0.22)"/><text x="445" y="121" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">利率</text><text x="445" y="140" text-anchor="middle" fill="#bcc9dd" font-size="11">钱的时间价格</text>
            <rect x="528" y="100" width="148" height="50" rx="10" fill="rgba(122,167,240,0.08)" stroke="rgba(122,167,240,0.22)"/><text x="602" y="121" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">通胀</text><text x="602" y="140" text-anchor="middle" fill="#bcc9dd" font-size="11">钱变薄了</text>
            <rect x="685" y="100" width="148" height="50" rx="10" fill="rgba(122,167,240,0.08)" stroke="rgba(122,167,240,0.22)"/><text x="759" y="121" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">股票</text><text x="759" y="140" text-anchor="middle" fill="#bcc9dd" font-size="11">公司的一小片</text>
            <rect x="57" y="160" width="148" height="50" rx="10" fill="rgba(122,167,240,0.08)" stroke="rgba(122,167,240,0.22)"/><text x="131" y="181" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">债券</text><text x="131" y="200" text-anchor="middle" fill="#bcc9dd" font-size="11">写进合同的借条</text>
            <rect x="214" y="160" width="148" height="50" rx="10" fill="rgba(122,167,240,0.08)" stroke="rgba(122,167,240,0.22)"/><text x="288" y="181" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">基金</text><text x="288" y="200" text-anchor="middle" fill="#bcc9dd" font-size="11">凑钱请人代投</text>
            <rect x="371" y="160" width="148" height="50" rx="10" fill="rgba(122,167,240,0.08)" stroke="rgba(122,167,240,0.22)"/><text x="445" y="181" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">ETF</text><text x="445" y="200" text-anchor="middle" fill="#bcc9dd" font-size="11">像股票买的篮子</text>
            <rect x="528" y="160" width="148" height="50" rx="10" fill="rgba(122,167,240,0.08)" stroke="rgba(122,167,240,0.22)"/><text x="602" y="181" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">期货</text><text x="602" y="200" text-anchor="middle" fill="#bcc9dd" font-size="11">锁住未来的价</text>
            <rect x="685" y="160" width="148" height="50" rx="10" fill="rgba(122,167,240,0.08)" stroke="rgba(122,167,240,0.22)"/><text x="759" y="181" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">期权</text><text x="759" y="200" text-anchor="middle" fill="#bcc9dd" font-size="11">一份选择的权利</text>
            <!-- 下卡:10 个量化词 -->
            <rect x="40" y="244" width="820" height="172" rx="14" fill="rgba(18,29,49,0.70)" stroke="rgba(240,201,106,0.42)"/>
            <text x="450" y="272" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">量化词 · 再看懂策略在说什么</text>
            <rect x="57" y="288" width="148" height="50" rx="10" fill="rgba(240,201,106,0.07)" stroke="rgba(240,201,106,0.30)"/><text x="131" y="309" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">Alpha</text><text x="131" y="328" text-anchor="middle" fill="#bcc9dd" font-size="11">跑赢市场的部分</text>
            <rect x="214" y="288" width="148" height="50" rx="10" fill="rgba(240,201,106,0.07)" stroke="rgba(240,201,106,0.30)"/><text x="288" y="309" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">Beta</text><text x="288" y="328" text-anchor="middle" fill="#bcc9dd" font-size="11">跟着大盘的部分</text>
            <rect x="371" y="288" width="148" height="50" rx="10" fill="rgba(240,201,106,0.07)" stroke="rgba(240,201,106,0.30)"/><text x="445" y="309" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">因子</text><text x="445" y="328" text-anchor="middle" fill="#bcc9dd" font-size="11">挑股票的依据</text>
            <rect x="528" y="288" width="148" height="50" rx="10" fill="rgba(240,201,106,0.07)" stroke="rgba(240,201,106,0.30)"/><text x="602" y="309" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">IC</text><text x="602" y="328" text-anchor="middle" fill="#bcc9dd" font-size="11">验因子灵不灵</text>
            <rect x="685" y="288" width="148" height="50" rx="10" fill="rgba(240,201,106,0.07)" stroke="rgba(240,201,106,0.30)"/><text x="759" y="309" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">回测</text><text x="759" y="328" text-anchor="middle" fill="#bcc9dd" font-size="11">用历史试跑策略</text>
            <rect x="57" y="348" width="148" height="50" rx="10" fill="rgba(240,201,106,0.07)" stroke="rgba(240,201,106,0.30)"/><text x="131" y="369" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">滑点</text><text x="131" y="388" text-anchor="middle" fill="#bcc9dd" font-size="11">预期价与成交的缝</text>
            <rect x="214" y="348" width="148" height="50" rx="10" fill="rgba(240,201,106,0.07)" stroke="rgba(240,201,106,0.30)"/><text x="288" y="369" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">容量</text><text x="288" y="388" text-anchor="middle" fill="#bcc9dd" font-size="11">最多装多少钱</text>
            <rect x="371" y="348" width="148" height="50" rx="10" fill="rgba(240,201,106,0.07)" stroke="rgba(240,201,106,0.30)"/><text x="445" y="369" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">跟踪误差</text><text x="445" y="388" text-anchor="middle" fill="#bcc9dd" font-size="11">偏离基准有多远</text>
            <rect x="528" y="348" width="148" height="50" rx="10" fill="rgba(240,201,106,0.07)" stroke="rgba(240,201,106,0.30)"/><text x="602" y="369" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">归因</text><text x="602" y="388" text-anchor="middle" fill="#bcc9dd" font-size="11">把盈亏拆出原因</text>
            <rect x="685" y="348" width="148" height="50" rx="10" fill="rgba(240,201,106,0.07)" stroke="rgba(240,201,106,0.30)"/><text x="759" y="369" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">风控</text><text x="759" y="388" text-anchor="middle" fill="#bcc9dd" font-size="11">先想好会怎么亏</text>
            <text x="450" y="440" text-anchor="middle" fill="#8499bd" font-size="12.5">先记住这 20 个,后面翻任何一章都用得上</text>"""
    return concept_figure(body, "0 0 900 455",
        "两组术语速查卡:上卡十个金融词,下卡十个量化词,每个词配一句人话注解",
        "二十个高频词,每个配一句人话:通胀是钱变薄了,滑点是预期价与成交价的缝,跟踪误差是偏离基准有多远。先用这些口语版本在脑子里占位,再去抠严格定义,术语就不再生疏。")


def _fig_b1_account_fields():
    body = """            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">总资产 ≠ 可花的钱:先分清三个口袋</text>
            <!-- 顶部:总资产 -->
            <rect x="360" y="58" width="180" height="58" rx="10" fill="rgba(240,201,106,0.14)" stroke="rgba(240,201,106,0.42)"/>
            <text x="450" y="82" text-anchor="middle" fill="#f0c96a" font-size="16" font-weight="800">总资产 93,000</text>
            <text x="450" y="104" text-anchor="middle" fill="#eef4f8" font-size="12.5">= 可用 25,000 + 持仓 68,000</text>
            <!-- 分叉线 -->
            <line x1="450" y1="116" x2="180" y2="164" stroke="#7aa7f0" stroke-width="1.5"/>
            <line x1="450" y1="116" x2="450" y2="164" stroke="#7aa7f0" stroke-width="1.5"/>
            <line x1="450" y1="116" x2="720" y2="164" stroke="#7aa7f0" stroke-width="1.5"/>
            <!-- 三个子框 -->
            <rect x="55" y="164" width="250" height="110" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>
            <text x="180" y="190" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">① 可用资金</text>
            <text x="180" y="214" text-anchor="middle" fill="#c9d4e8" font-size="12.5">能买股票用</text>
            <text x="180" y="240" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">例 25,000</text>
            <text x="180" y="262" text-anchor="middle" fill="#8499bd" font-size="11">含当天卖出回款:能买不能取</text>
            <rect x="325" y="164" width="250" height="110" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>
            <text x="450" y="190" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">② 可取资金</text>
            <text x="450" y="214" text-anchor="middle" fill="#c9d4e8" font-size="12.5">能转出银行卡</text>
            <text x="450" y="240" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">例 10,000</text>
            <text x="450" y="262" text-anchor="middle" fill="#8499bd" font-size="11">前一晚对账后的可用( ≤ 可用)</text>
            <rect x="595" y="164" width="250" height="110" rx="12" fill="rgba(232,120,120,0.08)" stroke="#e88"/>
            <text x="720" y="190" text-anchor="middle" fill="#ffb4b4" font-size="15" font-weight="800">③ 持仓市值</text>
            <text x="720" y="214" text-anchor="middle" fill="#c9d4e8" font-size="12.5">还没变成钱</text>
            <text x="720" y="240" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">例 68,000</text>
            <text x="720" y="262" text-anchor="middle" fill="#8499bd" font-size="11">浮盈要等卖成现金才算数</text>
            <!-- 流转箭头 1:可用 → 可取(两框间隙,标注 T+1) -->
            <line x1="305" y1="219" x2="321" y2="219" stroke="#7aa7f0" stroke-width="2.5" marker-end="url(#b1at)"/>
            <text x="313" y="206" text-anchor="middle" fill="#8499bd" font-size="11">T+1</text>
            <!-- 流转箭头 2:持仓 → 可用(底部大弧线) -->
            <path d="M 720 276 C 690 348, 230 348, 200 280" fill="none" stroke="#a8c6ff" stroke-width="2.5" marker-end="url(#b1af)"/>
            <text x="450" y="352" text-anchor="middle" fill="#a8c6ff" font-size="12.5">卖出成交:可用 +10,000,当天这笔钱不可取</text>
            <defs>
              <marker id="b1at" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#7aa7f0"/></marker>
              <marker id="b1af" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#a8c6ff"/></marker>
            </defs>
            <text x="450" y="404" text-anchor="middle" fill="#ffb4b4" font-size="14">持仓市值不是钱——涨了的浮盈,先要能卖成现金;当天卖出的钱,T+1 才能取</text>"""
    return concept_figure(body, "0 0 900 425",
        "开户软件资产字段分解:总资产拆成可用资金、可取资金和持仓市值,卖出成交先进可用,隔日对账后才进可取",
        "总资产 93,000 里,能买股票的是可用 25,000,能转出银行卡的只有可取 10,000,剩下的 68,000 是还没变成钱的持仓市值。卖出成交先进可用,当晚对账后(T+1)才进可取——浮盈再多,先要能卖成现金。")
















def _fig_b2_week():
    """第 27 章:模拟盘一周时间线,周一~周五每天一个事故卡,周末写复盘。"""
    # (x, 日标签, 事故标题, 应对动作, 是否周末卡)
    cards = [
        (15, "周一", "数据没按时到", "停机告警·记日志", False),
        (163, "周二", "信号文件为空", "不交易·查日志", False),
        (312, "周三", "涨停买不到", "涨停不买·记偏离", False),
        (460, "周四", "成本比预期高", "分组查滑点·再改", False),
        (609, "周五", "盘后对账", "对账到0.01元再下班", False),
        (757, "周末", "写复盘", "病历·药方都留档", True),
    ]
    parts = []
    parts.append('            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">模拟盘第一周:五个事故,一次复盘</text>')
    parts.append('            <defs><marker id="wk" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#8499bd"/></marker></defs>')
    for x, day, title, act, weekend in cards:
        cx = x + 64
        stroke = "rgba(240,201,106,0.42)" if weekend else "rgba(232,136,136,0.35)"
        fill = "rgba(240,201,106,0.08)" if weekend else "rgba(18,29,49,0.70)"
        dayc = "#f0c96a" if weekend else "#ffb4b4"
        parts.append('            <rect x="%d" y="64" width="128" height="172" rx="12" fill="%s" stroke="%s"/>' % (x, fill, stroke))
        parts.append('            <text x="%d" y="96" text-anchor="middle" fill="%s" font-size="15" font-weight="800">%s</text>' % (cx, dayc, day))
        parts.append('            ' + svg_text(title, cx, 122, 116, size=14, color="#eef4f8", max_chars=7, max_lines=2))
        parts.append('            <line x1="%d" y1="142" x2="%d" y2="142" stroke="rgba(122,167,240,0.18)"/>' % (x + 16, x + 112))
        parts.append('            <text x="%d" y="164" text-anchor="middle" fill="#8499bd" font-size="11.5">%s</text>' % (cx, "收尾" if weekend else "应对动作"))
        parts.append('            ' + svg_text(act, cx, 194, 116, size=12.5, color="#bcc9dd", weight=600, max_chars=8, max_lines=2))
    for i in range(5):
        ax = cards[i][0] + 131
        bx = cards[i + 1][0] - 3
        parts.append('            <path d="M %d 118 L %d 118" stroke="#8499bd" stroke-width="2" fill="none" marker-end="url(#wk)"/>' % (ax, bx))
    parts.append('            <text x="450" y="258" text-anchor="middle" fill="#8499bd" font-size="12.5">本周末的事故清单:数据延迟 ×1 · 空信号 ×1 · 涨停未成交 ×1 · 滑点持续偏高 · 账实错位 ×1</text>')
    parts.append('            <text x="450" y="282" text-anchor="middle" fill="#c9d4e8" font-size="13.5">一周只证明流程通了,证明不了策略有效 —— 模拟盘至少再跑几个月,才谈实盘</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 300",
        "模拟盘一周时间线:周一数据没到、周二信号为空、周三涨停买不到、周四成本超标、周五盘后对账,周末写复盘",
        "模拟盘第一周把回测里不会发生的事演了个遍:数据迟到、空信号、涨停买不进、滑点超标、账实错位。每条事故都要落成一条事先写好的处理规则,周末复盘把病历和药方一起留档——但一周只证明流程通了,证明不了策略有效。")


def _fig_b2_guards():
    """第 28 章:小实盘的三层护栏,从最外圈一路走到实盘。"""
    body = """            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">小实盘的三层护栏:从最外圈走到实盘</text>
            <defs><marker id="gd" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#f0c96a"/></marker></defs>
            <!-- 人:从外往里走 -->
            <circle cx="64" cy="150" r="8" fill="none" stroke="#a8c6ff" stroke-width="2.5"/>
            <path d="M 64 158 L 64 186" stroke="#a8c6ff" stroke-width="2.5" fill="none"/>
            <path d="M 64 166 L 50 180 M 64 166 L 78 180" stroke="#a8c6ff" stroke-width="2.5" fill="none"/>
            <path d="M 64 186 L 52 206 M 64 186 L 76 206" stroke="#a8c6ff" stroke-width="2.5" fill="none"/>
            <text x="64" y="228" text-anchor="middle" fill="#8499bd" font-size="12">从外往里走</text>
            <!-- 第 1 层:资金上限(金) -->
            <rect x="155" y="84" width="170" height="198" rx="18" fill="rgba(240,201,106,0.07)" stroke="rgba(240,201,106,0.42)" stroke-width="1.8"/>
            <circle cx="183" cy="84" r="14" fill="#101d33" stroke="rgba(240,201,106,0.6)" stroke-width="1.5"/>
            <text x="183" y="89" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">1</text>
            <text x="240" y="116" text-anchor="middle" fill="#f0c96a" font-size="16" font-weight="800">资金上限</text>
            <text x="240" y="148" text-anchor="middle" fill="#8499bd" font-size="12">标准只有一条:</text>
            <text x="240" y="172" text-anchor="middle" fill="#eef4f8" font-size="13">全部亏光,也不心疼</text>
            <text x="240" y="196" text-anchor="middle" fill="#eef4f8" font-size="13">不影响吃饭和房租</text>
            <text x="240" y="222" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">示例上限:1 万元</text>
            <rect x="200" y="244" width="80" height="26" rx="13" fill="none" stroke="#f0c96a"/>
            <text x="240" y="262" text-anchor="middle" fill="#f0c96a" font-size="12" font-weight="800">硬约束</text>
            <!-- 第 2 层:停止规则(红) -->
            <rect x="395" y="84" width="170" height="198" rx="18" fill="rgba(232,120,120,0.07)" stroke="rgba(232,136,136,0.42)" stroke-width="1.8"/>
            <circle cx="423" cy="84" r="14" fill="#101d33" stroke="rgba(232,136,136,0.6)" stroke-width="1.5"/>
            <text x="423" y="89" text-anchor="middle" fill="#ffb4b4" font-size="14" font-weight="800">2</text>
            <text x="480" y="116" text-anchor="middle" fill="#ffb4b4" font-size="16" font-weight="800">停止规则</text>
            <text x="480" y="148" text-anchor="middle" fill="#8499bd" font-size="12">入场前写死触发线:</text>
            <text x="480" y="172" text-anchor="middle" fill="#eef4f8" font-size="13">浮亏 10% → 强制停</text>
            <text x="480" y="196" text-anchor="middle" fill="#eef4f8" font-size="13">对不上账连两周 → 停</text>
            <text x="480" y="220" text-anchor="middle" fill="#eef4f8" font-size="13">行为变形说不清 → 停</text>
            <rect x="440" y="244" width="80" height="26" rx="13" fill="none" stroke="#f0c96a"/>
            <text x="480" y="262" text-anchor="middle" fill="#f0c96a" font-size="12" font-weight="800">硬约束</text>
            <!-- 第 3 层:记录纪律(蓝) -->
            <rect x="635" y="84" width="170" height="198" rx="18" fill="rgba(122,167,240,0.08)" stroke="rgba(122,167,240,0.30)" stroke-width="1.8"/>
            <circle cx="663" cy="84" r="14" fill="#101d33" stroke="rgba(122,167,240,0.55)" stroke-width="1.5"/>
            <text x="663" y="89" text-anchor="middle" fill="#a8c6ff" font-size="14" font-weight="800">3</text>
            <text x="720" y="116" text-anchor="middle" fill="#a8c6ff" font-size="16" font-weight="800">记录纪律</text>
            <text x="720" y="148" text-anchor="middle" fill="#8499bd" font-size="12">一笔一笔写成表:</text>
            <text x="720" y="172" text-anchor="middle" fill="#eef4f8" font-size="13">委托价 · 成交价 · 滑点</text>
            <text x="720" y="196" text-anchor="middle" fill="#eef4f8" font-size="13">费用 · 未成交原因</text>
            <text x="720" y="220" text-anchor="middle" fill="#eef4f8" font-size="13">当时的心理状态</text>
            <text x="720" y="248" text-anchor="middle" fill="#8499bd" font-size="11.5">盈亏不会说话,记录会</text>
            <!-- 向左向右的推进箭头 -->
            <path d="M 84 184 L 151 184" stroke="#a8c6ff" stroke-width="2" fill="none" marker-end="url(#gd)"/>
            <path d="M 329 184 L 391 184" stroke="#8499bd" stroke-width="2" fill="none" marker-end="url(#gd)"/>
            <path d="M 569 184 L 631 184" stroke="#8499bd" stroke-width="2" fill="none" marker-end="url(#gd)"/>
            <path d="M 809 184 L 850 184" stroke="#f0c96a" stroke-width="2.5" fill="none" marker-end="url(#gd)"/>
            <text x="868" y="189" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">实盘</text>"""
    body += "\n" + '            <text x="450" y="316" text-anchor="middle" fill="#c9d4e8" font-size="13.5">三层护栏入金前写死:钱有上限 · 碰到线就停 · 每笔都留痕 —— 触发停止不是失败,是护栏在工作</text>'
    return concept_figure(body, "0 0 900 336",
        "小实盘三层护栏:第1层资金上限(亏光也不影响生活的钱,示例1万)、第2层停止规则(浮亏10%强制停、连续对不上账停)、第3层记录纪律(每笔委托价成交价滑点心理状态留痕)",
        "第一次小实盘的三层护栏都写在入金之前:钱的上限是「全亏光也不影响生活」的学费;停止线碰到就停,停不是失败;每一笔委托价、成交价、滑点和当时心理状态都留痕——盈亏这个数字最不会说话,记录才会。")


def _fig_b2_checklist():
    """第 29 章:金融直觉 8 件事 vs 量化纪律 10 件事,两列对照,门后才是代码。"""
    left = [
        ("钱和财富的区别", "票子 ≠ 产出"),
        ("银行有用又脆弱", "挤兑是信心病"),
        ("区分股票和债券", "股东排债主后"),
        ("基金和 ETF 结构", "一篮子打包卖"),
        ("A 股交易规则", "T+1 与涨跌停"),
        ("收益和风险指标", "回撤 · 夏普口径"),
        ("有效市场与行为偏差", "便宜不会白捡"),
        ("自己的资金边界", "亏光也不心疼"),
    ]
    right = [
        ("数据必须可追溯", "来路留得住"),
        ("时间线必须正确", "按公告日对齐"),
        ("股票池必须点时", "成分随日期变"),
        ("交易规则进回测", "涨停撮合不掉"),
        ("成本做敏感性", "佣金·滑点·冲击"),
        ("因子有单独报告", "不过堂不合成"),
        ("模型必须有基线", "先赢过等权持有"),
        ("组合必须有约束", "单票·行业上限"),
        ("报告必须能复现", "同配置同结果"),
        ("模拟盘先于实盘", "免费犯错阶段"),
    ]
    parts = []
    parts.append('            <text x="450" y="30" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">动手写代码前,先过完这 18 道关</text>')
    parts.append('            <defs><marker id="ky" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#f0c96a"/></marker></defs>')
    parts.append('            <text x="201" y="60" text-anchor="middle" fill="#a8c6ff" font-size="16" font-weight="800">金融直觉 · 8 件事</text>')
    parts.append('            <text x="706" y="60" text-anchor="middle" fill="#f0c96a" font-size="16" font-weight="800">量化纪律 · 10 件事</text>')
    for i, (t, a) in enumerate(left):
        y = 78 + i * 44
        cy = y + 20
        parts.append('            <rect x="28" y="%d" width="346" height="40" rx="10" fill="rgba(18,29,49,0.55)" stroke="rgba(122,167,240,0.22)"/>' % y)
        parts.append('            <circle cx="46" cy="%d" r="4.5" fill="#7aa7f0"/>' % cy)
        parts.append('            <text x="60" y="%d" fill="#eef4f8" font-size="13.5" font-weight="700">%s  <tspan fill="#8499bd" font-size="11.5" font-weight="400">%s</tspan></text>' % (cy + 5, t, a))
    for i, (t, a) in enumerate(right):
        y = 76 + i * 36
        cy = y + 16
        parts.append('            <rect x="540" y="%d" width="332" height="32" rx="9" fill="rgba(18,29,49,0.55)" stroke="rgba(240,201,106,0.25)"/>' % y)
        parts.append('            <circle cx="558" cy="%d" r="4.5" fill="#f0c96a"/>' % cy)
        parts.append('            <text x="572" y="%d" fill="#eef4f8" font-size="13" font-weight="700">%s  <tspan fill="#8499bd" font-size="11.5" font-weight="400">%s</tspan></text>' % (cy + 4, t, a))
    parts.append('            <!-- 中间的门:两边是钥匙,门后才是代码 -->')
    parts.append('            <path d="M 418 300 L 418 216 A 32 34 0 0 1 482 216 L 482 300 Z" fill="rgba(240,201,106,0.08)" stroke="rgba(240,201,106,0.55)" stroke-width="2"/>')
    parts.append('            <circle cx="450" cy="250" r="7" fill="#f0c96a"/>')
    parts.append('            <rect x="447" y="255" width="6" height="22" rx="2" fill="#f0c96a"/>')
    parts.append('            <path d="M 384 254 L 412 254" stroke="#f0c96a" stroke-width="2" fill="none" marker-end="url(#ky)"/>')
    parts.append('            <path d="M 530 254 L 488 254" stroke="#f0c96a" stroke-width="2" fill="none" marker-end="url(#ky)"/>')
    parts.append('            <text x="450" y="196" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">两列就是两把钥匙</text>')
    parts.append('            <text x="450" y="326" text-anchor="middle" fill="#f0c96a" font-size="13.5" font-weight="800">8 + 10 = 18 关,一关不能跳</text>')
    parts.append('            <text x="450" y="470" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">门后才是代码:左边看懂世界,右边管住自己</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 492",
        "两列对照表:左列金融直觉8件事(钱和财富、银行脆弱、股票债券、基金ETF、A股规则、收益风险、有效市场、资金边界),右列量化纪律10件事(数据、时间线、股票池、交易规则、成本、因子、基线、约束、复现、模拟盘),中间一扇门",
        "动手写代码之前要真正过的 18 道关:左边 8 件是看懂金融世界的直觉,右边 10 件是量化工程的纪律,对应本书前面每一章的地基。两列合在一起是钥匙,门打开之后,才轮得到代码上场。")


def _fig_b2_failure():
    """第 30 章:程序员七步翻车(红)与正确姿势(金)逐步对照。"""
    # (左主句, 左细节, 右主句, 右细节)
    rows = [
        ("先找模型,后找问题", "拿 60 天价格,预测未来 5 天", "先定义问题,再选模型", "股票池 · 频率 · 成本先写死"),
        ("忽略时间线", "1 月就用上 3 月公布的年报", "先画时间线,再写代码", "每个字段按公告日对齐"),
        ("低估交易成本", "只扣了个拍脑袋的低佣金", "成本敏感性拉满 0~3 倍", "佣金 · 印花税 · 滑点逐项扣"),
        ("相信最佳参数", "试一百次,留下样本内第一", "看最差情况,不看最优", "样本外普普通通才算数"),
        ("小赚后马上加仓", "两周翻红,资金放大 5 倍", "加仓前先有停止线", "每放大一档,重验一遍"),
        ("没有停止规则", "继续怕亏,停了怕反弹", "先定「什么时候不买」", "回撤超 95% 分位就降仓"),
        ("最后才复盘", "亏了才想起打印记录", "每次亏损都留日志收尾", "错误清单 6 条,逐条认账"),
    ]
    parts = []
    parts.append('            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">一个程序员的七步翻车,逐条翻正</text>')
    parts.append('            <defs><marker id="fl" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#f0c96a"/></marker></defs>')
    parts.append('            <text x="200" y="70" text-anchor="middle" fill="#ffb4b4" font-size="15" font-weight="800">翻车七步</text>')
    parts.append('            <text x="450" y="70" text-anchor="middle" fill="#8499bd" font-size="12">→ 逐条翻正 →</text>')
    parts.append('            <text x="700" y="70" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">正确姿势</text>')
    for i, (lm, ls, rm, rs) in enumerate(rows):
        y = 80 + i * 52
        cy = y + 23
        parts.append('            <rect x="36" y="%d" width="330" height="46" rx="10" fill="rgba(232,120,120,0.10)" stroke="rgba(232,136,136,0.35)"/>' % y)
        parts.append('            <circle cx="58" cy="%d" r="11" fill="rgba(232,120,120,0.25)"/>' % cy)
        parts.append('            <text x="58" y="%d" text-anchor="middle" fill="#ffb4b4" font-size="12.5" font-weight="800">%d</text>' % (cy + 4, i + 1))
        parts.append('            <text x="76" y="%d" fill="#ffb4b4" font-size="13" font-weight="800">%s</text>' % (cy - 4, lm))
        parts.append('            <text x="76" y="%d" fill="#bcc9dd" font-size="11.5">%s</text>' % (cy + 16, ls))
        parts.append('            <path d="M 372 %d C 415 %d 485 %d 528 %d" stroke="#f0c96a" stroke-width="2" fill="none" marker-end="url(#fl)"/>' % (cy, cy - 16, cy - 16, cy))
        parts.append('            <rect x="534" y="%d" width="330" height="46" rx="10" fill="rgba(240,201,106,0.10)" stroke="rgba(240,201,106,0.42)"/>' % y)
        parts.append('            <text x="556" y="%d" fill="#f0c96a" font-size="13" font-weight="800">%s</text>' % (cy - 4, rm))
        parts.append('            <text x="556" y="%d" fill="#bcc9dd" font-size="11.5">%s</text>' % (cy + 16, rs))
    parts.append('            <text x="450" y="456" text-anchor="middle" fill="#c9d4e8" font-size="13">他的补救是:列 6 条错误清单,然后按和第一次完全相反的顺序,重做整个项目</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 470",
        "七步翻车与修正对照:先找模型后找问题、忽略时间线、低估成本、相信最佳参数、小赚加仓、没停止规则、最后才复盘;右侧逐条给出正确姿势",
        "每一步翻车,回测曲线都很好看:60 天价格预测未来 5 天收益、1 月就用上 3 月才公布的年报、只扣拍脑袋的低佣金、试一百次留下样本内第一、两周翻红后资金放大 5 倍……直到亏完才复盘。每一步的正确顺序,都写在右边那列。")


def _fig_b2_pipeline():
    """第 31 章:八步稳妥项目流水线,每步带推进/停止判据,小赚后回到第 5 步。"""
    # (步名, 判据, 判据是否停止线)
    nodes = [
        ("问题很小", "说不清问题 → 停", True),
        ("先查数据", "数据对不上 → 停", True),
        ("最简单基线", "先赢过等权基线", False),
        ("单因子报告", "单因子单独打分", False),
        ("多因子组合", "等权合成 + 约束", False),
        ("样本外模拟盘", "样本外普通而不崩", False),
        ("小资金半自动", "亏光也扛得住的钱", False),
        ("复盘判断", "先加仪表,再加钱", False),
    ]
    parts = []
    parts.append('            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">稳妥项目的八步流水线:每步都带闸门</text>')
    parts.append('            <defs><marker id="pl" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#8499bd"/></marker><marker id="plg" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#f0c96a"/></marker></defs>')
    for i, (name, crit, is_stop) in enumerate(nodes):
        cx = 62 + i * 110
        parts.append('            <rect x="%d" y="66" width="96" height="84" rx="10" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.30)"/>' % (cx - 48))
        parts.append('            <circle cx="%d" cy="66" r="11" fill="rgba(122,167,240,0.25)"/>' % (cx - 34))
        parts.append('            <text x="%d" y="70" text-anchor="middle" fill="#a8c6ff" font-size="12" font-weight="800">%d</text>' % (cx - 34, i + 1))
        parts.append('            ' + svg_text(name, cx, 108, 90, size=13, color="#eef4f8", weight=800, max_chars=6, max_lines=1))
        parts.append('            ' + svg_text(crit, cx, 172, 98, size=11, color=("#ffb4b4" if is_stop else "#bcc9dd"), weight=600, max_chars=8, max_lines=1))
        if i < 7:
            parts.append('            <path d="M %d 108 L %d 108" stroke="#8499bd" stroke-width="2" fill="none" marker-end="url(#pl)"/>' % (cx + 49, cx + 61))
    # 分叉:从第 7 步小赚后回到第 5 步重验,不直接放大
    parts.append('            <path d="M 722 152 L 722 198 L 502 198 L 502 158" stroke="#f0c96a" stroke-width="2" stroke-dasharray="6 5" fill="none" marker-end="url(#plg)"/>')
    parts.append('            <text x="612" y="220" text-anchor="middle" fill="#f0c96a" font-size="12">小赚后想放大 → 回到第 5 步重验,别直接放大资金</text>')
    # 主线末端的小旗
    parts.append('            <line x1="832" y1="66" x2="832" y2="36" stroke="#f0c96a" stroke-width="2"/>')
    parts.append('            <path d="M 832 36 L 860 43 L 832 50 Z" fill="#f0c96a"/>')
    parts.append('            <text x="450" y="268" text-anchor="middle" fill="#c9d4e8" font-size="13">顺序不许跳:每一步先过了自己的判据,才迈下一步</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 300",
        "八步稳妥项目流水线:问题很小、先查数据、最简单基线、单因子报告、多因子组合、样本外模拟盘、小资金半自动、复盘判断;每步带停止或推进判据,小赚后回到第5步重验",
        "一个稳妥的个人量化项目按八步长大:问题先要小到一句话说清,数据先体检再谈策略,基线先立住、因子单独过堂、组合先等权;样本外「普通而不崩」才上模拟盘,小资金半自动跑顺之后,依然先加仪表再谈放大资金。")


def _fig_b2_questions():
    """第 32 章:六问检查牌,六张等高卡上下堆叠,六关都过才准开始。"""
    cards = [
        ("问题足够小?", "一句话说清:哪个池子 · 哪个因子 · 哪个频率"),
        ("最坏情况知道?", "先想「全亏光那天」长什么样,再谈收益"),
        ("当时可见?", "从下单到成交,不能让代码看到未来"),
        ("成本算过?", "佣金 · 印花税 · 滑点 · 冲击:先算成本再看收益"),
        ("能随时停止?", "停止线开工前写死:数据坏停 · 对不上账停"),
        ("能复盘写三行?", "数据版本 · 参数 · 成交记录,环环说清"),
    ]
    parts = []
    parts.append('            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">研究动手前,先刷六道闸</text>')
    parts.append('            <line x1="118" y1="86" x2="118" y2="396" stroke="rgba(240,201,106,0.35)" stroke-width="2"/>')
    for i, (q, k) in enumerate(cards):
        y = 58 + i * 62
        cy = y + 28
        parts.append('            <rect x="78" y="%d" width="754" height="56" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>' % y)
        parts.append('            <circle cx="118" cy="%d" r="16" fill="#f0c96a"/>' % cy)
        parts.append('            <text x="118" y="%d" text-anchor="middle" fill="#101420" font-size="17" font-weight="900">?</text>' % (cy + 6))
        parts.append('            <text x="150" y="%d" fill="#eef4f8" font-size="15.5" font-weight="800">%s</text>' % (cy - 3, q))
        parts.append('            <text x="150" y="%d" fill="#bcc9dd" font-size="12.5">%s</text>' % (cy + 19, k))
        parts.append('            <text x="812" y="%d" text-anchor="end" fill="#8499bd" font-size="12">第 %d 闸</text>' % (cy + 4, i + 1))
    parts.append('            <text x="450" y="452" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">六关都过,才准开始</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 470",
        "六问检查牌:问题足够小、最坏情况知道、当时可见、成本算过、能随时停止、能复盘写三行;六关都过才准开始",
        "每次研究、交易、回测、实盘之前,先把这六张牌从上到下刷一遍:问题要小到一句话说清,先想最坏那一天,每个字段按当时可见性对齐,先算成本再看收益,停止线提前写死,资料留到能复盘——六关都过,才准开始。")


CONCEPT_FIGURES_FREE = {
    12: [("第一阶段", _fig_b1_roadmap)],
    20: [("保证金和现金", _fig_b1_neutral_ledger)],
    23: [("真实财富和生产力", _fig_b1_ten_layers)],
    24: [("指数增强回测", _fig_b1_portfolio)],
    25: [("货币", _fig_b1_glossary)],
    26: [("总资产不是可花的钱", _fig_b1_account_fields)],
    27: [("数据没有按时到", _fig_b2_week)],
    28: [("先定资金上限", _fig_b2_guards)],
    29: [("能解释钱和财富的区别", _fig_b2_checklist)],
    30: [("他先找模型", _fig_b2_failure)],
    31: [("问题很小", _fig_b2_pipeline)],
    32: [("问题是否足够小", _fig_b2_questions)],
}



# ============ 信息型概念图 批次 C/D ============
# -*- coding: utf-8 -*-
"""概念图 batch C(ch05-ch09 新增,合计 7 张)。

交付约定(与 build_book.py 现有 _fig_xxx 函数一致):
- 纯字符串拼接,不含 f-string;body 用 % 或字符串加号组拼。
- 每张图通过 concept_figure(body, "0 0 900 高", aria, cap) 收尾,
  内部混用 svg_text(...) 与手写 <text>。
- 调色板与全书一致,禁用暖米色底。

锚点关键词:全部是「渲染后小节标题」的子串,且已逐一 grep 验证唯一命中。
注意 build_book.attach_figures 匹配的是不带 x.y. 编号前缀的原始小节标题,
故关键词一律取标题文字本身(如「为什么期货会放大盈亏」),它同样是渲染后
「1.3. 为什么期货会放大盈亏」的子串;纯「1.3」这类编号关键词在该机制下
反而匹配不上,故不采用。

grep 验证(chapter-NN.html 内 `<h3>` 行):
  ch05 "为什么期货会放大盈亏"      -> chapter-05.html:37  <h3>1.3. 为什么期货会放大盈亏</h3>
  ch05 "买方亏损有限"              -> chapter-05.html:87  <h3>2.3. 买方亏损有限,卖方风险更复杂</h3>
  ch06 "券商是通道"                -> chapter-06.html:33  <h3>1.2. 券商是通道,不是交易所</h3>
  ch07 "影线只是压缩图"            -> chapter-07.html:61  <h3>1.3. K 线实体和影线只是压缩图</h3>
  ch08 "这条路颠不颠"              -> chapter-08.html:40  <h3>1.4. 这条路颠不颠</h3>
  ch08 "每承担一份波动赚多少超额收益" -> chapter-08.html:67 <h3>1.6. 每承担一份波动赚多少超额收益</h3>
  ch09 "高分组是不是真的更好"      -> chapter-09.html:72  <h3>1.6. 高分组是不是真的更好</h3>
已有占用锚点(不能重复占用): ch05 "看涨期权和看跌期权"、ch06 "价格优先和时间优先"、
ch07 "一天被压成四个价格"、ch08 "从高点跌到低点有多痛"、ch09 "常见因子家族"。
"""


def _fig_c5_margin_timeline():
    """ch05 期货逐日盯市时间线。锚点:chapter-05.html:37 <h3>1.3. 为什么期货会放大盈亏</h3>。
    数字沿用该节正文:100 万名义合约、10% 保证金、标的每天跌 1% 划走 1 万、维持线 8 万。"""
    cards = [
        (150, "开仓日", "#7aa7f0",
         ["缴保证金 10 万", "控制名义 100 万", "当日余额 10 万"],
         "rgba(122,167,240,0.28)"),
        (360, "第 1 天收盘", "#a8c6ff",
         ["结算价 -1%", "当日划走 1 万", "余额 9 万"],
         "rgba(122,167,240,0.28)"),
        (570, "第 2 天收盘", "#ffb4b4",
         ["再跌 -1%", "又划走 1 万", "余额 8 万", "触到维持线 8 万"],
         "rgba(232,120,120,0.45)"),
        (780, "第 3 天开盘前", "#f0c96a",
         ["追加保证金电话", "补足 10 万 → 留下", "拿不出 → 强平清仓"],
         "rgba(240,201,106,0.42)"),
    ]
    parts = []
    parts.append('            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">期货逐日盯市:10 万保证金,两天亏到维持线</text>')
    parts.append('            <text x="450" y="58" text-anchor="middle" fill="#8499bd" font-size="12.5">名义 100 万合约 · 保证金比例 10% → 缴 10 万;标的每跌 1%,合约当天就亏 1 万</text>')
    parts.append('            <defs><marker id="c5m" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#8499bd"/></marker></defs>')
    for i, (cx, head, hcolor, lines, stroke) in enumerate(cards):
        parts.append('            <rect x="%d" y="76" width="180" height="150" rx="12" fill="rgba(18,29,49,0.70)" stroke="%s"/>' % (cx - 90, stroke))
        parts.append('            ' + svg_text(head, cx, 101, 168, size=14, color=hcolor, weight=800, max_chars=10, max_lines=1))
        for li, ln in enumerate(lines):
            parts.append('            <text x="%d" y="%d" text-anchor="middle" fill="#c9d4e8" font-size="12">%s</text>' % (cx, 132 + li * 24, ln))
        if i < 3:
            parts.append('            <path d="M %d 151 L %d 151" stroke="#8499bd" stroke-width="2" fill="none" marker-end="url(#c5m)"/>' % (cx + 92, cx + 116))
    # 下方余额刻度带:10 万 → 9 万 → 8 万(维持线)
    parts.append('            <text x="100" y="252" fill="#8499bd" font-size="11">账户保证金余额 ↓</text>')
    parts.append('            <line x1="100" y1="316" x2="830" y2="316" stroke="#e88" stroke-width="1.5" stroke-dasharray="6 5"/>')
    parts.append('            <text x="100" y="308" fill="#ffb4b4" font-size="12">维持线 8 万:低于它就要追加</text>')
    parts.append('            <path d="M 150 278 L 360 297 L 570 316 L 780 316" fill="none" stroke="#f0c96a" stroke-width="2"/>')
    for dx, dy, lab in [(150, 278, "10 万"), (360, 297, "9 万"), (570, 316, "8 万")]:
        parts.append('            <circle cx="%d" cy="%d" r="5" fill="#f0c96a"/>' % (dx, dy))
        parts.append('            <text x="%d" y="%d" text-anchor="middle" fill="#f0c96a" font-size="11.5" font-weight="800">%s</text>' % (dx, dy - 14, lab))
    parts.append('            <circle cx="780" cy="316" r="8" fill="none" stroke="#e88" stroke-width="2"/>')
    parts.append('            <text x="780" y="336" text-anchor="middle" fill="#ffb4b4" font-size="11.5" font-weight="800">第 3 天开盘前:触发追加电话</text>')
    parts.append('            <text x="450" y="364" text-anchor="middle" fill="#c9d4e8" font-size="13">每天收盘按结算价当场结清:连「等反弹再说」的选项都没有——划走的是现金,不是浮亏数字</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 380",
        "期货逐日盯市时间线:缴 10 万保证金控制 100 万合约;标的每天跌 1% 就划走 1 万,余额 10 万、9 万、8 万,触到维持线 8 万后第三天开盘前必须追加,否则强平",
        "把每日结算用数字走一遍:第一天亏 1 万剩 9 万,第二天再亏 1 万剩 8 万,正好触到维持线——第三天开盘前追加电话就到。杠杆不提高判断胜率,只放大结果,而且你连「装死等反弹」的选项都没有。")


def _fig_c5_option_mirror():
    """ch05 期权买卖双方损益镜像。锚点:chapter-05.html:87 <h3>2.3. 买方亏损有限,卖方风险更复杂</h3>。
    具体账:K=10 元、权利金 0.5 元,平衡点 10.5 元;股价 12 元时买方 +1.5、卖方 -1.5。"""
    parts = []
    parts.append('            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">看涨期权:买方和卖方,同一条曲线的两面镜子</text>')
    parts.append('            <text x="450" y="56" text-anchor="middle" fill="#8499bd" font-size="12.5">例:行权价 K = 10 元,权利金 0.5 元/股 → 股价涨过 10.5 元,买方才真正开始赚钱</text>')
    parts.append('            <defs><marker id="c5x" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#46587a"/></marker></defs>')
    # 坐标轴:横轴到期股价,纵轴到期盈亏;0 轴即横轴
    parts.append('            <line x1="100" y1="190" x2="800" y2="190" stroke="#46587a" stroke-width="1.5" marker-end="url(#c5x)"/>')
    parts.append('            <line x1="100" y1="60" x2="100" y2="300" stroke="#46587a" stroke-width="1.5"/>')
    parts.append('            <text x="796" y="212" text-anchor="end" fill="#8499bd" font-size="12">到期股价</text>')
    parts.append('            <text x="88" y="64" text-anchor="end" fill="#8499bd" font-size="12">盈亏</text>')
    for lv in [("+%.1f" % 1.5, 85), ("+0.5", 155), ("0", 190), ("-0.5", 225)]:
        parts.append('            <text x="92" y="%d" text-anchor="end" fill="#8499bd" font-size="11">%s</text>' % (lv[1] + 4, lv[0]))
    parts.append('            <line x1="104" y1="155" x2="798" y2="155" stroke="rgba(122,167,240,0.14)" stroke-width="1"/>')
    parts.append('            <line x1="104" y1="225" x2="798" y2="225" stroke="rgba(122,167,240,0.14)" stroke-width="1"/>')
    # 行权价与盈亏平衡点竖线:x(p)=140+(p-9)*200 → K=10 在 340,平衡点 10.5 在 440
    parts.append('            <line x1="340" y1="70" x2="340" y2="310" stroke="rgba(122,167,240,0.35)" stroke-width="1.5" stroke-dasharray="5 5"/>')
    parts.append('            <text x="340" y="330" text-anchor="middle" fill="#c9d4e8" font-size="12">行权价 K = 10</text>')
    parts.append('            <line x1="440" y1="70" x2="440" y2="310" stroke="rgba(240,201,106,0.5)" stroke-width="1.5" stroke-dasharray="5 5"/>')
    parts.append('            <text x="440" y="330" text-anchor="middle" fill="#f0c96a" font-size="12" font-weight="800">盈亏平衡点 10.5</text>')
    # 买方(蓝实线):亏不过权利金,涨起来不封顶;卖方(红虚线):严格镜像
    parts.append('            <path d="M 140 225 L 340 225 L 740 85" fill="none" stroke="#a8c6ff" stroke-width="3"/>')
    parts.append('            <path d="M 140 155 L 340 155 L 740 295" fill="none" stroke="#ffb4b4" stroke-width="3" stroke-dasharray="7 5"/>')
    parts.append('            <circle cx="440" cy="190" r="4.5" fill="#f0c96a"/>')
    parts.append('            <circle cx="740" cy="85" r="4" fill="#a8c6ff"/>')
    parts.append('            <circle cx="740" cy="295" r="4" fill="#ffb4b4"/>')
    parts.append('            <text x="752" y="89" fill="#a8c6ff" font-size="12" font-weight="800">+1.5</text>')
    parts.append('            <text x="752" y="299" fill="#ffb4b4" font-size="12" font-weight="800">-1.5</text>')
    parts.append('            <text x="612" y="70" text-anchor="end" fill="#a8c6ff" font-size="12" font-weight="800">买方(实线):盈利不封顶</text>')
    parts.append('            <text x="612" y="302" text-anchor="end" fill="#ffb4b4" font-size="12" font-weight="800">卖方(虚线):亏损不见底</text>')
    parts.append('            <text x="212" y="246" text-anchor="middle" fill="#a8c6ff" font-size="12">买方最坏:-0.5 权利金(有底)</text>')
    parts.append('            <text x="212" y="136" text-anchor="middle" fill="#ffb4b4" font-size="12">卖方最好:+0.5 权利金(有顶)</text>')
    parts.append('            <text x="450" y="348" text-anchor="middle" fill="#c9d4e8" font-size="12.5">两条线关于 0 轴严格镜像:买方赚的每一分都是卖方亏的——期权是零和的风险转移,不是一起赚钱的地方</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 350",
        "看涨期权买卖双方到期损益镜像图:行权价 10 元、权利金 0.5 元,盈亏平衡点 10.5 元;买方亏损有限盈利不封顶,卖方盈利有限亏损不见底,两条曲线关于零轴镜像",
        "买方最多亏掉权利金 0.5 元(亏损有底),价格涨过平衡点 10.5 元后赚多少没有顶;卖方镜像相反:最多赚 0.5 元,亏损理论上看不到底。所以卖方收的「保费」,本质是替别人扛尾部风险的价格。")


def _fig_c6_order_pipeline():
    """ch06 一笔委托的链路。锚点:chapter-06.html:33 <h3>1.2. 券商是通道,不是交易所</h3>。
    环节措辞回看 1.2(券商接收委托做前置风控)、1.4(清算轧净额、交收钱货两清)。"""
    rows = [
        ("券商 App 下单", "点下买入:委托先进券商,永远直接进不了交易所",
         "出错:非交易时间 → 挂着或废单", "你 + 券商"),
        ("券商柜台", "校验身份与三方存管,接收委托,先冻结资金或持仓",
         "出错:可用资金不足 → 当场拒单", "券商"),
        ("前置风控", "拦查停牌、涨跌幅、申报价格、数量单位,合规才放行",
         "出错:不合规 → 拦在交易所门外", "券商"),
        ("交易所撮合", "价格优先、时间优先,排队配对撞出成交价",
         "出错:没排上对手价 → 干等或撤单", "交易所"),
        ("登记结算", "清算把买卖轧成净额,T+1 交收钱货两清、登记簿改名",
         "提醒:成交 ≠ 结束,交收才算数", "登记结算机构"),
    ]
    parts = []
    parts.append('            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">一笔委托的旅程:从你点下买入,到钱货两清</text>')
    parts.append('            <line x1="110" y1="86" x2="110" y2="350" stroke="rgba(240,201,106,0.35)" stroke-width="2"/>')
    for i, (name, desc, err, actor) in enumerate(rows):
        y = 58 + i * 66
        cy = y + 28
        stroke = "rgba(240,201,106,0.42)" if i == 4 else "rgba(122,167,240,0.28)"
        parts.append('            <rect x="70" y="%d" width="760" height="56" rx="12" fill="rgba(18,29,49,0.70)" stroke="%s"/>' % (y, stroke))
        parts.append('            <circle cx="110" cy="%d" r="15" fill="rgba(240,201,106,0.18)"/>' % cy)
        parts.append('            <text x="110" y="%d" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="900">%d</text>' % (cy + 5, i + 1))
        parts.append('            <text x="150" y="%d" fill="#eef4f8" font-size="15" font-weight="800">%s</text>' % (cy - 4, name))
        parts.append('            <text x="150" y="%d" fill="#bcc9dd" font-size="12">%s</text>' % (cy + 18, desc))
        err_color = "#f0c96a" if i == 4 else "#ffb4b4"
        parts.append('            <text x="818" y="%d" text-anchor="end" fill="%s" font-size="12">%s</text>' % (cy - 4, err_color, err))
        parts.append('            <text x="818" y="%d" text-anchor="end" fill="#8499bd" font-size="11">%s</text>' % (cy + 18, actor))
    parts.append('            <text x="450" y="416" text-anchor="middle" fill="#c9d4e8" font-size="13">五道闸各有分工:订单穿过哪一环、在哪一环出事,决定了报错长什么样;假设「下单即成交」的回测,落地一定数错钱</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 430",
        "委托链路图:券商App下单、券商柜台校验并冻结资金、前置风控拦截不合规单、交易所按价格时间优先撮合、登记结算清算轧净额并交收;每环标注出错后果",
        "你点一次买入,委托要穿过券商柜台、前置风控、交易所撮合、登记结算五道闸:柜台先冻结资金,风控把不合规订单拦在交易所门外,成交之后清算还要轧净额、交收才算钱货两清。每一环出错的后果完全不同。")


def _fig_c7_ohlc_aggregation():
    """ch07 五笔成交聚合成一根 K 线。锚点:chapter-07.html:61 <h3>1.3. K 线实体和影线只是压缩图</h3>。
    成交序列沿用 1.2 节正文:9.90 / 10.05 / 10.20 / 9.95 / 10.10 → OHLC = 9.90/10.20/9.90/10.10。"""
    trades = [(1, 9.90, "9.90"), (2, 10.05, "10.05"), (3, 10.20, "10.20"),
              (4, 9.95, "9.95"), (5, 10.10, "10.10")]
    pts = []
    for i, (_n, p, _s) in enumerate(trades):
        x = 90 + i * 65
        y = 250 - (p - 9.90) * 500  # 9.90→250, 10.20→100
        pts.append((x, int(round(y))))
    parts = []
    parts.append('            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">五笔真实成交,聚合成一根 K 线</text>')
    parts.append('            <defs><marker id="c7a" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#f0c96a"/></marker><marker id="c7b" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#46587a"/></marker></defs>')
    # 左面板:逐笔成交
    parts.append('            <rect x="40" y="56" width="400" height="232" rx="14" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>')
    parts.append('            <text x="240" y="82" text-anchor="middle" fill="#a8c6ff" font-size="13.5" font-weight="800">全天 5 笔成交(按时间顺序)</text>')
    parts.append('            <path d="M ' + " L ".join("%d %d" % p for p in pts) + '" fill="none" stroke="#7aa7f0" stroke-width="2.5"/>')
    big = {1, 3, 5}  # 首笔、最高笔、末笔画大一点
    for (i, (n, _p, s)), (x, y) in zip(enumerate(trades), pts):
        idx = i + 1
        r = 6 if idx in big else 4.5
        col = "#f0c96a" if idx in big else "#a8c6ff"
        parts.append('            <circle cx="%d" cy="%d" r="%s" fill="%s"/>' % (x, y, ("%g" % r), col))
    parts.append('            <text x="76" y="254" text-anchor="end" fill="#f0c96a" font-size="11.5" font-weight="800">① 9.90</text>')
    parts.append('            <text x="%d" y="%d" text-anchor="middle" fill="#eef4f8" font-size="11.5">② %s</text>' % (pts[1][0] - 8, pts[1][1] + 22, trades[1][2]))
    parts.append('            <text x="%d" y="%d" fill="#f0c96a" font-size="11.5" font-weight="800">③ %s 最高</text>' % (pts[2][0] + 12, pts[2][1] + 4, trades[2][2]))
    parts.append('            <text x="%d" y="%d" text-anchor="middle" fill="#eef4f8" font-size="11.5">④ %s</text>' % (pts[3][0] + 8, pts[3][1] + 24, trades[3][2]))
    parts.append('            <text x="%d" y="%d" fill="#f0c96a" font-size="11.5" font-weight="800">⑤ %s</text>' % (pts[4][0] + 12, pts[4][1] + 2, trades[4][2]))
    parts.append('            <line x1="60" y1="270" x2="398" y2="270" stroke="#46587a" stroke-width="1.5" marker-end="url(#c7b)"/>')
    parts.append('            <text x="402" y="274" fill="#8499bd" font-size="11">时间</text>')
    # 聚合箭头
    parts.append('            <path d="M 448 165 L 512 165" stroke="#f0c96a" stroke-width="3" fill="none" marker-end="url(#c7a)"/>')
    parts.append('            <text x="480" y="148" text-anchor="middle" fill="#f0c96a" font-size="11.5">聚合</text>')
    # 右面板:聚合出的一根阳线(收 10.10 > 开 9.90)
    parts.append('            <rect x="520" y="56" width="340" height="232" rx="14" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>')
    parts.append('            <text x="690" y="82" text-anchor="middle" fill="#a8c6ff" font-size="13.5" font-weight="800">得到一根阳线(收盘 &gt; 开盘)</text>')
    parts.append('            <line x1="640" y1="100" x2="640" y2="250" stroke="#a8c6ff" stroke-width="2.5"/>')
    parts.append('            <rect x="612" y="150" width="56" height="100" rx="3" fill="rgba(122,167,240,0.30)" stroke="#a8c6ff" stroke-width="2"/>')
    parts.append('            <text x="692" y="104" fill="#eef4f8" font-size="12">最高 10.20 ← 第③笔</text>')
    parts.append('            <text x="692" y="154" fill="#eef4f8" font-size="12">收盘 10.10 ← 末笔⑤</text>')
    parts.append('            <text x="692" y="254" fill="#eef4f8" font-size="12">开盘=最低 9.90 ← 首笔①</text>')
    parts.append('            <text x="640" y="278" text-anchor="middle" fill="#f0c96a" font-size="12" font-weight="800">实体 +0.20 元 ≈ +2.0%</text>')
    parts.append('            <text x="450" y="320" text-anchor="middle" fill="#c9d4e8" font-size="12.5">四个数各有着落:开=首笔、高低=极值、收=末笔;被压掉的是路径——上午拉升下午跳水,也可能得到同样的四个数</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 340",
        "OHLC 聚合示意:五笔成交 9.90/10.05/10.20/9.95/10.10 聚合成一根阳线,开 9.90、高 10.20、低 9.90、收 10.10,实体约 +2.0%",
        "日线上的四个价格来自一次 first/max/min/last 聚合:开是首笔、收是末笔、高低是极值。这只股票恰好最低=开盘,所以下影线长度为零。聚合很优雅,但路径被压掉了——看 K 线时心里要装着这个前提。")


def _fig_c8_volatility_cluster():
    """ch08 波动率聚集示意。锚点:chapter-08.html:40 <h3>1.4. 这条路颠不颠</h3>。
    呼应 1.4 节「今天涨 5%、明天跌 4%、后天涨 6%」口径:平静期/风暴期交替。"""
    nav = [(70, 215), (110, 212), (150, 216), (190, 210), (230, 213), (270, 208),
           (300, 206), (330, 150), (360, 238), (390, 132), (420, 222), (450, 162),
           (470, 158), (510, 156), (550, 160), (590, 155), (620, 152),
           (650, 206), (680, 120), (710, 190), (740, 104), (770, 176),
           (800, 168), (830, 162)]
    parts = []
    parts.append('            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">波动率聚集:平静期和大风大浪是扎堆来的</text>')
    # 背景分带
    parts.append('            <rect x="70" y="60" width="210" height="210" fill="rgba(122,167,240,0.07)"/>')
    parts.append('            <rect x="300" y="60" width="140" height="210" fill="rgba(232,120,120,0.07)"/>')
    parts.append('            <rect x="460" y="60" width="160" height="210" fill="rgba(122,167,240,0.07)"/>')
    parts.append('            <rect x="640" y="60" width="140" height="210" fill="rgba(232,120,120,0.07)"/>')
    parts.append('            ' + svg_text("平静期 日波动~0.3%", 175, 76, 200, size=11.5, color="#a8c6ff", weight=700, max_chars=16, max_lines=1))
    parts.append('            ' + svg_text("风暴期 单日±5%连发", 370, 76, 132, size=11.5, color="#ffb4b4", weight=700, max_chars=8, max_lines=2))
    parts.append('            ' + svg_text("又一段平静", 540, 76, 150, size=11.5, color="#a8c6ff", weight=700, max_chars=10, max_lines=1))
    parts.append('            ' + svg_text("又一阵风暴", 710, 76, 132, size=11.5, color="#ffb4b4", weight=700, max_chars=10, max_lines=1))
    # 净值折线
    parts.append('            <path d="M ' + " L ".join("%d %d" % p for p in nav) + '" fill="none" stroke="#eef4f8" stroke-width="2.5"/>')
    # 极端单日标注
    parts.append('            <circle cx="360" cy="238" r="5" fill="#e88"/>')
    parts.append('            <text x="360" y="258" text-anchor="middle" fill="#ffb4b4" font-size="11.5" font-weight="800">单日 -6%</text>')
    parts.append('            <circle cx="740" cy="104" r="5" fill="#f0c96a"/>')
    parts.append('            <text x="740" y="90" text-anchor="middle" fill="#f0c96a" font-size="11.5" font-weight="800">单日 +7%</text>')
    # 长期中枢(均值回归)
    parts.append('            <line x1="70" y1="208" x2="830" y2="150" stroke="#f0c96a" stroke-width="1.5" stroke-dasharray="7 6"/>')
    parts.append('            <text x="545" y="130" text-anchor="middle" fill="#f0c96a" font-size="11.5" font-weight="800">长期中枢:偏离远了会被拉回</text>')
    # 坐标轴
    parts.append('            <line x1="70" y1="60" x2="70" y2="270" stroke="#46587a" stroke-width="1.5"/>')
    parts.append('            <line x1="70" y1="270" x2="830" y2="270" stroke="#46587a" stroke-width="1.5"/>')
    parts.append('            <text x="60" y="66" text-anchor="end" fill="#8499bd" font-size="12">净值</text>')
    parts.append('            <text x="828" y="290" text-anchor="end" fill="#8499bd" font-size="12">时间</text>')
    parts.append('            <text x="450" y="312" text-anchor="middle" fill="#c9d4e8" font-size="12.5">大涨大跌喜欢扎堆,而不是均匀撒开:刚刮过风暴的市场,往往还要再晃一阵——波动会聚集</text>')
    parts.append('            <text x="450" y="336" text-anchor="middle" fill="#8499bd" font-size="12">拿「最近 20 天」估风险要记住这回事:风暴刚过时高估、平静太久时低估</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 350",
        "波动率聚集示意:净值曲线上平静期与风暴期交替,风暴期单日 -6%、+7% 扎堆出现,价格围绕长期中枢上下枢转、但分布并不均匀",
        "收益率长期围着一条中枢转,但波动本身一阵一阵:平静期每天零点几个百分点,风暴期单日 ±5% 起步且接连不断。市场难赢的原因之一就在这——用最近一段外推风险,总会在错误的时间大意。")


def _fig_c8_sharpe_compare():
    """ch08 夏普比率直觉。锚点:chapter-08.html:67 <h3>1.6. 每承担一份波动赚多少超额收益</h3>。
    账可手算:两条曲线同到年化 +8%,无风险 2%;波动 6% → 夏普 1.00,波动 24% → 夏普 0.25。"""
    parts = []
    parts.append('            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">夏普比率的直觉:同样的终点,颠簸的价格不同</text>')
    parts.append('            <line x1="70" y1="60" x2="70" y2="260" stroke="#46587a" stroke-width="1.5"/>')
    parts.append('            <line x1="70" y1="260" x2="520" y2="260" stroke="#46587a" stroke-width="1.5"/>')
    parts.append('            <text x="60" y="66" text-anchor="end" fill="#8499bd" font-size="12">净值</text>')
    parts.append('            <text x="518" y="280" text-anchor="end" fill="#8499bd" font-size="12">时间</text>')
    parts.append('            <path d="M 70 235 C 190 215 340 160 500 120" fill="none" stroke="#a8c6ff" stroke-width="3"/>')
    parts.append('            <path d="M 70 235 L 115 150 L 165 265 L 225 105 L 285 250 L 345 140 L 405 230 L 455 165 L 500 120" fill="none" stroke="#f0c96a" stroke-width="2.5"/>')
    parts.append('            <circle cx="500" cy="120" r="5" fill="#eef4f8"/>')
    parts.append('            <text x="448" y="104" text-anchor="middle" fill="#eef4f8" font-size="12" font-weight="800">同一终点</text>')
    parts.append('            <line x1="92" y1="288" x2="116" y2="288" stroke="#a8c6ff" stroke-width="3"/>')
    parts.append('            <text x="124" y="292" fill="#a8c6ff" font-size="12.5" font-weight="800">A 平稳:波动率 6%</text>')
    parts.append('            <line x1="300" y1="288" x2="324" y2="288" stroke="#f0c96a" stroke-width="3"/>')
    parts.append('            <text x="332" y="292" fill="#f0c96a" font-size="12.5" font-weight="800">B 毛刺:波动率 24%</text>')
    # 右侧这笔账
    parts.append('            <rect x="560" y="70" width="300" height="190" rx="14" fill="rgba(18,29,49,0.70)" stroke="rgba(240,201,106,0.42)"/>')
    parts.append('            ' + svg_text("夏普 =(年化-无风险2%)/波动率", 710, 94, 284, size=12.5, color="#f0c96a", weight=800, max_chars=17, max_lines=1))
    parts.append('            <text x="584" y="128" fill="#a8c6ff" font-size="13" font-weight="800">A:(8% - 2%) / 6% = 1.00</text>')
    parts.append('            <text x="584" y="156" fill="#f0c96a" font-size="13" font-weight="800">B:(8% - 2%) / 24% = 0.25</text>')
    parts.append('            <line x1="584" y1="174" x2="836" y2="174" stroke="rgba(122,167,240,0.2)" stroke-width="1"/>')
    parts.append('            <text x="584" y="200" fill="#bcc9dd" font-size="12">赚的总数一样,但 B 每扛一份颠簸,</text>')
    parts.append('            <text x="584" y="224" fill="#bcc9dd" font-size="12">换来的超额报酬只有 A 的 1/4</text>')
    parts.append('            <text x="450" y="322" text-anchor="middle" fill="#c9d4e8" font-size="12.5">夏普把收益摊到每份波动上:它衡量「每扛一份晃荡换来多少超额」,所以卖期权这类「平时小赚、偶尔暴雷」的策略,暴雷前夏普会很好看</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 340",
        "夏普比率直觉对比:两条净值曲线到同一终点年化+8%,平稳的 A 波动率 6% 夏普 1.00,毛刺多的 B 波动率 24% 夏普 0.25",
        "终点相同不等于质量相同:A 波动 6% 夏普 1.00,B 波动 24% 夏普 0.25——B 每扛一份颠簸只换来 A 四分之一的超额报酬。看收益先问颠簸价格,这是「每个数字回答不同问题」里夏普负责的那个。")


def _fig_c9_factor_groups():
    """ch09 分层回测五组柱状图。锚点:chapter-09.html:72 <h3>1.6. 高分组是不是真的更好</h3>。
    口径沿用该节:第 1 组装因子值最高(股息率)的股票,每月调仓、连跑数年看未来收益。"""
    groups = [
        ("第 1 组", "股息率最高", 5.1, "rgba(240,201,106,0.45)", "#f0c96a", "#f0c96a"),
        ("第 2 组", "", 4.0, "rgba(122,167,240,0.42)", "none", "#a8c6ff"),
        ("第 3 组", "", 3.3, "rgba(122,167,240,0.34)", "none", "#a8c6ff"),
        ("第 4 组", "", 2.8, "rgba(122,167,240,0.27)", "none", "#a8c6ff"),
        ("第 5 组", "股息率最低", 2.1, "rgba(232,120,120,0.22)", "#e88", "#ffb4b4"),
    ]
    parts = []
    parts.append('            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">分层回测:按股息率分 5 组,未来收益是否单调</text>')
    parts.append('            <text x="450" y="57" text-anchor="middle" fill="#8499bd" font-size="12">口径沿用本节:第 1 组装股息率最高的股票、第 5 组装最低的,每月调仓、连跑数年取平均</text>')
    parts.append('            <line x1="90" y1="60" x2="90" y2="250" stroke="#46587a" stroke-width="1.5"/>')
    parts.append('            <line x1="90" y1="250" x2="850" y2="250" stroke="#46587a" stroke-width="1.5"/>')
    parts.append('            <text x="32" y="74" fill="#8499bd" font-size="11">年均收益↑</text>')
    tops = []
    for i, (name, tag, ret, fill, stroke, vcol) in enumerate(groups):
        cx = 175 + i * 140
        h = int(round(ret * 30))  # 1% → 30px
        top = 250 - h
        tops.append((cx, top))
        rect = '            <rect x="%d" y="%d" width="90" height="%d" fill="%s"' % (cx - 45, top, h, fill)
        if stroke != "none":
            rect += ' stroke="%s" stroke-width="1.5"' % stroke
        rect += '/>'
        parts.append(rect)
        parts.append('            <text x="%d" y="%d" text-anchor="middle" fill="%s" font-size="14" font-weight="800">+%.1f%%</text>' % (cx, top - 16, vcol, ret))
        parts.append('            <text x="%d" y="272" text-anchor="middle" fill="#eef4f8" font-size="12.5" font-weight="800">%s</text>' % (cx, name))
        if tag:
            parts.append('            <text x="%d" y="291" text-anchor="middle" fill="#8499bd" font-size="11">%s</text>' % (cx, tag))
    parts.append('            <path d="M ' + " L ".join("%d %d" % p for p in tops) + '" fill="none" stroke="#eef4f8" stroke-width="2" stroke-dasharray="6 5"/>')
    parts.append('            <text x="706" y="76" text-anchor="middle" fill="#eef4f8" font-size="12.5" font-weight="800">单调递减 = 因子值越大,未来收益越好</text>')
    parts.append('            <text x="706" y="96" text-anchor="middle" fill="#f0c96a" font-size="11.5" font-weight="800">多空差 +5.1% - 2.1% ≈ +3.0 个百分点/年</text>')
    parts.append('            <text x="450" y="316" text-anchor="middle" fill="#ffb4b4" font-size="12.5">反过来,要是第 3 组反超第 1 组、顺序乱跳——先怀疑运气和行业暴露,别急着下注;单调才算有用</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 330",
        "分层回测柱状图:按股息率把股票分五组,未来一年平均收益从第1组+5.1%单调降到第5组+2.1%,多空差约+3.0个百分点/年",
        "把股票按股息率排队分五组、每月调仓跑上几年:高分组 +5.1% 一路降到低分组 +2.1%,单调才算有用——说明因子分数和未来收益同向。顺序一旦乱跳,先怀疑运气或行业暴露,别急着下注。")


# -*- coding: utf-8 -*-
# 批次 D:6 张信息型概念图,风格对齐 build_book.py 现有 _fig_*。
# 纯字符串拼接,不用 f-string;依赖 build_book.py 的 concept_figure()/svg_text()。


def _fig_d10_split():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">训练、验证、测试:一条只能向前的河</text>
            <!-- 时间轴 -->
            <line x1="70" y1="120" x2="830" y2="120" stroke="#46587a" stroke-width="2"/>
            <defs><marker id="d10a" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#8499bd"/></marker></defs>
            <line x1="70" y1="120" x2="826" y2="120" stroke="#7aa7f0" stroke-width="2.5" marker-end="url(#d10a)"/>
            <!-- 三段 -->
            <rect x="70" y="80" width="450" height="80" rx="12" fill="rgba(122,167,240,0.14)" stroke="rgba(122,167,240,0.45)"/>
            <text x="295" y="106" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">训练集</text>
            <text x="295" y="128" text-anchor="middle" fill="#eef4f8" font-size="13">模型在这里学参数</text>
            <text x="295" y="148" text-anchor="middle" fill="#8499bd" font-size="11.5">随便用,用多少遍都行</text>
            <rect x="530" y="80" width="150" height="80" rx="12" fill="rgba(240,201,106,0.13)" stroke="rgba(240,201,106,0.45)"/>
            <text x="605" y="106" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">验证集</text>
            <text x="605" y="128" text-anchor="middle" fill="#eef4f8" font-size="13">用来调超参和选模型</text>
            <text x="605" y="148" text-anchor="middle" fill="#8499bd" font-size="11.5">可反复用,但会"被用脏"</text>
            <rect x="690" y="80" width="140" height="80" rx="12" fill="rgba(232,120,120,0.12)" stroke="rgba(232,120,120,0.5)"/>
            <text x="760" y="106" text-anchor="middle" fill="#ffb4b4" font-size="15" font-weight="800">测试集</text>
            <text x="760" y="128" text-anchor="middle" fill="#eef4f8" font-size="13">封存到最后一刻</text>
            <text x="760" y="148" text-anchor="middle" fill="#8499bd" font-size="11.5">只用一次,报告它</text>
            <!-- 信息只能向前 -->
            <text x="295" y="196" text-anchor="middle" fill="#8499bd" font-size="12">时光</text>
            <line x1="330" y1="192" x2="500" y2="192" stroke="#8499bd" stroke-width="1.5" marker-end="url(#d10a)"/>
            <text x="605" y="196" text-anchor="middle" fill="#8499bd" font-size="12"></text>
            <line x1="680" y1="192" x2="690" y2="192" stroke="#8499bd" stroke-width="1.5"/>
            <!-- 红色回流禁止 -->
            <path d="M 760 200 C 700 250, 420 250, 300 200" fill="none" stroke="#e88" stroke-width="2.5" stroke-dasharray="7 6" marker-end="url(#d10r)"/>
            <defs><marker id="d10r" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#e88"/></marker></defs>
            <line x1="560" y1="212" x2="586" y2="238" stroke="#e88" stroke-width="3.5" stroke-linecap="round"/>
            <line x1="586" y1="212" x2="560" y2="238" stroke="#e88" stroke-width="3.5" stroke-linecap="round"/>
            <text x="450" y="272" text-anchor="middle" fill="#ffb4b4" font-size="14" font-weight="800">测试集的信息流回前段 = 回测被判作弊</text>
            <text x="450" y="298" text-anchor="middle" fill="#c9d4e8" font-size="12.5">顺序变体:时间序列必须按时间切,不能随机打乱——那是另一种偷看未来</text>"""
    return concept_figure(body, "0 0 900 315",
        "训练集、验证集、测试集按时间轴依次排列,测试集信息回流训练的红色虚线被打叉",
        "切分不是比例问题,是流向问题:训练集随便用,验证集用来挑超参所以会慢慢被用脏,测试集封存到最后只用一次。任何信息从右往左回流,回测就在作弊;时间序列还必须按时间切,随机打乱等于另一个方向的作弊。")


def _fig_d11_pipeline():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">从分数到订单:五步流水线,每步都可能改形</text>
            <defs>
              <marker id="d11a" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#7aa7f0"/></marker>
            </defs>
            <!-- 五个步骤框 -->
            <rect x="30" y="84" width="150" height="118" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>
            <text x="105" y="112" text-anchor="middle" fill="#a8c6ff" font-size="14" font-weight="800">① 模型打分</text>
            <text x="105" y="136" text-anchor="middle" fill="#bcc9dd" font-size="11.5">每只股一个分</text>
            <text x="105" y="156" text-anchor="middle" fill="#8499bd" font-size="11">输入:因子值</text>
            <text x="105" y="174" text-anchor="middle" fill="#8499bd" font-size="11">输出:预期收益排序</text>
            <rect x="202" y="84" width="150" height="118" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(240,201,106,0.42)"/>
            <text x="277" y="112" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">② 组合约束</text>
            <text x="277" y="136" text-anchor="middle" fill="#bcc9dd" font-size="11.5">单票上限·行业上限</text>
            <text x="277" y="156" text-anchor="middle" fill="#bcc9dd" font-size="11.5">跟踪误差预算</text>
            <text x="277" y="174" text-anchor="middle" fill="#8499bd" font-size="11">分数不是仓位,先过笼头</text>
            <rect x="374" y="84" width="150" height="118" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>
            <text x="449" y="112" text-anchor="middle" fill="#a8c6ff" font-size="14" font-weight="800">③ 目标组合</text>
            <text x="449" y="136" text-anchor="middle" fill="#bcc9dd" font-size="11.5">一张目标权重表</text>
            <text x="449" y="156" text-anchor="middle" fill="#8499bd" font-size="11">它还不存在</text>
            <text x="449" y="174" text-anchor="middle" fill="#8499bd" font-size="11">只是计算的结果</text>
            <rect x="546" y="84" width="150" height="118" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>
            <text x="621" y="112" text-anchor="middle" fill="#a8c6ff" font-size="14" font-weight="800">④ 对比现持仓</text>
            <text x="621" y="136" text-anchor="middle" fill="#bcc9dd" font-size="11.5">目标 vs 实有</text>
            <text x="621" y="156" text-anchor="middle" fill="#8499bd" font-size="11">差出来的才是交易</text>
            <text x="621" y="174" text-anchor="middle" fill="#8499bd" font-size="11">差得多 = 换手高 = 成本高</text>
            <rect x="718" y="84" width="150" height="118" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(232,120,120,0.45)"/>
            <text x="793" y="112" text-anchor="middle" fill="#ffb4b4" font-size="14" font-weight="800">⑤ 拆成订单</text>
            <text x="793" y="136" text-anchor="middle" fill="#bcc9dd" font-size="11.5">按时间/价格平滑拆单</text>
            <text x="793" y="156" text-anchor="middle" fill="#8499bd" font-size="11">市价·限价·算法单</text>
            <text x="793" y="174" text-anchor="middle" fill="#8499bd" font-size="11">下单前三检查拦截</text>
            <!-- 连线 -->
            <line x1="180" y1="143" x2="198" y2="143" stroke="#7aa7f0" stroke-width="2.5" marker-end="url(#d11a)"/>
            <line x1="352" y1="143" x2="370" y2="143" stroke="#7aa7f0" stroke-width="2.5" marker-end="url(#d11a)"/>
            <line x1="524" y1="143" x2="542" y2="143" stroke="#7aa7f0" stroke-width="2.5" marker-end="url(#d11a)"/>
            <line x1="696" y1="143" x2="714" y2="143" stroke="#7aa7f0" stroke-width="2.5" marker-end="url(#d11a)"/>
            <text x="450" y="248" text-anchor="middle" fill="#eef4f8" font-size="14">每一步都在"变形":分数→满足约束的组合→和现在不同的差→一条条订单</text>
            <text x="450" y="274" text-anchor="middle" fill="#c9d4e8" font-size="12.5">失误排查从后往前查:先看订单是不是下错,再看持仓对没对,最后才怪模型分数</text>"""
    return concept_figure(body, "0 0 900 300",
        "五步流水线:模型打分、组合约束、目标组合、对比现持仓、拆成订单,每步标注输入输出",
        "分数一路到订单要经过五道工序:打分、过约束、成目标、比现仓、拆订单。故事从后往前排查:订单下错最先看订单系统,组合走形先看约束,最后才轮到怪模型。")


def _fig_d13_alpha_beta():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">指增的收益拆开看:Beta、Alpha、成本三截账</text>
            <!-- 三根柱状:左组合总收益,拆右两根 -->
            <!-- 左:沪深300涨10%,组合涨 +11.5% -->
            <rect x="90" y="150" width="110" height="200" rx="6" fill="rgba(122,167,240,0.25)" stroke="rgba(122,167,240,0.45)"/>
            <text x="145" y="170" text-anchor="middle" fill="#eef4f8" font-size="14" font-weight="800">基准(沪深300)</text>
            <text x="145" y="248" text-anchor="middle" fill="#a8c6ff" font-size="24" font-weight="800">+10%</text>
            <text x="145" y="275" text-anchor="middle" fill="#8499bd" font-size="11.5">全部来自大盘</text>
            <!-- 中:分解堆叠:Beta +9/Alpha +2.5/成本 -1 -->
            <rect x="330" y="170" width="110" height="162" fill="rgba(122,167,240,0.3)" stroke="rgba(122,167,240,0.5)"/>
            <rect x="330" y="150" width="110" height="20" fill="rgba(240,201,106,0.4)" stroke="rgba(240,201,106,0.6)"/>
            <rect x="330" y="132" width="110" height="18" fill="rgba(232,120,120,0.4)" stroke="rgba(232,120,120,0.6)"/>
            <text x="385" y="360" text-anchor="middle" fill="#eef4f8" font-size="14" font-weight="800">指增组合  +11.5%</text>
            <text x="385" y="250" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">Beta +10%</text>
            <text x="385" y="163" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">Alpha +2%</text>
            <text x="385" y="144" text-anchor="middle" fill="#ffb4b4" font-size="14" font-weight="800">成本 −0.5%</text>
            <!-- 右:公式 -->
            <rect x="560" y="150" width="300" height="200" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(240,201,106,0.42)"/>
            <text x="710" y="182" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">一句话账</text>
            <text x="578" y="214" fill="#eef4f8" font-size="13.5">组合收益 = Beta + Alpha − 摩擦</text>
            <text x="578" y="240" fill="#bcc9dd" font-size="13">= 10% + 2% − 0.5% = 11.5%</text>
            <text x="578" y="268" fill="#bcc9dd" font-size="12.5">Beta 是大盘给的,学不来也避不掉;</text>
            <text x="578" y="290" fill="#bcc9dd" font-size="12.5">Alpha 是选股选出来的,指增拼命争它;</text>
            <text x="578" y="312" fill="#bcc9dd" font-size="12.5">摩擦是每次调仓的买路钱,只能想办法省。</text>
            <!-- 中间等号 -->
            <text x="480" y="260" text-anchor="middle" fill="#eef4f8" font-size="22" font-weight="800">≈</text>
            <text x="450" y="392" text-anchor="middle" fill="#c9d4e8" font-size="13">年报上那个"年化收益"从来不自己拆开——先学会自己拆,才看得懂是谁的功劳</text>"""
    return concept_figure(body, "0 0 900 415",
        "指增收益分解:基准+10%,指增+11.5%拆成Beta下段、Alpha段和成本负截",
        "任何一股指增收益都是三截账:Beta 是跟着大盘的,+2% 是拼选股拼出来的 Alpha,−0.5% 是摩擦成本。看年化收益之前先拆开——市场一跌,你会发现 Beta 功劳巨大,Alpha 往往只剩一点点。")


def _fig_d14_hedge_vol():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">对冲不是让收益变高,是让带子收窄</text>
            <defs>
              <marker id="d14a" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#8499bd"/></marker>
            </defs>
            <!-- 坐标轴 -->
            <line x1="60" y1="320" x2="850" y2="320" stroke="#46587a" stroke-width="1.5"/>
            <line x1="60" y1="60" x2="60" y2="320" stroke="#46587a" stroke-width="1.5" marker-end="url(#d14a)"/>
            <!-- 纯多头:大起大落带子 -->
            <path d="M 60 290 L 140 250 L 200 280 L 300 190 L 380 240 L 460 160 L 540 220 L 620 120 L 700 180 L 790 90 L 850 140" fill="none" stroke="#ffb4b4" stroke-width="2.5"/>
            <!-- 对冲后:窄带子缓慢上行 -->
            <path d="M 60 300 L 140 285 L 200 292 L 300 262 L 380 268 L 460 240 L 540 248 L 620 222 L 700 228 L 790 205 L 850 212" fill="none" stroke="#7aa7f0" stroke-width="2.8"/>
            <!-- 对比标注 -->
            <text x="120" y="80" fill="#ffb4b4" font-size="13.5" font-weight="800">纯多头:大起大落</text>
            <text x="120" y="100" fill="#bcc9dd" font-size="11.5">年化波动约 ±16%</text>
            <text x="120" y="118" fill="#8499bd" font-size="11">赚多赚有,坐不住才是风险</text>
            <text x="600" y="268" fill="#a8c6ff" font-size="13.5" font-weight="800">对冲后:带子收窄</text>
            <text x="600" y="288" fill="#bcc9dd" font-size="11.5">年化波动压到 ±5% 上下</text>
            <text x="600" y="306" fill="#8499bd" font-size="11">方向削平了,选股能力留下</text>
            <!-- 对比数字卡 -->
            <rect x="660" y="60" width="230" height="110" rx="12" fill="rgba(18,29,49,0.75)" stroke="rgba(240,201,106,0.42)"/>
            <text x="775" y="86" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">同一组持仓,同一时段内</text>
            <text x="675" y="110" fill="#bcc9dd" font-size="12">纯多头  年化波动 16.7%</text>
            <text x="675" y="132" fill="#bcc9dd" font-size="12">对冲后  年化波动  4.8%</text>
            <text x="675" y="156" fill="#8499bd" font-size="11">代价:付出期指名义和保证金</text>
            <text x="450" y="364" text-anchor="middle" fill="#c9d4e8" font-size="12.5">对冲的变化不在终点高不高,在路稳不稳——中性策略买的是"拿得住",不是"赚更多"</text>"""
    return concept_figure(body, "0 0 900 385",
        "两条净值曲线:纯多头大起大落(波动约16.7%),对冲后收窄到4.8%缓慢上行",
        "对冲做对的事是把波动带子收窄,不是把终点抬高。同一组持仓,纯多头一年 ±16.7% 的大起大落,对冲后收窄到 ±4.8%;代价是你要付期指名义和保证金。")


def _fig_d15_pair_trading():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">配对交易:两条腿一买一空,赌价差回归</text>
            <defs>
              <marker id="d15a" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#8499bd"/></marker>
            </defs>
            <!-- 双坐标系 -->
            <line x1="70" y1="260" x2="830" y2="260" stroke="#46587a" stroke-width="1.5"/>
            <!-- A 腿:低(蓝色) -->
            <path d="M 70 236 L 150 226 L 230 232 L 310 240 L 390 244 L 470 240 L 550 246 L 630 238 L 710 242 L 830 240" fill="none" stroke="#7aa7f0" stroke-width="2.5"/>
            <text x="80" y="216" fill="#a8c6ff" font-size="13">A 市场(被低估)</text>
            <!-- B 腿:高(金色) -->
            <path d="M 70 96 L 150 106 L 230 100 L 310 92 L 390 88 L 470 92 L 550 86 L 630 94 L 710 90 L 830 92" fill="none" stroke="#f0c96a" stroke-width="2.5"/>
            <text x="80" y="80" fill="#f0c96a" font-size="13">B 市场(被高估)</text>
            <!-- 价差带 -->
            <path d="M 70 136 L 150 136 L 230 136 L 310 136 L 390 136 L 470 136 L 550 136 L 630 136 L 710 136 L 830 136" fill="none" stroke="#8499bd" stroke-width="1" stroke-dasharray="4 4"/>
            <text x="840" y="130" fill="#8499bd" font-size="11" text-anchor="end">价差均值线</text>
            <!-- 开仓区间打标 -->
            <line x1="240" y1="105" x2="240" y2="250" stroke="#e88" stroke-width="2" stroke-dasharray="5 4"/>
            <text x="240" y="96" text-anchor="middle" fill="#ffb4b4" font-size="12" font-weight="800">① 价差扩到阈值</text>
            <text x="240" y="278" text-anchor="middle" fill="#bcc9dd" font-size="11">开:多 A / 空 B</text>
            <!-- 平仓 -->
            <line x1="700" y1="96" x2="700" y2="246" stroke="#8fb37a" stroke-width="2" stroke-dasharray="5 4"/>
            <text x="700" y="88" text-anchor="middle" fill="#8fb37a" font-size="12" font-weight="800">② 价差回归</text>
            <text x="700" y="268" text-anchor="middle" fill="#bcc9dd" font-size="11">收:两腿同时平</text>
            <!-- 数字例 -->
            <rect x="490" y="290" width="320" height="80" rx="10" fill="rgba(18,29,49,0.75)" stroke="rgba(122,167,240,0.28)"/>
            <text x="505" y="314" fill="#eef4f8" font-size="12.5" font-weight="800">示意一笔账:</text>
            <text x="505" y="336" fill="#bcc9dd" font-size="12">开仓 A=100 / B=102;收仓 A=100.5 / B=100.5</text>
            <text x="505" y="356" fill="#bcc9dd" font-size="12">两腿各赚 +0.5 / +1.5?错了——多A赚 0.5,空B赚 1.5,各算各的</text>
            <text x="450" y="402" text-anchor="middle" fill="#c9d4e8" font-size="12.5">指望的不是某一边涨,是两边重新贴合——方向赢不赢不影响你,大小盘风格切换才是你的风险</text>"""
    return concept_figure(body, "0 0 900 420",
        "配对交易:两条贴着走的价差线,价差拉到阈值时开多A空B,回归时同时平仓",
        "配对交易永远两腿各算各的:开多被低估的 A、同时空等额的被高估的 B,赌的是它们重新贴合。赚的不是谁涨,是价差回归;方向涨不涨跟你没关系,风格切换才是你的风险。")


def _fig_d17_three_tables():
    body = """            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">小面包店一年:三张报表互相指着对方</text>
            <defs>
              <marker id="d17a" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#7aa7f0"/></marker>
              <marker id="d17g" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#f0c96a"/></marker>
            </defs>
            <!-- 三个报表卡 -->
            <rect x="40" y="68" width="250" height="210" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.4)"/>
            <text x="165" y="94" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">利润表(今年赚没赚)</text>
            <text x="58" y="124" fill="#eef4f8" font-size="12.5">收入              80 万</text>
            <text x="58" y="146" fill="#bcc9dd" font-size="12.5">- 材料/人工        55 万</text>
            <text x="58" y="168" fill="#bcc9dd" font-size="12.5">- 房租/折旧/税     20 万</text>
            <line x1="58" y1="176" x2="272" y2="176" stroke="#46587a" stroke-width="1"/>
            <text x="58" y="196" fill="#f0c96a" font-size="12.5" font-weight="800">= 净利润            5 万</text>
            <text x="58" y="220" fill="#8499bd" font-size="11">净利 ≠ 到手的钱(有赊账)</text>
            <text x="58" y="240" fill="#8499bd" font-size="11">是一年干出来的结果</text>
            <rect x="330" y="68" width="250" height="210" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(240,201,106,0.45)"/>
            <text x="455" y="94" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">资产负债表(手里有啥)</text>
            <text x="348" y="124" fill="#eef4f8" font-size="12.5">现金             12 万</text>
            <text x="348" y="146" fill="#bcc9dd" font-size="12.5">存货(面粉)        3 万</text>
            <text x="348" y="168" fill="#bcc9dd" font-size="12.5">设备(烤箱)       15 万</text>
            <line x1="348" y1="176" x2="562" y2="176" stroke="#46587a" stroke-width="1"/>
            <text x="348" y="196" fill="#eef4f8" font-size="12.5">= 总资产           30 万</text>
            <text x="348" y="218" fill="#bcc9dd" font-size="12.5">- 借款              5 万</text>
            <text x="348" y="240" fill="#f0c96a" font-size="12.5" font-weight="800">= 净资产           25 万</text>
            <rect x="620" y="68" width="250" height="210" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.4)"/>
            <text x="745" y="94" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">现金流量表(钱往哪走)</text>
            <text x="638" y="124" fill="#eef4f8" font-size="12.5">经营活动净流入  +8 万</text>
            <text x="638" y="146" fill="#bcc9dd" font-size="12.5">投资(买烤箱)     -15 万</text>
            <text x="638" y="168" fill="#bcc9dd" font-size="12.5">筹资(借来)      +5 万</text>
            <line x1="638" y1="176" x2="852" y2="176" stroke="#46587a" stroke-width="1"/>
            <text x="638" y="196" fill="#f0c96a" font-size="12.5" font-weight="800">= 现金净变化      -2 万</text>
            <text x="638" y="220" fill="#8499bd" font-size="11">利润 5 万但现金少了 2 万:</text>
            <text x="638" y="240" fill="#8499bd" font-size="11">净利被存货/应收/折旧吃掉</text>
            <!-- 三表互指 -->
            <path d="M 300 178 L 322 178" stroke="#7aa7f0" stroke-width="2" fill="none" marker-end="url(#d17a)"/>
            <text x="311" y="168" text-anchor="middle" fill="#8499bd" font-size="10.5">净利进净资产</text>
            <path d="M 590 178 L 612 178" stroke="#f0c96a" stroke-width="2" fill="none" marker-end="url(#d17g)"/>
            <text x="601" y="168" text-anchor="middle" fill="#8499bd" font-size="10.5">现金对上末数</text>
            <text x="450" y="312" text-anchor="middle" fill="#c9d4e8" font-size="13">利润表问"赚了吗",资产负债表问"有啥、欠啥",现金流量表问"钱真到手了吗"</text>
            <text x="450" y="336" text-anchor="middle" fill="#ffb4b4" font-size="12.5">三张表数字对不上 = 有个地方在造假或藏雷;对得上,是真的还是假的,要进一步看经营现金流</text>"""
    return concept_figure(body, "0 0 900 360",
        "小面包店一年的三张报表卡:利润表净利润5万、资产负债表30万总资产25万净资产、现金流量表现金减少2万,互相用箭头勾连",
        "同一个小面包店,三张表各回答一件事:利润表说净赚 5 万,资产负债表说年底手里 30 万总资产、25 万净资产,现金流量表说钱实际上少了 2 万。三张表任何一个数字对不上,背后就有个地方在藏雷。")


PATCH_C = {
    5: [("为什么期货会放大盈亏", _fig_c5_margin_timeline),
        ("买方亏损有限", _fig_c5_option_mirror)],
    6: [("券商是通道", _fig_c6_order_pipeline)],
    7: [("影线只是压缩图", _fig_c7_ohlc_aggregation)],
    8: [("这条路颠不颠", _fig_c8_volatility_cluster),
        ("每承担一份波动赚多少超额收益", _fig_c8_sharpe_compare)],
    9: [("高分组是不是真的更好", _fig_c9_factor_groups)],
}


PATCH_D = {
    10: [("历史答案背得太熟", _fig_d10_split)],
    11: [("预测分数不是仓位", _fig_d11_pipeline)],
    13: [("指数收益加超额", _fig_d13_alpha_beta)],
    14: [("Beta 对冲的直觉", _fig_d14_hedge_vol)],
    15: [("配对交易", _fig_d15_pair_trading)],
    17: [("三张报表分别回答什么", _fig_d17_three_tables)],
}


CONCEPT_FIGURES = {
    0: [("鱼票为什么会缩水", _fig_inflation)],
    1: [("一张极简资产负债表", _fig_bank_balance), ("信心为什么这么重要", _fig_bank_run)],
    2: [("钱不是直接从一个人", _fig_money_flow)],
    3: [("先从一家小店说起", _fig_stock_ownership)],
    4: [("债券先当作一张标准化借条", _fig_bond_cashflow)],
    5: [("看涨期权和看跌期权", _fig_option_payoff)],
    6: [("价格优先和时间优先", _fig_orderbook)],
    7: [("一天被压成四个价格", _fig_candlestick)],
    8: [("从高点跌到低点有多痛", _fig_drawdown_sharpe)],
    9: [("常见因子家族", _fig_factor_quantile)],
    10: [("收盘价成交最容易骗人", _fig_lookahead)],
    11: [("约束优化的直觉", _fig_quant_pipeline)],
    13: [("指数增强", _fig_index_enhance)],
    14: [("市场中性想解决什么", _fig_market_neutral)],
    15: [("配对交易", _fig_arbitrage)],
    16: [("净值和收益披露", _fig_fund_nav)],
    17: [("三张报表分别回答什么", _fig_income_statement)],
    18: [("目录结构先分层", _fig_project_layout)],
    19: [("模拟调仓", _fig_backtest_loop)],
    21: [("过拟合", _fig_overfitting)],
    22: [("回撤里最容易做错决定", _fig_loss_recovery)],
}

def _merge_figures(base, patch):
    """按章合并锚点列表,不覆盖既有条目"""
    for k, v in patch.items():
        base.setdefault(k, []).extend(v)

_merge_figures(CONCEPT_FIGURES, CONCEPT_FIGURES_FREE)
_merge_figures(CONCEPT_FIGURES, PATCH_C)
_merge_figures(CONCEPT_FIGURES, PATCH_D)


SUMMARY_LABEL_OVERRIDES = {
    (27, 0): "量化机构是一条协作生产线",
    (27, 2): "个人先做低频完整流程",
    (28, 0): "个人量化应分阶段推进",
    (28, 1): "每阶段都要有可检查产出",
    (28, 2): "计算机优势在工程和模型",
    (37, 0): "三张报表看赚钱家底现金",
    (37, 1): "指标要结合行业周期",
    (37, 2): "基本面因子先处理时间口径",
    (39, 0): "量化项目要分层组织",
    (39, 1): "配置版本记录支撑复现",
    (39, 2): "测试断言挡住假收益",
    (41, 0): "指数增强要检查基准股票池因子组合成本",
    (48, 0): "金融到量化可分十层理解",
    (48, 1): "量化不是脱离金融的算法",
    (48, 2): "越接近实盘越要管风险",
    (49, 0): "工程数据模型要接到金融问题",
    (49, 1): "作品集要展示真实流程",
    (49, 2): "岗位不同能力重点不同",
    (50, 0): "长期学习要逐层推进",
    (50, 1): "每阶段都要有可检查产出",
    (50, 2): "资料服务项目别追热点",
    (51, 0): "术语回到现金流权利风险价格",
    (51, 1): "基础资产要回到权利和风险",
    (51, 2): "复盘术语不是背定义",
    (52, 0): "术语回答收益预测交易风险",
    (52, 1): "Alpha先扣掉Beta再谈",
    (52, 2): "信号要走向真实交易",
    (59, 0): "量化项目最低标准是流程可信",
    (59, 1): "复杂模型不能替代基础检查",
    (59, 2): "每个环节都要能审查",
    (61, 1): "严重亏损常由小错误叠加",
    (61, 2): "亏损要复盘成流程改进",
    (63, 0): "金融看现金流权利风险价格",
    (63, 1): "先建可信流程再谈模型",
    (63, 2): "最好动作是完成小项目",
}


def concise_summary_label(ch_num: int, idx: int, text: str) -> str:
    override = SUMMARY_LABEL_OVERRIDES.get((ch_num, idx))
    if override:
        return override
    clean = re.sub(r"\s+", "", str(text)).strip("。；;，,")
    if len(clean) <= 28:
        return clean
    for sep in ("；", ";", "。", "，", ","):
        if sep in clean:
            first = clean.split(sep)[0].strip("。；;，,")
            if 8 <= len(first) <= 28:
                return first
    if "不是" in clean and "而是" in clean:
        first = clean.split("而是")[0].strip("。；;，,")
        if len(first) <= 28:
            return first
    if "必须" in clean:
        head = clean.split("必须")[0]
        if 4 <= len(head) <= 16:
            return head + "必须先过关"
    return clean[:24] + "要检查"


def render_head(title: str, desc: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(desc or BOOK_SUBTITLE)}" />
    <link rel="icon" href="assets/favicon.svg" />
    <link rel="stylesheet" href="assets/book.css" />
  </head>
"""


def render_summary_figure(ch: dict) -> str:
    """章末小结图:没有专属概念图的章,用"本章留下三件事"卡片图收尾。"""
    title = esc(ch["title"])
    summary_labels = [
        concise_summary_label(ch["num"], i, text)
        for i, text in enumerate(ch["summary"][:3])
    ]
    while len(summary_labels) < 3:
        summary_labels.append(ch["title"])
    summary_positions = [(180, 220), (450, 220), (720, 220)]
    summary_cards = []
    for i, (label, (x, y)) in enumerate(zip(summary_labels, summary_positions), 1):
        summary_cards.append(f"""
            <g>
              <rect x="{x - 115}" y="{y - 70}" width="230" height="140" rx="16" fill="rgba(13,20,36,0.85)" stroke="rgba(122,167,240,0.4)" stroke-width="1.2" />
              <rect x="{x - 103}" y="{y - 58}" width="26" height="26" rx="13" fill="#f0c96a" />
              <text x="{x - 90}" y="{y - 39}" text-anchor="middle" fill="#101420" font-size="13" font-weight="900">{i}</text>
              {svg_text(label, x - 96, y - 8, 192, size=14, color="#eef4f8", max_chars=9, max_lines=5)}
            </g>""")
    return f"""
        <div class="figure figure--reading reveal">
          <svg class="chapter-map" viewBox="0 0 900 360" role="img" aria-label="第 {ch['num']} 章小结图: {title}">
            <rect x="18" y="18" width="864" height="324" rx="20" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.25)" />
            <text x="450" y="68" text-anchor="middle" fill="#eef4f8" font-size="22" font-weight="850">本章留下的三件事</text>
            {''.join(summary_cards)}
          </svg>
          <p class="figure__cap">读完第 {ch['num']} 章后,至少要能复述“{esc(summary_labels[0])}”这一条判断,再用另外两张卡片检查自己是否真的理解。</p>
        </div>
"""


# 正文排版增强:在不改手稿的前提下,机械地把单调段落串升级成有呼吸感的版式。
#
# 1. 句首带标志词的段落(记住/注意/先说结论/铁律...) -> callout 卡片;
# 2. 短语级强调“xxx” -> 金色高亮 span(参照《从神经元到大模型》的彩色术语);
# 3. 金融术语(IC/Beta/夏普/ETF...) -> 天青点线术语(同 dl 的 .term);
# 4. 数值+单位(46 亿美元/3%/20 倍...) -> 金色数字 .num(做全书里的视觉锚点)。
_ENRICH_TERMS_RE = re.compile(
    r"(?<![A-Za-z])(?:RankIC(?![a-z])|VaR|ROE|IC(?![a-zA-Z])|IR(?![a-zA-Z])|ETF|REITs?|IPO|PE(?![a-zA-Z])|PB(?![a-zA-Z])|"
    r"T\+1|T\+0|Alpha|Beta|alpha|beta|夏普比率|夏普|信息比率|最大回撤|波动率|换手率|跟踪误差|"
    r"超额收益|年化收益|市盈率|市净率|股指期货|保证金|基差|升水|贴水|杠杆|动量|反转|沪深 300|中证 500)"
)
_ENRICH_NUM_RE = re.compile(
    r"(?<![0-9A-Za-z#])(-?\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?\s*(?:亿美元|万元|亿元|万美元|万|亿|%|倍|个基点|bp|"
    r"个百分点|年|个月|月|个交易日|交易日|日|天|股|手|张|点|元|次|分钟|小时))(?![0-9A-Za-z「」])"
)


def _enrich_terms_nums(inner: str) -> str:
    """只处理纯文本片段,跳过已有标签,避免嵌套错乱。"""
    parts = re.split(r"(<[^>]+>)", inner)
    for i in range(len(parts)):
        seg = parts[i]
        if not seg or seg.startswith("<"):
            continue
        seg = _ENRICH_TERMS_RE.sub(r'<span class="term">\g<0></span>', seg)
        seg = _ENRICH_NUM_RE.sub(r'<span class="num">\g<0></span>', seg)
        parts[i] = seg
    return "".join(parts)
_CALLOUT_MARKERS = [
    ("郑重提醒", "warn", "郑重提醒"),
    ("先说结论", "note", "先说结论"),
    ("先说最重要的", "note", "先说最重要的"),
    ("先说一件事", "note", "先说一件事"),
    ("一句话记住", "tip", "一句话记住"),
    ("记住这条铁律", "warn", "铁律"),
    ("记住两件事", "tip", "记住两件事"),
    ("记住", "tip", "记住"),
    ("别搞错", "warn", "别搞错"),
    ("小心", "warn", "小心"),
    ("陷阱", "warn", "陷阱"),
    ("关键", "note", "关键"),
    ("要点", "tip", "要点"),
    ("注意", "warn", "注意"),
    ("提醒", "warn", "提醒"),
]

def _marker_title(plain: str) -> tuple:
    """句首 0-16 字内出现标志词,返回 (标志词, 样式, 标题)。"""
    head = plain[:16]
    for kw, style, title in _CALLOUT_MARKERS:
        if kw in head:
            return (kw, style, title)
    return (None, None, None)


def enrich_body(htmltext: str) -> str:
    """对单个小节 body 做富文本增强(不改原文文字,只加包装)。

    手稿 body 由 p(...) + ... 直接拼接,段落之间没有换行,因此按 <p>...</p>
    边界切分;含 figure/pre/table/svg 的复合块保持原样。
    """
    parts = re.split(r"(<p>[\s\S]*?</p>)", htmltext)
    out = []
    for seg in parts:
        if not (seg.startswith("<p>") and seg.endswith("</p>")) or any(tag in seg for tag in ("<pre", "<figure", "<table", "<svg", "<ol", "<ul", "code-walk")):
            out.append(seg)
            continue
        inner = seg[3:-4]
        plain = re.sub(r"<[^>]+>", "", inner)
        # 1) 标志词段落升级成 callout
        kw, style, title = _marker_title(plain)
        if kw and len(plain) <= 260:
            out.append(f'<div class="callout callout--{style} reveal"><span class="callout__title">{esc(title)}</span><p>{_enrich_terms_nums(inner)}</p></div>')
            continue
        # 2) 双引号短语高亮(避免已含标签的片段错乱)
        def _hl(m):
            return f'<span class="hl">“{m.group(1)}”</span>'
        new_inner = re.sub(r"“([^”<>]{2,18})”", _hl, inner)
        # 3) 术语与数字标注:对已含 <span class="hl"> 的嵌套安全(split 按标签切)
        new_inner = _enrich_terms_nums(new_inner)
        out.append(f"<p>{new_inner}</p>")
    return "".join(out)


def render_chapter(ch: dict) -> str:
    idx = ch["num"]
    # 概念图按锚点关键词挂到对应小节后面
    anchors = CONCEPT_FIGURES.get(idx, [])
    used = [False] * len(anchors)

    def attach_figures(title: str, out: list):
        for ai, (keyword, maker) in enumerate(anchors):
            if not used[ai] and keyword in title:
                out.append(maker())
                used[ai] = True

    units = ch.get("units") or []
    sections = []
    recap_rows = []
    if len(units) > 1:
        # 多单元章:单元 = h2 大块,单元内小节 = h3(x.y 编号)
        for ui, unit in enumerate(units, 1):
            unit_sections = prepare_sections(unit["sections"])
            sections.append(f"""
        <h2>{ui}. {esc(unit["title"])}</h2>
""")
            if unit.get("lead"):
                sections.append(f"        <p>{esc(unit['lead'])}</p>\n")
            for si, (title, body) in enumerate(unit_sections, 1):
                sections.append(f"""
        <h3>{ui}.{si}. {esc(title)}</h3>
{enrich_body(body.rstrip())}
""")
                recap_rows.append((f"{ui}.{si}.", title))
                attach_figures(title, sections)
    else:
        rendered_sections = prepare_sections(ch["sections"])
        for n, (title, body) in enumerate(rendered_sections, 1):
            sections.append(f"""
        <h2>{n}. {esc(title)}</h2>
{enrich_body(body.rstrip())}
""")
            recap_rows.append((f"{n}.", title))
            attach_figures(title, sections)
    # 没匹配上的概念图(锚点关键词没找到)兜底追加到正文末尾,避免丢图
    for ai, (keyword, maker) in enumerate(anchors):
        if not used[ai]:
            sections.append(maker())
    top_map = ""
    # 没有手画概念图的章(不分单元数),用"留下三件事"图收尾
    tail_figure = "" if anchors else render_summary_figure(ch)

    summary = "\n".join(f"            <li>{esc(x)}</li>" for x in ch["summary"])
    section_recap = "\n".join(
        f"            <li><strong>{num}</strong> {esc(title)}</li>"
        for num, title in recap_rows
    )
    quiz = "\n".join(
        f"""          <details class="quiz__item">
            <summary>{esc(q)}</summary>
            <p>{esc(a)}</p>
          </details>"""
        for q, a in ch["quiz"]
    )
    # 页面含实验台(data-lab 占位)才挂 labs.js
    labs_script = '\n    <script src="assets/labs.js"></script>' if 'data-lab="' in "".join(sections) else ""
    return render_head(f"第 {idx} 章 · {ch['title']} | {BOOK_TITLE}", ch["desc"]) + f"""  <body data-chapter="{idx}">
    <main class="chapter">
      <div class="chapter__inner">
        <p class="chapter__eyebrow">{esc(ch["part"])} · 第 {idx} 章</p>
        <h1>{esc(ch["title"])}</h1>
        <p class="lead">{esc(ch["lead"])}</p>
        <section class="objectives reveal">
          <h2>读完这一章,你会明白</h2>
          <ul>
{summary}
          </ul>
        </section>
{top_map}
{''.join(sections)}
{tail_figure}
        <section class="summary reveal">
          <h2>小结</h2>
          <p>这一章的正文不是让你记住几个孤立名词,而是要把它们放回同一条因果链里。读完后,先用自己的话复述下面几条判断,再顺着“小节回看”检查是否能解释每一步。</p>
          <ul>
{summary}
          </ul>
          <h3>小节回看</h3>
          <ul>
{section_recap}
          </ul>
        </section>
        <section class="quiz reveal">
          <h2>自测</h2>
{quiz}
        </section>
      </div>
    </main>
    <script src="assets/book.js"></script>{labs_script}
  </body>
</html>
"""


def render_index() -> str:
    cards = []
    last_part = None
    for ch in CHAPTERS:
        if ch["part"] != last_part:
            if last_part is not None:
                cards.append("      </div>\n")
            last_part = ch["part"]
            cards.append(f"""      <p class="toc-part">{esc(last_part)}</p>
      <div class="toc-grid">
""")
        cards.append(f"""        <a class="toc-card reveal" href="{chapter_file(ch['num'])}">
          <span class="toc-card__num">第 {ch['num']} 章</span>
          <span class="toc-card__title">{esc(ch['title'])}</span>
          <span class="toc-card__desc">{esc(ch['desc'])}</span>
        </a>
""")
    cards.append("      </div>\n")

    return render_head(f"{BOOK_TITLE} · {BOOK_SUBTITLE}", "给计算机背景读者的金融与量化入门书。") + f"""  <body data-cover>
    <a
      class="github-corner"
      href="{REPO_URL}"
      target="_blank"
      rel="noopener noreferrer"
      aria-label="在 GitHub 上查看源码"
    >
      <svg viewBox="0 0 250 250" aria-hidden="true">
        <path class="github-corner__ribbon" d="M0 0l115 115h15l12 27 108 108V0z" />
        <path
          class="github-corner__arm"
          d="M128 109c-15-9-9-19-9-19 3-7 2-11 2-11-1-7 3-2 3-2 4 5 2 11 2 11-3 10 5 15 9 16"
        />
        <path
          class="github-corner__body"
          d="M115 115s4 2 5 0l14-14c3-2 6-3 8-3-8-11-15-24 2-41 5-5 10-7 16-7 1-2 3-7 12-11 0 0 5 3 7 16 4 2 8 5 12 9s7 8 9 12c14 3 17 7 17 7-4 8-9 11-11 11 0 6-2 11-7 16-16 16-30 10-41 2 0 3-1 7-5 11l-12 11c-1 1 1 5 1 5z"
        />
      </svg>
    </a>
    <header class="cover">
      <div class="cover__inner">
        <p class="cover__eyebrow">{esc(BOOK_SUBTITLE)}</p>
        <h1>{esc(BOOK_TITLE)}</h1>
        <p class="cover__lead">
          一本写给计算机背景金融小白的路线书。先把货币、银行、股票、债券、券商、基金、衍生品、A 股交易制度和宏观周期讲清楚,
          再进入量化行业的因子、回测、机器学习、组合优化、交易执行、风控、机构案例、个人项目和上线检查清单。
        </p>
        <div class="cover__actions">
          <a class="button button--primary" data-continue href="chapter-00.html">开始阅读</a>
          <a class="button button--ghost" href="glossary.html">术语表</a>
          <a class="button button--ghost" href="{REPO_URL}" target="_blank" rel="noopener">GitHub 源码</a>
        </div>
        <p class="muted">
          内容借鉴《小岛经济学》的生产和信用直觉,以及《漫步华尔街》的市场有效性和指数投资思想;
          文字为原创整理,不复写原书章节。
        </p>
        <p class="muted" style="margin-top: 0.6rem; font-size: 0.88rem">
          在线版:
          <a class="xref" href="https://finance-to-quant.pages.dev/" target="_blank" rel="noopener">finance-to-quant.pages.dev</a>
          · 源码:
          <a class="xref" href="{REPO_URL}" target="_blank" rel="noopener">GitHub</a>
          · PDF:
          <a class="xref" href="{REPO_URL}/releases" target="_blank" rel="noopener">Releases</a>
        </p>
      </div>
    </header>
    <main class="toc-section" id="toc">
      <h2>全书目录</h2>
      <p class="toc-section__hint">建议顺序阅读。第 0-5 章建立金融和主要资产地基,第 6-8 章理解 A 股交易、行情、指数、收益风险和有效市场,第 9-12 章进入量化研究生产线,第 13-18 章理解行业、策略、产品、监管和多资产,第 19-32 章完成项目、场景练习、检查清单和结语。</p>
{''.join(cards)}
      <section class="about reveal">
        <h2>关于本书</h2>
        <p>
          这本书写给和我一样计算机背景、对金融和量化好奇却不知从何下手的人。它不假设你懂任何金融知识,
          从"钱到底是什么"这种最朴素的问题讲起,用小岛经济学式的直觉、真实历史案例(郁金香狂热、南海泡沫、
          雷曼、长期资本管理公司、西蒙斯、骑士资本)和手绘概念图,一步步走到量化研究的因子、回测、机器学习、
          组合优化、交易执行和风控。
        </p>
        <p>
          全书 33 章,正文全部手写,配 22 张解释概念的手绘 SVG 图。内容尽量做到通俗又不失专业,
          但金融和量化涉及真实资金与风险,书中所有案例、数字和结论仅用于学习,<strong>不构成任何投资建议</strong>。
          行业、机构和监管信息会随时间变化,实盘和引用前请以交易所、证监会、协会、券商和数据服务商的最新原文为准。
        </p>
        <p class="about__meta">
          作者 <a class="xref" href="https://github.com/chenxuan520" target="_blank" rel="noopener">@chenxuan520</a>
          · 源码与勘误见 <a class="xref" href="{REPO_URL}" target="_blank" rel="noopener">GitHub 仓库</a>
          · 以 MIT License 开源
        </p>
      </section>
    </main>
    <script src="assets/book.js"></script>
  </body>
</html>
"""


def render_glossary() -> str:
    items = "\n".join(
        f"""          <li id="g-{slugify(term)}">
            <strong>{esc(term)}</strong>
            <p>{esc(desc)}</p>
          </li>"""
        for term, desc in GLOSSARY
    )
    refs = "\n".join(
        f"""          <li><a class="xref" href="{esc(url)}" target="_blank" rel="noopener">{esc(name)}</a></li>"""
        for name, url in REFERENCES
    )
    return render_head(f"术语表与参考资料 | {BOOK_TITLE}", "金融与量化术语速查。") + f"""  <body data-extra="glossary">
    <main class="chapter">
      <div class="chapter__inner">
        <p class="chapter__eyebrow">附录</p>
        <h1>术语表与参考资料</h1>
        <p class="lead">这里收录全书反复出现的概念。第一次读不必背,读章节时随时回来查。</p>
        <section class="glossary-list reveal">
          <h2>术语表</h2>
          <ul>
{items}
          </ul>
        </section>
        <section class="references reveal">
          <h2>参考资料与延伸阅读</h2>
          <p>以下链接用于核对监管、机构公开资料和两本启发性读物。部分行业资料会随时间变化,后续版本应定期刷新。</p>
          <ul>
{refs}
          </ul>
        </section>
      </div>
    </main>
    <script src="assets/book.js"></script>
  </body>
</html>
"""


def write_assets() -> None:
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    (assets / "favicon.svg").write_text(
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#0f1622"/><path d="M12 44h40M18 38V24m14 14V16m14 22V28" stroke="#f0c96a" stroke-width="5" stroke-linecap="round"/><path d="M14 20h36" stroke="#7aa7f0" stroke-width="4" stroke-linecap="round"/></svg>\n""",
        encoding="utf-8",
    )
    (assets / "book.css").write_text(CSS, encoding="utf-8")
    (assets / "book.js").write_text(render_js(), encoding="utf-8")


def render_js() -> str:
    chapter_rows = ",\n    ".join(
        "{ num: %d, title: %r, file: %r, part: %r }"
        % (ch["num"], ch["title"], chapter_file(ch["num"]), ch["part"])
        for ch in CHAPTERS
    )
    return JS_TEMPLATE.replace("__CHAPTERS__", chapter_rows).replace("__BOOK_TITLE__", BOOK_TITLE)


CSS = r"""
:root {
  --bg: #101420;
  --bg-soft: #181e2c;
  --panel: rgba(214, 228, 248, 0.06);
  --panel-strong: rgba(214, 228, 248, 0.1);
  --text: #eef4f8;
  --text-soft: #bcc9dd;
  --text-dim: #8b9cb4;
  --line: rgba(240, 201, 106, 0.2);
  --primary: #f0c96a;
  --accent: #7aa7f0;
  --danger: #ee8877;
  --reading-width: 47rem;
  --header-height: 56px;
  --font-sans: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; scroll-padding-top: calc(var(--header-height) + 20px); }
html, body { overflow-x: hidden; }
body {
  margin: 0;
  min-height: 100vh;
  color: var(--text);
  font-family: var(--font-sans);
  line-height: 1.85;
  font-size: 1.0625rem;
  background:
    linear-gradient(115deg, rgba(122, 167, 240, 0.12), transparent 34%),
    linear-gradient(245deg, rgba(240, 201, 106, 0.13), transparent 30%),
    linear-gradient(180deg, #0f141f 0%, #121828 54%, #0d121c 100%);
  background-attachment: fixed;
}
a { color: var(--primary); text-decoration: none; }
a:hover { text-decoration: underline; }

.book-header {
  position: fixed;
  inset: 0 0 auto 0;
  z-index: 50;
  height: var(--header-height);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0 1rem;
  background: rgba(13, 18, 28, 0.86);
  border-bottom: 1px solid var(--line);
  backdrop-filter: blur(14px);
}
.book-header__menu, .book-header__home {
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text);
  min-height: 40px;
}
.book-header__menu {
  width: 40px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.1rem;
}
.book-header__home {
  display: inline-flex;
  align-items: center;
  padding: 0 0.75rem;
  border-radius: 8px;
  font-weight: 750;
  white-space: nowrap;
}
.book-header__current {
  min-width: 0;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-dim);
  font-size: 0.95rem;
}
.book-progress {
  position: fixed;
  top: var(--header-height);
  left: 0;
  z-index: 51;
  height: 3px;
  width: 0;
  background: linear-gradient(90deg, var(--primary), var(--accent));
}

.book-toc-backdrop {
  position: fixed;
  inset: 0;
  z-index: 60;
  background: rgba(0, 0, 0, 0.48);
  opacity: 0;
  pointer-events: none;
  transition: opacity 180ms ease;
}
.book-toc-backdrop.is-open { opacity: 1; pointer-events: auto; }
.book-toc {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 61;
  width: min(25rem, 86vw);
  padding: 1rem;
  overflow-y: auto;
  background: #131a28;
  border-right: 1px solid var(--line);
  display: none;
  transform: translateX(calc(-100% - 24px));
}
.book-toc.is-open { display: block; transform: translateX(0); visibility: visible; }
.book-toc__title {
  margin: 0.25rem 0 1rem;
  color: var(--primary);
  font-weight: 850;
}
.book-toc__part {
  margin: 1rem 0 0.35rem;
  color: var(--text-dim);
  font-size: 0.86rem;
}
.book-toc__link {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: 0.5rem;
  padding: 0.55rem 0.65rem;
  border-radius: 8px;
  color: var(--text-soft);
}
.book-toc__link > span:first-child { white-space: nowrap; color: var(--accent); font-weight: 700; }
.book-toc__link:hover, .book-toc__link.is-current {
  background: rgba(240, 201, 106, 0.11);
  color: var(--text);
  text-decoration: none;
}

.book-layout {
  width: 100%;
}

.book-layout__main {
  min-width: 0;
}

.book-rail--chapters { grid-column: 1; }
.book-layout__main { grid-column: 2; }
.book-rail--outline { grid-column: 3; }

.book-rail {
  display: none;
}

.book-rail__title {
  margin: 0 0 0.75rem;
  color: var(--primary);
  font-weight: 850;
  font-size: 0.92rem;
}

.book-rail__list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.book-rail__part {
  margin: 1rem 0 0.35rem;
  color: var(--text-dim);
  font-size: 0.78rem;
  font-weight: 800;
}

.book-rail__part:first-child {
  margin-top: 0;
}

.book-rail__link,
.book-rail__outline-link {
  display: grid;
  gap: 0.25rem;
  padding: 0.46rem 0.55rem;
  border-radius: 8px;
  color: var(--text-soft);
  line-height: 1.35;
}

.book-rail__link {
  grid-template-columns: 2.2rem minmax(0, 1fr);
}

.book-rail__link:hover,
.book-rail__outline-link:hover {
  background: rgba(240, 201, 106, 0.1);
  color: var(--text);
  text-decoration: none;
}

.book-rail__link.is-current,
.book-rail__outline-link.is-current {
  background: rgba(240, 201, 106, 0.15);
  color: var(--text);
}

.book-rail__num {
  color: var(--accent);
  font-size: 0.8rem;
  font-weight: 850;
}

.book-rail__name {
  min-width: 0;
  overflow-wrap: anywhere;
}

.book-rail__outline-item--sub .book-rail__outline-link {
  padding-left: 1.25rem;
  font-size: 0.9rem;
  color: var(--text-dim);
}

.book-rail__empty {
  margin: 0;
  color: var(--text-dim);
  font-size: 0.9rem;
}

.cover {
  min-height: 78vh;
  display: grid;
  place-items: center;
  padding: 7rem 1.25rem 4rem;
}
.cover__inner {
  width: min(68rem, 100%);
}
.cover__eyebrow, .chapter__eyebrow, .toc-part {
  color: var(--primary);
  font-weight: 800;
  letter-spacing: 0;
}
.cover h1 {
  margin: 0;
  max-width: 12ch;
  font-size: clamp(3.2rem, 7vw, 6.5rem);
  line-height: 1.02;
  letter-spacing: 0;
}
.cover__lead {
  max-width: 48rem;
  color: var(--text-soft);
  font-size: 1.22rem;
}
.cover__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
  margin: 2rem 0 1rem;
}
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0.55rem 1rem;
  border-radius: 8px;
  border: 1px solid var(--line);
  font-weight: 800;
}
.button--primary { background: var(--primary); color: #15130c; }
.button--ghost { color: var(--text); background: rgba(255,255,255,0.05); }
.muted { color: var(--text-dim); }

.toc-section {
  width: min(72rem, calc(100% - 2rem));
  margin: 0 auto 5rem;
}
.toc-section h2 {
  margin-top: 0;
  font-size: 2rem;
}
.toc-section__hint { color: var(--text-soft); }
.toc-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
  margin-bottom: 2rem;
}
.toc-card {
  display: grid;
  gap: 0.25rem;
  min-height: 9.5rem;
  padding: 1rem;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.045);
  color: var(--text);
}
.toc-card:hover {
  text-decoration: none;
  border-color: rgba(240, 201, 106, 0.42);
  background: rgba(255, 255, 255, 0.07);
}
.toc-card__num { color: var(--accent); font-weight: 800; font-size: 0.92rem; }
.toc-card__title { font-size: 1.18rem; font-weight: 850; }
.toc-card__desc { color: var(--text-soft); font-size: 0.96rem; }

/* GitHub 右上角翻角 */
.github-corner {
  position: fixed;
  top: 0;
  right: 0;
  z-index: 20;
  width: 88px;
  height: 88px;
}
.github-corner svg {
  width: 100%;
  height: 100%;
  display: block;
}
.github-corner__ribbon { fill: #f0c96a; }
.github-corner__arm,
.github-corner__body { fill: #101420; }
.github-corner:hover .github-corner__ribbon { fill: #f6d98a; }

/* 关于本书 */
.about {
  margin-top: 1rem;
  padding: 1.6rem 1.8rem;
  border: 1px solid var(--line);
  border-left: 3px solid rgba(240, 201, 106, 0.55);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.03);
}
.about h2 { margin-top: 0; font-size: 1.5rem; }
.about p { color: var(--text-soft); }
.about__meta { color: var(--text-dim); font-size: 0.9rem; margin-bottom: 0; }
@media (max-width: 640px) {
  .github-corner { width: 64px; height: 64px; }
}

.chapter {
  padding: calc(var(--header-height) + 2.4rem) 1.2rem 2rem;
}
.chapter__inner {
  max-width: var(--reading-width);
  margin: 0 auto;
}
.chapter h1 {
  margin: 0 0 1rem;
  font-size: clamp(2rem, 5vw, 2.9rem);
  line-height: 1.14;
  letter-spacing: 0;
}
.lead {
  margin: 0 0 2.5rem;
  color: var(--text);
  font-size: 1.18rem;
  line-height: 1.8;
}
.chapter p {
  margin: 1rem 0;
  color: var(--text-soft);
}
.chapter h2 {
  margin: 3rem 0 1rem;
  padding-top: 1.4rem;
  border-top: 1px solid var(--line);
  font-size: clamp(1.5rem, 3.4vw, 2rem);
  line-height: 1.2;
  letter-spacing: 0;
}
.chapter h3 {
  margin: 2.2rem 0 0.8rem;
  font-size: 1.28rem;
  color: var(--text);
}
.summary, .quiz, .glossary-list, .references {
  border-left: 2px solid rgba(240, 201, 106, 0.28);
  padding-left: 1.1rem;
}
ul, ol { padding-left: 1.35rem; }
li + li { margin-top: 0.25rem; }
strong { color: #ffffff; }

.table-wrap {
  overflow-x: auto;
  margin: 1.2rem 0;
}
table {
  width: 100%;
  border-collapse: collapse;
  min-width: 40rem;
  background: rgba(255, 255, 255, 0.035);
}
th, td {
  border: 1px solid rgba(240, 201, 106, 0.18);
  padding: 0.68rem 0.75rem;
  vertical-align: top;
}
th {
  color: var(--primary);
  text-align: left;
  background: rgba(240, 201, 106, 0.07);
}

pre {
  max-width: 100%;
  overflow-x: auto;
  white-space: pre;
}

code {
  font-family: var(--font-mono);
}

.code-walk__code {
  display: block;
  margin: 1rem 0;
  padding: 1rem;
  border: 1px solid rgba(240, 201, 106, 0.18);
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.22);
  color: var(--text-soft);
  line-height: 1.55;
}

.callout {
  margin: 1.2rem 0;
  padding: 1rem 1rem 1rem 0.95rem;
  border: 1px solid var(--line);
  border-left: 3px solid var(--accent);
  border-radius: 10px;
  background: var(--panel);
}

.callout__title {
  display: block;
  margin-bottom: 0.35rem;
  font-weight: 800;
  font-size: 0.95rem;
  color: var(--accent);
}

.callout p { margin: 0; }

.callout--note { border-left-color: var(--primary); background: rgba(240, 201, 106, 0.07); }
.callout--note .callout__title { color: var(--primary); }
.callout--warn { border-left-color: var(--danger); background: rgba(238, 136, 119, 0.09); }
.callout--warn .callout__title { color: var(--danger); }
.callout--tip { border-left-color: var(--accent); }

/* 正文内短语级金色高亮("双引号"关键说法) */
.hl {
  color: #ffd97a;
  font-weight: 650;
}

/* 金融术语:天青点线,与 deeplearning 书 .term 一致 */
.term {
  color: var(--accent);
  font-weight: 700;
  border-bottom: 1px dotted rgba(122, 167, 240, 0.55);
}

/* 数值锚点:数字+单位 */
.num {
  color: #ffd97a;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

/* 已有 .hl/.term/.num 在 strong 内优先显示金色 */
strong .hl, strong .term, strong .num { color: #ffd97a; }

.objectives {
  margin: 1.6rem 0 2rem;
  padding: 1.1rem 1.3rem;
  border: 1px solid var(--line);
  border-radius: 20px;
  background: var(--panel);
}

.objectives h2 {
  margin: 0 0 0.6rem;
  padding: 0;
  border: 0;
  color: var(--accent);
  font-size: 1rem;
}

.objectives ul {
  margin: 0;
}

.figure {
  margin: 1.8rem 0 2.2rem;
}

.figure--reading {
  padding: 0;
}

.chapter-map {
  display: block;
  width: 100%;
  height: auto;
  border-radius: 20px;
}

.chapter-diagram {
  display: block;
  width: 100%;
  height: auto;
  border-radius: 20px;
  background: rgba(18, 29, 49, 0.55);
  border: 1px solid rgba(122, 167, 240, 0.22);
  padding: 0.4rem;
}

.figure__cap {
  margin: 0.55rem 0 0;
  color: var(--text-dim);
  font-size: 0.92rem;
  text-align: center;
}
.summary {
  margin-top: 3rem;
  padding: 1rem 1rem 1rem 1.25rem;
  border: 1px solid rgba(240, 201, 106, 0.22);
  border-radius: 8px;
  background: rgba(240, 201, 106, 0.06);
}
.summary h2, .quiz h2, .glossary-list h2, .references h2 { margin-top: 0; }
.quiz {
  margin-top: 2rem;
  padding: 1rem 0 0 1.1rem;
}
.quiz__item {
  margin: 0.8rem 0;
  padding: 0.8rem 1rem;
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 8px;
  background: rgba(255,255,255,0.04);
}
.quiz__item summary {
  cursor: pointer;
  font-weight: 800;
  color: var(--text);
}
.quiz__item p { color: var(--text-soft); }

.map-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.8rem;
  margin: 1.2rem 0;
}
.map-grid div {
  min-height: 7rem;
  padding: 1rem;
  border: 1px solid rgba(240, 201, 106, 0.2);
  border-radius: 8px;
  background: rgba(255,255,255,0.045);
}
.map-grid strong, .map-grid span { display: block; }
.map-grid span { color: var(--text-soft); margin-top: 0.35rem; }

.glossary-list ul {
  list-style: none;
  padding: 0;
}
.glossary-list li {
  padding: 1rem 0;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
.glossary-list p { margin: 0.2rem 0 0; color: var(--text-soft); }
.references li { overflow-wrap: anywhere; }

.chapter-nav {
  width: min(var(--reading-width), calc(100% - 2rem));
  margin: 3rem auto 0;
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}
.chapter-nav a {
  flex: 1;
  padding: 0.9rem 1rem;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: rgba(255,255,255,0.04);
  color: var(--text);
}
.chapter-nav a:last-child { text-align: right; }

.reveal { opacity: 0; transform: translateY(10px); transition: opacity 260ms ease, transform 260ms ease; }
.reveal.is-visible { opacity: 1; transform: none; }

@media (max-width: 760px) {
  body { font-size: 1rem; }
  .cover { min-height: 72vh; padding-top: 6rem; }
  .cover h1 { font-size: 3rem; }
  .cover__lead, .lead { font-size: 1.08rem; }
  .toc-grid, .map-grid { grid-template-columns: 1fr; }
  .toc-card { min-height: auto; }
  .chapter { padding-left: 1rem; padding-right: 1rem; }
  .chapter h1 { font-size: 2.25rem; }
  .chapter h2 { font-size: 1.42rem; }
  .summary, .quiz, .glossary-list, .references { padding-left: 0.85rem; }
  .book-header__home { max-width: 7.5rem; overflow: hidden; text-overflow: ellipsis; }
}

@media (min-width: 1180px) {
  .chapter {
    padding: calc(var(--header-height) + 1.4rem) 1rem 4rem;
  }

  .book-layout {
    display: grid;
    grid-template-columns: 220px minmax(0, var(--reading-width)) minmax(180px, 220px);
    gap: 2rem;
    align-items: start;
    max-width: 1280px;
    width: auto;
    margin: 0 auto;
  }

  .book-layout__main .chapter__inner {
    width: 100%;
    max-width: none;
    margin: 0;
  }

  .book-rail {
    display: block;
    position: sticky;
    top: calc(var(--header-height) + 1.25rem);
    max-height: calc(100vh - var(--header-height) - 2rem);
    overflow-y: auto;
    padding: 0.2rem 0.2rem 1rem 0;
    border: 0;
    border-radius: 0;
    background: transparent;
    scrollbar-width: none;
  }

  .book-rail.is-fixed {
    position: fixed;
    top: calc(var(--header-height) + 1.25rem);
    z-index: 20;
  }

  .book-rail::-webkit-scrollbar {
    width: 0;
    height: 0;
    display: none;
  }

  .book-rail::-webkit-scrollbar-thumb {
    background: rgba(240, 201, 106, 0.25);
    border-radius: 999px;
  }

  .chapter-nav {
    width: 100%;
  }
}

@media (min-width: 1320px) {
  .book-layout {
    max-width: 1480px;
    grid-template-columns: 248px minmax(0, 52rem) 248px;
    gap: 2.4rem;
  }
}

@media (min-width: 1680px) {
  .book-layout {
    max-width: 1600px;
    grid-template-columns: 280px minmax(0, 56rem) 300px;
    gap: 3rem;
  }
}

/* ============ 代码走读卡片(code-walk) ============ */
.code-walk {
  margin: 1.8rem auto;
  max-width: 54rem;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: #0d1220;
  box-shadow: 0 14px 34px rgba(0, 0, 0, 0.38);
  overflow: hidden;
}

.code-walk__file {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.6rem 1rem;
  background: rgba(255, 255, 255, 0.04);
  border-bottom: 1px solid var(--line);
  color: var(--text-dim);
  font-family: var(--font-mono);
  font-size: 0.82rem;
}

.code-walk__file::before {
  content: "";
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: var(--accent);
  box-shadow: 14px 0 0 var(--primary), 28px 0 0 var(--danger);
  margin-right: 1.6rem;
}

.code-walk__code {
  margin: 0;
  padding: 1rem 1.1rem;
  overflow-x: auto;
  font-family: var(--font-mono);
  font-size: 0.86rem;
  line-height: 1.7;
  color: #d7e3f7;
  border: none;
  background: none;
  tab-size: 2;
}

.code-walk__code code {
  background: none;
  padding: 0;
  color: inherit;
  font-size: inherit;
}

.cw-tag {
  display: inline-grid;
  place-items: center;
  min-width: 1.25rem;
  height: 1.25rem;
  margin-left: 0.4rem;
  padding: 0 0.2rem;
  border-radius: 999px;
  background: var(--primary);
  color: #10120f;
  font-family: var(--font-sans);
  font-size: 0.74rem;
  font-weight: 800;
  vertical-align: middle;
}

.code-walk__notes {
  margin: 0;
  padding: 1rem 1.4rem 1.2rem;
  border-top: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.02);
  counter-reset: cw;
  list-style: none;
}

.code-walk__notes li {
  position: relative;
  margin: 0.7rem 0;
  padding-left: 2rem;
  color: var(--text-soft);
}

.code-walk__notes li::before {
  counter-increment: cw;
  content: counter(cw);
  position: absolute;
  left: 0;
  top: 0.15rem;
  width: 1.4rem;
  height: 1.4rem;
  display: grid;
  place-items: center;
  border-radius: 999px;
  background: rgba(122, 167, 240, 0.16);
  border: 1px solid rgba(122, 167, 240, 0.4);
  color: var(--primary);
  font-size: 0.78rem;
  font-weight: 800;
}

.code-walk__notes li code {
  font-size: 0.85em;
}

@media (max-width: 720px) {
  .code-walk { border-radius: 10px; }
  .code-walk__code { font-size: 0.78rem; padding: 0.8rem 0.9rem; }
}

/* ============ 交互实验台(lab,data-lab 注入) ============ */
.lab {
  margin: 1.8rem auto;
  max-width: 54rem;
  border: 1px solid rgba(122, 167, 240, 0.22);
  border-radius: 14px;
  background: linear-gradient(160deg, rgba(122, 167, 240, 0.05), rgba(240, 201, 106, 0.03)), #0f1626;
  box-shadow: 0 14px 34px rgba(0, 0, 0, 0.36);
  overflow: hidden;
}

/* 顶部窗口栏 */
.lab__head {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.55rem 1.1rem;
  background: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid rgba(122, 167, 240, 0.18);
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: var(--text-dim);
}
.lab__head-tag {
  color: #f0c96a;
  font-weight: 800;
  letter-spacing: 0.04em;
}
.lab__head-name { opacity: 0.75; }

/* 内部主标题 */
.lab__title {
  padding: 0.95rem 1.2rem 0.4rem;
  font-size: 1.02rem;
  font-weight: 800;
  color: var(--text);
  letter-spacing: 0.01em;
}

/* 滑杆控件 */
.lab__ctl {
  display: grid;
  grid-template-columns: 9rem 5.5rem 1fr;
  align-items: center;
  gap: 0.9rem;
  padding: 0.5rem 1.2rem;
}
.lab__lab {
  font-size: 0.92rem;
  color: var(--text-soft);
}
.lab__val {
  font-family: var(--font-mono);
  font-size: 0.84rem;
  color: #ffd97a;
  text-align: right;
  font-variant-numeric: tabular-nums;
}
.lab__range {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 5px;
  border-radius: 999px;
  background: rgba(122, 167, 240, 0.18);
  outline: none;
}
.lab__range::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 999px;
  background: #f0c96a;
  border: 2.5px solid #101420;
  box-shadow: 0 1px 8px rgba(240, 201, 106, 0.55);
  cursor: pointer;
}
.lab__range::-moz-range-thumb {
  width: 13px;
  height: 13px;
  border-radius: 999px;
  background: #f0c96a;
  border: 2.5px solid #101420;
  box-shadow: 0 1px 8px rgba(240, 201, 106, 0.55);
  cursor: pointer;
}
.lab__range:focus-visible {
  box-shadow: 0 0 0 3px rgba(240, 201, 106, 0.22);
}

/* 图表区 */
.lab__chart {
  display: block;
  width: calc(100% - 2.4rem);
  margin: 0.7rem 1.2rem 0.4rem;
  border-radius: 10px;
  background: rgba(8, 13, 24, 0.72);
  border: 1px solid rgba(122, 167, 240, 0.1);
}

/* 结论行 */
.lab__out {
  padding: 0.4rem 1.2rem 0.2rem;
}
.lab__row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 1rem;
  padding: 0.3rem 0;
  font-size: 0.94rem;
  color: var(--text-soft);
  border-top: 1px dashed rgba(160, 180, 215, 0.14);
}
.lab__row:first-child { border-top: none; }
.lab__row strong {
  font-family: var(--font-mono);
  font-size: 0.9rem;
  color: #ffd97a;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
.lab__row strong.lab__accent { color: #7aa7f0; font-weight: 800; }
.lab__hint {
  font-size: 0.84rem;
  color: var(--text-dim);
}

/* 教师注 */
.lab__tip {
  margin: 0.7rem 1.2rem 1.1rem;
  padding: 0.65rem 0.95rem;
  border-left: 3px solid rgba(240, 201, 106, 0.5);
  border-radius: 0 8px 8px 0;
  background: rgba(240, 201, 106, 0.055);
  font-size: 0.86rem;
  color: var(--text-dim);
  line-height: 1.7;
}

@media (max-width: 720px) {
  .lab { border-radius: 11px; margin-left: -0.4rem; margin-right: -0.4rem; }
  .lab__ctl { grid-template-columns: 1fr auto; row-gap: 0.1rem; }
  .lab__lab { grid-column: 1; }
  .lab__val { grid-column: 2; }
  .lab__range { grid-column: 1 / -1; height: 7px; }
  .lab__chart { width: calc(100% - 1.4rem); margin: 0.6rem 0.7rem 0.3rem; }
}
"""


JS_TEMPLATE = r"""
(function () {
  "use strict";
  var CHAPTERS = [
    __CHAPTERS__
  ];
  var BOOK_TITLE = "__BOOK_TITLE__";
  var STORAGE_LAST = "financebook:last";
  var sectionNavigate = null;
  var HEADING_ANCHOR_RATIO = 0.28;

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text != null) node.textContent = text;
    return node;
  }
  function chapterIndex() {
    var value = document.body.getAttribute("data-chapter");
    if (value == null) return -1;
    var n = Number(value);
    return isNaN(n) ? -1 : n;
  }
  function pageBaseName() {
    var p = location.pathname || "";
    var i = p.lastIndexOf("/");
    return i >= 0 ? p.slice(i + 1) : p;
  }
  function slugify(text, index) {
    var base = String(text || "")
      .trim()
      .toLowerCase()
      .replace(/[：:]/g, " ")
      .replace(/\s+/g, "-")
      .replace(/[^\w\u4e00-\u9fff-]/g, "");
    return base || "section-" + index;
  }
  function scrollRailToCurrent(scroller, link) {
    if (!scroller || !link) return;
    var target = link.offsetTop - scroller.clientHeight / 2 + link.offsetHeight / 2;
    scroller.scrollTop = Math.max(0, target);
  }
  function scheduleRailToCurrent(scroller, link) {
    if (!scroller || !link) return;
    function run() { scrollRailToCurrent(scroller, link); }
    requestAnimationFrame(run);
    setTimeout(run, 80);
    setTimeout(run, 240);
    if (document.readyState !== "complete") {
      window.addEventListener("load", run, { once: true });
    }
  }
  function assignHeadingIds(inner) {
    var headings = [].slice.call(inner.querySelectorAll("h2, h3"));
    var usedIds = {};
    var entries = [];
    headings.forEach(function (heading, index) {
      if (heading.closest(".quiz")) return;
      var text = heading.textContent.replace(/\s+/g, " ").trim();
      if (!text) return;
      var id = slugify(text, index);
      while (usedIds[id]) id = id + "-" + index;
      usedIds[id] = true;
      heading.id = id;
      entries.push({ heading: heading, id: id, text: text });
    });
    return entries;
  }
  function buildChapterRail(currentIdx) {
    var aside = el("aside", "book-rail book-rail--chapters");
    aside.setAttribute("aria-label", "章节导航");
    aside.appendChild(el("div", "book-rail__title", "章节"));
    var list = el("ol", "book-rail__list");
    var lastPart = "";
    CHAPTERS.forEach(function (ch, i) {
      if (ch.part !== lastPart) {
        lastPart = ch.part;
        list.appendChild(el("li", "book-rail__part", ch.part));
      }
      var li = el("li");
      var a = el("a", "book-rail__link" + (i === currentIdx ? " is-current" : ""));
      a.href = ch.file;
      a.appendChild(el("span", "book-rail__num", String(ch.num)));
      a.appendChild(el("span", "book-rail__name", ch.title));
      if (i === currentIdx) aside._currentLink = a;
      li.appendChild(a);
      list.appendChild(li);
    });
    list.appendChild(el("li", "book-rail__part", "附录"));
    var gli = el("li");
    var ga = el("a", "book-rail__link" + (/glossary\.html$/.test(pageBaseName()) ? " is-current" : ""));
    ga.href = "glossary.html";
    ga.appendChild(el("span", "book-rail__num", "附"));
    ga.appendChild(el("span", "book-rail__name", "术语表与参考资料"));
    gli.appendChild(ga);
    list.appendChild(gli);
    aside.appendChild(list);
    return aside;
  }
  function buildOutlineRail(inner) {
    var aside = el("aside", "book-rail book-rail--outline");
    aside.setAttribute("aria-label", "本章目录");
    aside.appendChild(el("div", "book-rail__title", "本章"));
    var list = el("ol", "book-rail__list book-rail__list--outline");
    var links = [];
    assignHeadingIds(inner).forEach(function (entry) {
      var li = el("li", entry.heading.tagName === "H3" ? "book-rail__outline-item book-rail__outline-item--sub" : "book-rail__outline-item");
      var a = el("a", "book-rail__outline-link");
      a.href = "#" + entry.id;
      a.textContent = entry.text;
      li.appendChild(a);
      list.appendChild(li);
      links.push({ link: a, heading: entry.heading });
    });
    if (!links.length) {
      aside.appendChild(el("p", "book-rail__empty", "本章暂无小节"));
      return { aside: aside, links: [] };
    }
    aside.appendChild(list);
    return { aside: aside, links: links };
  }
  function scrollHeadingIntoView(target, smooth) {
    if (!target) return;
    var y = target.getBoundingClientRect().top + window.pageYOffset - window.innerHeight * HEADING_ANCHOR_RATIO;
    y = Math.max(0, y);
    if (smooth) window.scrollTo({ top: y, behavior: "smooth" });
    else window.scrollTo(0, y);
  }
  function findSectionHeading(node) {
    var inner = document.querySelector(".chapter__inner");
    if (!inner || !node || !inner.contains(node)) return null;
    var headings = [].slice.call(inner.querySelectorAll("h2, h3")).filter(function (h) {
      return !h.closest(".quiz");
    });
    if (!headings.length) return null;
    for (var i = headings.length - 1; i >= 0; i--) {
      if (headings[i].compareDocumentPosition(node) & Node.DOCUMENT_POSITION_FOLLOWING) {
        return headings[i];
      }
    }
    return headings[0];
  }
  function isSectionHeading(elm) {
    if (!elm || !elm.tagName) return false;
    var tag = elm.tagName.toUpperCase();
    return tag === "H2" || tag === "H3";
  }
  function scrollToSectionTarget(target, smooth) {
    if (!target) return;
    var heading = isSectionHeading(target) ? target : findSectionHeading(target);
    if (heading && sectionNavigate) {
      sectionNavigate(heading, smooth);
      return;
    }
    scrollHeadingIntoView(target, smooth);
  }
  function setupOutlineSpy(links) {
    if (!links.length) return;
    var current = null;
    var lockUntil = 0;
    function setCurrent(link) {
      if (current === link) return;
      if (current) current.classList.remove("is-current");
      current = link;
      if (current) {
        current.classList.add("is-current");
        scrollRailToCurrent(current.closest(".book-rail"), current);
      }
    }
    function navigateToSection(heading, smooth) {
      if (!heading) return;
      var item = null;
      for (var i = 0; i < links.length; i++) {
        if (links[i].heading === heading) {
          item = links[i];
          break;
        }
      }
      if (smooth) lockUntil = Date.now() + 900;
      if (item) setCurrent(item.link);
      scrollHeadingIntoView(heading, smooth);
    }
    sectionNavigate = navigateToSection;
    links.forEach(function (item) {
      item.link.addEventListener("click", function (e) {
        e.preventDefault();
        navigateToSection(item.heading, true);
        if (window.history && window.history.replaceState) {
          window.history.replaceState(null, "", "#" + item.heading.id);
        }
      });
    });
    if ("IntersectionObserver" in window) {
      var obs = new IntersectionObserver(function (entries) {
        if (Date.now() < lockUntil) return;
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          links.forEach(function (item) {
            if (item.heading === entry.target) setCurrent(item.link);
          });
        });
      }, { rootMargin: "-28% 0px -72% 0px", threshold: 0 });
      links.forEach(function (item) { obs.observe(item.heading); });
    }
    setCurrent(links[0].link);
  }
  function syncFixedRails(layout, leftRail, rightRail) {
    if (!layout || !leftRail || !rightRail) return;
    function resetRails() {
      leftRail.classList.remove("is-fixed");
      rightRail.classList.remove("is-fixed");
      leftRail.style.left = "";
      rightRail.style.left = "";
      leftRail.style.width = "";
      rightRail.style.width = "";
    }
    function apply() {
      var desktop = window.matchMedia("(min-width: 1180px)").matches;
      if (!desktop) {
        resetRails();
        return;
      }
      resetRails();
      var rect = layout.getBoundingClientRect();
      var cs = getComputedStyle(layout);
      var cols = cs.gridTemplateColumns.split(" ").map(function (v) { return parseFloat(v) || 0; });
      var gap = parseFloat(cs.columnGap || cs.gap) || 0;
      var leftWidth = cols[0] || leftRail.getBoundingClientRect().width;
      var rightWidth = cols[2] || rightRail.getBoundingClientRect().width;
      leftRail.style.left = Math.round(rect.left) + "px";
      leftRail.style.width = Math.round(leftWidth) + "px";
      rightRail.style.left = Math.round(rect.right - rightWidth) + "px";
      rightRail.style.width = Math.round(rightWidth) + "px";
      leftRail.classList.add("is-fixed");
      rightRail.classList.add("is-fixed");
    }
    requestAnimationFrame(apply);
    setTimeout(apply, 80);
    window.addEventListener("resize", function () {
      resetRails();
      requestAnimationFrame(apply);
      setTimeout(apply, 120);
    });
  }
  function buildDesktopLayout(currentIdx) {
    var chapter = document.querySelector(".chapter");
    var inner = chapter && chapter.querySelector(".chapter__inner");
    if (!chapter || !inner) return;
    var layout = el("div", "book-layout");
    var main = el("div", "book-layout__main");
    var chapterRail = buildChapterRail(currentIdx);
    var outline = buildOutlineRail(inner);
    layout.appendChild(chapterRail);
    layout.appendChild(main);
    layout.appendChild(outline.aside);
    chapter.insertBefore(layout, inner);
    main.appendChild(inner);
    setupOutlineSpy(outline.links);
    syncFixedRails(layout, chapterRail, outline.aside);
    scheduleRailToCurrent(chapterRail, chapterRail._currentLink);
    window.addEventListener("resize", function () {
      scheduleRailToCurrent(chapterRail, chapterRail._currentLink);
    });
    requestAnimationFrame(function () {
      if (location.hash) {
        var target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
        if (target) scrollToSectionTarget(target, false);
      }
    });
  }
  function storeSet(k, v) {
    try { localStorage.setItem(k, v); } catch (e) {}
  }
  function storeGet(k) {
    try { return localStorage.getItem(k); } catch (e) { return null; }
  }
  function buildHeader(idx) {
    var header = el("header", "book-header");
    var menu = el("button", "book-header__menu", "☰");
    menu.type = "button";
    menu.setAttribute("aria-label", "打开目录");
    var home = el("a", "book-header__home", BOOK_TITLE);
    home.href = "index.html";
    var current = el("div", "book-header__current", idx >= 0 ? ("第 " + idx + " 章 · " + CHAPTERS[idx].title) : "目录");
    header.appendChild(menu);
    header.appendChild(home);
    header.appendChild(current);
    document.body.prepend(header);

    var progress = el("div", "book-progress");
    document.body.appendChild(progress);
    function onScroll() {
      var max = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
      progress.style.width = Math.max(0, Math.min(100, window.scrollY / max * 100)) + "%";
    }
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    return menu;
  }
  function buildDrawer(idx, button) {
    var backdrop = el("div", "book-toc-backdrop");
    var drawer = el("nav", "book-toc");
    drawer.setAttribute("aria-label", "全书目录");
    drawer.appendChild(el("p", "book-toc__title", "全书目录"));
    var lastPart = "";
    CHAPTERS.forEach(function (ch, i) {
      if (ch.part !== lastPart) {
        lastPart = ch.part;
        drawer.appendChild(el("div", "book-toc__part", ch.part));
      }
      var a = el("a", "book-toc__link" + (i === idx ? " is-current" : ""));
      a.href = ch.file;
      a.innerHTML = "<span>第 " + ch.num + " 章</span><span>" + ch.title + "</span>";
      if (i === idx) drawer._currentLink = a;
      drawer.appendChild(a);
    });
    var glossary = el("a", "book-toc__link");
    glossary.href = "glossary.html";
    glossary.innerHTML = "<span>附录</span><span>术语表与参考资料</span>";
    if (/glossary\.html$/.test(pageBaseName())) drawer._currentLink = glossary;
    drawer.appendChild(glossary);
    document.body.appendChild(backdrop);
    document.body.appendChild(drawer);
    function open() {
      backdrop.classList.add("is-open");
      drawer.classList.add("is-open");
      scheduleRailToCurrent(drawer, drawer._currentLink);
    }
    function close() {
      backdrop.classList.remove("is-open");
      drawer.classList.remove("is-open");
    }
    button.addEventListener("click", open);
    backdrop.addEventListener("click", close);
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") close();
    });
  }
  function isKeyboardBlockedTarget(target) {
    if (!target) return false;
    if (/^(INPUT|SELECT|TEXTAREA)$/.test(target.tagName)) return true;
    return Boolean(target.isContentEditable);
  }
  function goPrevChapter(idx) {
    if (idx > 0) location.href = CHAPTERS[idx - 1].file;
    else if (idx === 0) location.href = "index.html";
    else if (/glossary\.html$/i.test(pageBaseName())) location.href = CHAPTERS[CHAPTERS.length - 1].file;
  }
  function goNextChapter(idx) {
    if (idx >= 0 && idx < CHAPTERS.length - 1) location.href = CHAPTERS[idx + 1].file;
    else if (document.body.hasAttribute("data-cover")) location.href = CHAPTERS[0].file;
    else if (/glossary\.html$/i.test(pageBaseName())) location.href = "index.html";
  }
  function setupVimNavigation(idx) {
    document.addEventListener("keydown", function (e) {
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      if (isKeyboardBlockedTarget(e.target)) return;
      var key = e.key;
      var step = Math.round(window.innerHeight * 0.72);
      if (key === "h" || key === "ArrowLeft") {
        if (key === "h") e.preventDefault();
        goPrevChapter(idx);
      } else if (key === "l" || key === "ArrowRight") {
        if (key === "l") e.preventDefault();
        goNextChapter(idx);
      } else if (key === "j") {
        e.preventDefault();
        window.scrollBy({ top: step, behavior: "smooth" });
      } else if (key === "k") {
        e.preventDefault();
        window.scrollBy({ top: -step, behavior: "smooth" });
      }
    });
  }
  function addChapterNav(idx) {
    if (idx < 0) return;
    storeSet(STORAGE_LAST, CHAPTERS[idx].file);
    var nav = el("nav", "chapter-nav");
    if (CHAPTERS[idx - 1]) {
      var prev = el("a", "", "← 第 " + CHAPTERS[idx - 1].num + " 章 · " + CHAPTERS[idx - 1].title);
      prev.href = CHAPTERS[idx - 1].file;
      nav.appendChild(prev);
    } else {
      nav.appendChild(el("span", ""));
    }
    if (CHAPTERS[idx + 1]) {
      var next = el("a", "", "第 " + CHAPTERS[idx + 1].num + " 章 · " + CHAPTERS[idx + 1].title + " →");
      next.href = CHAPTERS[idx + 1].file;
      nav.appendChild(next);
    } else {
      var glossary = el("a", "", "术语表与参考资料 →");
      glossary.href = "glossary.html";
      nav.appendChild(glossary);
    }
    var host = document.querySelector(".book-layout__main") || document.querySelector("main");
    host.appendChild(nav);
  }
  function reveal() {
    var nodes = [].slice.call(document.querySelectorAll(".reveal"));
    if (!("IntersectionObserver" in window)) {
      nodes.forEach(function (n) { n.classList.add("is-visible"); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    nodes.forEach(function (n) { io.observe(n); });
  }
  function continueLink() {
    var a = document.querySelector("[data-continue]");
    if (!a) return;
    var last = storeGet(STORAGE_LAST);
    var exists = CHAPTERS.some(function (ch) { return ch.file === last; });
    if (last && exists && last !== CHAPTERS[0].file) {
      a.href = last;
      a.textContent = "继续阅读";
    } else {
      a.href = CHAPTERS[0].file;
      a.textContent = "开始阅读";
      if (last && !exists) storeSet(STORAGE_LAST, CHAPTERS[0].file);
    }
  }
  var idx = chapterIndex();
  var menu = buildHeader(idx);
  buildDrawer(idx, menu);
  buildDesktopLayout(idx);
  addChapterNav(idx);
  setupVimNavigation(idx);
  continueLink();
  reveal();
})();
"""


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    write_assets()
    for old in ROOT.glob("chapter-*.html"):
        old.unlink()
    (ROOT / "index.html").write_text(render_index(), encoding="utf-8")
    for ch in CHAPTERS:
        (ROOT / chapter_file(ch["num"])).write_text(render_chapter(ch), encoding="utf-8")
    (ROOT / "glossary.html").write_text(render_glossary(), encoding="utf-8")
    print(f"built {len(CHAPTERS)} chapters in {ROOT}")


if __name__ == "__main__":
    main()
