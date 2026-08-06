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


def svg_text(text: str, x: int, y: int, width: int, *, size: int = 17, color: str = "#f6f0df",
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
    body = """            <text x="450" y="34" text-anchor="middle" fill="#f6f0df" font-size="19" font-weight="800">多印鱼票,鱼没变多:每张票能换到的鱼变少</text>
            <!-- 左:发票前 -->
            <text x="230" y="74" text-anchor="middle" fill="#69b3a2" font-size="16" font-weight="800">发票前</text>
            <text x="230" y="98" text-anchor="middle" fill="#c9d4e8" font-size="13">仓库 100 条鱼 · 流通 100 张票</text>
            <g fill="#f0c96a"><circle cx="150" cy="150" r="13"/><circle cx="190" cy="150" r="13"/><circle cx="230" cy="150" r="13"/><circle cx="270" cy="150" r="13"/><circle cx="310" cy="150" r="13"/></g>
            <text x="230" y="196" text-anchor="middle" fill="#8ef0d1" font-size="17" font-weight="800">1 张票 → 1 条鱼</text>
            <!-- 右:多印一倍票 -->
            <text x="670" y="74" text-anchor="middle" fill="#e88" font-size="16" font-weight="800">多印一倍票后</text>
            <text x="670" y="98" text-anchor="middle" fill="#c9d4e8" font-size="13">仓库仍 100 条鱼 · 流通 200 张票</text>
            <g fill="#f0c96a"><circle cx="590" cy="150" r="13"/><circle cx="630" cy="150" r="13"/><circle cx="670" cy="150" r="13"/><circle cx="710" cy="150" r="13"/><circle cx="750" cy="150" r="13"/></g>
            <text x="670" y="196" text-anchor="middle" fill="#ffb4b4" font-size="17" font-weight="800">2 张票 → 1 条鱼</text>
            <line x1="450" y1="60" x2="450" y2="210" stroke="#46587a" stroke-width="1.5" stroke-dasharray="6 6"/>
            <text x="450" y="246" text-anchor="middle" fill="#f6f0df" font-size="15">票变多,鱼没变多 → 同一条鱼要更多票 → 这就是通胀:购买力下降</text>"""
    return concept_figure(body, "0 0 900 270",
        "通胀示意:鱼票翻倍但鱼不变,每张票能换的鱼减半",
        "鱼票从 100 张翻到 200 张,仓库还是 100 条鱼,于是换一条鱼需要的票翻倍。通胀不是某样东西偶尔涨价,而是整体购买力下降。")


def _fig_bank_balance():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#f6f0df" font-size="19" font-weight="800">银行资产负债表:钱不是躺在保险柜里</text>
            <!-- 资产侧 -->
            <rect x="70" y="70" width="330" height="200" rx="14" fill="rgba(105,179,162,0.10)" stroke="#69b3a2" stroke-width="2"/>
            <text x="235" y="98" text-anchor="middle" fill="#8ef0d1" font-size="16" font-weight="800">资产(钱用到哪去了)</text>
            <rect x="92" y="116" width="286" height="52" rx="8" fill="rgba(105,179,162,0.18)"/>
            <text x="104" y="148" fill="#eef4ff" font-size="15">发放的贷款(最大一块,不在柜里)</text>
            <rect x="92" y="176" width="286" height="34" rx="8" fill="rgba(105,179,162,0.14)"/>
            <text x="104" y="198" fill="#eef4ff" font-size="14">债券等投资</text>
            <rect x="92" y="218" width="286" height="34" rx="8" fill="rgba(105,179,162,0.14)"/>
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
    body = """            <text x="450" y="34" text-anchor="middle" fill="#f6f0df" font-size="19" font-weight="800">挤兑:为什么信心一崩,好银行也会倒</text>
            <text x="230" y="72" text-anchor="middle" fill="#8ef0d1" font-size="16" font-weight="800">正常时</text>
            <rect x="120" y="90" width="220" height="120" rx="12" fill="rgba(105,179,162,0.12)" stroke="#69b3a2" stroke-width="2"/>
            <text x="230" y="120" text-anchor="middle" fill="#eef4ff" font-size="14">少数人来取钱</text>
            <text x="230" y="150" text-anchor="middle" fill="#eef4ff" font-size="14">准备金够付</text>
            <text x="230" y="184" text-anchor="middle" fill="#8ef0d1" font-size="15" font-weight="800">银行照常运转</text>
            <text x="670" y="72" text-anchor="middle" fill="#ffb4b4" font-size="16" font-weight="800">恐慌时</text>
            <rect x="560" y="90" width="220" height="120" rx="12" fill="rgba(232,120,120,0.12)" stroke="#e88" stroke-width="2"/>
            <text x="670" y="118" text-anchor="middle" fill="#eef4ff" font-size="14">所有人同时来取钱</text>
            <text x="670" y="146" text-anchor="middle" fill="#eef4ff" font-size="14">贷款一时收不回</text>
            <text x="670" y="180" text-anchor="middle" fill="#ffb4b4" font-size="15" font-weight="800">准备金瞬间见底</text>
            <path d="M 355 150 L 545 150" fill="none" stroke="#f0c96a" stroke-width="2.5" marker-end="url(#runarrow)"/>
            <defs><marker id="runarrow" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#f0c96a"/></marker></defs>
            <text x="450" y="140" text-anchor="middle" fill="#c9d4e8" font-size="13">信心消失</text>
            <text x="450" y="250" text-anchor="middle" fill="#f6f0df" font-size="15">部分准备金制度下,银行本就没留够全额现金;挤兑是信心问题,不只是资产问题</text>"""
    return concept_figure(body, "0 0 900 275",
        "挤兑示意:正常时准备金够付,所有人同时取钱时准备金瞬间见底",
        "银行只留部分准备金,平时够用;一旦所有人同时来取,贷款收不回、准备金见底,连经营正常的银行也可能倒下。这就是存款保险和央行存在的原因之一。")


def _fig_bond_cashflow():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#f6f0df" font-size="19" font-weight="800">一张 3 年期债券的现金流(面值 100,票息 5%)</text>
            <line x1="70" y1="180" x2="830" y2="180" stroke="#46587a" stroke-width="2" marker-end="url(#tarrow)"/>
            <defs><marker id="tarrow" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#46587a"/></marker></defs>
            <text x="828" y="205" text-anchor="end" fill="#8499bd" font-size="13">时间</text>
            <!-- 买入:现金流出 -->
            <line x1="130" y1="180" x2="130" y2="250" stroke="#e88" stroke-width="3"/>
            <path d="M 130 250 L 124 238 M 130 250 L 136 238" stroke="#e88" stroke-width="3" fill="none"/>
            <text x="130" y="272" text-anchor="middle" fill="#ffb4b4" font-size="14" font-weight="800">-100</text>
            <text x="130" y="150" text-anchor="middle" fill="#c9d4e8" font-size="13">买入</text>
            <!-- 每年票息:现金流入 -->
            <line x1="320" y1="180" x2="320" y2="130" stroke="#8ef0d1" stroke-width="3"/>
            <path d="M 320 130 L 314 142 M 320 130 L 326 142" stroke="#8ef0d1" stroke-width="3" fill="none"/>
            <text x="320" y="118" text-anchor="middle" fill="#8ef0d1" font-size="14" font-weight="800">+5</text>
            <text x="320" y="205" text-anchor="middle" fill="#8499bd" font-size="13">第1年</text>
            <line x1="510" y1="180" x2="510" y2="130" stroke="#8ef0d1" stroke-width="3"/>
            <path d="M 510 130 L 504 142 M 510 130 L 516 142" stroke="#8ef0d1" stroke-width="3" fill="none"/>
            <text x="510" y="118" text-anchor="middle" fill="#8ef0d1" font-size="14" font-weight="800">+5</text>
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
    body = """            <text x="450" y="30" text-anchor="middle" fill="#f6f0df" font-size="19" font-weight="800">期权到期收益:亏损有底,盈利放大</text>
            <!-- 看涨期权 -->
            <text x="230" y="60" text-anchor="middle" fill="#8ef0d1" font-size="16" font-weight="800">买入看涨期权</text>
            <line x1="80" y1="240" x2="400" y2="240" stroke="#46587a" stroke-width="1.5"/>
            <line x1="240" y1="90" x2="240" y2="250" stroke="#46587a" stroke-width="1.5"/>
            <text x="398" y="262" text-anchor="end" fill="#8499bd" font-size="12">到期股价</text>
            <text x="150" y="256" text-anchor="middle" fill="#8499bd" font-size="12">行权价 K</text>
            <path d="M 100 210 L 240 210 L 380 110" fill="none" stroke="#8ef0d1" stroke-width="3"/>
            <line x1="100" y1="210" x2="240" y2="210" stroke="#ffb4b4" stroke-width="3"/>
            <text x="150" y="200" text-anchor="middle" fill="#ffb4b4" font-size="12">亏损=权利金(有底)</text>
            <text x="350" y="98" text-anchor="middle" fill="#8ef0d1" font-size="12">涨越多赚越多</text>
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
    body = """            <text x="450" y="30" text-anchor="middle" fill="#f6f0df" font-size="19" font-weight="800">同样终点,体验完全不同:回撤决定能不能拿得住</text>
            <line x1="70" y1="250" x2="850" y2="250" stroke="#46587a" stroke-width="1.5"/>
            <line x1="70" y1="60" x2="70" y2="250" stroke="#46587a" stroke-width="1.5"/>
            <text x="848" y="272" text-anchor="end" fill="#8499bd" font-size="13">时间</text>
            <text x="52" y="70" fill="#8499bd" font-size="13">净值</text>
            <!-- 平稳曲线 A -->
            <path d="M 70 230 Q 300 190 500 150 T 830 90" fill="none" stroke="#8ef0d1" stroke-width="3"/>
            <text x="700" y="110" fill="#8ef0d1" font-size="14" font-weight="800">A:平稳上行(夏普高)</text>
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
    body = """            <text x="450" y="30" text-anchor="middle" fill="#f6f0df" font-size="19" font-weight="800">分层回测:把股票按因子值分成5组,看收益是否单调</text>
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
            <rect x="710" y="90" width="90" height="160" fill="#8ef0d1" opacity="0.9"/>
            <text x="755" y="270" text-anchor="middle" fill="#8499bd" font-size="12">第5组(因子最高)</text>
            <path d="M 195 195 L 335 170 L 475 145 L 615 115 L 755 85" fill="none" stroke="#f6f0df" stroke-width="2" stroke-dasharray="6 5"/>
            <text x="600" y="70" fill="#eef4ff" font-size="13">收益随分组单调上升 → 因子可能有效</text>"""
    return concept_figure(body, "0 0 900 290",
        "因子分层回测柱状图:按因子值把股票分成5组,从第1组到第5组未来收益单调递增",
        "把股票按因子值排序、平均分成几组,再看每组之后的平均收益。如果从低到高单调递增(或递减),说明这个因子可能真的携带信息,而不是随机噪声。")


def _fig_lookahead():
    body = """            <text x="450" y="30" text-anchor="middle" fill="#f6f0df" font-size="19" font-weight="800">回测最致命的错:偷看了未来</text>
            <line x1="70" y1="150" x2="830" y2="150" stroke="#46587a" stroke-width="2" marker-end="url(#la)"/>
            <defs><marker id="la" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#46587a"/></marker></defs>
            <line x1="450" y1="80" x2="450" y2="220" stroke="#f0c96a" stroke-width="2" stroke-dasharray="6 5"/>
            <text x="450" y="70" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">决策时点(此刻)</text>
            <rect x="110" y="112" width="320" height="40" rx="8" fill="rgba(105,179,162,0.2)" stroke="#69b3a2"/>
            <text x="270" y="138" text-anchor="middle" fill="#8ef0d1" font-size="14" font-weight="800">已知:历史数据(能用)</text>
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
    body = """            <text x="450" y="32" text-anchor="middle" fill="#f6f0df" font-size="19" font-weight="800">钱和风险怎么在金融系统里流动</text>
            <!-- 左:资金盈余方 -->
            <rect x="40" y="90" width="170" height="130" rx="14" fill="rgba(105,179,162,0.12)" stroke="#69b3a2" stroke-width="2"/>
            <text x="125" y="128" text-anchor="middle" fill="#8ef0d1" font-size="15" font-weight="800">有钱的人</text>
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
            <rect x="690" y="90" width="170" height="130" rx="14" fill="rgba(105,179,162,0.12)" stroke="#69b3a2" stroke-width="2"/>
            <text x="775" y="128" text-anchor="middle" fill="#8ef0d1" font-size="15" font-weight="800">缺钱的人</text>
            <text x="775" y="156" text-anchor="middle" fill="#c9d4e8" font-size="13">企业、政府</text>
            <text x="775" y="182" text-anchor="middle" fill="#c9d4e8" font-size="13">想融资办事</text>
            <!-- 箭头:资金右流,收益权左流 -->
            <path d="M 214 130 L 326 130" fill="none" stroke="#8ef0d1" stroke-width="3" marker-end="url(#mfa)"/>
            <text x="270" y="120" text-anchor="middle" fill="#8ef0d1" font-size="12">资金</text>
            <path d="M 570 130 L 686 130" fill="none" stroke="#8ef0d1" stroke-width="3" marker-end="url(#mfa)"/>
            <text x="628" y="120" text-anchor="middle" fill="#8ef0d1" font-size="12">资金</text>
            <path d="M 686 200 L 570 200" fill="none" stroke="#f0c96a" stroke-width="3" marker-end="url(#mfb)"/>
            <path d="M 326 200 L 214 200" fill="none" stroke="#f0c96a" stroke-width="3" marker-end="url(#mfb)"/>
            <text x="450" y="272" text-anchor="middle" fill="#c9d4e8" font-size="13">钱从盈余方流向需求方;股权、债权和利息等\u201c收益和风险\u201d反向流回</text>
            <defs>
              <marker id="mfa" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#8ef0d1"/></marker>
              <marker id="mfb" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#f0c96a"/></marker>
            </defs>"""
    return concept_figure(body, "0 0 900 290",
        "金融系统资金流示意:资金从盈余方经中介流向需求方,收益和风险反向流回",
        "金融系统的核心就是这张图:把有钱但暂时不用的人,和缺钱但能创造价值的人对接起来。中间的银行、券商、基金、交易所负责撮合、定价、托管和分配风险。")


def _fig_stock_ownership():
    body = """            <text x="450" y="32" text-anchor="middle" fill="#f6f0df" font-size="19" font-weight="800">买一股,就是把公司切成很多份、你拿其中一份</text>
            <!-- 公司大饼 -->
            <circle cx="230" cy="160" r="95" fill="rgba(18,29,49,0.6)" stroke="#f0c96a" stroke-width="2"/>
            <path d="M 230 160 L 230 65 A 95 95 0 0 1 315 200 Z" fill="rgba(240,201,106,0.28)" stroke="#f0c96a"/>
            <path d="M 230 160 L 315 200 A 95 95 0 0 1 175 249 Z" fill="rgba(105,179,162,0.22)" stroke="#69b3a2"/>
            <path d="M 230 160 L 175 249 A 95 95 0 0 1 149 100 Z" fill="rgba(105,179,162,0.14)" stroke="#69b3a2"/>
            <path d="M 230 160 L 149 100 A 95 95 0 0 1 230 65 Z" fill="rgba(105,179,162,0.14)" stroke="#69b3a2"/>
            <text x="230" y="285" text-anchor="middle" fill="#c9d4e8" font-size="13">一家公司 = 总股本</text>
            <text x="272" y="130" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">你的1股</text>
            <!-- 右:你这一份意味着什么 -->
            <text x="600" y="86" text-anchor="middle" fill="#8ef0d1" font-size="15" font-weight="800">持有这一份,你就有</text>
            <rect x="440" y="104" width="410" height="40" rx="8" fill="rgba(105,179,162,0.12)"/>
            <text x="460" y="130" fill="#eef4ff" font-size="14">· 分红权:公司赚钱后按份额分你一部分</text>
            <rect x="440" y="152" width="410" height="40" rx="8" fill="rgba(105,179,162,0.12)"/>
            <text x="460" y="178" fill="#eef4ff" font-size="14">· 投票权:重大事项按份额投票</text>
            <rect x="440" y="200" width="410" height="40" rx="8" fill="rgba(105,179,162,0.12)"/>
            <text x="460" y="226" fill="#eef4ff" font-size="14">· 剩余索取权:还完债、剩下的才归股东</text>
            <text x="645" y="270" text-anchor="middle" fill="#ffb4b4" font-size="13">上不封顶,但也可能归零</text>"""
    return concept_figure(body, "0 0 900 300",
        "股票所有权示意:公司被切成很多股,持有一股即拥有对应比例的分红权、投票权和剩余索取权",
        "买股票不是买一个会涨的数字,而是买下公司的一小片所有权。公司做大,你这一份跟着变值钱;公司倒了,你排在债主后面,可能血本无归。")


def _fig_orderbook():
    body = """            <text x="450" y="32" text-anchor="middle" fill="#f6f0df" font-size="19" font-weight="800">订单簿:买卖双方在这里排队,价格优先、时间优先</text>
            <!-- 卖盘(上,红) -->
            <text x="250" y="70" text-anchor="middle" fill="#ffb4b4" font-size="14" font-weight="800">卖盘(想卖的人)</text>
            <rect x="150" y="80" width="200" height="26" rx="4" fill="rgba(232,120,120,0.28)"/><text x="160" y="99" fill="#eef4ff" font-size="13">卖三  10.03  ×  800</text>
            <rect x="150" y="110" width="200" height="26" rx="4" fill="rgba(232,120,120,0.22)"/><text x="160" y="129" fill="#eef4ff" font-size="13">卖二  10.02  ×  500</text>
            <rect x="150" y="140" width="200" height="26" rx="4" fill="rgba(232,120,120,0.16)"/><text x="160" y="159" fill="#eef4ff" font-size="13">卖一  10.01  ×  300</text>
            <!-- 价差 -->
            <line x1="150" y1="176" x2="350" y2="176" stroke="#f0c96a" stroke-width="1.5" stroke-dasharray="5 4"/>
            <text x="370" y="181" fill="#f0c96a" font-size="12">← 买一卖一之间是价差</text>
            <!-- 买盘(下,绿) -->
            <rect x="150" y="186" width="200" height="26" rx="4" fill="rgba(105,179,162,0.16)"/><text x="160" y="205" fill="#eef4ff" font-size="13">买一  10.00  ×  400</text>
            <rect x="150" y="216" width="200" height="26" rx="4" fill="rgba(105,179,162,0.22)"/><text x="160" y="235" fill="#eef4ff" font-size="13">买二   9.99  ×  600</text>
            <rect x="150" y="246" width="200" height="26" rx="4" fill="rgba(105,179,162,0.28)"/><text x="160" y="265" fill="#eef4ff" font-size="13">买三   9.98  ×  900</text>
            <text x="250" y="292" text-anchor="middle" fill="#8ef0d1" font-size="14" font-weight="800">买盘(想买的人)</text>
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
    body = """            <text x="450" y="32" text-anchor="middle" fill="#f6f0df" font-size="19" font-weight="800">一根 K 线,记录一段时间里的四个价格</text>
            <!-- 阳线 -->
            <text x="250" y="76" text-anchor="middle" fill="#8ef0d1" font-size="15" font-weight="800">阳线(收盘 &gt; 开盘)</text>
            <line x1="250" y1="96" x2="250" y2="130" stroke="#8ef0d1" stroke-width="2"/>
            <line x1="250" y1="230" x2="250" y2="262" stroke="#8ef0d1" stroke-width="2"/>
            <rect x="222" y="130" width="56" height="100" rx="3" fill="rgba(105,179,162,0.30)" stroke="#8ef0d1" stroke-width="2"/>
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
    body = """            <text x="450" y="32" text-anchor="middle" fill="#f6f0df" font-size="19" font-weight="800">量化是一条流水线,算法只是其中一环</text>
            <!-- 5 个流程块 -->
            <rect x="30" y="90" width="150" height="90" rx="12" fill="rgba(105,179,162,0.14)" stroke="#69b3a2" stroke-width="2"/>
            <text x="105" y="126" text-anchor="middle" fill="#8ef0d1" font-size="15" font-weight="800">数据</text>
            <text x="105" y="150" text-anchor="middle" fill="#c9d4e8" font-size="12">采集·清洗·对齐</text>
            <rect x="205" y="90" width="150" height="90" rx="12" fill="rgba(105,179,162,0.14)" stroke="#69b3a2" stroke-width="2"/>
            <text x="280" y="126" text-anchor="middle" fill="#8ef0d1" font-size="15" font-weight="800">信号/因子</text>
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
    body = """            <text x="450" y="30" text-anchor="middle" fill="#f6f0df" font-size="19" font-weight="800">指数增强:紧贴指数,再想办法多赚一点点</text>
            <line x1="70" y1="250" x2="850" y2="250" stroke="#46587a" stroke-width="1.5"/>
            <line x1="70" y1="60" x2="70" y2="250" stroke="#46587a" stroke-width="1.5"/>
            <text x="848" y="272" text-anchor="end" fill="#8499bd" font-size="13">时间</text>
            <text x="52" y="70" fill="#8499bd" font-size="13">净值</text>
            <!-- 指数基准线 -->
            <path d="M 70 235 Q 300 195 520 165 T 830 120" fill="none" stroke="#8499bd" stroke-width="2.5" stroke-dasharray="7 5"/>
            <text x="700" y="150" fill="#8499bd" font-size="14" font-weight="800">指数基准</text>
            <!-- 增强线,略高于基准 -->
            <path d="M 70 235 Q 300 182 520 145 T 830 92" fill="none" stroke="#8ef0d1" stroke-width="3"/>
            <text x="600" y="96" fill="#8ef0d1" font-size="14" font-weight="800">指数增强</text>
            <!-- 超额区间标注 -->
            <line x1="830" y1="92" x2="830" y2="120" stroke="#f0c96a" stroke-width="2"/>
            <path d="M 830 92 L 825 102 M 830 92 L 835 102" stroke="#f0c96a" stroke-width="2" fill="none"/>
            <text x="815" y="80" text-anchor="end" fill="#f0c96a" font-size="13">超额收益(Alpha)</text>
            <text x="450" y="292" text-anchor="middle" fill="#c9d4e8" font-size="13">大方向跟着指数走(Beta),再靠选股在上面抠出一层薄薄的超额</text>"""
    return concept_figure(body, "0 0 900 305",
        "指数增强示意:增强曲线贴着指数基准走,并持续高出一小截超额收益",
        "指数增强不追求暴利。它先老老实实跟住指数(拿到市场平均的 Beta),再用量化选股在基准之上多挤出一点超额收益(Alpha)。日积月累,这一点点也很可观。")


def _fig_market_neutral():
    body = """            <text x="450" y="30" text-anchor="middle" fill="#f6f0df" font-size="19" font-weight="800">市场中性:买一篮子、卖空等额,抵掉大盘涨跌</text>
            <!-- 多头柱 -->
            <text x="200" y="76" text-anchor="middle" fill="#8ef0d1" font-size="15" font-weight="800">多头:买入看好的股票</text>
            <rect x="130" y="90" width="140" height="70" rx="6" fill="rgba(105,179,162,0.25)" stroke="#8ef0d1" stroke-width="2"/>
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
            <text x="410" y="222" fill="#8ef0d1" font-size="13.5">· 赚的是\u201c选股能力\u201d,不赌大盘方向</text>
            <text x="410" y="252" fill="#ffb4b4" font-size="12.5">· 但对冲有成本,基差、融券、极端行情仍是风险</text>"""
    return concept_figure(body, "0 0 900 300",
        "市场中性示意:多头买入等额、空头卖空,大盘方向被对冲,只留下选股超额",
        "市场中性用一手买、一手卖空,把\u201c大盘涨不涨\u201d这个最大的不确定性对冲掉,只留下你选股比别人强的那一小块收益。代价是对冲本身要花钱,也有失效的时候。")


def _fig_income_statement():
    body = """            <text x="450" y="30" text-anchor="middle" fill="#f6f0df" font-size="19" font-weight="800">利润表:收入一层层减下去,才剩净利润</text>
            <!-- 漏斗式递减条 -->
            <rect x="250" y="60" width="400" height="40" rx="4" fill="rgba(105,179,162,0.30)" stroke="#8ef0d1"/>
            <text x="450" y="86" text-anchor="middle" fill="#eef4ff" font-size="14" font-weight="800">营业收入(卖东西收到的钱)</text>
            <text x="672" y="86" fill="#8499bd" font-size="12">100</text>
            <rect x="285" y="108" width="330" height="36" rx="4" fill="rgba(105,179,162,0.24)"/>
            <text x="450" y="132" text-anchor="middle" fill="#eef4ff" font-size="13.5">− 成本 → 毛利</text>
            <text x="637" y="131" fill="#8499bd" font-size="12">60</text>
            <rect x="320" y="152" width="260" height="36" rx="4" fill="rgba(105,179,162,0.18)"/>
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
    body = """            <text x="450" y="30" text-anchor="middle" fill="#f6f0df" font-size="19" font-weight="800">量化项目要分层,别塞进一个大 notebook</text>
            <!-- 分层结构 -->
            <rect x="120" y="60" width="660" height="40" rx="8" fill="rgba(105,179,162,0.20)" stroke="#8ef0d1" stroke-width="1.5"/>
            <text x="140" y="85" fill="#eef4ff" font-size="14">data/  原始与清洗后的数据,来源和口径清楚</text>
            <rect x="120" y="106" width="660" height="40" rx="8" fill="rgba(105,179,162,0.16)" stroke="#69b3a2" stroke-width="1.5"/>
            <text x="140" y="131" fill="#eef4ff" font-size="14">factors/  因子计算,每个因子一个可复现脚本</text>
            <rect x="120" y="152" width="660" height="40" rx="8" fill="rgba(240,201,106,0.16)" stroke="#f0c96a" stroke-width="1.5"/>
            <text x="140" y="177" fill="#eef4ff" font-size="14">backtest/  回测引擎与成交、成本、约束假设</text>
            <rect x="120" y="198" width="660" height="40" rx="8" fill="rgba(240,201,106,0.16)" stroke="#f0c96a" stroke-width="1.5"/>
            <text x="140" y="223" fill="#eef4ff" font-size="14">config/  参数与实验配置,可重复、可追溯</text>
            <rect x="120" y="244" width="660" height="40" rx="8" fill="rgba(105,179,162,0.16)" stroke="#69b3a2" stroke-width="1.5"/>
            <text x="140" y="269" fill="#eef4ff" font-size="14">reports/  自动生成的净值、指标和归因报告</text>
            <text x="450" y="300" text-anchor="middle" fill="#8499bd" font-size="12.5">每层职责单一,换人接手也能看懂,几周后自己也不会迷路</text>"""
    return concept_figure(body, "0 0 900 315",
        "量化项目分层结构示意:data、factors、backtest、config、reports 各司其职",
        "把项目按职责拆成清晰的几层,而不是全写进一个越拉越长的 notebook。数据、因子、回测、配置、报告各归各位,几周后你和接手的人都还能看懂。")


def _fig_arbitrage():
    body = """            <text x="450" y="30" text-anchor="middle" fill="#f6f0df" font-size="19" font-weight="800">相对价值套利:赌两个价格的价差会收敛回来</text>
            <line x1="70" y1="250" x2="850" y2="250" stroke="#46587a" stroke-width="1.5"/>
            <line x1="70" y1="55" x2="70" y2="250" stroke="#46587a" stroke-width="1.5"/>
            <text x="848" y="272" text-anchor="end" fill="#8499bd" font-size="13">时间</text>
            <text x="52" y="65" fill="#8499bd" font-size="13">价格</text>
            <!-- 两条本应同步的价格线,中间张开又收回 -->
            <path d="M 90 180 C 250 120 320 100 430 95 C 540 100 650 150 830 150" fill="none" stroke="#8ef0d1" stroke-width="2.5"/>
            <path d="M 90 190 C 250 185 320 190 430 175 C 540 165 650 155 830 152" fill="none" stroke="#f0c96a" stroke-width="2.5"/>
            <text x="250" y="95" fill="#8ef0d1" font-size="13">资产 A</text>
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
    body = """            <text x="450" y="30" text-anchor="middle" fill="#f6f0df" font-size="19" font-weight="800">你买到的不是模型,是扣费后的一条净值曲线</text>
            <line x1="70" y1="250" x2="850" y2="250" stroke="#46587a" stroke-width="1.5"/>
            <line x1="70" y1="55" x2="70" y2="250" stroke="#46587a" stroke-width="1.5"/>
            <text x="52" y="65" fill="#8499bd" font-size="13">净值</text>
            <!-- 毛收益线 -->
            <path d="M 70 225 Q 300 175 520 140 T 830 85" fill="none" stroke="#8499bd" stroke-width="2.5" stroke-dasharray="7 5"/>
            <text x="640" y="108" fill="#8499bd" font-size="13.5">策略毛收益(宣传里常展示这条)</text>
            <!-- 净收益线,被费用压低 -->
            <path d="M 70 225 Q 300 195 520 170 T 830 130" fill="none" stroke="#8ef0d1" stroke-width="3"/>
            <text x="610" y="150" fill="#8ef0d1" font-size="13.5">你到手的净值(扣费后)</text>
            <!-- 费用差 -->
            <line x1="830" y1="85" x2="830" y2="130" stroke="#ffb4b4" stroke-width="2"/>
            <text x="822" y="76" text-anchor="end" fill="#ffb4b4" font-size="12.5">管理费+业绩报酬+申赎</text>
            <text x="450" y="288" text-anchor="middle" fill="#c9d4e8" font-size="13">还要看封闭期能不能赎、净值多久披露一次、回撤时能不能扛得住</text>"""
    return concept_figure(body, "0 0 900 300",
        "基金净值示意:毛收益曲线在上,扣掉各项费用后的净值曲线在下,差额是费用",
        "买量化产品,真正到你手里的是\u201c扣费后\u201d那条净值曲线,不是宣传页上的毛收益。管理费、业绩报酬、申赎费、封闭期,每一项都在你和策略收益之间。")


def _fig_backtest_loop():
    body = """            <text x="450" y="30" text-anchor="middle" fill="#f6f0df" font-size="19" font-weight="800">回测就是在历史里,一天天重放这个循环</text>
            <!-- 环形流程 6 步 -->
            <rect x="360" y="60" width="180" height="46" rx="10" fill="rgba(105,179,162,0.16)" stroke="#69b3a2" stroke-width="1.5"/>
            <text x="450" y="88" text-anchor="middle" fill="#eef4ff" font-size="13.5">① 读取当时可见数据</text>
            <rect x="640" y="120" width="180" height="46" rx="10" fill="rgba(105,179,162,0.16)" stroke="#69b3a2" stroke-width="1.5"/>
            <text x="730" y="148" text-anchor="middle" fill="#eef4ff" font-size="13.5">② 计算信号</text>
            <rect x="640" y="210" width="180" height="46" rx="10" fill="rgba(240,201,106,0.16)" stroke="#f0c96a" stroke-width="1.5"/>
            <text x="730" y="238" text-anchor="middle" fill="#eef4ff" font-size="13.5">③ 生成目标持仓</text>
            <rect x="360" y="270" width="180" height="46" rx="10" fill="rgba(240,201,106,0.16)" stroke="#f0c96a" stroke-width="1.5"/>
            <text x="450" y="298" text-anchor="middle" fill="#eef4ff" font-size="13.5">④ 模拟成交+扣成本</text>
            <rect x="80" y="210" width="180" height="46" rx="10" fill="rgba(105,179,162,0.16)" stroke="#69b3a2" stroke-width="1.5"/>
            <text x="170" y="238" text-anchor="middle" fill="#eef4ff" font-size="13.5">⑤ 更新现金持仓</text>
            <rect x="80" y="120" width="180" height="46" rx="10" fill="rgba(105,179,162,0.16)" stroke="#69b3a2" stroke-width="1.5"/>
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
    body = """            <text x="450" y="30" text-anchor="middle" fill="#f6f0df" font-size="19" font-weight="800">过拟合:样本内越漂亮,样本外可能越崩</text>
            <line x1="70" y1="250" x2="850" y2="250" stroke="#46587a" stroke-width="1.5"/>
            <line x1="70" y1="55" x2="70" y2="250" stroke="#46587a" stroke-width="1.5"/>
            <text x="52" y="65" fill="#8499bd" font-size="13">净值</text>
            <!-- 分界线:样本内/样本外 -->
            <line x1="470" y1="55" x2="470" y2="250" stroke="#f0c96a" stroke-width="1.5" stroke-dasharray="6 5"/>
            <text x="270" y="75" text-anchor="middle" fill="#8499bd" font-size="13">样本内(用来调参数)</text>
            <text x="660" y="75" text-anchor="middle" fill="#8499bd" font-size="13">样本外(没见过的新数据)</text>
            <!-- 过拟合线:样本内极好,样本外崩 -->
            <path d="M 90 240 Q 260 130 470 90" fill="none" stroke="#8ef0d1" stroke-width="3"/>
            <path d="M 470 90 Q 620 130 830 215" fill="none" stroke="#e88" stroke-width="3"/>
            <text x="250" y="120" fill="#8ef0d1" font-size="13">回测里美如画</text>
            <text x="660" y="200" fill="#ffb4b4" font-size="13" font-weight="800">实盘一上就崩</text>
            <text x="450" y="290" text-anchor="middle" fill="#c9d4e8" font-size="13">参数试得越多、模型越复杂,越容易\u201c背下\u201d历史噪声,而不是学到规律</text>"""
    return concept_figure(body, "0 0 900 305",
        "过拟合示意:样本内净值曲线极其漂亮,越过样本外分界线后急转直下",
        "过拟合是量化头号杀手:你在历史数据里反复调参,做出一条完美曲线,其实只是把当年的偶然噪声背了下来。换到没见过的新数据(样本外),立刻原形毕露。")


def _fig_loss_recovery():
    body = """            <text x="450" y="30" text-anchor="middle" fill="#f6f0df" font-size="19" font-weight="800">亏得越多,回本要涨得越狠(先活下来)</text>
            <line x1="110" y1="250" x2="850" y2="250" stroke="#46587a" stroke-width="1.5"/>
            <line x1="110" y1="55" x2="110" y2="250" stroke="#46587a" stroke-width="1.5"/>
            <text x="90" y="60" text-anchor="end" fill="#8499bd" font-size="12.5">回本涨幅</text>
            <text x="848" y="272" text-anchor="end" fill="#8499bd" font-size="13">亏损幅度</text>
            <!-- 柱子:亏损 vs 需要涨幅 -->
            <rect x="160" y="228" width="60" height="22" fill="rgba(105,179,162,0.5)"/><text x="190" y="222" text-anchor="middle" fill="#c9d4e8" font-size="12">亏10%→涨11%</text>
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


def render_chapter_svg(ch: dict, rendered_sections: list) -> str:
    title = esc(ch["title"])
    raw_sections = [s[0] for s in rendered_sections]
    if len(raw_sections) <= 8:
        section_labels = raw_sections
    else:
        section_labels = raw_sections[:7] + [raw_sections[-1]]
    while len(section_labels) < 8:
        section_labels.append(ch["summary"][len(section_labels) % len(ch["summary"])])
    node_positions = [
        (130, 140), (345, 140), (560, 140), (775, 140),
        (130, 310), (345, 310), (560, 310), (775, 310),
    ]
    flow_nodes = []
    for i, (label, (x, y)) in enumerate(zip(section_labels, node_positions), 1):
        flow_nodes.append(f"""
            <g filter="url(#softShadow{ch['num']})">
              <rect x="{x - 92}" y="{y - 58}" width="184" height="116" rx="18" fill="#0f1a2e" stroke="rgba(240,201,106,0.42)" stroke-width="2" />
              <circle cx="{x - 70}" cy="{y - 36}" r="14" fill="#f0c96a" fill-opacity="0.95" />
              <text x="{x - 70}" y="{y - 31}" text-anchor="middle" fill="#101412" font-size="14" font-weight="900">{i}</text>
              {svg_text(label, x + 6, y + 7, 148, size=15, max_chars=8, max_lines=4)}
            </g>""")
    flow_figure = f"""
        <div class="figure figure--reading reveal">
          <svg class="chapter-map" viewBox="0 0 900 410" role="img" aria-label="第 {ch['num']} 章流程图: {title}">
            <defs>
              <linearGradient id="mapGrad{ch['num']}" x1="0" x2="1" y1="0" y2="1">
                <stop offset="0%" stop-color="#f0c96a" stop-opacity="0.9" />
                <stop offset="100%" stop-color="#69b3a2" stop-opacity="0.85" />
              </linearGradient>
              <filter id="softShadow{ch['num']}" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="12" stdDeviation="12" flood-color="#000" flood-opacity="0.28" />
              </filter>
            </defs>
            <rect x="18" y="18" width="864" height="374" rx="24" fill="rgba(18,29,49,0.70)" stroke="rgba(240,201,106,0.25)" />
            <text x="450" y="62" text-anchor="middle" fill="#f6f0df" font-size="25" font-weight="850">第 {ch['num']} 章概念路径</text>
            <path d="M222 140 H253 M437 140 H468 M652 140 H683 M775 198 V252 M683 310 H652 M468 310 H437 M253 310 H222" fill="none" stroke="url(#mapGrad{ch['num']})" stroke-width="7" stroke-linecap="round" stroke-dasharray="10 13" />
            {''.join(flow_nodes)}
          </svg>
          <p class="figure__cap">本图从“{esc(section_labels[0])}”走到“{esc(section_labels[-1])}”,用于先看第 {ch['num']} 章的关键路径,再回到正文补细节。</p>
        </div>"""
    return flow_figure


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
              <rect x="{x - 115}" y="{y - 70}" width="230" height="140" rx="20" fill="rgba(15,26,46,0.92)" stroke="rgba(105,179,162,0.50)" stroke-width="2" />
              <path d="M{x - 65} {y - 30} L{x - 22} {y - 30} L{x - 22} {y - 42} L{x + 60} {y} L{x - 22} {y + 42} L{x - 22} {y + 30} L{x - 65} {y + 30} Z" fill="rgba(105,179,162,0.18)" stroke="rgba(105,179,162,0.48)" />
              <text x="{x}" y="{y - 38}" text-anchor="middle" fill="#69b3a2" font-size="15" font-weight="900">留下 {i}</text>
              {svg_text(label, x, y + 24, 185, size=15, color="#f6f0df", max_chars=8, max_lines=5)}
            </g>""")
    return f"""
        <div class="figure figure--reading reveal">
          <svg class="chapter-map" viewBox="0 0 900 360" role="img" aria-label="第 {ch['num']} 章小结图: {title}">
            <defs>
              <linearGradient id="sumGrad{ch['num']}" x1="0" x2="1" y1="0" y2="0">
                <stop offset="0%" stop-color="#f0c96a" stop-opacity="0.75" />
                <stop offset="100%" stop-color="#69b3a2" stop-opacity="0.75" />
              </linearGradient>
            </defs>
            <rect x="18" y="18" width="864" height="324" rx="24" fill="rgba(18,29,49,0.70)" stroke="rgba(105,179,162,0.28)" />
            <text x="450" y="68" text-anchor="middle" fill="#f6f0df" font-size="25" font-weight="850">本章留下的三件事</text>
            <path d="M295 220 H335 M565 220 H605" fill="none" stroke="url(#sumGrad{ch['num']})" stroke-width="7" stroke-linecap="round" />
            {''.join(summary_cards)}
          </svg>
          <p class="figure__cap">读完第 {ch['num']} 章后,至少要能复述“{esc(summary_labels[0])}”这一条判断,再用另外两张卡片检查自己是否真的理解。</p>
        </div>
"""


def render_chapter(ch: dict) -> str:
    idx = ch["num"]
    rendered_sections = prepare_sections(ch["sections"])
    # 概念图按锚点关键词挂到对应小节后面
    anchors = CONCEPT_FIGURES.get(idx, [])
    used = [False] * len(anchors)
    sections = []
    for n, (title, body) in enumerate(rendered_sections, 1):
        sections.append(f"""
        <h2>{n}. {esc(title)}</h2>
{body.rstrip()}
""")
        for ai, (keyword, maker) in enumerate(anchors):
            if not used[ai] and keyword in title:
                sections.append(maker())
                used[ai] = True
    # 没匹配上的概念图(锚点关键词没找到)兜底追加到正文末尾,避免丢图
    for ai, (keyword, maker) in enumerate(anchors):
        if not used[ai]:
            sections.append(maker())
    # 没有专属概念图的章,用"留下三件事"图收尾
    tail_figure = "" if anchors else render_summary_figure(ch)

    summary = "\n".join(f"            <li>{esc(x)}</li>" for x in ch["summary"])
    section_recap = "\n".join(
        f"            <li><strong>{i}.</strong> {esc(title)}</li>"
        for i, (title, _body) in enumerate(rendered_sections, 1)
    )
    quiz = "\n".join(
        f"""          <details class="quiz__item">
            <summary>{esc(q)}</summary>
            <p>{esc(a)}</p>
          </details>"""
        for q, a in ch["quiz"]
    )
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
{render_chapter_svg(ch, rendered_sections)}
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
    <script src="assets/book.js"></script>
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
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#10231f"/><path d="M12 44h40M18 38V24m14 14V16m14 22V28" stroke="#f0c96a" stroke-width="5" stroke-linecap="round"/><path d="M14 20h36" stroke="#69b3a2" stroke-width="4" stroke-linecap="round"/></svg>\n""",
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
  --bg: #101412;
  --bg-soft: #17201c;
  --panel: rgba(245, 241, 229, 0.06);
  --panel-strong: rgba(245, 241, 229, 0.1);
  --text: #f6f0df;
  --text-soft: #d9cfb8;
  --text-dim: #a99f89;
  --line: rgba(240, 201, 106, 0.2);
  --primary: #f0c96a;
  --accent: #69b3a2;
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
    linear-gradient(115deg, rgba(105, 179, 162, 0.12), transparent 34%),
    linear-gradient(245deg, rgba(240, 201, 106, 0.13), transparent 30%),
    linear-gradient(180deg, #0f1412 0%, #111714 54%, #0d1110 100%);
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
  background: rgba(13, 18, 16, 0.86);
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
  background: #121915;
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
  grid-template-columns: 2.5rem 1fr;
  gap: 0.5rem;
  padding: 0.55rem 0.65rem;
  border-radius: 8px;
  color: var(--text-soft);
}
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
.github-corner__body { fill: #101412; }
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
  padding-top: 0.6rem;
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
strong { color: #fff7df; }

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
  padding: 1rem;
  border: 1px solid rgba(105, 179, 162, 0.35);
  border-radius: 8px;
  background: rgba(105, 179, 162, 0.08);
}

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
  border: 1px solid rgba(105, 179, 162, 0.22);
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
