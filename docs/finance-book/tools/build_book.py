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


# 概念图最初按旧公开章号登记。这里只保留旧章到源单元的映射,
# 用于把图按小节锚点迁回正文;公开目录不再依赖这张表。
LEGACY_CHAPTER_GROUPS = [
    [0, 1], [2, 3], [4, 5], [6, 7], [8, 9], [10, 11, 12],
    [70], [37, 38, 65], [66], [67], [68], [69], [71], [72],
    [13, 14], [76],
    [15, 16], [17, 18, 19], [74], [75],
    [20, 21], [22, 23], [24, 25, 26],
    [27, 28], [29, 30], [31, 32], [33, 34], [35, 36],
    [39, 40], [41], [42, 43], [44, 45], [46, 47], [48],
    [49, 50], [51, 52], [53, 54], [55, 56], [77], [57], [58, 59],
    [60, 61], [62, 63], [64],
]


# 公开版只从这张结构表生成。每个分部同时声明它在主线中的问题、
# 读完后的产出和包含的手稿单元,避免目录、导航和说明文档各维护一套范围。
BOOK_STRUCTURE = [
    {
        "title": "第一部分 · 金融为什么存在",
        "kind": "main",
        "badge": "主线一",
        "question": "真实财富有限,为什么人类还需要货币、信用、银行和市场?",
        "outcome": "读完后,你能沿着资源、时间和风险解释金融系统,不再把金融理解成一堆产品名词。",
        "groups": [[0], [1], [2], [3], [4, 5]],
    },
    {
        "title": "第二部分 · 资产如何承载现金流与风险",
        "kind": "main",
        "badge": "主线二",
        "question": "股票、债券和衍生品为什么有价值,它们把什么权利和风险交给了你?",
        "outcome": "读完后,你能先拆现金流、权利、期限和最坏情况,再讨论价格涨跌。",
        "groups": [[6, 7], [8], [9], [10], [11], [12], [70]],
    },
    {
        "title": "第三部分 · 市场如何形成价格与数据",
        "kind": "main",
        "badge": "主线三",
        "question": "一项金融权利怎样上市、成交、留下数据,又该怎样评价它的收益和风险?",
        "outcome": "读完后,你能把交易界面上的数字还原为制度、现金流和可研究的数据口径。",
        "groups": [[13, 53], [76, 14], [15], [16], [37], [17], [18], [19, 74]],
    },
    {
        "title": "第四部分 · 宏观环境如何改变资产",
        "kind": "main",
        "badge": "主线四",
        "question": "增长、通胀、央行、美元和金融危机怎样穿过市场,改变资产的现金流与折现率?",
        "outcome": "读完后,你能把宏观新闻放回传导链,而不是用一个大词解释所有涨跌。",
        "groups": [[66], [38], [69], [65], [67], [68]],
    },
    {
        "title": "专题篇 · 个人金融的安全底盘",
        "kind": "special",
        "badge": "专题选读",
        "question": "在研究收益之前,个人怎样先守住不能承受的风险?",
        "outcome": "这一篇不阻塞量化主线;它把保险、社保、养老金和家庭配置放回个人现金流。",
        "groups": [[71], [72, 75]],
    },
    {
        "title": "第五部分 · 量化研究如何产生可信结论",
        "kind": "main",
        "badge": "主线五",
        "question": "一个金融判断怎样变成可证伪假设,再经过数据、回测、模型和实盘约束?",
        "outcome": "读完后,你能从问题出发完成研究闭环,而不是先找模型、再给结果编故事。",
        "groups": [[20], [21], [22], [23], [24], [25], [26], [39], [44, 47], [45, 55]],
    },
    {
        "title": "第六部分 · 策略如何变成产品",
        "kind": "main",
        "badge": "主线六",
        "question": "不同量化策略赚的是什么钱,承担什么风险,最终怎样装进受约束的产品?",
        "outcome": "读完后,你能按收益来源和风险结构比较策略,而不是只按历史年化排名。",
        "groups": [[29], [30], [31], [32], [33], [34], [35, 54, 77], [36]],
    },
    {
        "title": "第七部分 · 把研究变成可运行项目",
        "kind": "main",
        "badge": "主线七",
        "question": "怎样让研究穿过代码、模拟盘、真实订单和人的情绪,仍然保持可信?",
        "outcome": "读完后,你会完成两类实战,并知道何时推进、何时停手、怎样复盘。",
        "groups": [[41], [42, 56], [43, 57], [46], [61, 62]],
    },
    {
        "title": "第八部分 · 职业、复盘与长期成长",
        "kind": "main",
        "badge": "主线八",
        "question": "做完第一个项目以后,怎样选择岗位、建设作品集并形成长期学习循环?",
        "outcome": "读完后,你会把全书收束成一条个人路线,而不是停在零散知识和一次性项目。",
        "groups": [[27, 49], [28, 50], [48, 60], [63]],
    },
    {
        "title": "附录 · 随时回来查",
        "kind": "appendix",
        "badge": "工具箱",
        "question": "哪些内容不必顺序阅读,但研究前值得反复核对?",
        "outcome": "术语、公式和最终检查表集中在这里,不再打断正文的收束。",
        "groups": [[51, 52], [40], [58, 59, 64]],
    },
]


EXCLUDED_SOURCE_CHAPTERS = {
    73: "内容已拆成 callout 嵌回相关章节,保留手稿仅作历史来源。",
}


# 多单元章和少量关键转折章必须有人工标题与导语,不能再机械拼成“X 与 Y”。
GROUP_OVERRIDES = {
    (12,): {
        "title": "跨资产入门: 外汇、商品与 REITs",
        "desc": "先用现金流、供需和计价货币理解外汇、商品与不动产份额,再建立跨资产研究的共同语言。",
        "lead": "股票和债券之外,资产仍然可以用同一组问题理解:现金流从哪里来,价格受什么供需约束,谁承担汇率、流动性和尾部风险。这一章先做跨资产地图,认识外汇、商品与 REITs,并把它们放进统一的数据口径。下一章再进入更复杂的结构性产品,拆开那些被重新包装的收益和风险。",
    },
    (70,): {
        "title": "结构性产品深拆: 收益和风险怎样被切开重卖",
        "desc": "拆开雪球、CDS、CDO、互换和另类资产的内部齿轮,识别高票息背后被卖出的尾部风险。",
        "lead": "上一章建立了跨资产地图,这一章专门深入最容易被包装话术遮住的区域。雪球、CDS、CDO 和利率互换没有凭空创造收益,只是把旧资产的现金流与风险重新切开、排序和出售。理解每一份高票息对应谁在承担什么最坏情况,才算真正读懂结构。",
    },
    (4, 5): {
        "title": "金融系统与市场: 钱、风险和证券如何流动",
        "desc": "把金融系统的参与者、资金与风险流向,和证券发行、交易、清算、交收放进同一张地图。",
        "lead": "货币和信用解决了跨时间调动资源的问题,但现代金融不是两个人之间的一张借条,而是一张由居民、企业、银行、基金、交易所和监管者共同组成的网络。这一章先看钱和风险怎样在网络中流动,再看一项权利怎样从一级市场发行,进入二级市场交易。地图搭好以后,后面的股票、债券和衍生品才各有位置。",
    },
    (6, 7): {
        "title": "股票与估值: 你买的权利为什么值这个价",
        "desc": "从股东权利、股票收益来源走到公司行为、估值倍数和现金流折现。",
        "lead": "股票不是屏幕上的红绿代码,而是公司剩余现金流的一小份权利。先弄清股东排在谁后面、收益从哪里来,才能继续讨论分红、回购、增发和估值。这一章沿着同一条线回答两个问题:你买到了什么权利,市场又为什么愿意为这项权利支付今天的价格。",
    },
    (13, 53): {
        "title": "账户与交易界面: 一笔委托从哪里出发",
        "desc": "把账户、券商、交易所、登记结算和交易软件上的资金、持仓、委托、成交连成一条链。",
        "lead": "真实交易不是从策略公式开始,而是从一个有资金、有持仓、有权限的账户开始。你在软件里看到的可用资金、可卖数量、委托和成交,背后分别对应券商、交易所和登记结算系统中的不同状态。这一章从制度走到界面,把一笔委托真正出发以前的链路讲清楚。",
    },
    (76, 14): {
        "title": "股票怎样上市、交易与退市",
        "desc": "沿着股票的一生理解注册制、IPO、打新、交易时间、涨跌幅、T+1、费用、ST 与退市。",
        "lead": "一只股票能够出现在交易软件里,先要完成发行与上市;能够被买卖,还要服从具体市场的交易规则;失去上市条件时,又会进入风险警示和退市通道。这一章沿着股票从出生到退出的生命周期,把 A 股回测最容易写错的制度约束放回真实市场。",
    },
    (19, 74): {
        "title": "市场为什么难赢: 有效性与行为偏差",
        "desc": "从有效市场、随机游走走到损失厌恶、锚定、从众与纪律,解释超额收益为什么稀缺。",
        "lead": "市场并不完美,人也并不理性,但这两句话都不等于市场会免费送钱。公开信息会被竞争者迅速写进价格,人的偏差又会让错误长期反复。这一章把市场的竞争压力和人的出厂设置放在一起,解释研究为什么必须同时保持怀疑、纪律和可证伪性。",
    },
    (72, 75): {
        "title": "社保、养老金与家庭资产配置",
        "desc": "从五险一金、养老三支柱走到应急资金、长期账户和家庭资产分桶。",
        "lead": "家庭资产配置不是先挑收益最高的产品,而是先回答哪些钱不能亏、什么时候要用、哪些风险个人扛不起。社保和养老金提供公共底牌,应急资金、保障和长期组合再补上个人责任。这一章按现金流的先后顺序,把工资条、养老账户和家庭投资放进同一张图。",
    },
    (44, 47): {
        "title": "识别回测幻觉: 错误清单与拆解案例",
        "desc": "系统识别未来函数、幸存者偏差、成本低估、容量忽略和参数挑选,并拆穿一条漂亮曲线。",
        "lead": "研究最重要的能力之一,不是证明策略有效,而是尽快证明它为什么可能无效。这一章先建立错误清单,再沿着一条异常漂亮的回测曲线逐项排查:股票池是否点时、信号是否偷看收盘、成本是否算够、涨跌停是否可成交、参数是否挑过头。坏消息越早出现,真钱越安全。",
    },
    (45, 55): {
        "title": "审查量化研究: 从论文到回测报告",
        "desc": "用同一套问题检查研报、论文和回测报告里的假设、数据、基准、成本、风险与样本外。",
        "lead": "读懂结论不等于审查过研究。无论面对券商研报、学术论文还是别人发来的一份回测报告,可靠的顺序都相同:先找问题和假设,再查数据与时间,随后看基准、成本、风险和样本外。这一章先给审查框架,再带你按这个顺序真正读一份报告。",
    },
    (35, 54, 77): {
        "title": "读懂量化产品: 净值、报告与合同",
        "desc": "从净值、费用、回撤和归因走到基金月报、招募书、定期报告与结构化产品确认书。",
        "lead": "策略研究回答的是一套方法可能怎样赚钱,产品文件回答的则是投资者实际买到了什么。费后净值、申赎限制、封闭期、规模和合同条款都会改变最终体验。这一章从产品指标走到月报和法律文件,训练一种稳定顺序:不听话术,先找基准、费用、流动性、风险和最坏情况。",
    },
    (42, 56): {
        "title": "市场中性模拟盘: 把策略放进真实时间",
        "desc": "搭建多头、对冲、保证金和归因账本,再用一周日志处理数据、信号、成交与对账异常。",
        "lead": "回测把多年历史压缩成几分钟,模拟盘却强迫系统按真实时间等待。市场中性还多了一本对冲账:Beta、基差、保证金和现金每天都在变化。这一章先搭出模拟盘,再跟着它过完一周,让数据迟到、信号为空、涨停买不到和盘后对不到账这些现实问题逐个出现。",
    },
    (43, 57): {
        "title": "从模拟盘到小实盘: 上线前必须检查什么",
        "desc": "逐项核对数据、模型、交易、风控、日志和权限,再用可承受的小资金验证真实链路。",
        "lead": "模拟盘稳定不代表可以直接放大资金,它只说明系统获得了进入下一道门的资格。这一章先给上线门禁,再讲第一笔小资金实盘怎样限定资金、品种、自动化程度和停止规则。目标不是证明自己能赚钱,而是验证真实订单、费用、对账和情绪是否仍在控制范围内。",
    },
    (61, 62): {
        "title": "两条项目路径: 程序员怎样失败、怎样做稳",
        "desc": "用一正一反两个案例,比较先找模型与先问问题、追最佳参数与守样本外的不同结局。",
        "lead": "同样会写代码、同样从公开数据开始,两个项目可以走向完全不同的结局。反面路径先找模型、后找问题,小赚后加杠杆;正面路径从一个小问题出发,先做数据检查和简单基线,再进模拟盘。这一章把两条路线并排,让方法论落到真实选择。",
    },
    (27, 49): {
        "title": "量化行业与职业路线: 你适合站在哪个位置",
        "desc": "把机构生产线、岗位分工、能力要求、作品集和面试表达放到同一张职业地图。",
        "lead": "量化机构不是只有研究员,一套策略要经过数据、研究、平台、交易、风控、合规和运营。进入行业之前,先看清每个岗位在生产线里消除什么失败,再判断自己的工程能力最适合接在哪一段。这一章从真实工作流走到作品集,帮你选择位置而不是追逐一个模糊的“量化”标签。",
    },
    (28, 50): {
        "title": "长期学习路线: 从零到可展示的量化项目",
        "desc": "安排金融、统计、数据工程、因子、回测、模型、模拟盘和长期复盘的学习顺序。",
        "lead": "学习量化最常见的失败不是不够努力,而是顺序倒置:金融问题没想清楚就训练模型,数据时间线没站稳就追求高收益。这一章把个人项目路线和长期学习节奏合在一起,每一阶段都要求留下可检查的产物,让“学过”逐步变成“做得出来、讲得清楚”。",
    },
    (48, 60): {
        "title": "全书复盘与自检: 从一条鱼到一个量化系统",
        "desc": "按真实财富、金融权利、市场数据、研究验证、组合交易和人的纪律重走全书,再用判断题自检。",
        "lead": "走到这里,最容易发生的事是记住很多术语,却忘了它们之间的因果关系。这一章先把全书重新压成一条链:真实财富产生现金流,金融工具分配权利与风险,市场形成价格和数据,研究寻找可证伪的优势,系统把优势变成受约束的交易。随后用十个判断题检查这条链是否真的站稳。",
    },
    (51, 52): {
        "title": "概念复盘: 用人话重走金融与量化关键词",
        "desc": "沿着因果关系复盘货币、信用、股票、债券、因子、回测、滑点、容量、归因与风控。",
        "lead": "这一章不是网站那份按词查找的术语表,而是一次按因果关系组织的概念复盘。忘记某个词时,先找它对应的真实问题:谁拿到现金流,谁承担风险,数据怎样计算,结果怎样进入仓位。能用自己的话把词连成机制,比背住定义更重要;只想查单个定义时,直接使用页头的术语表。",
    },
    (58, 59, 64): {
        "title": "最终检查表: 研究、交易和实盘前先读",
        "desc": "集中核对金融常识、数据时间线、回测假设、组合约束、交易成本、模拟盘和停止规则。",
        "lead": "附录最后不再增加新知识,只保留三道门禁:进入量化前是否理解基本金融机制,开始项目时是否做到数据与实验可信,把系统推向交易前是否知道最坏情况和停止方式。每次研究、买产品或准备实盘时,都可以从这里重新检查。",
    },
    (20,): {
        "title": "从问题到因子: 把投资判断变成可检验假设",
        "lead": "量化研究不该从下载数据或挑模型开始,而该从一个足够小、能够被证伪的金融问题开始。因子只是把问题写成一列可重复计算的数字。这一章先问收益可能来自现金流、风险补偿、行为偏差还是市场摩擦,再把解释变成信号,用 IC、分层回测和失效条件检查它。",
    },
}


CHAPTER_SPECS = []
for part_index, part in enumerate(BOOK_STRUCTURE):
    for part_chapter_index, nums in enumerate(part["groups"]):
        CHAPTER_SPECS.append({
            "source_nums": nums,
            "part": part,
            "part_index": part_index,
            "part_chapter_index": part_chapter_index,
            "part_chapter_count": len(part["groups"]),
        })

CHAPTER_GROUPS = [spec["source_nums"] for spec in CHAPTER_SPECS]


def strip_num_prefix(title: str) -> str:
    return re.sub(r"^[0-9一二三四五六七八九十]+[.、．]\s*", "", str(title)).strip()


def merge_title(nums: list, parts: list) -> str:
    override = GROUP_OVERRIDES.get(tuple(nums), {})
    if "title" in override:
        return override["title"]
    titles = [strip_num_prefix(ch["title"]) for ch in parts]
    if len(titles) == 1:
        return titles[0]
    raise ValueError(f"多单元章缺少人工标题覆盖: {nums}")


def merge_desc(nums: list, parts: list) -> str:
    override = GROUP_OVERRIDES.get(tuple(nums), {})
    if "desc" in override:
        return override["desc"]
    if len(parts) == 1:
        return parts[0]["desc"]
    raise ValueError(f"多单元章缺少人工描述覆盖: {nums}")


def merge_lead(nums: list, parts: list) -> str:
    override = GROUP_OVERRIDES.get(tuple(nums), {})
    if "lead" in override:
        return override["lead"]
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
    for new_num, spec in enumerate(CHAPTER_SPECS):
        nums = spec["source_nums"]
        parts = [by_num[n] for n in nums]
        part = spec["part"]
        visible.append({
            "num": new_num,
            "source_nums": nums,
            "part": part["title"],
            "part_kind": part["kind"],
            "part_badge": part["badge"],
            "part_question": part["question"],
            "part_outcome": part["outcome"],
            "part_index": spec["part_index"],
            "part_chapter_index": spec["part_chapter_index"],
            "part_chapter_count": spec["part_chapter_count"],
            "title": merge_title(nums, parts),
            "desc": merge_desc(nums, parts),
            "lead": merge_lead(nums, parts),
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
    """模拟盘一周时间线,周一~周五每天一个事故卡,周末写复盘。"""
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
    """小实盘的三层护栏,从最外圈一路走到实盘。"""
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
    """金融直觉 8 件事 vs 量化纪律 10 件事,两列对照,门后才是代码。"""
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
    """程序员七步翻车(红)与正确姿势(金)逐步对照。"""
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
    """八步稳妥项目流水线,每步带推进/停止判据,小赚后回到复核步骤。"""
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
    """六问检查牌,六张等高卡上下堆叠,六关都过才准开始。"""
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
    23: [("先把金融地图补齐", _fig_b1_roadmap)],
    30: [("中性组合也会缺钱", _fig_b1_neutral_ledger)],
    33: [("真实财富和生产力", _fig_b1_ten_layers)],
    34: [("指数增强回测", _fig_b1_portfolio)],
    35: [("货币", _fig_b1_glossary)],
    36: [("总资产不是可花的钱", _fig_b1_account_fields)],
    37: [("数据没有按时到", _fig_b2_week)],
    39: [("先定资金上限", _fig_b2_guards)],
    40: [("能解释钱和财富的区别", _fig_b2_checklist)],
    41: [("他先找模型", _fig_b2_failure)],
    42: [("问题很小", _fig_b2_pipeline)],
    43: [("问题是否足够小", _fig_b2_questions)],
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
    14: [("券商是通道", _fig_c6_order_pipeline)],
    16: [("影线只是压缩图", _fig_c7_ohlc_aggregation)],
    17: [("这条路颠不颠", _fig_c8_volatility_cluster),
        ("每承担一份波动赚多少超额收益", _fig_c8_sharpe_compare)],
    20: [("高分组是不是真的更好", _fig_c9_factor_groups)],
}


PATCH_D = {
    21: [("历史答案背得太熟", _fig_d10_split)],
    22: [("预测分数不是仓位", _fig_d11_pipeline)],
    24: [("指数收益加超额", _fig_d13_alpha_beta)],
    25: [("Beta 对冲的直觉", _fig_d14_hedge_vol)],
    26: [("配对交易", _fig_d15_pair_trading)],
    7: [("三张报表分别回答什么", _fig_d17_three_tables)],
}


CONCEPT_FIGURES = {
    0: [("为什么钱多了不一定更富", _fig_inflation)],
    1: [("一张极简资产负债表", _fig_bank_balance), ("信心为什么这么重要", _fig_bank_run)],
    2: [("钱不是直接从一个人", _fig_money_flow)],
    3: [("先从一家小店说起", _fig_stock_ownership)],
    4: [("债券先当作一张标准化借条", _fig_bond_cashflow)],
    5: [("看涨期权和看跌期权", _fig_option_payoff)],
    14: [("价格优先和时间优先", _fig_orderbook)],
    16: [("一天被压成四个价格", _fig_candlestick)],
    17: [("从高点跌到低点有多痛", _fig_drawdown_sharpe)],
    20: [("常见因子家族", _fig_factor_quantile)],
    21: [("收盘价成交最容易骗人", _fig_lookahead)],
    22: [("约束优化的直觉", _fig_quant_pipeline)],
    24: [("指数增强", _fig_index_enhance)],
    25: [("市场中性想解决什么", _fig_market_neutral)],
    26: [("配对交易", _fig_arbitrage)],
    27: [("净值和收益披露", _fig_fund_nav)],
    7: [("三张报表分别回答什么", _fig_income_statement)],
    28: [("目录结构先分层", _fig_project_layout)],
    29: [("纸面组合落地的第一道关", _fig_backtest_loop)],
    31: [("把历史噪声背成了规律", _fig_overfitting)],
    32: [("回撤里最容易做错决定", _fig_loss_recovery)],
}




# -*- coding: utf-8 -*-
"""batchE:6 张信息型概念图(章号按主题修正后挂载):
  ch00 生产力的复利阶梯   -> 1.2 "储蓄不是抠门,是给未来留出空间"
  ch00 价格三问卡         -> 2.3 "价格是信号,不是敌人"
  ch01 信用-利率-估值传导链 -> 1.5 "为什么利率上升,老债会跌"
  ch03 平价 vs 波动对照    -> 1.2 "股东排在最后,所以风险和机会都大"
  ch10 特征-模型-预测-决策四格 -> 2.1 "模型先服务于问题定义"
  ch13 超额收益来源五格卡   -> 2.3 "超额收益从哪里来"
数字均取自对应章正文真账(见各函数 docstring)。
用法: 在 build_book.py 末尾 _merge_figures(CONCEPT_FIGURES, CONCEPT_FIGURES_PATCH)。
"""
import sys

sys.path.insert(0, "/data00/home/lingchen.judy/self/finance/docs/finance-book/tools")
from build_book import concept_figure, svg_text  # noqa: E402


def _fig_e00_productivity_ladder():
    """ch00 生产力复利阶梯。锚点:chapter-00.html <h3>1.2. 储蓄不是抠门,是给未来留出空间</h3>。
    数字沿用 1.2 节正文:徒手 1 条/天;少吃 1 条省出本钱;腾出 1 天编网;
    网成后 3 条/天(多 2 条);十天多 20 条 = 20 倍回报。"""
    steps = [
        (40, 284, 170, 56, "① 徒手抓鱼", "1 条/天", ["吃 1 条,存下 0 条"]),
        (240, 240, 170, 100, "② 储蓄:饿 1 天", "省出 1 条鱼", ["成本:1 条鱼 + 1 整天", "这两天产出是 0"]),
        (440, 195, 170, 145, "③ 投资:编网 1 天", "织出 1 张网", ["钱变资本:效率 ×3", "工具会磨损,要补要修"]),
        (640, 130, 170, 210, "④ 渔网上岗", "3 条/天", ["徒手 ×3,每天多 2 条", "10 天多 20 条", "回报 20 倍于那条鱼"]),
    ]
    parts = []
    parts.append('            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">生产力的复利阶梯:从一天 1 条鱼到一天 3 条鱼</text>')
    parts.append('            <text x="450" y="56" text-anchor="middle" fill="#8499bd" font-size="12.5">每一级都要先垫一层:省一条鱼、腾一天工,产出才上一个台阶——垫层决定上限</text>')
    for x, y, w, h, name, num, notes in steps:
        parts.append('            <rect x="%d" y="%d" width="%d" height="%d" rx="10" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>' % (x, y, w, h))
        cx = x + w // 2
        parts.append('            ' + svg_text(name, cx, y + 24, w - 16, size=13, color="#bcc9dd", weight=800, max_chars=10, max_lines=1))
        parts.append('            <text x="%d" y="%d" text-anchor="middle" fill="#f0c96a" font-size="17" font-weight="800">%s</text>' % (cx, y + 50, num))
        for li, ln in enumerate(notes):
            if h < 80:
                parts.append('            <text x="%d" y="%d" text-anchor="middle" fill="#8499bd" font-size="11.5">%s</text>' % (cx, y - 14 + li * 20, ln))
            else:
                parts.append('            <text x="%d" y="%d" text-anchor="middle" fill="#8499bd" font-size="11.5">%s</text>' % (cx, y + 74 + li * 22, ln))
    # 台阶间的小箭头(竖向爬升)
    for ax, ay in [(214, 268), (414, 218), (614, 168)]:
        parts.append('            <path d="M %d %d L %d %d L %d %d" stroke="#f0c96a" stroke-width="2" fill="none"/>' % (ax, ay + 28, ax, ay, ax + 24, ay))
    # 末端小旗:财富上限 = 生产率垫层
    parts.append('            <line x1="830" y1="50" x2="830" y2="130" stroke="#f0c96a" stroke-width="2.5"/>')
    parts.append('            <path d="M 830 54 L 868 64 L 830 74 Z" fill="rgba(240,201,106,0.85)"/>')
    parts.append('            <text x="830" y="98" text-anchor="middle" fill="#f0c96a" font-size="12" font-weight="800">财富上限</text>')
    parts.append('            <text x="830" y="116" text-anchor="middle" fill="#f0c96a" font-size="12" font-weight="800">= 生产率垫层</text>')
    parts.append('            <text x="450" y="376" text-anchor="middle" fill="#c9d4e8" font-size="13">一天 −1 条,换每天 +2 条:财富的上限不看票有多少,看生产率垫了多高——垫层以下的钱,只是账面数字</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 400",
        "生产力复利阶梯:徒手一天 1 条鱼;饿一天省下 1 条当本钱;腾出一天编出渔网;网成后一天 3 条,十天多 20 条;阶梯尽头一面小旗写着财富上限等于生产率垫层",
        "阿岛的账:储蓄省下 1 条鱼、腾出 1 天编网,产出从 1 条/天翻到 3 条/天,十天多抓 20 条——一天 −1 条换每天 +2 条。财富上限从来不看票加几个零,看生产率垫了多高。")


def _fig_e00_price_three_questions():
    """ch00 价格三问卡。锚点:chapter-00.html <h3>2.3. 价格是信号,不是敌人</h3>。
    素材沿用 2.3 节:渔夫难捕(供给)、食客叫好(需求)、碎片信息压成一个数字;
    1637 年郁金香球茎 1 万荷兰盾 ≈ 普通人年薪 150 盾的 66 年 ≈ 一栋豪宅。"""
    cards = [
        (30, "谁在生产?供给", "#a8c6ff",
         ["渔夫知道今天难捕", "网厂看出机会,连夜赶工", "成本、产量都在里面"],
         "没人生产:有价无货,谈不上价"),
        (310, "谁需要?需求", "#f0c96a",
         ["食客知道今天叫好", "人人想多分一条鱼", "愿出多高的价全在这里"],
         "没人需要:无人出价,也没有价"),
        (590, "多少钱?成交价", "#a8c6ff",
         ["碎片信息压成一个数字", "1637 年郁金香:1 颗球茎报 1 万盾", "≈ 年薪 150 盾 × 66 ≈ 一栋豪宅"],
         "没有价格:稀缺信号传不出去"),
    ]
    parts = []
    parts.append('            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">价格三问:每个成交价背后,都压着三个答案</text>')
    for x, name, ncolor, lines, missing in cards:
        cx = x + 125
        parts.append('            <rect x="%d" y="64" width="250" height="190" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>' % x)
        parts.append('            <text x="%d" y="94" text-anchor="middle" fill="%s" font-size="15" font-weight="800">%s</text>' % (cx, ncolor, name))
        for li, ln in enumerate(lines):
            parts.append('            ' + svg_text(ln, cx, 126 + li * 30, 230, size=12, color="#bcc9dd", weight=600, max_chars=16, max_lines=1))
        parts.append('            <line x1="%d" y1="216" x2="%d" y2="216" stroke="rgba(122,167,240,0.18)"/>' % (x + 20, x + 230))
        parts.append('            <text x="%d" y="240" text-anchor="middle" fill="#ffb4b4" font-size="12" font-weight="800">%s</text>' % (cx, missing))
    parts.append('            <text x="450" y="294" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">看懂价格 ≈ 同时回答这三问:价格是把答案压成一个数字的报信人,不是敌人</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 320",
        "价格三问卡:谁在生产(供给)、谁需要(需求)、多少钱(成交价);第三卡带 1637 年郁金香账:一颗球茎一万盾约等于普通人 66 年工资;每卡配一句没它就没价格",
        "把一个价格拆开看,背后就是三问:谁在生产、谁需要、多少钱——供给、需求、成交价,缺了任何一个都没有价格。1637 年那颗报一万盾的郁金香提醒你:三问的答案可以是泡沫,看价格也要看它背后的货和人。")


def _fig_e01_credit_rate_value():
    """ch01 信用→利率→估值传导链。锚点:chapter-01.html <h3>1.5. 为什么利率上升,老债会跌</h3>。
    数字沿用该节正文:一年后确定拿 105 元的债;市场利率 5%→10%;105÷1.1=95.45 元。
    左格借鱼账沿用 ch00 1.4:借 1 条还 2 条,利息补等待、风险、不方便。"""
    nodes = [
        (30, "信用:有人今天肯借", "#f0c96a",
         ("借 1 条 → 还 2 条", "利息 = 1 条鱼"),
         "利息补三样:等待·风险·不方便",
         "没信用:利率再高也没人付"),
        (320, "利率:多借要付利息", "#a8c6ff",
         ("市场要求的回报", "5% → 10%"),
         "折现率 = 市场当下要求的回报",
         "利率升 → 未来的钱更不值钱"),
        (610, "估值:把未来折回今天", "#a8c6ff",
         ("105 ÷ 1.1 = 95.45 元", "1 年后拿 105 元"),
         "今天的价 = 未来的钱 ÷ (1 + 折现率)",
         "没折现:未来 1 元 ≠ 今天 1 元"),
    ]
    parts = []
    parts.append('            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">信用 → 利率 → 估值:同一条传导链走一遍</text>')
    parts.append('            <text x="450" y="56" text-anchor="middle" fill="#8499bd" font-size="12.5">先有人肯今天借出,再看市场要多少回报,最后才知道未来的钱折回今天值多少</text>')
    parts.append('            <defs><marker id="e01a" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#8499bd"/></marker></defs>')
    for x, name, ncolor, big, note, warn in nodes:
        cx = x + 130
        parts.append('            <rect x="%d" y="76" width="260" height="200" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>' % x)
        parts.append('            <text x="%d" y="106" text-anchor="middle" fill="%s" font-size="15.5" font-weight="800">%s</text>' % (cx, ncolor, name))
        parts.append('            <text x="%d" y="140" text-anchor="middle" fill="#c9d4e8" font-size="12">%s</text>' % (cx, big[0]))
        parts.append('            <text x="%d" y="166" text-anchor="middle" fill="#f0c96a" font-size="16" font-weight="800">%s</text>' % (cx, big[1]))
        parts.append('            ' + svg_text(note, cx, 198, 240, size=11.5, color="#8499bd", weight=600, max_chars=17, max_lines=1))
        parts.append('            <line x1="%d" y1="220" x2="%d" y2="220" stroke="rgba(122,167,240,0.18)"/>' % (x + 20, x + 240))
        parts.append('            ' + svg_text(warn, cx, 248, 240, size=12, color="#ffb4b4", weight=800, max_chars=16, max_lines=1))
    for ax in (292, 582):
        parts.append('            <path d="M %d 176 L %d 176" stroke="#8499bd" stroke-width="2.5" fill="none" marker-end="url(#e01a)"/>' % (ax, ax + 24))
    parts.append('            <text x="450" y="310" text-anchor="middle" fill="#eef4f8" font-size="13.5" font-weight="800">传导一遍:利率从 5% 到 10%,同一张 105 元的债,今天只值 95.45 元(100 → 95.45)</text>')
    parts.append('            <text x="450" y="336" text-anchor="middle" fill="#c9d4e8" font-size="12.5">债券价格与市场利率反着走;股票、房子,一切长期资产都被这根折现率拽着走</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 360",
        "信用利率估值传导链:借一条还两条的信用账,市场利率从 5% 升到 10%,一年后 105 元的债折现 105÷1.1=95.45 元,老债从 100 元跌到 95.45 元",
        "链条走一遍:信用是有人肯今天借鱼(借 1 还 2),利率是多借要付的价(5%→10%),估值是把未来的钱折回今天(105÷1.1=95.45)。利率一升,同一张 105 元的债从 100 元掉到 95.45 元——折现率拽着所有长期资产。")


def _fig_e03_flat_vs_volatile():
    """ch03 平价 vs 波动两商品对照。锚点:chapter-03.html <h3>1.2. 股东排在最后,所以风险和机会都大</h3>。
    左图:A 商品常年 100±1(债主本息),B 商品 100±30(股东回报);
    右账卡沿用 1.2 节真账:借款 100 万年息 5 万;利润 10 万→债主 5 万/股东 5 万;
    利润 30 万→债主 5 万/股东 25 万(回报 5% vs 25%);利润 4 万→股东倒贴。"""
    def y_of(p):
        return int(round(300 - (p - 70) * 2.3))
    xs = [80 + i * 58 for i in range(9)]
    a_prices = [100, 100, 101, 100, 99, 100, 100, 101, 100]
    b_prices = [100, 122, 84, 126, 80, 112, 94, 106, 90]
    a_pts = " L ".join("%d %d" % (x, y_of(p)) for x, p in zip(xs, a_prices))
    b_pts = " L ".join("%d %d" % (x, y_of(p)) for x, p in zip(xs, b_prices))
    parts = []
    parts.append('            <text x="450" y="30" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">同样都在 100 附近,谁的风险大?</text>')
    parts.append('            <text x="450" y="54" text-anchor="middle" fill="#8499bd" font-size="12.5">左:两件商品一年走势;右:1.2 节那家公司的两笔真账——债主与股东</text>')
    # 左图:价格带
    parts.append('            <rect x="70" y="70" width="490" height="232" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>')
    parts.append('            <text x="305" y="92" text-anchor="middle" fill="#a8c6ff" font-size="13" font-weight="800">A:借出去的钱:常年 100 ± 1</text>')
    parts.append('            <text x="305" y="112" text-anchor="middle" fill="#ffb4b4" font-size="13" font-weight="800">B:当股东拿的回报:100 ± 30</text>')
    parts.append('            <rect x="84" y="%d" width="452" height="%d" fill="rgba(232,120,120,0.09)"/>' % (y_of(130), y_of(70) - y_of(130)))
    parts.append('            <rect x="84" y="%d" width="452" height="%d" fill="rgba(122,167,240,0.14)"/>' % (y_of(101), y_of(99) - y_of(101)))
    parts.append('            <path d="M ' + a_pts + '" fill="none" stroke="#7aa7f0" stroke-width="2.5"/>')
    parts.append('            <path d="M ' + b_pts + '" fill="none" stroke="#ffb4b4" stroke-width="2.5"/>')
    parts.append('            <line x1="84" y1="%d" x2="536" y2="%d" stroke="rgba(201,212,232,0.35)" stroke-width="1" stroke-dasharray="4 5"/>' % (y_of(100), y_of(100)))
    parts.append('            <text x="90" y="%d" fill="#8499bd" font-size="11">基准 100</text>' % (y_of(130) + 16))
    parts.append('            <text x="548" y="212" fill="#a8c6ff" font-size="11.5" font-weight="800">±1</text>')
    parts.append('            <text x="548" y="240" fill="#ffb4b4" font-size="11.5" font-weight="800">±30</text>')
    # 右账卡
    parts.append('            <rect x="600" y="70" width="260" height="232" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(240,201,106,0.42)"/>')
    parts.append('            <text x="730" y="96" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">同一家公司,两笔账</text>')
    rows = [
        ("公司借 100 万,年息 5 万", "#c9d4e8", 600, 122),
        ("利润 10 万那年:", "#8499bd", 600, 148),
        ("债主 5 万(5%) · 股东 5 万(5%)", "#eef4f8", 600, 168),
        ("利润 30 万那年:", "#8499bd", 600, 194),
        ("债主还是 5 万(雷打不动 5%)", "#a8c6ff", 600, 214),
        ("股东 25 万 → 回报 25%", "#ffb4b4", 600, 234),
        ("利润 4 万那年:股东一分没有还倒贴", "#ffb4b4", 600, 262),
        ("利润的全部波动,都挤到股东身上", "#f0c96a", 600, 286),
    ]
    for txt, col, _x, y in rows:
        parts.append('            <text x="730" y="%d" text-anchor="middle" fill="%s" font-size="12">%s</text>' % (y, col, txt))
    parts.append('            <text x="450" y="336" text-anchor="middle" fill="#eef4f8" font-size="13.5" font-weight="800">哪个风险大,不看价格高低,看波动带宽度:±1 vs ±30,差出 30 倍</text>')
    parts.append('            <text x="450" y="362" text-anchor="middle" fill="#c9d4e8" font-size="12.5">波动率就是把这种不确定数字化;拿走固定收益的人不坐过山车,拿剩余收益的人坐全程</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 400",
        "平价与波动对照:商品 A 常年 100±1,商品 B 100±30;右账卡写债主雷打不动拿 5 万,股东回报从 5% 到 25% 再到倒贴;风险看波动带宽度不看价格高低",
        "两件商品都围着 100 转:A 带宽 ±1,B 带宽 ±30,风险差 30 倍。1.2 节的账就是这条:B 是股东,利润 10 万拿 5 万(5%),利润 30 万拿 25 万(25%),利润 4 万就倒贴——波动率是把不确定性数字化。")


def _fig_e10_ml_shutter():
    """ch10 特征→模型→预测→决策四格快门。锚点:chapter-10.html <h3>2.1. 模型先服务于问题定义</h3>。
    硬信息:2.2 节打分式 0.3×价值+0.2×质量+0.2×动量−0.1×波动;
    2.10 节个人项目:沪深300/中证500、标签=未来20日相对收益、看 RankIC;
    四个坑对应小节 1.4(泄漏)、1.9(过拟合)、2.9(信号衰减)、1.5(执行成本)。"""
    cards = [
        (24, "① 特征", "#a8c6ff",
         ["原始行情与财报", "压成因子:估值动量", "波动、质量、流动性"],
         "坑:数据泄漏", "用了当天之后的数据(1.4)"),
        (246, "② 模型", "#f0c96a",
         ["打分式(2.2 节):", "分 = 0.3×价值", "+0.2×质量 +0.2×动量", "−0.1×波动"],
         "坑:过拟合", "历史答案背得太熟(1.9)"),
        (468, "③ 预测", "#a8c6ff",
         ["每只股一个预期分", "标签:未来 20 日收益", "看 RankIC 与分层"],
         "坑:信号衰减", "上线后 IC 慢慢掉(2.9)"),
        (690, "④ 决策", "#8fb37a",
         ["规则:超配前 20%", "月频调仓生成订单", "下进市场才算数"],
         "坑:执行成本", "佣金滑点吃掉超额(1.5)"),
    ]
    parts = []
    parts.append('            <text x="450" y="30" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">特征 → 模型 → 预测 → 决策:四道快门,每道都在吃收益</text>')
    parts.append('            <text x="450" y="54" text-anchor="middle" fill="#8499bd" font-size="12.5">顺序不可倒:先定义问题,再谈模型——本章 2.1 节:模型必须由前面的问题来定义</text>')
    parts.append('            <defs><marker id="e10a" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#8499bd"/></marker></defs>')
    for x, name, ncolor, lines, pit, pit_note in cards:
        cx = x + 93
        parts.append('            <rect x="%d" y="72" width="186" height="210" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>' % x)
        parts.append('            <text x="%d" y="100" text-anchor="middle" fill="%s" font-size="15" font-weight="800">%s</text>' % (cx, ncolor, name))
        parts.append('            <line x1="%d" y1="112" x2="%d" y2="112" stroke="rgba(122,167,240,0.18)"/>' % (x + 16, x + 170))
        for li, ln in enumerate(lines):
            parts.append('            ' + svg_text(ln, cx, 136 + li * 26, 170, size=11.5, color="#bcc9dd", weight=600, max_chars=14, max_lines=1))
        parts.append('            <line x1="%d" y1="230" x2="%d" y2="230" stroke="rgba(232,136,136,0.30)"/>' % (x + 16, x + 170))
        parts.append('            <text x="%d" y="252" text-anchor="middle" fill="#ffb4b4" font-size="12.5" font-weight="800">%s</text>' % (cx, pit))
        parts.append('            <text x="%d" y="272" text-anchor="middle" fill="#c9d4e8" font-size="10.5">%s</text>' % (cx, pit_note))
    for ax in (212, 434, 656):
        parts.append('            <path d="M %d 176 L %d 176" stroke="#8499bd" stroke-width="2.5" fill="none" marker-end="url(#e10a)"/>' % (ax, ax + 28))
    parts.append('            <text x="450" y="318" text-anchor="middle" fill="#eef4f8" font-size="13.5" font-weight="800">出厂前死于泄漏和过拟合,上线后死于衰减与成本——四道快门,一道都省不掉</text>')
    parts.append('            <text x="450" y="344" text-anchor="middle" fill="#c9d4e8" font-size="12.5">本章路线因此反过来排:金融问题 → 可交易假设 → 标签 → 数据口径 → 简单基线 → 复杂模型</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 380",
        "机器学习四道快门:特征(估值动量波动质量流动性因子)、模型(0.3×价值+0.2×质量+0.2×动量−0.1×波动)、预测(未来20日相对收益看RankIC)、决策(超配前20%月频调仓);每格标注一个坑:泄漏、过拟合、信号衰减、执行成本",
        "从原始数据到下单要过四道快门:特征压成因子、模型压成分数、分数变预测、预测进规则。每道都有一个主题坑:泄漏(1.4)、过拟合(1.9)、衰减(2.9)、成本(1.5)——前两道死在出厂前,后两道死在上线后。")


def _fig_e13_alpha_five():
    """ch13 超额收益来源五格卡。锚点:chapter-13.html <h3>2.3. 超额收益从哪里来</h3>。
    五格:行业偏离、风格偏离、个股偏离、时点、其他(成本/执行);
    收底账沿用 2.5 节:产品 A 超额 6% 跟踪误差 6% IR≈1;B 超额 8% 误差 16% IR≈0.5;
    2.6 节:客户买的是指数增强,不是行业轮动基金。"""
    cards = [
        (20, "行业偏离", "#f0c96a", "超配景气行业", "行业反转", "大幅跑输"),
        (192, "风格偏离", "#a8c6ff", "押市值/价值/动量暴露", "风格切换", "就被打脸"),
        (364, "个股偏离", "#f0c96a", "模型看好的多配一点", "个股踩雷", "停牌违约"),
        (536, "时点偏离", "#a8c6ff", "偏离调仓日,卡事件窗口", "交易拥挤", "信号过期"),
        (708, "其他:成本", "#8fb37a", "成本压一点,执行稳一点", "容量上限", "滑点反噬"),
    ]
    parts = []
    parts.append('            <text x="450" y="30" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">超额收益从哪来:五种偏离,各赚各的钱,各背各的雷</text>')
    parts.append('            <text x="450" y="54" text-anchor="middle" fill="#8499bd" font-size="12.5">想赚超额就必须偏离基准(2.4 自由度的价格);偏离多大,用跟踪误差预算写死(2.6)</text>')
    for x, name, ncolor, gain, risk1, risk2 in cards:
        cx = x + 81
        parts.append('            <rect x="%d" y="72" width="162" height="240" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>' % x)
        parts.append('            <text x="%d" y="100" text-anchor="middle" fill="%s" font-size="14" font-weight="800">%s</text>' % (cx, ncolor, name))
        parts.append('            <line x1="%d" y1="112" x2="%d" y2="112" stroke="rgba(122,167,240,0.18)"/>' % (x + 14, x + 148))
        parts.append('            <text x="%d" y="132" text-anchor="middle" fill="#8499bd" font-size="10.5">赚它的决策</text>' % cx)
        parts.append('            ' + svg_text(gain, cx, 152, 148, size=11.5, color="#eef4f8", weight=800, max_chars=11, max_lines=2))
        parts.append('            <text x="%d" y="206" text-anchor="middle" fill="#8499bd" font-size="10.5">背什么雷</text>' % cx)
        parts.append('            <text x="%d" y="232" text-anchor="middle" fill="#ffb4b4" font-size="11.5" font-weight="800">%s</text>' % (cx, risk1))
        parts.append('            <text x="%d" y="252" text-anchor="middle" fill="#ffb4b4" font-size="11.5" font-weight="800">%s</text>' % (cx, risk2))
        parts.append('            <line x1="%d" y1="272" x2="%d" y2="272" stroke="rgba(122,167,240,0.14)"/>' % (x + 14, x + 148))
        parts.append('            <text x="%d" y="294" text-anchor="middle" fill="#8499bd" font-size="10.5">偏离即自由度,也是风险</text>' % cx)
    parts.append('            <text x="450" y="350" text-anchor="middle" fill="#eef4f8" font-size="13.5" font-weight="800">收底看信息比率(2.5):A 超额 6% / 偏离 6% → IR≈1;B 超额 8% / 偏离 16% → IR≈0.5</text>')
    parts.append('            <text x="450" y="376" text-anchor="middle" fill="#c9d4e8" font-size="12.5">超额多高不重要,每份偏离换多少才重要;客户买的是指数增强,不是行业轮动基金</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 420",
        "超额收益五格卡:行业偏离、风格偏离、个股偏离、时点偏离、其他(成本与执行),每格写赚它的决策和背的雷;收底用信息比率两笔账:A 超额6%偏离6% IR=1,B 超额8%偏离16% IR=0.5",
        "超额只有五个来路:行业、风格、个股、时点的偏离,加上成本与执行的省。每个来路都背一颗对应的雷。收尾用 2.5 节的账:B 超额 8% 看着更高,IR 只有 0.5——拿两倍多的偏离风险换来的,不如 A 的 1。")


PATCH_E = {
    0: [("储蓄不是抠门", _fig_e00_productivity_ladder),
        ("价格是信号", _fig_e00_price_three_questions)],
    1: [("老债会跌", _fig_e01_credit_rate_value)],
    3: [("股东排在最后", _fig_e03_flat_vs_volatile)],
    21: [("问题定义", _fig_e10_ml_shutter)],
    24: [("超额收益从哪里", _fig_e13_alpha_five)],
}
# -*- coding: utf-8 -*-
"""概念图 batch F(ch12/16/18/19/20/21/22 各新增第二张,合计 7 张)。

交付约定(与 build_book.py 现有 _fig_xxx 函数一致):
- 纯字符串拼接,不含 f-string;body 用 % 或字符串加号组拼。
- 每张图通过 concept_figure(body, "0 0 900 高", aria, cap) 收尾,
  内部混用 svg_text(...) 与手写 <text>。
- 调色板与全书一致,禁用暖米色底(全书禁色的那个浅米色)。
- viewBox 高度 280~480,x 类坐标与 path d 内数字均 <= 890。

锚点关键词:全部是「渲染后小节标题」的子串,已逐一 grep 验证唯一命中,
且与同章既有锚点("先把金融地图补齐"/"净值和收益披露"/"目录结构先分层"/"纸面组合落地的第一道关"/
"中性组合也会缺钱"/"把历史噪声背成了规律"/"回撤里最容易做错决定")互不包含,不会被抢挂。

说明:用户原始清单里 ch12/ch16/ch18/ch20 的预设主题与章节实际内容不符
(ch12 实为「量化机构分工 + 学习路线」,ch16 实为「产品净值费用 + 合规」,
ch18 实为「工程组织 + 指标公式」,ch20 实为「市场中性 + 上线清单」,
且 ch21 已有一张过拟合曲线图),故按 AGENTS 规则如实改选本章内
真正带硬信息的小节绘图,主题向用户原意图尽量靠拢:

grep 验证(<h2>/<h3> 命中行,各唯一):
  ch12 "研究员每天在做什么"   -> chapter-12.html:33 <h3>1.2. 研究员每天在做什么</h3>
  ch16 "业绩归因报告怎么看"   -> chapter-16.html:64 <h3>1.6. 业绩归因报告怎么看</h3>
  ch18 "最大回撤"             -> chapter-18.html:151 <h3>2.4. 最大回撤</h3>
  ch19 "让时间线先立正"       -> chapter-19.html:44 <h2>3. 让时间线先立正</h2>
  ch20 "把总收益拆回零件"     -> chapter-20.html:93 <h3>1.7. 把总收益拆回零件</h3>
  ch21 "手续费不是小零头"     -> chapter-21.html:51 <h3>1.3. 手续费不是小零头</h3>
  ch22 "复盘顺序"             -> chapter-22.html:101 <h3>2.8. 复盘顺序</h3>
"""


def _fig_f12_researcher_loop():
    """ch12 研究员的真实日常循环。锚点:chapter-12.html:33 <h3>1.2. 研究员每天在做什么</h3>。
    流程与措辞沿用 1.2 正文:提出假设、取数据、清洗样本、构造特征、跑回测、看风险、
    写报告、和已有因子比较、解释为什么失效、重复迭代;典型问题与五关
    (IC·分层·换手·成本·容量)均为该节原文。"""
    nodes = ["提出假设", "取数清洗", "构造特征", "跑回测", "风险比较", "报告归档"]
    parts = []
    parts.append('            <text x="450" y="30" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">量化研究员的一天:循环体力活,不是灵感爆发</text>')
    parts.append('            <text x="450" y="54" text-anchor="middle" fill="#8499bd" font-size="12.5">提出假设 → 取数清洗 → 构造特征 → 回测 → 和老因子比较 → 写报告;大多数想法最后没用,但失败统统归档</text>')
    parts.append('            <defs>'
                 '<marker id="f12a" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#8499bd"/></marker>'
                 '<marker id="f12g" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#f0c96a"/></marker>'
                 '</defs>')
    for i, name in enumerate(nodes):
        cx = 83 + i * 148
        parts.append('            <rect x="%d" y="82" width="126" height="72" rx="10" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>' % (cx - 63))
        parts.append('            <circle cx="%d" cy="96" r="10" fill="rgba(122,167,240,0.25)"/>' % (cx - 50))
        parts.append('            <text x="%d" y="100" text-anchor="middle" fill="#a8c6ff" font-size="11.5" font-weight="800">%d</text>' % (cx - 50, i + 1))
        parts.append('            ' + svg_text(name, cx, 126, 118, size=12, color="#eef4f8", weight=800, max_chars=4, max_lines=1))
        if i < 5:
            parts.append('            <path d="M %d 118 L %d 118" stroke="#8499bd" stroke-width="2" fill="none" marker-end="url(#f12a)"/>' % (cx + 65, cx + 83))
    # 循环虚线:从第 6 步回到第 1 步
    parts.append('            <path d="M 823 158 L 823 186 L 83 186 L 83 158" stroke="#f0c96a" stroke-width="2" stroke-dasharray="6 5" fill="none" marker-end="url(#f12g)"/>')
    parts.append('            <text x="453" y="203" text-anchor="middle" fill="#bcc9dd" font-size="12">↩ 大多数想法最后没用:失败记录照样归档——方向已拥挤 · 数据有坑 · 假设站不住</text>')
    # 典型问题案例卡
    parts.append('            <rect x="30" y="220" width="840" height="180" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(240,201,106,0.42)"/>')
    parts.append('            <text x="450" y="246" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">一个典型问题:某类财务质量指标,在中证 1000 里有没有选股效果?</text>')
    blocks = [
        ("定义指标口径", "字段对齐公告日期"),
        ("行业中性·市值中性", "剥离行业和大小盘"),
        ("五关逐项打分", "任何一关不够就停"),
        ("判定能否入库", "够格才准加入模型"),
    ]
    for i, (main, sub) in enumerate(blocks):
        cx = 124 + i * 208
        parts.append('            <rect x="%d" y="264" width="176" height="56" rx="10" fill="rgba(122,167,240,0.08)" stroke="rgba(122,167,240,0.28)"/>' % (cx - 88))
        parts.append('            <text x="%d" y="287" text-anchor="middle" fill="#eef4f8" font-size="12" font-weight="800">%s</text>' % (cx, main))
        parts.append('            <text x="%d" y="307" text-anchor="middle" fill="#bcc9dd" font-size="11">%s</text>' % (cx, sub))
        if i < 3:
            parts.append('            <path d="M %d 292 L %d 292" stroke="#f0c96a" stroke-width="2" fill="none" marker-end="url(#f12g)"/>' % (cx + 90, cx + 118))
    parts.append('            <text x="70" y="352" fill="#8499bd" font-size="12">入库前五关连看:</text>')
    gates = ["IC 表现", "分层单调", "换手率", "交易成本", "容量"]
    for i, g in enumerate(gates):
        gx = 262 + i * 118
        parts.append('            <rect x="%d" y="336" width="104" height="26" rx="8" fill="rgba(122,167,240,0.14)" stroke="rgba(122,167,240,0.35)"/>' % gx)
        parts.append('            <text x="%d" y="354" text-anchor="middle" fill="#a8c6ff" font-size="11.5" font-weight="800">%s</text>' % (gx + 52, g))
    parts.append('            <text x="450" y="386" text-anchor="middle" fill="#8499bd" font-size="11.5">五关同时过才算数:有效不够——还得分层单调、换手受控、扣完成本还剩、装得下资金</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 430",
        "研究员日常循环:提出假设、取数清洗、构造特征、跑回测、风险比较、报告归档,失败也归档后回到起点;下方一个典型问题:财务质量指标在中证1000里有没有选股效果,要过口径、中性化、五关(IC、分层、换手、成本、容量)才能入库",
        "研究员的真实日常是一个循环:提出假设、取数清洗、构造特征、跑回测、和老因子比、写报告解释失效,大多数想法最后没用——但失败记录照样归档。一个典型问题(财务质量指标在中证 1000 有没有选股效果)要过口径、中性化和 IC、分层、换手、成本、容量五关,才谈得上加入现有模型。")


def _fig_f16_attribution_bar():
    """ch16 超额收益归因拆分卡。锚点:chapter-16.html:64 <h3>1.6. 业绩归因报告怎么看</h3>。
    拆分口径沿用 1.6 正文(行业配置/风格暴露/选股/交易执行/现金管理类),
    数字为自洽账:1.8+0.6+0.4-0.2-0.5=+2.1%;反面例 0.3+1.9+0.2-0.1=+2.3%。"""
    parts = []
    parts.append('            <text x="450" y="30" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">超额从哪来:五段加总,必须严丝合缝对上总超额</text>')
    parts.append('            <text x="450" y="54" text-anchor="middle" fill="#8499bd" font-size="12.5">产品甲:组合 +12.1% − 基准 +10.0% = 超额 +2.1% —— 拆开看谁贡献的;负段向下扣,直到净线</text>')
    # 左柱:产品甲堆积(底 y=350,1% = 70px)
    segs = [
        (350, 126, "rgba(143,179,122,0.45)", "rgba(143,179,122,0.7)"),   # 选股 +1.8 -> y 224..350
        (224, 42, "rgba(240,201,106,0.45)", "rgba(240,201,106,0.6)"),    # 行业 +0.6 -> y 182..224
        (182, 28, "rgba(122,167,240,0.45)", "rgba(122,167,240,0.6)"),    # 风格 +0.4 -> y 154..182
        (154, 14, "rgba(232,120,120,0.45)", "rgba(232,136,136,0.6)"),    # 时点 -0.2 -> y 140..154
        (140, 35, "rgba(232,120,120,0.45)", "rgba(232,136,136,0.6)"),    # 成本 -0.5 -> y 105..140
    ]
    for y0, h, fill, stroke in segs:
        parts.append('            <rect x="120" y="%d" width="140" height="%d" fill="%s" stroke="%s"/>' % (y0 - h, h, fill, stroke))
    # 净超额水平线 y=203
    parts.append('            <line x1="120" y1="203" x2="260" y2="203" stroke="#f0c96a" stroke-width="2" stroke-dasharray="6 4"/>')
    parts.append('            <text x="112" y="207" text-anchor="end" fill="#f0c96a" font-size="12.5" font-weight="800">合计 +2.1%</text>')
    parts.append('            <text x="190" y="372" text-anchor="middle" fill="#eef4f8" font-size="12.5" font-weight="800">产品甲:来源均衡</text>')
    labels = [
        (287, "#eef4f8", "选股 +1.8%(真正想要的 Alpha)"),
        (203, "#eef4f8", "行业偏离 +0.6%(超配 / 低配)"),
        (168, "#eef4f8", "风格暴露 +0.4%(大小盘 / 价值成长)"),
        (147, "#ffb4b4", "交易执行(时点)−0.2%"),
        (122, "#ffb4b4", "摩擦成本 −0.5%(佣金·印花税·滑点)"),
    ]
    for y, color, txt in labels:
        parts.append('            <line x1="262" y1="%d" x2="292" y2="%d" stroke="#46587a" stroke-width="1"/>' % (y, y))
        parts.append('            <text x="300" y="%d" fill="%s" font-size="11.5">%s</text>' % (y + 4, color, txt))
    # 右柱:反面例,超额 +2.3% 但行业独占 +1.9%
    parts.append('            <text x="595" y="250" text-anchor="middle" fill="#8499bd" font-size="16" font-weight="800">vs</text>')
    segs2 = [
        (350, 21, "rgba(143,179,122,0.45)", "rgba(143,179,122,0.7)"),    # 选股 +0.3
        (329, 14, "rgba(122,167,240,0.45)", "rgba(122,167,240,0.6)"),    # 风格 +0.2
        (315, 133, "rgba(240,201,106,0.50)", "rgba(240,201,106,0.65)"),  # 行业 +1.9
        (182, 7, "rgba(232,120,120,0.45)", "rgba(232,136,136,0.6)"),     # 成本 -0.1
    ]
    for y0, h, fill, stroke in segs2:
        parts.append('            <rect x="640" y="%d" width="70" height="%d" fill="%s" stroke="%s"/>' % (y0 - h, h, fill, stroke))
    parts.append('            <line x1="640" y1="189" x2="710" y2="189" stroke="#f0c96a" stroke-width="2" stroke-dasharray="6 4"/>')
    parts.append('            <text x="675" y="372" text-anchor="middle" fill="#eef4f8" font-size="12.5" font-weight="800">产品乙:押注中奖</text>')
    parts.append('            <text x="728" y="196" fill="#f0c96a" font-size="12.5" font-weight="800">这只超额 +2.3%</text>')
    parts.append('            <text x="728" y="218" fill="#bcc9dd" font-size="11.5">行业独占 +1.9%</text>')
    parts.append('            <text x="728" y="240" fill="#bcc9dd" font-size="11.5">选股仅 +0.3%</text>')
    parts.append('            <text x="728" y="268" fill="#ffb4b4" font-size="12" font-weight="800">→ 是押注,不是增强</text>')
    parts.append('            ' + svg_text("归因报告就是体检:判断它是不是按承诺的方式在赚钱——超额高不高其次,来源对不对才要紧", 450, 400, 880, size=12, color="#c9d4e8", weight=600, max_chars=44, max_lines=1))
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 420",
        "超额归因堆积柱:产品甲超额+2.1%拆成选股+1.8、行业偏离+0.6、风格暴露+0.4、时点-0.2、成本-0.5;对照产品乙超额+2.3%但行业独占+1.9,选股只有+0.3",
        "把总超额拆成五段:选股 +1.8%、行业偏离 +0.6%、风格暴露 +0.4%、时点 −0.2%、摩擦成本 −0.5%,加起来必须正好等于 +2.1%。对照右边那只:超额 +2.3% 看着更高,可行业偏离独占 +1.9%——那不是增强,是一次押注中奖。")


def _fig_f18_max_drawdown():
    """ch18 最大回撤的测量。锚点:chapter-18.html:151 <h3>2.4. 最大回撤</h3>。
    数字沿用 2.4 正文:净值爬到 1.5 又跌到 1.2,最大回撤 = 1.2/1.5 − 1 = −20%;
    尾巴「跌 50% 要涨 100% 才回本」同为原文。"""
    parts = []
    parts.append('            <text x="450" y="30" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">最大回撤怎么量:净值从 1.5 跌回 1.2,疼多少?</text>')
    parts.append('            <text x="450" y="54" text-anchor="middle" fill="#8499bd" font-size="12.5">最大回撤 = 净值从历史高点跌到之后低点的最大跌幅——人不是从起点看账户,是牢牢记得那个最高点</text>')
    # 坐标轴
    parts.append('            <line x1="120" y1="300" x2="830" y2="300" stroke="#46587a" stroke-width="1.5"/>')
    parts.append('            <line x1="120" y1="300" x2="120" y2="60" stroke="#46587a" stroke-width="1.5"/>')
    parts.append('            <text x="812" y="322" text-anchor="end" fill="#8499bd" font-size="12">时间</text>')
    parts.append('            <text x="96" y="66" text-anchor="end" fill="#8499bd" font-size="12">净值</text>')
    # 净值曲线(0.1 净值 = 32px,1.0 在 y=280)
    parts.append('            <path d="M 150 280 L 230 238 L 310 196 L 390 150 L 480 120 L 560 180 L 640 216 L 720 192 L 800 170" fill="none" stroke="#7aa7f0" stroke-width="3"/>')
    # 高点 1.5 虚线与标记
    parts.append('            <line x1="120" y1="120" x2="480" y2="120" stroke="rgba(240,201,106,0.5)" stroke-width="1.5" stroke-dasharray="6 5"/>')
    parts.append('            <circle cx="480" cy="120" r="5" fill="#f0c96a"/>')
    parts.append('            <text x="112" y="116" text-anchor="end" fill="#f0c96a" font-size="12" font-weight="800">高点 1.5</text>')
    parts.append('            <text x="480" y="98" text-anchor="middle" fill="#f0c96a" font-size="12.5" font-weight="800">你记得的是它</text>')
    # 低点 1.2 虚线与标记
    parts.append('            <line x1="120" y1="216" x2="640" y2="216" stroke="rgba(232,136,136,0.5)" stroke-width="1.5" stroke-dasharray="6 5"/>')
    parts.append('            <circle cx="640" cy="216" r="5" fill="#e88"/>')
    parts.append('            <text x="112" y="212" text-anchor="end" fill="#ffb4b4" font-size="12" font-weight="800">低点 1.2</text>')
    parts.append('            <text x="640" y="242" text-anchor="middle" fill="#ffb4b4" font-size="12">很多人恰恰停在这附近</text>')
    # 起点净值 1.0
    parts.append('            <text x="112" y="276" text-anchor="end" fill="#8499bd" font-size="12">起点 1.0</text>')
    # 落差括号(x=664)
    parts.append('            <line x1="664" y1="120" x2="664" y2="216" stroke="#e88" stroke-width="2"/>')
    parts.append('            <line x1="656" y1="120" x2="672" y2="120" stroke="#e88" stroke-width="2"/>')
    parts.append('            <line x1="656" y1="216" x2="672" y2="216" stroke="#e88" stroke-width="2"/>')
    parts.append('            <text x="684" y="172" fill="#e88" font-size="15" font-weight="800">落差 −20%</text>')
    # 公式卡(左上空白区,避开曲线上升段和高点虚线)
    parts.append('            <rect x="140" y="62" width="300" height="52" rx="10" fill="rgba(18,29,49,0.70)" stroke="rgba(240,201,106,0.42)"/>')
    parts.append('            <text x="156" y="84" fill="#eef4f8" font-size="12.5" font-weight="800">最大回撤 = 低点 ÷ 高点 − 1</text>')
    parts.append('            <text x="156" y="105" fill="#bcc9dd" font-size="12">= 1.2 ÷ 1.5 − 1 = −20%(跌了五分之一)</text>')
    parts.append('            ' + svg_text("拿不拿得住一个策略,看回撤比看收益更准——账面亏的是钱,心里亏的是落差", 450, 338, 880, size=12, color="#c9d4e8", weight=600, max_chars=36, max_lines=1))
    parts.append('            <text x="450" y="364" text-anchor="middle" fill="#f0c96a" font-size="12.5" font-weight="800">复利的尾巴:跌 50%,要涨 100% 才回本;刀砍得越深,爬回来的坡越长</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 380",
        "最大回撤示意:净值曲线从1.0爬到高点1.5后跌到低点1.2,落差括号标-20%,公式为1.2除以1.5减1;复利尾巴是跌50%要涨100%才回本",
        "净值一路爬到 1.5,你还没来得及截图炫耀,它掉头跌到 1.2——最大回撤就是 1.2 ÷ 1.5 − 1 = −20%。拖着一条复利的尾巴:跌 50% 要涨 100% 才回本。控回撤不是为曲线好看,是不让复利被一次深亏拦腰打断。")


def _fig_f19_one_day_timeline():
    """ch19 回测里的一天:T/T+1 时间线。锚点:chapter-19.html:44 <h2>3. 让时间线先立正</h2>。
    四个节点与该时刻「允许看到什么」逐格沿用第 3 节正文表格;
    红色警示为原文「教科书级别未来函数」例。"""
    parts = []
    parts.append('            <text x="450" y="30" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">回测里的一天:T 日算什么,T+1 做什么,钉死不许挪</text>')
    parts.append('            <text x="450" y="54" text-anchor="middle" fill="#8499bd" font-size="12.5">标准做法:每月最后一个交易日收盘后生成信号,下一个交易日才买卖——每个动作只允许看到当时已公开的数据</text>')
    parts.append('            <defs><marker id="f19a" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#7aa7f0"/></marker></defs>')
    cards = [
        ("T 日收盘后", "计算因子和目标组合", "只能见 T 日收盘", "及以前已公开数据"),
        ("T+1 开盘", "按规则提交订单", "不得修改 T 日", "已经确定的信号"),
        ("T+1 盘中", "模拟成交和未成交", "涨跌停 · 停牌", "成交额约束"),
        ("T+1 收盘后", "更新持仓和净值", "成交回报 · 收盘估值", "费用入账"),
    ]
    for i, (head, act, allow1, allow2) in enumerate(cards):
        cx = 132 + i * 212
        parts.append('            <rect x="%d" y="84" width="190" height="132" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>' % (cx - 95))
        parts.append('            <text x="%d" y="112" text-anchor="middle" fill="#f0c96a" font-size="13.5" font-weight="800">%s</text>' % (cx, head))
        parts.append('            <text x="%d" y="146" text-anchor="middle" fill="#eef4f8" font-size="12" font-weight="800">%s</text>' % (cx, act))
        parts.append('            <text x="%d" y="174" text-anchor="middle" fill="#8499bd" font-size="11">%s</text>' % (cx, allow1))
        parts.append('            <text x="%d" y="194" text-anchor="middle" fill="#8499bd" font-size="11">%s</text>' % (cx, allow2))
        if i < 3:
            parts.append('            <path d="M %d 150 L %d 150" stroke="#7aa7f0" stroke-width="2.5" fill="none" marker-end="url(#f19a)"/>' % (cx + 97, cx + 115))
    # 未来函数警示卡
    parts.append('            <rect x="60" y="240" width="780" height="86" rx="12" fill="rgba(232,120,120,0.08)" stroke="rgba(232,136,136,0.5)"/>')
    parts.append('            <text x="88" y="268" fill="#ffb4b4" font-size="13" font-weight="800">教科书级未来函数长这样:</text>')
    parts.append('            <text x="88" y="292" fill="#eef4f8" font-size="12.5">用 T 日收盘价算特征,又假设自己按 T 日收盘价成交</text>')
    parts.append('            <text x="88" y="314" fill="#bcc9dd" font-size="12">= 用收盘后才知道的信息,做了收盘时的决策</text>')
    parts.append('            <circle cx="790" cy="283" r="24" fill="none" stroke="#e88" stroke-width="2.5"/>')
    parts.append('            <text x="790" y="293" text-anchor="middle" fill="#e88" font-size="26" font-weight="800">×</text>')
    parts.append('            ' + svg_text("每次你想按某个价格成交,先问自己:信号是不是也用了这个价格?这个数据在那个时刻真的已经公开了吗?", 450, 354, 880, size=13, color="#c9d4e8", weight=600, max_chars=50, max_lines=1))
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 385",
        "回测单日时间线:T日收盘后计算因子和目标组合(只见T日收盘前公开数据),T+1开盘提交订单(不得改信号),T+1盘中模拟成交受涨跌停停牌成交额约束,T+1收盘后更新持仓净值;红卡警示用T日收盘价又算特征又成交是教科书级未来函数",
        "把这张时间线钉在墙上:T 日收盘后算因子、订目标;T+1 开盘交订单、盘中按涨跌停和成交额约束模拟成交、收盘后再记账。最常见的未来函数就一种长相——用 T 日收盘价算特征,又假设自己按 T 日收盘价成交。")


def _fig_f20_neutral_decompose():
    """ch20 中性组合单日收益拆零件。锚点:chapter-20.html:93 <h3>1.7. 把总收益拆回零件</h3>。
    三段口径沿用 1.7 正文:股票多头收益 + 期货对冲收益 + 现金和费用;
    两张判案卡为原文两类归因情形。数字自洽:+0.40 − 0.25 − 0.03 = +0.12。"""
    parts = []
    parts.append('            <text x="450" y="30" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">中性组合的一天收益,拆回三个零件</text>')
    parts.append('            <text x="450" y="54" text-anchor="middle" fill="#8499bd" font-size="12.5">当日总收益 = 股票多头收益 + 期货对冲收益 + 现金和费用;想更细,再拆行业、风格、选股和基差</text>')
    # 底轴
    parts.append('            <line x1="80" y1="280" x2="830" y2="280" stroke="#46587a" stroke-width="1.5"/>')
    # 瀑布(1% = 200px):多头 +0.40 -> 80px;对冲 −0.25 -> 50px;费用 −0.03 -> 6px;合计 +0.12 -> 24px
    parts.append('            <rect x="132" y="200" width="96" height="80" fill="rgba(143,179,122,0.45)" stroke="rgba(143,179,122,0.7)"/>')
    parts.append('            <rect x="312" y="200" width="96" height="50" fill="rgba(232,120,120,0.40)" stroke="rgba(232,136,136,0.6)"/>')
    parts.append('            <rect x="492" y="250" width="96" height="6" fill="rgba(232,120,120,0.55)" stroke="rgba(232,136,136,0.7)"/>')
    parts.append('            <rect x="672" y="256" width="96" height="24" fill="rgba(240,201,106,0.50)" stroke="rgba(240,201,106,0.65)"/>')
    # 台阶虚线
    parts.append('            <line x1="228" y1="200" x2="312" y2="200" stroke="#8499bd" stroke-width="1" stroke-dasharray="4 4"/>')
    parts.append('            <line x1="408" y1="250" x2="492" y2="250" stroke="#8499bd" stroke-width="1" stroke-dasharray="4 4"/>')
    parts.append('            <line x1="588" y1="256" x2="672" y2="256" stroke="#8499bd" stroke-width="1" stroke-dasharray="4 4"/>')
    # 段标签
    parts.append('            <text x="180" y="188" text-anchor="middle" fill="#eef4f8" font-size="12.5" font-weight="800">股票多头 +0.40%</text>')
    parts.append('            <text x="360" y="188" text-anchor="middle" fill="#eef4f8" font-size="12.5" font-weight="800">期货对冲 −0.25%</text>')
    parts.append('            <line x1="540" y1="248" x2="540" y2="196" stroke="#8499bd" stroke-width="1"/>')
    parts.append('            <text x="540" y="188" text-anchor="middle" fill="#eef4f8" font-size="12.5" font-weight="800">现金和费用 −0.03%</text>')
    parts.append('            <text x="720" y="244" text-anchor="middle" fill="#f0c96a" font-size="12.5" font-weight="800">当日合计 +0.12%</text>')
    # 柱下短名
    parts.append('            <text x="180" y="296" text-anchor="middle" fill="#8499bd" font-size="11">选股赚的</text>')
    parts.append('            <text x="360" y="296" text-anchor="middle" fill="#8499bd" font-size="11">对冲亏的</text>')
    parts.append('            <text x="540" y="296" text-anchor="middle" fill="#8499bd" font-size="11">每天固定扣</text>')
    parts.append('            <text x="720" y="296" text-anchor="middle" fill="#f0c96a" font-size="11">落进口袋的</text>')
    # 两张归因判案卡
    parts.append('            <rect x="50" y="336" width="390" height="64" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(240,201,106,0.42)"/>')
    parts.append('            <text x="66" y="360" fill="#f0c96a" font-size="12" font-weight="800">总收益好,但主要来自期货基差 →</text>')
    parts.append('            <text x="66" y="382" fill="#bcc9dd" font-size="11.5">不是纯选股 Alpha,是基差行情赏的饭</text>')
    parts.append('            <rect x="460" y="336" width="390" height="64" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>')
    parts.append('            <text x="476" y="360" fill="#a8c6ff" font-size="12" font-weight="800">总收益差,但多头跑赢、对冲成本过高 →</text>')
    parts.append('            <text x="476" y="382" fill="#bcc9dd" font-size="11.5">药方是换工具或降成本,不是推翻选股模型</text>')
    parts.append('            ' + svg_text("归因是用来抓说谎的:月度归因累计着看——中性策略的错误,是在多个阶段慢慢暴露的", 450, 420, 880, size=12, color="#c9d4e8", weight=600, max_chars=44, max_lines=1))
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 430",
        "中性组合单日收益瀑布:股票多头+0.40%、期货对冲-0.25%、现金和费用-0.03%,合计+0.12%;两张判案卡:收益好但来自基差不是Alpha,收益差但多头跑赢则问题在对冲成本",
        "每天收益可以拆成三个零件:股票多头 +0.40%、期货对冲 −0.25%、现金和费用 −0.03%,合计 +0.12%。归因用来抓说谎:收益好但主要来自基差,那是行情赏饭;收益差但多头跑赢、只是对冲太贵,药方是换工具降成本,不是推翻选股模型。")


def _fig_f21_cost_erosion():
    """ch21 成本敏感性照妖镜。锚点:chapter-21.html:51 <h3>1.3. 手续费不是小零头</h3>。
    方法沿用 1.3 正文「0 / 1 / 2 / 3 倍成本各跑一遍」;成本清单为原文逐项;
    两策略数字自洽:甲 12 − 7.5k,乙 15 − 6k(k = 成本倍数)。"""
    parts = []
    parts.append('            <text x="450" y="30" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">手续费不是小零头:同一条策略,成本翻几倍就现原形</text>')
    parts.append('            <text x="450" y="54" text-anchor="middle" fill="#8499bd" font-size="12.5">成本敏感性测试:同一策略拿 0 / 1 / 2 / 3 倍成本各跑一遍——健康的策略,成本加一倍还能活</text>')
    parts.append('            <text x="450" y="78" text-anchor="middle" fill="#8499bd" font-size="11.5">成本全家桶:佣金 · 印花税 · 过户费 · 买卖价差 · 滑点 · 冲击成本 · 融资融券 · 期货展期和基差</text>')
    # 零线
    parts.append('            <line x1="60" y1="235" x2="866" y2="235" stroke="#8499bd" stroke-width="1.5"/>')
    parts.append('            <text x="66" y="225" fill="#8499bd" font-size="11">0</text>')
    groups = [
        # (cx, 收益%, 柱高 px@7px/%, 是否非负) 甲:12 - 7.5k;乙:15 - 6k
        [(130, "+12%", 84, 1), (210, "+4.5%", 32, 1), (290, "−3%", 21, 0), (370, "−10.5%", 74, 0)],
        [(520, "+15%", 105, 1), (600, "+9%", 63, 1), (680, "+3%", 21, 1), (760, "−3%", 21, 0)],
    ]
    scale_labels = ["0 成本", "1× 成本", "2× 成本", "3× 成本"]
    for g in groups:
        for i, (cx, lab, h, ok) in enumerate(g):
            x = cx - 28
            if ok:
                y = 235 - h
                parts.append('            <rect x="%d" y="%d" width="56" height="%d" rx="4" fill="rgba(143,179,122,0.45)" stroke="rgba(143,179,122,0.7)"/>' % (x, y, h))
                parts.append('            <text x="%d" y="%d" text-anchor="middle" fill="#8fb37a" font-size="12" font-weight="800">%s</text>' % (cx, y - 8, lab))
            else:
                parts.append('            <rect x="%d" y="235" width="56" height="%d" rx="4" fill="rgba(232,120,120,0.40)" stroke="rgba(232,136,136,0.6)"/>' % (x, h))
                parts.append('            <text x="%d" y="%d" text-anchor="middle" fill="#ffb4b4" font-size="12" font-weight="800">%s</text>' % (cx, 235 + h + 17, lab))
            parts.append('            <text x="%d" y="344" text-anchor="middle" fill="#bcc9dd" font-size="11.5">%s</text>' % (cx, scale_labels[i]))
    parts.append('            <text x="250" y="368" text-anchor="middle" fill="#ffb4b4" font-size="12" font-weight="800">策略甲:毛 +12%,年换手成本约 7.5%/倍 → 一倍就重伤</text>')
    parts.append('            <text x="640" y="368" text-anchor="middle" fill="#8fb37a" font-size="12" font-weight="800">策略乙:毛 +15%,成本约 6%/倍 → 两倍还活着</text>')
    parts.append('            ' + svg_text("回测里少扣 0.05% 看似小数点后的事,高换手策略一年买卖几百回,每回都交一遍过路费", 450, 392, 880, size=12, color="#c9d4e8", weight=600, max_chars=46, max_lines=1))
    parts.append('            <text x="450" y="414" text-anchor="middle" fill="#f0c96a" font-size="13.5" font-weight="800">只在 0 成本下赚钱的策略,赚的不是市场的钱,是你少扣的钱</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 420",
        "成本敏感性对比:策略甲毛收益+12%,1倍成本剩+4.5%,2倍变-3%,3倍-10.5%;策略乙毛+15%,1倍+9%,2倍+3%,3倍才转负;成本清单含佣金印花税过户费价差滑点冲击融资融券展期基差",
        "同一策略按 0、1、2、3 倍成本各跑一遍:甲毛收益 +12%,一倍成本只剩 +4.5%,两倍转负;乙毛 +15%,两倍成本还有 +3%。成本远不只是佣金——印花税、过户费、买卖价差、滑点、冲击、融资融券、展期基差,每一项单看不起眼,加起来足够吃掉一整个策略。")


def _fig_f22_strip_curve():
    """ch22 拆穿漂亮曲线的十步检查顺序。锚点:chapter-22.html:101 <h3>2.8. 复盘顺序</h3>。
    故事数字沿用 2.1 原文(年化 45%、回撤 8%、夏普 2 以上),
    修正账沿用 2.7 原文(年化 8%~12%、回撤约 25%),十步为 2.8 原文顺序。"""
    parts = []
    parts.append('            <text x="450" y="30" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">一条漂亮回测曲线,照这个顺序被拆穿</text>')
    # 左上:故事卡
    parts.append('            <rect x="40" y="58" width="410" height="80" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(240,201,106,0.42)"/>')
    parts.append('            <text x="58" y="82" fill="#f0c96a" font-size="12" font-weight="800">故事:月频 · 过去 20 日涨幅选 30 只 · 十年回测</text>')
    badges = [("年化 +45%", "#f0c96a"), ("回撤仅 8%", "#a8c6ff"), ("夏普 > 2", "#a8c6ff")]
    for i, (b, c) in enumerate(badges):
        bx = 58 + i * 126
        parts.append('            <rect x="%d" y="94" width="114" height="32" rx="8" fill="rgba(122,167,240,0.10)" stroke="rgba(122,167,240,0.30)"/>' % bx)
        parts.append('            <text x="%d" y="115" text-anchor="middle" fill="%s" font-size="12.5" font-weight="800">%s</text>' % (bx + 57, c, b))
    # 右上:修正总账卡
    parts.append('            <rect x="470" y="58" width="390" height="80" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>')
    parts.append('            <text x="488" y="82" fill="#a8c6ff" font-size="12" font-weight="800">剔完假收益,盘一下总账:</text>')
    parts.append('            <text x="488" y="104" fill="#eef4f8" font-size="12.5" font-weight="800">年化 8%~12% · 回撤约 25% · 样本外不稳</text>')
    parts.append('            <text x="488" y="126" fill="#bcc9dd" font-size="11">还能当一个偏弱动量信号,进多因子模型尽一份力</text>')
    steps = [
        ("股票池", "是否点时"), ("数据在当时", "是否可见"), ("信号与成交", "时点对吗"), ("成本", "是否完整"), ("涨跌停·停牌", "T+1 处理了吗"),
        ("容量假设", "合理吗"), ("参数", "是否稳定"), ("样本外留了没", "有没有污染"), ("收益集中在", "少数年份吗"), ("风险暴露", "能解释吗"),
    ]
    for i, (s1, s2) in enumerate(steps):
        row = i // 5
        col = i % 5
        cx = 102 + col * 168
        y = 162 + row * 84
        parts.append('            <rect x="%d" y="%d" width="150" height="72" rx="10" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>' % (cx - 75, y))
        parts.append('            <circle cx="%d" cy="%d" r="10" fill="rgba(240,201,106,0.85)"/>' % (cx - 59, y + 16))
        parts.append('            <text x="%d" y="%d" text-anchor="middle" fill="#101420" font-size="11" font-weight="900">%d</text>' % (cx - 59, y + 20, i + 1))
        parts.append('            <text x="%d" y="%d" text-anchor="middle" fill="#eef4f8" font-size="11" font-weight="700">%s</text>' % (cx + 8, y + 40, s1))
        parts.append('            <text x="%d" y="%d" text-anchor="middle" fill="#bcc9dd" font-size="11">%s</text>' % (cx + 8, y + 58, s2))
    parts.append('            ' + svg_text("这个顺序比闷头调模型有用:把假收益一样一样剔掉,剔完还活着的,才值得被复杂化", 450, 352, 880, size=12, color="#c9d4e8", weight=600, max_chars=38, max_lines=1))
    parts.append('            <text x="450" y="378" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">你不是从 45% 亏到 8%——是从假的好结果,走到了真的普通结果</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 395",
        "拆穿漂亮回测曲线十步顺序:股票池点时、数据当时可见、信号与成交时点、成本完整、涨跌停停牌T加1、容量、参数稳定、样本外、收益集中度、风险暴露解释;故事卡年化45%回撤8%夏普大于2,修正后年化8%至12%回撤约25%",
        "十年回测年化 45%、回撤 8%、夏普 2 以上——第一反应不该是庆祝,而该按十步顺序查:股票池、数据可见性、成交时点、成本、交易规则、容量、参数、样本外、收益集中度、风险解释。剔完假收益还剩年化 8%~12%、回撤约 25%:普通但真实,永远比惊艳但虚假值钱。")


PATCH_F = {
    23: [("研究员每天在做什么", _fig_f12_researcher_loop)],
    27: [("业绩归因报告怎么看", _fig_f16_attribution_bar)],
    28: [("最大回撤", _fig_f18_max_drawdown)],
    29: [("让时间线先立正", _fig_f19_one_day_timeline)],
    30: [("把总收益拆回零件", _fig_f20_neutral_decompose)],
    31: [("手续费不是小零头", _fig_f21_cost_erosion)],
    32: [("复盘顺序", _fig_f22_strip_curve)],
}
# -*- coding: utf-8 -*-
"""概念图 batch G(ch23-ch32 每章各加 1 张,合计 10 张)。

交付约定(与 build_book.py 现有 _fig_xxx / PATCH_C / PATCH_D 一致):
- 纯字符串拼接,不含 f-string;body 用 % 或字符串加号组拼。
- 每张图通过 concept_figure(body, "0 0 900 高", aria, cap) 收尾,
  内部混用 svg_text(...) 与手写 <text>(svg_text 的 x 为中心点)。
- 调色板与全书一致;禁用暖米色底。
- viewBox 高度 280~480;x 类坐标与 path d 数字均 <= 890。

锚点关键词:全部是「小节标题文字片段」的子串(h3 的 x.y. 编号不算),
且已逐一 grep 验证在本章小节标题中唯一。本批 10 章此前每章各已挂一张图
(见 CONCEPT_FIGURES_FREE),本批全部另选小节、另选主题,不重复已覆盖内容:

  ch23 已有「十层金字塔」@真实财富和生产力 -> 本批:回测查错老顺序七刀
  ch24 已有「三个作品集」@指数增强回测     -> 本批:可信回测报告 12 栏目 + 复盘四问
  ch25 已有「二十个词速查」@货币           -> 本批:风控 11 件家伙各管一类失控
  ch26 已有「资产三口袋」@总资产不是可花的钱 -> 本批:月报风险指标六格 + 回撤 20% 算例
  ch27 已有「模拟盘一周」@数据没有按时到    -> 本批:收益/回撤两策略并排对比
  ch28 已有「三层护栏」@先定资金上限        -> 本批:小实盘毕业评审四象限
  ch29 已有「18 道关」@能解释钱和财富的区别 -> 本批:成本九项清单 + 敏感性四档
  ch30 已有「七步翻车」@他先找模型          -> 本批:胜率错觉(90% 亏钱 vs 40% 赚钱)
  ch31 已有「八步流水线」@问题很小          -> 本批:单因子档案六栏 + 三因子性格
  ch32 已有「六道闸」@问题是否足够小        -> 本批:停止规则三行表(触发/动作/恢复)
"""

try:
    from build_book import concept_figure, svg_text
except ImportError:
    # 预览/测试时由 harness 注入 build_book.concept_figure / build_book.svg_text
    concept_figure = None
    svg_text = None


def _fig_g23_backtest_audit():
    """ch23 §7 回测和验证:看到漂亮曲线先按老顺序查错的七刀。"""
    rows = [
        ("股票池是不是点时", "按当时的成分名单,不许拿今天的名单回填历史", "#7aa7f0"),
        ("成交价有没有偷看", "信号日和成交日要错开,当天收盘价不许当天用", "#7aa7f0"),
        ("成本是否完整", "佣金、滑点、冲击缺一项,纸面收益就虚高一截", "#7aa7f0"),
        ("涨跌停停牌处理没有", "买不进、卖不出的日子,不许假装成交", "#f0c96a"),
        ("容量合不合理", "小资金做出来的成绩,不能原样平移到大资金", "#f0c96a"),
        ("参数是不是过拟合", "试了无数次留下的「最佳」,先打问号再上桌", "#f0c96a"),
        ("样本外有没有被污染", "反复看测试集回头改策略,测试集就进了回路", "#e88"),
    ]
    parts = []
    parts.append('            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">看到漂亮曲线先别鼓掌:按老顺序查错,七刀砍完再谈好不好</text>')
    parts.append('            <text x="450" y="58" text-anchor="middle" fill="#8499bd" font-size="12.5">回测是在历史里排练,不是对未来的证明;查错顺序对应前面拆穿漂亮曲线的那几章</text>')
    parts.append('            <line x1="56" y1="106" x2="56" y2="394" stroke="rgba(122,167,240,0.28)" stroke-width="2" stroke-dasharray="5 5"/>')
    for i, (t, d, c) in enumerate(rows):
        y = 80 + i * 48
        cy = y + 26
        parts.append('            <rect x="28" y="%d" width="844" height="40" rx="10" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>' % y)
        parts.append('            <circle cx="56" cy="%d" r="13" fill="#101d33" stroke="%s" stroke-width="1.5"/>' % (cy, c))
        parts.append('            <text x="56" y="%d" text-anchor="middle" fill="%s" font-size="13" font-weight="800">%d</text>' % (cy + 5, c, i + 1))
        parts.append('            ' + svg_text(t, 190, cy + 1, 210, size=13.5, color="#eef4f8", weight=800, max_chars=10, max_lines=1))
        parts.append('            <text x="318" y="%d" fill="#8499bd" font-size="12">%s</text>' % (cy + 5, d))
    parts.append('            <text x="450" y="438" text-anchor="middle" fill="#f0c96a" font-size="13.5" font-weight="800">验证的目标不是保住最漂亮的曲线,是把不真实的收益一样样剔掉——剔完还留在桌上的,才可能是真优势</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 452",
        "回测查错七刀:按顺序检查股票池是否点时、成交价有没有偷看、成本是否完整、涨跌停停牌处理、容量合理性、参数过拟合、样本外污染",
        "看到漂亮回测,先按老顺序查错:股票池是不是点时、成交价有没有偷看、成本是否完整、涨跌停停牌处理没有、容量合不合理、参数是不是过拟合、样本外有没有被污染。查完错的曲线,才有资格谈好不好。")


def _fig_g24_report_lines():
    """ch24 §2.4:一份可信回测报告的 12 个栏目,外加复盘四问。"""
    tiles = [
        ("净值", "策略自己的曲线"),
        ("基准", "超额的对照物"),
        ("超额", "比基准多赚的"),
        ("回撤", "从峰值摔下多疼"),
        ("年化", "拉平时间的外推"),
        ("波动", "一路上有多颠"),
        ("夏普", "每份波动换多少"),
        ("换手", "策略有多爱交易"),
        ("成本", "扣完还剩多少"),
        ("年度收益", "按年拆开看"),
        ("月度收益", "逐月看稳定性"),
        ("持仓暴露", "组合押在什么上"),
    ]
    qs = [
        "① 它在哪些环境有效",
        "② 它在哪些地方失效",
        "③ 它对哪个假设最敏感",
        "④ 这条路值不值得继续",
    ]
    parts = []
    parts.append('            <text x="450" y="30" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">可信回测报告的底线:自动生成,12 个栏目一个不能少</text>')
    parts.append('            <text x="450" y="56" text-anchor="middle" fill="#8499bd" font-size="12.5">报告不许手工拼图;没有它,视线会自动粘在信息密度最低的那个数——总收益上</text>')
    for i, (name, note) in enumerate(tiles):
        col = i % 4
        row = i // 4
        x = 40 + col * 208
        y = 76 + row * 64
        parts.append('            <rect x="%d" y="%d" width="196" height="56" rx="10" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>' % (x, y))
        parts.append('            ' + svg_text(name, x + 98, y + 22, 176, size=13.5, color="#a8c6ff", weight=800, max_chars=8, max_lines=1))
        parts.append('            <text x="%d" y="%d" text-anchor="middle" fill="#bcc9dd" font-size="11">%s</text>' % (x + 98, y + 42, note))
    parts.append('            <text x="450" y="290" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">跑完不算完:复盘再答四个扎心问题</text>')
    for i, q in enumerate(qs):
        x = 40 + i * 208
        parts.append('            <rect x="%d" y="304" width="196" height="46" rx="10" fill="rgba(240,201,106,0.07)" stroke="rgba(240,201,106,0.42)"/>' % x)
        parts.append('            ' + svg_text(q, x + 98, 328, 180, size=12.5, color="#f0c96a", weight=800, max_chars=11, max_lines=1))
    parts.append('            <text x="450" y="388" text-anchor="middle" fill="#c9d4e8" font-size="13">答完这四问,才算「做完」回测,而不只是「跑完」回测</text>')
    parts.append('            <text x="450" y="414" text-anchor="middle" fill="#8499bd" font-size="12">第一份报告策略越简单越好:复杂度不是重点,可信度才是</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 440",
        "回测报告必备十二栏目:净值、基准、超额、回撤、年化、波动、夏普、换手、成本、年度收益、月度收益、持仓暴露;跑完后复盘回答四问:哪些环境有效、哪里失效、对哪个假设最敏感、值不值得继续",
        "第一份可信的回测报告要自动生成、不许手工拼图,至少摆齐净值、基准、超额、回撤、年化、波动、夏普、换手、成本、年度收益、月度收益和持仓暴露十二个栏目;跑完再回答四问——哪里有效、哪里失效、对什么假设敏感、值不值得继续,答完才算「做完」回测。")


def _fig_g25_risk_toolbox():
    """ch25 §2.10 风控:一整套家伙,每件对应一类具体的失控方式。"""
    row1 = [
        ("仓位", "管押多大"),
        ("杠杆", "管放大几倍"),
        ("个股上限", "管单票爆雷"),
        ("行业上限", "管押单一赛道"),
        ("回撤", "管从峰值亏多深"),
    ]
    row2 = [
        ("VaR", "管常态日子亏多少"),
        ("压力测试", "管极端行情亏多惨"),
        ("数据监控", "管喂错的料"),
        ("模型监控", "管信号悄悄漂移"),
        ("订单限额", "管一笔错单闯多大祸"),
    ]
    parts = []
    parts.append('            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">风控不预测明天跌不跌:它是熔断器和监控告警</text>')
    parts.append('            <rect x="60" y="54" width="780" height="40" rx="10" fill="rgba(18,29,49,0.70)" stroke="rgba(240,201,106,0.42)"/>')
    parts.append('            <text x="450" y="79" text-anchor="middle" fill="#c9d4e8" font-size="13">不预测事故——事故一旦发生,先把火情控制住,把信息亮出来,让异常可见、可处理</text>')
    for row, items in enumerate([row1, row2]):
        y = 112 + row * 88
        for i, (name, job) in enumerate(items):
            x = 41 + i * 166
            parts.append('            <rect x="%d" y="%d" width="154" height="76" rx="10" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>' % (x, y))
            parts.append('            ' + svg_text(name, x + 77, y + 28, 134, size=13.5, color="#a8c6ff", weight=800, max_chars=6, max_lines=1))
            parts.append('            ' + svg_text(job, x + 77, y + 54, 134, size=11, color="#bcc9dd", weight=400, max_chars=9, max_lines=1))
    parts.append('            <rect x="180" y="292" width="540" height="56" rx="12" fill="rgba(240,201,106,0.07)" stroke="rgba(240,201,106,0.42)"/>')
    parts.append('            ' + svg_text("灾难开关 · 管「先拉闸再说」", 450, 312, 480, size=13.5, color="#f0c96a", weight=800, max_chars=16, max_lines=1))
    parts.append('            <text x="450" y="334" text-anchor="middle" fill="#bcc9dd" font-size="11.5">不管原因先把交易停下来——像烟雾报警器响,响不是失败,是防护还在工作</text>')
    parts.append('            <text x="450" y="382" text-anchor="middle" fill="#c9d4e8" font-size="13">好风控不是让策略不亏——那不叫风控,叫许愿;它要的是亏得明明白白,停得有条不紊</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 400",
        "风控工具箱:仓位、杠杆、个股上限、行业上限、回撤、VaR、压力测试、数据监控、模型监控、订单限额各管一类失控,灾难开关管先拉闸再说",
        "风控不是预测明天跌不跌,而是一整套家伙:仓位管押多大,限额管一笔错单闯多大祸,灾难开关管先拉闸再说——每一件都对应一类具体的失控方式。目标是策略在亏损和异常发生时不失控:亏得明明白白,停得有条不紊。")


def _fig_g26_risk_metrics():
    """ch26 §2.4 看风险指标:六个指标 + 最大回撤 20% 亲手算一遍。"""
    tiles = [
        ("最大回撤", "从峰值摔下", "那一下有多疼"),
        ("波动率", "赚钱的路上", "有多颠簸"),
        ("夏普比率", "每份波动", "换多少收益"),
        ("卡玛比率", "每份回撤", "换多少年化"),
        ("跟踪误差", "偏离基准", "有多远"),
        ("信息比率", "每单位偏离", "换多少超额"),
    ]
    parts = []
    parts.append('            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">月报风险指标别光看:峰值 1.5 跌到 1.2,回撤自己算一遍</text>')
    # 左卡:回撤算例
    parts.append('            <rect x="40" y="64" width="430" height="240" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>')
    parts.append('            ' + svg_text("最大回撤 =(峰值 − 谷底)÷ 峰值", 255, 92, 380, size=14, color="#a8c6ff", weight=800, max_chars=19, max_lines=1))
    parts.append('            <path d="M 80 158 L 170 134 L 350 226 L 425 188" fill="none" stroke="#7aa7f0" stroke-width="2.5"/>')
    parts.append('            <line x1="80" y1="134" x2="425" y2="134" stroke="#f0c96a" stroke-width="1.2" stroke-dasharray="5 4"/>')
    parts.append('            <circle cx="170" cy="134" r="5" fill="#f0c96a"/>')
    parts.append('            <text x="170" y="120" text-anchor="middle" fill="#f0c96a" font-size="12.5" font-weight="800">净值最高 1.5</text>')
    parts.append('            <circle cx="350" cy="226" r="5" fill="#e88"/>')
    parts.append('            <text x="350" y="252" text-anchor="middle" fill="#ffb4b4" font-size="12.5" font-weight="800">后来跌到 1.2</text>')
    parts.append('            <path d="M 170 144 L 170 217" stroke="#e88" stroke-width="1.5" stroke-dasharray="4 4"/>')
    parts.append('            <text x="150" y="182" text-anchor="end" fill="#ffb4b4" font-size="11.5">亏掉 0.3</text>')
    parts.append('            <text x="255" y="284" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">(1.5 − 1.2) ÷ 1.5 = 回撤 20%</text>')
    # 右侧六格
    for i, (name, l1, l2) in enumerate(tiles):
        col = i % 2
        row = i // 2
        x = 490 + col * 191
        y = 64 + row * 84
        parts.append('            <rect x="%d" y="%d" width="179" height="74" rx="10" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>' % (x, y))
        parts.append('            ' + svg_text(name, x + 89, y + 23, 159, size=13, color="#a8c6ff", weight=800, max_chars=6, max_lines=1))
        parts.append('            <text x="%d" y="%d" text-anchor="middle" fill="#bcc9dd" font-size="10.5">%s</text>' % (x + 89, y + 46, l1))
        parts.append('            <text x="%d" y="%d" text-anchor="middle" fill="#bcc9dd" font-size="10.5">%s</text>' % (x + 89, y + 63, l2))
    # 底部两卡
    parts.append('            <rect x="40" y="322" width="400" height="62" rx="10" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>')
    parts.append('            <text x="240" y="346" text-anchor="middle" fill="#c9d4e8" font-size="12">按策略类型读:CTA 的回撤形态和指增长得不一样</text>')
    parts.append('            <text x="240" y="368" text-anchor="middle" fill="#c9d4e8" font-size="12">市场中性波动应相对低——读出来高了要警觉</text>')
    parts.append('            <rect x="460" y="322" width="400" height="62" rx="10" fill="rgba(240,201,106,0.07)" stroke="rgba(240,201,106,0.42)"/>')
    parts.append('            <text x="660" y="346" text-anchor="middle" fill="#f0c96a" font-size="12" font-weight="800">闭眼想象:这是你的账户,从峰值眼睁睁亏两成</text>')
    parts.append('            <text x="660" y="368" text-anchor="middle" fill="#f0c96a" font-size="12" font-weight="800">拿不住,这个产品的风险对你就超标</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 400",
        "基金月报风险指标:最大回撤、波动率、夏普比率、卡玛比率、跟踪误差、信息比率;最大回撤算例为净值从峰值1.5跌到1.2,回撤等于(1.5减1.2)除以1.5等于百分之二十",
        "风险指标都在回答两件朴素的事:赚钱的过程稳不稳,相对基准跑偏多少。最大回撤要亲手算——净值从 1.5 跌到 1.2,回撤就是 (1.5−1.2)÷1.5 = 20%;再闭眼想想:真钱从峰值亏两成,你拿不拿得住。")


def _fig_g27_two_funds():
    """ch27 §1.5 看收益和回撤:年化20/回撤40 vs 年化12/回撤8 并排。"""
    parts = []
    parts.append('            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">收益高不代表「更好」,只代表「更陡」:两个策略并排看</text>')
    cards = [
        (40, "策略甲 · 陡而痛", 140, 280, "20%", "40%", "适合扛得住账户接近腰斩的人", "#7aa7f0"),
        (460, "策略乙 · 缓而稳", 84, 56, "12%", "8%", "适合要睡安稳觉的人", "#f0c96a"),
    ]
    for x0, name, wg, wr, vg, vr, note, hc in cards:
        parts.append('            <rect x="%d" y="60" width="400" height="176" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>' % x0)
        parts.append('            ' + svg_text(name, x0 + 200, 86, 360, size=14.5, color=hc, weight=800, max_chars=16, max_lines=1))
        parts.append('            <text x="%d" y="122" fill="#c9d4e8" font-size="12">年化收益</text>' % (x0 + 14))
        parts.append('            <rect x="%d" y="108" width="280" height="18" rx="9" fill="rgba(122,167,240,0.14)"/>' % (x0 + 96))
        parts.append('            <rect x="%d" y="108" width="%d" height="18" rx="9" fill="#7aa7f0"/>' % (x0 + 96, wg))
        parts.append('            <text x="%d" y="122" fill="#eef4f8" font-size="12" font-weight="800">%s</text>' % (x0 + 96 + wg + 10, vg))
        parts.append('            <text x="%d" y="166" fill="#c9d4e8" font-size="12">最大回撤</text>' % (x0 + 14))
        parts.append('            <rect x="%d" y="152" width="280" height="18" rx="9" fill="rgba(232,136,136,0.14)"/>' % (x0 + 96))
        parts.append('            <rect x="%d" y="152" width="%d" height="18" rx="9" fill="#e88"/>' % (x0 + 96, wr))
        if vr == "40%":
            parts.append('            <text x="%d" y="166" text-anchor="end" fill="#101d33" font-size="12" font-weight="800">%s</text>' % (x0 + 96 + wr - 10, vr))
        else:
            parts.append('            <text x="%d" y="166" fill="#ffb4b4" font-size="12" font-weight="800">%s</text>' % (x0 + 96 + wr + 10, vr))
        parts.append('            <text x="%d" y="204" text-anchor="middle" fill="#8499bd" font-size="12">%s</text>' % (x0 + 200, note))
        parts.append('            <text x="%d" y="224" text-anchor="middle" fill="#bcc9dd" font-size="11">回撤刻度:0 ───────── 40%%</text>' % (x0 + 200))
    parts.append('            <rect x="40" y="256" width="400" height="64" rx="10" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>')
    parts.append('            <text x="240" y="280" text-anchor="middle" fill="#a8c6ff" font-size="12.5" font-weight="800">看收益四个刻度:累计 · 年化 · 年度 · 月度</text>')
    parts.append('            <text x="240" y="302" text-anchor="middle" fill="#bcc9dd" font-size="11.5">年度收益表能拆穿「收益集中在某一年」的曲线</text>')
    parts.append('            <rect x="460" y="256" width="400" height="64" rx="10" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>')
    parts.append('            <text x="660" y="280" text-anchor="middle" fill="#a8c6ff" font-size="12.5" font-weight="800">看回撤三个维度:跌多深 · 持续多久 · 修复多长</text>')
    parts.append('            <text x="660" y="302" text-anchor="middle" fill="#bcc9dd" font-size="11.5">只盯最终收益,是只看了记分牌,错过整场比赛</text>')
    parts.append('            <text x="450" y="356" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">年化 20% 回撤 40% 和年化 12% 回撤 8%,哪个好?看你的心脏</text>')
    parts.append('            <text x="450" y="382" text-anchor="middle" fill="#c9d4e8" font-size="12.5">你能不能承受这条路径,才是属于你的指标</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 396",
        "两个策略并排对比:策略甲年化收益百分之二十、最大回撤百分之四十,策略乙年化收益百分之十二、最大回撤百分之八;看收益要四个刻度,看回撤要三个维度",
        "报告里把两个策略并排:年化 20%、最大回撤 40%,和年化 12%、最大回撤 8%——哪个好,看你的心脏。收益看四个刻度(累计、年化、年度、月度),回撤看三个维度(多深、持续多久、修复多长);只盯终点,是只看了比赛的记分牌。")


def _fig_g28_graduation_matrix():
    """ch28 §8:小实盘毕业评审,流程稳不稳 × 账户赚不赚四象限。"""
    quads = [
        (150, 88, "rgba(132,153,189,0.35)", "#bcc9dd", "流程乱 + 亏钱",
         "整套退回模拟盘重练", "错上加错,归因都归不了"),
        (490, 88, "#e88", "#ffb4b4", "流程乱 + 赚钱",
         "运气成分大,千万别放大资金", "流程乱时的盈利,下一笔未必客气"),
        (150, 204, "rgba(122,167,240,0.45)", "#a8c6ff", "流程稳 + 亏钱",
         "系统合格,问题在策略本身", "不用动系统,继续改策略就好"),
        (490, 204, "#8fb37a", "#8fb37a", "流程稳 + 赚钱",
         "四项齐备,小实盘才算毕业", "此时才谈得上放大——仍按事先规则"),
    ]
    chips = ["① 流程稳定", "② 风险可控", "③ 成本符合预期", "④ 管住手按规则执行"]
    parts = []
    parts.append('            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">小实盘毕业评审:流程稳不稳 × 账户赚不赚,四象限分开诊断</text>')
    parts.append('            <text x="310" y="76" text-anchor="middle" fill="#ffb4b4" font-size="13" font-weight="800">账户亏钱</text>')
    parts.append('            <text x="650" y="76" text-anchor="middle" fill="#8fb37a" font-size="13" font-weight="800">账户赚钱</text>')
    parts.append('            <text x="134" y="144" text-anchor="end" fill="#8499bd" font-size="12.5" font-weight="800">流程混乱</text>')
    parts.append('            <text x="134" y="260" text-anchor="end" fill="#8499bd" font-size="12.5" font-weight="800">流程稳定</text>')
    for x, y, sc, tc, head, verdict, note in quads:
        parts.append('            <rect x="%d" y="%d" width="330" height="104" rx="12" fill="rgba(18,29,49,0.70)" stroke="%s"/>' % (x, y, sc))
        parts.append('            ' + svg_text(head, x + 165, y + 28, 290, size=14, color=tc, weight=800, max_chars=12, max_lines=1))
        parts.append('            ' + svg_text(verdict, x + 165, y + 58, 290, size=12.5, color="#eef4f8", weight=800, max_chars=15, max_lines=1))
        parts.append('            ' + svg_text(note, x + 165, y + 84, 290, size=11, color="#8499bd", weight=400, max_chars=16, max_lines=1))
    parts.append('            <text x="450" y="344" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">毕业线:四件事同时成立,缺哪项先补哪项——别拿盈利替流程缺陷盖章</text>')
    for i, c in enumerate(chips):
        x = 40 + i * 208
        parts.append('            <rect x="%d" y="358" width="196" height="46" rx="10" fill="rgba(240,201,106,0.07)" stroke="rgba(240,201,106,0.42)"/>' % x)
        parts.append('            ' + svg_text(c, x + 98, 382, 176, size=12.5, color="#f0c96a", weight=800, max_chars=11, max_lines=1))
    parts.append('            <text x="450" y="436" text-anchor="middle" fill="#8499bd" font-size="12">评审另有一串流程指标:信号按时生成?订单按计划执行?真实成本差多少?未成交占比多高?对账一致吗?手痒干预了几次?</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 448",
        "小实盘验收四象限:流程乱亏钱退回模拟盘,流程乱赚钱是运气别放大,流程稳亏钱说明系统合格回去改策略,流程稳赚钱且流程稳定、风险可控、成本符合预期、能管住手才算毕业",
        "小实盘跑了足够长,验收别只盯盈亏:流程稳定但策略亏,说明系统合格、问题在策略;策略赚了但流程一团糟,运气成分大,千万别放大资金。通过线是四件事同时成立——流程稳定、风险可控、成本符合预期、能管住手按规则执行。")


def _fig_g29_cost_stress():
    """ch29 §2.5 成本必须做敏感性:九项清单 + 0/1/2/3 倍四档并排。"""
    items = ["佣金", "印花税", "过户费", "买卖价差", "滑点", "市场冲击", "融资成本", "融券成本", "合约展期"]
    bars = [
        ("无成本", 250, "#7aa7f0", "12%"),
        ("1× 正常成本", 167, "#a8c6ff", "8%"),
        ("2× 成本", 83, "#f0c96a", "4%"),
        ("3× 成本", 11, "#e88", "0.5%"),
    ]
    parts = []
    parts.append('            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">成本不是报表末尾的小数点,是一张九项开支清单</text>')
    parts.append('            <rect x="40" y="64" width="296" height="268" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>')
    parts.append('            ' + svg_text("每一项都在啃净收益", 188, 92, 260, size=13.5, color="#a8c6ff", weight=800, max_chars=11, max_lines=1))
    for i, it in enumerate(items):
        col = i % 3
        row = i // 3
        x = 58 + col * 92
        y = 110 + row * 70
        parts.append('            <rect x="%d" y="%d" width="80" height="56" rx="9" fill="rgba(122,167,240,0.08)" stroke="rgba(122,167,240,0.22)"/>' % (x, y))
        parts.append('            ' + svg_text(it, x + 40, y + 34, 68, size=12.5, color="#eef4f8", weight=800, max_chars=4, max_lines=1))
    parts.append('            <rect x="360" y="64" width="500" height="268" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(240,201,106,0.42)"/>')
    parts.append('            ' + svg_text("最低标准:同一报告摆四档成本(示意)", 610, 92, 460, size=13.5, color="#f0c96a", weight=800, max_chars=23, max_lines=1))
    for i, (lab, w, c, v) in enumerate(bars):
        y = 116 + i * 46
        parts.append('            <text x="382" y="%d" fill="#c9d4e8" font-size="12.5">%s</text>' % (y + 16, lab))
        parts.append('            <rect x="556" y="%d" width="264" height="20" rx="10" fill="rgba(122,167,240,0.12)"/>' % y)
        parts.append('            <rect x="556" y="%d" width="%d" height="20" rx="10" fill="%s"/>' % (y, max(w, 11), c))
        parts.append('            <text x="%d" y="%d" fill="#eef4f8" font-size="12.5" font-weight="800">%s</text>' % (556 + w + 14 if w > 30 else 556 + 26, y + 16, v))
    parts.append('            <text x="610" y="308" text-anchor="middle" fill="#8499bd" font-size="11.5">刻度 0 ── 12%;数字仅示意,换成你自己策略的实测四档再来排</text>')
    parts.append('            <rect x="60" y="352" width="780" height="56" rx="12" fill="rgba(232,136,136,0.07)" stroke="rgba(232,136,136,0.45)"/>')
    parts.append('            <text x="450" y="376" text-anchor="middle" fill="#ffb4b4" font-size="13" font-weight="800">试金石:成本假设翻一倍,策略就由盈转亏 → 边际薄得像纸,可以继续研究,别当强策略宣称</text>')
    parts.append('            <text x="450" y="398" text-anchor="middle" fill="#c9d4e8" font-size="12.5">一条曲线扛住几倍成本还剩多少收益,是策略成色的第一道公开检验</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 424",
        "交易成本九项清单:佣金、印花税、过户费、买卖价差、滑点、市场冲击、融资成本、融券成本、合约展期;敏感性最低标准是同一份报告并列展示无成本、一倍、两倍、三倍成本下的结果",
        "成本清单有九项:佣金、印花税、过户费、买卖价差、滑点、市场冲击、融资成本、融券成本、合约展期,每一项都在啃净收益。最低标准是同一份报告并列摆出无成本、一倍、两倍、三倍成本四档结果——成本翻一倍就由盈转亏的策略,边际薄得像纸。")


def _fig_g30_winrate_trap():
    """ch30 §1.7:胜率最会骗人——90% 亏钱 vs 40% 赚钱,十笔记账。"""
    cards = [
        (40, "策略甲 · 胜率 90%", "#ffb4b4", "十次赚小钱,一次亏大的",
         9, "9×(+1%) + 1×(−12%) = −3%", "#e88",
         "小赚大亏:卖期权式形态,一次极端行情收走多年收益"),
        (460, "策略乙 · 胜率 40%", "#8fb37a", "亏的次数多但每次小,赢的次数少但每次大",
         4, "4×(+2%) + 6×(−0.5%) = +5%", "#8fb37a",
         "趋势策略常态:胜率四成出头,盈利靠少数几波大趋势"),
    ]
    chips = ["期望值", "盈亏比", "最大回撤", "尾部风险", "杠杆"]
    parts = []
    parts.append('            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">胜率最会骗人:90% 胜率亏钱,40% 胜率赚钱</text>')
    for x0, head, hc, sub, wins, formula, fc, verdict in cards:
        parts.append('            <rect x="%d" y="60" width="400" height="200" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>' % x0)
        parts.append('            ' + svg_text(head, x0 + 200, 88, 360, size=15, color=hc, weight=800, max_chars=16, max_lines=1))
        parts.append('            ' + svg_text(sub, x0 + 200, 112, 360, size=11.5, color="#8499bd", weight=400, max_chars=20, max_lines=1))
        for i in range(10):
            sx = x0 + 33 + i * 35
            c = "#8fb37a" if i < wins else "#e88"
            parts.append('            <rect x="%d" y="126" width="28" height="26" rx="5" fill="%s"/>' % (sx, c))
        parts.append('            <text x="%d" y="172" fill="#8499bd" font-size="11">10 笔账,绿赢红亏</text>' % (x0 + 40))
        parts.append('            <text x="%d" y="198" text-anchor="middle" fill="%s" font-size="14" font-weight="800">%s</text>' % (x0 + 200, fc, formula))
        parts.append('            ' + svg_text(verdict, x0 + 200, 232, 360, size=11.5, color="#c9d4e8", weight=400, max_chars=22, max_lines=1))
    parts.append('            <text x="450" y="288" text-anchor="middle" fill="#a8c6ff" font-size="13.5" font-weight="800">评价策略至少摆五件套,缺一个维度结论都可能翻转</text>')
    for i, c in enumerate(chips):
        x = 56 + i * 160
        parts.append('            <rect x="%d" y="302" width="148" height="42" rx="10" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>' % x)
        parts.append('            ' + svg_text(c, x + 74, 324, 128, size=13, color="#a8c6ff", weight=800, max_chars=5, max_lines=1))
    parts.append('            <text x="450" y="378" text-anchor="middle" fill="#c9d4e8" font-size="12.5">只看胜率,相当于选车只看方向盘手感,不看刹车</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 396",
        "胜率错觉:策略甲胜率百分之九十,九笔各赚百分之一、一笔亏百分之十二,合计负百分之三;策略乙胜率百分之四十,四笔各赚百分之二、六笔各亏百分之零点五,合计正百分之五",
        "胜率 90% 的策略可以亏钱:九笔各 +1%、一笔 −12%,合计 −3%;胜率 40% 的趋势策略可以赚钱:四笔各 +2%、六笔各 −0.5%,合计 +5%。评价策略要把期望值、盈亏比、最大回撤、尾部风险和杠杆五件套摆在一起——只看胜率,等于选车不看刹车。")


def _fig_g31_factor_files():
    """ch31 §1.4 单因子报告:六栏档案 + 三个因子的性格速写。"""
    tiles = [
        ("覆盖率", "覆盖多少只股票"),
        ("IC · RankIC", "排序灵不灵"),
        ("五分组收益", "高分组真更好吗"),
        ("换手率", "这因子爱交易吗"),
        ("行业暴露", "押在哪个行业"),
        ("失效年份", "哪些年罢工过"),
    ]
    rows = [
        ("低估值", "某些年份挺管用", "", "但行业暴露重"),
        ("动量", "收益不错", "但换手偏高", "成本敏感"),
        ("质量", "单独看收益一般", "", "但回撤比较低"),
    ]
    parts = []
    parts.append('            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">因子登场前先过堂:一个因子一份档案,谁也不许蒙混</text>')
    parts.append('            <text x="450" y="58" text-anchor="middle" fill="#8499bd" font-size="12.5">低估值、质量、动量一个个单独测:六栏体检,外加三份性格速写</text>')
    parts.append('            <rect x="40" y="76" width="400" height="248" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>')
    parts.append('            ' + svg_text("单因子档案 · 六栏", 240, 104, 340, size=13.5, color="#a8c6ff", weight=800, max_chars=11, max_lines=1))
    for i, (name, note) in enumerate(tiles):
        col = i % 2
        row = i // 2
        x = 62 + col * 194
        y = 120 + row * 64
        parts.append('            <rect x="%d" y="%d" width="182" height="56" rx="9" fill="rgba(122,167,240,0.08)" stroke="rgba(122,167,240,0.22)"/>' % (x, y))
        parts.append('            ' + svg_text(name, x + 91, y + 22, 162, size=12.5, color="#f0c96a", weight=800, max_chars=9, max_lines=1))
        parts.append('            <text x="%d" y="%d" text-anchor="middle" fill="#bcc9dd" font-size="11">%s</text>' % (x + 91, y + 42, note))
    parts.append('            <rect x="460" y="76" width="400" height="248" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(240,201,106,0.42)"/>')
    parts.append('            ' + svg_text("三因子体检结论(各自的性格)", 660, 104, 340, size=13.5, color="#f0c96a", weight=800, max_chars=15, max_lines=1))
    for i, (name, l1, l2, l3) in enumerate(rows):
        y = 122 + i * 66
        parts.append('            <rect x="482" y="%d" width="356" height="56" rx="9" fill="rgba(240,201,106,0.06)" stroke="rgba(240,201,106,0.25)"/>' % y)
        parts.append('            <rect x="482" y="%d" width="80" height="56" rx="9" fill="rgba(122,167,240,0.14)"/>' % y)
        parts.append('            ' + svg_text(name, 522, y + 34, 72, size=13, color="#a8c6ff", weight=800, max_chars=4, max_lines=1))
        detail = l1
        if l2:
            detail = l1 + " · " + l2
        if l3:
            detail = detail + ";" + l3
        parts.append('            <text x="576" y="%d" fill="#eef4f8" font-size="12">%s</text>' % (y + 34, detail))
    parts.append('            <text x="450" y="358" text-anchor="middle" fill="#f0c96a" font-size="13.5" font-weight="800">没有一条神奇结论,但每一条都真实可查</text>')
    parts.append('            <text x="450" y="384" text-anchor="middle" fill="#c9d4e8" font-size="12.5">摸清性格再合成组合:知道自己在合什么,而不是闭着眼睛搅一锅</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 404",
        "单因子报告:每个因子按覆盖率、IC与RankIC、五分组收益、换手率、行业暴露、失效年份六栏出档案;示例三因子性格为低估值某些年份管用但行业暴露重、动量收益不错但换手偏高成本敏感、质量收益一般但回撤比较低",
        "因子一个个单独测,每个都出六栏档案:覆盖率、IC 和 RankIC、五分组收益、换手率、行业暴露、哪些年失效过。低估值某些年份管用但行业暴露重,动量收益不错但换手偏高、成本敏感,质量收益一般但回撤低——摸清性格,合成时才知道自己在合什么。")


def _fig_g32_stop_rules():
    """ch32 §5 实盘前先问能否停止:触发→动作→恢复三行写死。"""
    rows = [
        ("① 数据缺失/异常超阈值", "停止生成新单", "数据检查连续通过才恢复"),
        ("② 对账对不上(不一致)", "暂停交易", "差异解释清楚并修复"),
        ("③ 回撤超过预设上限", "降仓或停用", "完成复盘并人工确认"),
    ]
    parts = []
    parts.append('            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">上线前最后一道闸:三行停止规则,写下来才算数</text>')
    parts.append('            <text x="220" y="72" text-anchor="middle" fill="#ffb4b4" font-size="13" font-weight="800">触发条件(开工前写死)</text>')
    parts.append('            <text x="515" y="72" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">触发后动作</text>')
    parts.append('            <text x="730" y="72" text-anchor="middle" fill="#a8c6ff" font-size="13" font-weight="800">恢复条件</text>')
    for i, (trig, act, back) in enumerate(rows):
        y = 90 + i * 68
        cy = y + 34
        parts.append('            <rect x="60" y="%d" width="320" height="58" rx="10" fill="rgba(18,29,49,0.70)" stroke="rgba(232,136,136,0.45)"/>' % y)
        parts.append('            ' + svg_text(trig, 220, cy + 1, 290, size=13, color="#eef4f8", weight=800, max_chars=15, max_lines=1))
        parts.append('            <text x="395" y="%d" text-anchor="middle" fill="#f0c96a" font-size="16" font-weight="800">→</text>' % (cy + 6))
        parts.append('            <rect x="420" y="%d" width="190" height="58" rx="10" fill="rgba(240,201,106,0.07)" stroke="rgba(240,201,106,0.42)"/>' % y)
        parts.append('            ' + svg_text(act, 515, cy + 1, 170, size=13, color="#f0c96a", weight=800, max_chars=10, max_lines=1))
        parts.append('            <text x="625" y="%d" text-anchor="middle" fill="#a8c6ff" font-size="16" font-weight="800">→</text>' % (cy + 6))
        parts.append('            <rect x="650" y="%d" width="210" height="58" rx="10" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.28)"/>' % y)
        parts.append('            ' + svg_text(back, 730, cy + 1, 190, size=12, color="#c9d4e8", weight=400, max_chars=12, max_lines=1))
    parts.append('            <text x="60" y="322" fill="#8499bd" font-size="12.5">正文还点名两个扳机:</text>')
    parts.append('            <rect x="200" y="300" width="310" height="40" rx="10" fill="rgba(18,29,49,0.70)" stroke="rgba(232,136,136,0.45)"/>')
    parts.append('            ' + svg_text("订单出现异常 → 停", 355, 321, 280, size=12.5, color="#ffb4b4", weight=800, max_chars=13, max_lines=1))
    parts.append('            <rect x="530" y="300" width="310" height="40" rx="10" fill="rgba(18,29,49,0.70)" stroke="rgba(232,136,136,0.45)"/>')
    parts.append('            ' + svg_text("模型指标长期反向 → 停", 685, 321, 280, size=12.5, color="#ffb4b4", weight=800, max_chars=15, max_lines=1))
    parts.append('            <rect x="60" y="358" width="800" height="66" rx="12" fill="rgba(240,201,106,0.06)" stroke="rgba(240,201,106,0.42)"/>')
    parts.append('            <text x="450" y="384" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">停止规则必须在还没赚钱也没亏钱的时候写好——等亏了再补写的,通常是情绪,不是规则</text>')
    parts.append('            <text x="450" y="408" text-anchor="middle" fill="#c9d4e8" font-size="12.5">别把停止当失败:它和烟雾报警器响一个性质,说明防护还在工作</text>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 440",
        "实盘前停止规则表:数据缺失或异常超阈值就停止生成新单、数据检查连续通过才恢复;对账不一致就暂停交易、差异解释清楚并修复后恢复;回撤超过预设上限就降仓或停用、完成复盘并人工确认后恢复",
        "上线前把停止规则写成三行表:触发条件、触发后动作、恢复条件——数据异常停止生成新单,对账不一致暂停交易,回撤超上限降仓或停用;另外订单异常、模型指标长期反向也得停。规则要在没赚钱也没亏钱时写好,亏着补写出来的通常是情绪。")


PATCH_G = {
    33: [("回测和验证", _fig_g23_backtest_audit)],
    34: [("写出第一份可信的回测报告", _fig_g24_report_lines)],
    35: [("风控", _fig_g25_risk_toolbox)],
    36: [("看风险指标", _fig_g26_risk_metrics)],
    37: [("看收益和回撤", _fig_g27_two_funds)],
    39: [("小实盘结束后看什么", _fig_g28_graduation_matrix)],
    40: [("成本必须做敏感性", _fig_g29_cost_stress)],
    41: [("高胜率策略一定好吗", _fig_g30_winrate_trap)],
    42: [("单因子报告", _fig_g31_factor_files)],
    43: [("实盘前先问能否停止", _fig_g32_stop_rules)],
}


def _fig_h02_four_roles():
    """ch02 四类角色资金作坊。锚点:chapter-02.html <h3>1.1. 先看四类人</h3>。
    数字全部出自本章正文:
      1.1 节:你把 10 万存进银行(盈余方),银行把 8 万贷给要扩产的企业(需求方);
              中介列 6 类:银行/券商/基金/保险/信托/期货;
              基础设施与监管:央行/证监会/交易所/登记结算/托管。
      1.3 节:用油 10 万吨、锁价 5000 元/吨,涨到 6000 元买油多掏 1 亿,
              期货赚回 1 亿,用油成本仍是 5 亿(中介帮风险搬家)。
      1.4 节:靠谱借款人违约约 1%,不靠谱约 10%,分不清只能按平均约 5.5% 定利率。"""
    parts = []
    parts.append('            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">四类人:一笔存款要踩的四个格子</text>')
    parts.append('            <text x="450" y="54" text-anchor="middle" fill="#8499bd" font-size="12.5">钱要流动:先有一出一进两方,再要中介撮合增信,还得有人记账立规矩——四个格子一个也省不掉</text>')
    # 顶上三张角色卡: 盈余方 -> 中介 -> 需求方
    cards = [
        (24, "#a8c6ff", "rgba(122,167,240,0.28)", "资金盈余方", "第一类:钱多,暂时不用",
         ["居民存款 · 养老金", "保险资金 · 企业闲钱"], "你存 10 万进银行", "要安稳,也想钱不躺平", None),
        (322, "#f0c96a", "rgba(240,201,106,0.42)", "金融中介", "第三类:帮钱搬家、撮合增信",
         ["银行 · 券商 · 基金公司", "保险 · 信托 · 期货公司"], "收进 10 万,贷出 8 万", "期货还帮企业搬风险:", "油价 5000→6000:期货赚回 1 亿,成本仍 5 亿"),
        (620, "#a8c6ff", "rgba(122,167,240,0.28)", "资金需求方", "第二类:缺钱,要办正事",
         ["要扩产的企业", "修路政府 · 按揭家庭"], "企业:到手 8 万", "承诺未来还本付息", None),
    ]
    for x, ncolor, scolor, name, tag, exs, gold, note, chip in cards:
        cx = x + 133
        parts.append('            <rect x="%d" y="72" width="266" height="192" rx="12" fill="rgba(18,29,49,0.70)" stroke="%s"/>' % (x, scolor))
        parts.append('            ' + svg_text(name, cx, 100, 240, size=15, color=ncolor, weight=800, max_chars=12, max_lines=1))
        parts.append('            <text x="%d" y="124" text-anchor="middle" fill="#8499bd" font-size="11.5">%s</text>' % (cx, tag))
        parts.append('            <text x="%d" y="152" text-anchor="middle" fill="#bcc9dd" font-size="12.5">%s</text>' % (cx, exs[0]))
        parts.append('            <text x="%d" y="174" text-anchor="middle" fill="#bcc9dd" font-size="12.5">%s</text>' % (cx, exs[1]))
        parts.append('            <text x="%d" y="206" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">%s</text>' % (cx, gold))
        parts.append('            <text x="%d" y="232" text-anchor="middle" fill="#c9d4e8" font-size="11.5">%s</text>' % (cx, note))
        if chip:
            parts.append('            <text x="%d" y="252" text-anchor="middle" fill="#8499bd" font-size="11">%s</text>' % (cx, chip))
    # 卡间钱流箭头: 存款 10 万 -> 中介 -> 贷款 8 万
    parts.append('            <path d="M 291 158 L 318 158" fill="none" stroke="#a8c6ff" stroke-width="3" marker-end="url(#hr2a)"/>')
    parts.append('            <text x="306" y="146" text-anchor="middle" fill="#a8c6ff" font-size="11">存款</text>')
    parts.append('            <path d="M 589 158 L 616 158" fill="none" stroke="#a8c6ff" stroke-width="3" marker-end="url(#hr2a)"/>')
    parts.append('            <text x="604" y="146" text-anchor="middle" fill="#a8c6ff" font-size="11">贷款</text>')
    # 三张卡向下接到地基
    for dx in (157, 455, 753):
        parts.append('            <line x1="%d" y1="264" x2="%d" y2="288" stroke="rgba(122,167,240,0.28)" stroke-width="1.5" stroke-dasharray="3 5"/>' % (dx, dx))
    # 底:基础设施和监管(第四格,托住整条流水线)
    parts.append('            <rect x="24" y="292" width="854" height="76" rx="12" fill="rgba(18,29,49,0.70)" stroke="rgba(240,201,106,0.42)"/>')
    parts.append('            ' + svg_text("第四格:基础设施和监管者", 220, 316, 400, size=14, color="#f0c96a", weight=800, max_chars=14, max_lines=1))
    parts.append('            <text x="220" y="340" text-anchor="middle" fill="#c9d4e8" font-size="12">央行 · 证监会 · 交易所 · 登记结算 · 托管</text>')
    parts.append('            <text x="220" y="360" text-anchor="middle" fill="#8499bd" font-size="11">不直接用钱生钱:管规则、账户、清算、稳定</text>')
    parts.append('            <line x1="470" y1="306" x2="470" y2="354" stroke="rgba(122,167,240,0.18)"/>')
    parts.append('            <text x="674" y="314" text-anchor="middle" fill="#8499bd" font-size="11.5">没人立规矩会怎样?拿违约概率算笔账:</text>')
    parts.append('            <text x="674" y="337" text-anchor="middle" fill="#eef4f8" font-size="13" font-weight="800">靠谱约 1% · 不靠谱约 10% → 只能按 5.5% 定价</text>')
    parts.append('            <text x="674" y="359" text-anchor="middle" fill="#8499bd" font-size="11">贵到把靠谱的人吓跑——制度是在给信任压价</text>')
    parts.append('            <text x="450" y="398" text-anchor="middle" fill="#c9d4e8" font-size="12.5">推演一遍:一出一进两方 → 中介撮合增信 → 记账立规矩——每一笔资金流动都踩过这四格</text>')
    parts.append('            <defs><marker id="hr2a" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#a8c6ff"/></marker></defs>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 420",
        "四类角色资金作坊:盈余方把 10 万存进银行,中介放出 8 万贷给扩产企业,需求方到手开工;底下基础设施和监管者托底;侧面一笔违约账:靠谱约 1%、不靠谱约 10%,分不清只能按 5.5% 定价;中介卡上附油价 5000 涨到 6000 时期货赚回 1 亿、成本仍 5 亿的对冲例",
        "你存的 10 万、银行贷出的 8 万,走的是这四格:一出一进两方,中介撮合增信,底下基础设施和监管立规矩。旁边那笔违约账(靠谱约 1%、不靠谱约 10%、只能按平均 5.5% 定价)提醒:立规矩不是形式,是在给信任压价。")


def _fig_h03_stock_lifecycle():
    """ch03 股票的一生五站。锚点:chapter-03.html <h3>1.6. 一级市场和二级市场再回看股票</h3>。
    数字全部出自本章(单元 6+7)正文手算账:
      1.1 节:店作价 100 万,切成 10 万股、每股 10 元;你花 1 万买 1000 股,占了 1%。
      1.4 节:分红前一天 10 元买入,拿走 1 元现金,再以 10 元卖回就白赚 1 元;
              除息就是把这份"白赚"提前扣掉的机制。
      1.6 节:IPO/增发发行新股,钱流进公司=一级市场;你买入的钱去了卖方=二级市场。
      2.1 节:总股本 1 亿股,你 10 万股占千分之一;增发 0.2 亿成 1.2 亿股,
              占比掉到约万分之 8.3。
      2.2 节:100 股年利润 1000 元、每股利润 10 元;买回注销 20 股剩 80 股,
              每股利润 12.5 元——账面上每股好看了 25%,但拿现金换的。"""
    parts = []
    parts.append('            <text x="450" y="32" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">一只股票的一生:钱只进公司那一次</text>')
    parts.append('            <text x="450" y="54" text-anchor="middle" fill="#8499bd" font-size="12.5">发行 → 换手 → 分红 → 增发 → 回购,五站各动一笔账——看懂每站把钱和权利搬给谁,才看懂"你这一份"</text>')
    # 五站卡片
    cards = [
        (16, "#a8c6ff", "rgba(122,167,240,0.28)", "① 发行", "一级市场",
         ["股份第一次见人", "店作价 100 万", "切成 10 万股", "每股 10 元"], "钱进公司账:变产线"),
        (194, "#a8c6ff", "rgba(122,167,240,0.28)", "② 换手", "二级市场",
         ["你买 = 另一位卖", "1 万买 1000 股", "= 店里 1% 的份额", "钱去卖方手里"], "公司一分没多收"),
        (372, "#f0c96a", "rgba(240,201,106,0.42)", "③ 分红", "公司行动 · 除息",
         ["10 元买入,派 1 元", "次日 10 元卖出", "白赚 1 元的洞", "除息提前扣掉"], "分红不是白送钱"),
        (550, "#f0c96a", "rgba(240,201,106,0.42)", "④ 增发", "公司行为 · 再融资",
         ["总股本 1 亿股", "你 10 万股=千分之 1", "增发 0.2 亿→1.2 亿股", "占比掉到约"], "万分之 8.3,股没少、份薄了"),
        (728, "#f0c96a", "rgba(240,201,106,0.42)", "⑤ 回购", "公司行为 · 注销",
         ["100 股,年利 1000 元", "买回注销 20 股", "剩 80 股,利不变", "每股利润 10→12.5"], "+25% 是拿现金换的"),
    ]
    for x, ncolor, scolor, stage, tag, rows, foot in cards:
        cx = x + 78
        parts.append('            <rect x="%d" y="76" width="156" height="206" rx="12" fill="rgba(18,29,49,0.70)" stroke="%s"/>' % (x, scolor))
        parts.append('            ' + svg_text(stage, cx, 102, 140, size=13.5, color=ncolor, weight=800, max_chars=8, max_lines=1))
        parts.append('            <text x="%d" y="124" text-anchor="middle" fill="#8499bd" font-size="11">%s</text>' % (cx, tag))
        for ri, row in enumerate(rows):
            col = "#eef4f8" if ri >= 2 else "#bcc9dd"
            parts.append('            <text x="%d" y="%d" text-anchor="middle" fill="%s" font-size="12">%s</text>' % (cx, 154 + ri * 24, col, row))
        parts.append('            <text x="%d" y="264" text-anchor="middle" fill="#f0c96a" font-size="11.5" font-weight="800">%s</text>' % (cx, foot))
    # 站间金色箭头(钱的流向)
    for ax in (174, 352, 530, 708):
        parts.append('            <path d="M %d 176 L %d 176" fill="none" stroke="#f0c96a" stroke-width="2.5" marker-end="url(#hr3a)"/>' % (ax + 2, ax + 17))
    # 底:两条路的收场账
    parts.append('            <text x="450" y="316" text-anchor="middle" fill="#a8c6ff" font-size="13" font-weight="750">钱的路:发行那天进公司一次 → 之后每天在股民之间换手 → 分红时现金才出公司进你账户</text>')
    parts.append('            <text x="450" y="344" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="750">"你这一份"的路:千分之 1 被增发摊到约万分之 8.3,回购又把每股利润从 10 元抬成 12.5 元</text>')
    parts.append('            <line x1="120" y1="360" x2="780" y2="360" stroke="rgba(122,167,240,0.18)"/>')
    parts.append('            <text x="450" y="386" text-anchor="middle" fill="#ffb4b4" font-size="12.5">别误读两处:+25% 的每股利润是拿真金白银换的,不是白赚;你点买入那一刻,钱多半进的是卖方口袋</text>')
    parts.append('            <defs><marker id="hr3a" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#f0c96a"/></marker></defs>')
    body = "\n".join(parts)
    return concept_figure(body, "0 0 900 420",
        "股票生命周期五站:发行切 10 万股每股 10 元(100 万的店),换手 1 万买 1000 股占 1%,分红 10 元派 1 元靠除息扣掉白赚 1 元的洞,增发 0.2 亿把占比从千分之 1 摊到约万分之 8.3,回购注销 20 股把每股利润从 10 元抬到 12.5 元",
        "钱只在发行那天进公司一次,之后天天换手都在投资者之间;分红要除息、增发会摊薄、回购的账面好看是拿现金换的。看懂每站把钱和权利搬给谁,才算看懂你买的这一份。")


PATCH_H = {
    2: [("先看四类人", _fig_h02_four_roles)],
    3: [("一级市场和二级市场再回看股票", _fig_h03_stock_lifecycle)],
}


def _fig_i4_seesaw():
    """利率、债价、期限敏感度的跷跷板(新老债主类)。"""
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">利率与债券价格的跷跷板:同一张 100 元债</text>
            <!-- 中央支点 -->
            <path d="M 430 244 L 470 244 L 450 200 Z" fill="rgba(240,201,106,0.3)" stroke="#f0c96a"/>
            <!-- 红色刃:熱度利率 -->
            <line x1="150" y1="210" x2="330" y2="150" stroke="#f0c96a" stroke-width="4"/>
            <circle cx="150" cy="210" r="8" fill="#f0c96a"/>
            <text x="150" y="232" text-anchor="middle" fill="#ffb4b4" font-size="13" font-weight="800">市场利率</text>
            <text x="150" y="250" text-anchor="middle" fill="#bcc9dd" font-size="11">5% 减到 3%</text>
            <!-- 蓝色刃:债券价格 -->
            <line x1="570" y1="150" x2="750" y2="210" stroke="#7aa7f0" stroke-width="4"/>
            <circle cx="750" cy="210" r="8" fill="#7aa7f0"/>
            <text x="750" y="232" text-anchor="middle" fill="#a8c6ff" font-size="13" font-weight="800">手中债券的价格</text>
            <text x="750" y="250" text-anchor="middle" fill="#bcc9dd" font-size="11">95.45 被托上 102</text>
            <!-- 支点名 -->
            <text x="450" y="248" text-anchor="middle" fill="#eef4f8" font-size="12" font-weight="800">折价兑换点</text>
            <!-- 股本面上的账:左右施面 -->
            <rect x="36" y="272" width="392" height="90" rx="10" fill="rgba(18,29,49,0.70)" stroke="rgba(232,120,120,0.45)"/>
            <text x="52" y="298" fill="#ffb4b4" font-size="13" font-weight="800">新发行利益</text>
            <text x="52" y="322" fill="#bcc9dd" font-size="12">刚买的人:一年只收 5 元息</text>
            <text x="52" y="344" fill="#bcc9dd" font-size="12">涨到 3% 后,新书票面息是 3 元</text>
            <rect x="464" y="272" width="392" height="90" rx="10" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.45)"/>
            <text x="480" y="298" fill="#a8c6ff" font-size="13" font-weight="800">老债面利益</text>
            <text x="480" y="322" fill="#bcc9dd" font-size="12">你拿到的还是当初 5 元票息</text>
            <text x="480" y="344" fill="#bcc9dd" font-size="12">可市场只愿意花 95.45 给 5 元,利率一跌你多赚</text>
            <!-- 补一个绿色反向 -->
            <text x="450" y="384" text-anchor="middle" fill="#8fb37a" font-size="13" font-weight="800">利率 3% -> 5%:95.45 变成 105/1.05 ≈ 90.48,老债主拿回本赚到钱,买的人补到了新利率所在</text>
            <text x="450" y="410" text-anchor="middle" fill="#8499bd" font-size="12.5">不对称只因为期限:三年期的跷跷板老大上下各 2-3 元,三十年期的老大能上下 30 元</text>"""
    return concept_figure(body, "0 0 900 430",
        "利率-债价跷跷板:左侧市场利率从 5% 减到 3%,右侧债券价格从 95.45 被托上 102,两侧的受益人与买方各算一笔账",
        "利率与债券价格永远在杠杆两端:当市场利率从 5% 减到 3%,你手上锁了 5 元票息的老债就从 95.45 被托到 102;反过来,利率从 3% 抬到 5%,它就被压到 90.48。短期债以毛计,三十年期的跷跷板能上下 30 元——久期就是这根杠杆的长度。")


PATCH_I = {
    4: [("信用风险和信用利差", _fig_i4_seesaw)],
}



def _fig_j6_snowball():
    """ch06:雪球结构的敲进敲出四条命。"""
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">雪球结构的四条命:同一张产品,四种结局</text>
            <!-- 图表区:时间横轴,标的价格纵轴 -->
            <line x1="70" y1="330" x2="830" y2="330" stroke="#41506b" stroke-width="2"/>
            <text x="836" y="334" fill="#8499bd" font-size="12">到期</text>
            <!-- 敲出线 103% -->
            <line x1="70" y1="110" x2="830" y2="110" stroke="#f0c96a" stroke-width="2" stroke-dasharray="8 6"/>
            <text x="76" y="102" fill="#f0c96a" font-size="12" font-weight="700">敲出线 103%(每月观察)</text>
            <!-- 敲入线 70% -->
            <line x1="70" y1="250" x2="830" y2="250" stroke="#e87878" stroke-width="2" stroke-dasharray="8 6"/>
            <text x="76" y="270" fill="#ffb4b4" font-size="12" font-weight="700">敲入线 70%(每日观察)</text>
            <text x="76" y="190" fill="#bcc9dd" font-size="12">起点 100%</text>
            <!-- 命 A:不碰两边,到期拿满票息 -->
            <polyline points="70,190 220,176 380,196 560,164 830,178" fill="none" stroke="#8fb37a" stroke-width="3"/>
            <text x="560" y="150" fill="#b8d6a3" font-size="12" font-weight="700">命 1:区间震荡,到期拿满两年票息 30%</text>
            <!-- 命 B:提前敲出 -->
            <polyline points="70,190 180,150 300,118 340,110" fill="none" stroke="#7aa7f0" stroke-width="3"/>
            <circle cx="340" cy="110" r="6" fill="#7aa7f0"/>
            <text x="360" y="88" fill="#a8c6ff" font-size="12" font-weight="700">命 2:第 6 个月敲出,提前结束,拿 6 个月票息≈7.5%</text>
            <!-- 命 C:先敲入再敲出 -->
            <polyline points="70,190 200,238 260,252 380,238 520,150 640,116 700,110" fill="none" stroke="#c9a7f5" stroke-width="3"/>
            <circle cx="260" cy="252" r="5" fill="#c9a7f5"/>
            <circle cx="700" cy="110" r="6" fill="#c9a7f5"/>
            <text x="420" y="300" fill="#d8c1f7" font-size="12" font-weight="700">命 3:先敲入、后敲出——捡回票息,虚惊一场</text>
            <!-- 命 D:敲入未敲出 -->
            <polyline points="70,190 220,246 300,252 430,286 600,300 830,312" fill="none" stroke="#e87878" stroke-width="3"/>
            <text x="560" y="340" fill="#ffb4b4" font-size="12" font-weight="700">命 4:敲入后没爬回——按到期跌幅赔本金,票息一分没有</text>
            <!-- 底部注解 -->
            <text x="450" y="392" text-anchor="middle" fill="#8499bd" font-size="13">你拿到的高票息,是替券商卖出了一张"障碍看跌期权"的权利金——命 4 发生时,你在替整个市场接盘。</text>"""
    return concept_figure(body, "0 0 900 420",
        "雪球产品两条障碍线之间,标的价格的四种路径:区间震荡拿满票息、提前敲出、先敲入再敲出、敲入未敲出赔本金",
        "雪球只有四种结局,三种都是小赚,一种是大亏——而且大亏恰恰发生在市场最差、你最需要钱的时候。票息两位数不是银行的慷慨,是你卖出保险换来的权利金。")


def _fig_j9_spine():
    """ch09:危机的同一根脊柱。"""
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">危机的同一根脊柱:四百年,四步走</text>
            <!-- 四步竖排 -->
            <rect x="60" y="64" width="330" height="72" rx="10" fill="rgba(18,29,49,0.70)" stroke="rgba(122,167,240,0.5)"/>
            <text x="80" y="92" fill="#a8c6ff" font-size="15" font-weight="800">① 叙事</text>
            <text x="80" y="118" fill="#bcc9dd" font-size="12.5">一个故事把价格抬离现金流的锚:球茎、南海股票、.com、算法稳定币</text>
            <path d="M 225 136 L 225 156" stroke="#41506b" stroke-width="2" fill="none"/>
            <path d="M 218 150 L 225 160 L 232 150 Z" fill="#41506b"/>
            <rect x="60" y="160" width="330" height="72" rx="10" fill="rgba(18,29,49,0.70)" stroke="rgba(240,201,106,0.5)"/>
            <text x="80" y="188" fill="#f0c96a" font-size="15" font-weight="800">② 杠杆</text>
            <text x="80" y="214" fill="#bcc9dd" font-size="12.5">短债长资:无保证金远期、分期认购、10 倍孖展、两融配资、90 天养 3 年</text>
            <path d="M 225 232 L 225 252" stroke="#41506b" stroke-width="2" fill="none"/>
            <path d="M 218 246 L 225 256 L 232 246 Z" fill="#41506b"/>
            <rect x="60" y="256" width="330" height="72" rx="10" fill="rgba(18,29,49,0.70)" stroke="rgba(232,120,120,0.5)"/>
            <text x="80" y="284" fill="#ffb4b4" font-size="15" font-weight="800">③ 点火</text>
            <text x="80" y="310" fill="#bcc9dd" font-size="12.5">利率上行或外部冲击,不对称性引爆:加息 525bp、储备耗光、千亿赎回</text>
            <path d="M 225 328 L 225 348" stroke="#41506b" stroke-width="2" fill="none"/>
            <path d="M 218 342 L 225 352 L 232 342 Z" fill="#41506b"/>
            <rect x="60" y="352" width="330" height="72" rx="10" fill="rgba(18,29,49,0.70)" stroke="rgba(143,183,122,0.5)"/>
            <text x="80" y="380" fill="#b8d6a3" font-size="15" font-weight="800">④ 清算:规则被重写</text>
            <text x="80" y="406" fill="#bcc9dd" font-size="12.5">期权化撕约、银行休假、废除金本位、熔断、无限 QE、周末 48 小时联姻</text>
            <!-- 右侧:12 场危机时间线 -->
            <text x="640" y="70" text-anchor="middle" fill="#eef4f8" font-size="14" font-weight="800">同一张脸,换了十二次妆</text>
            <line x1="470" y1="96" x2="470" y2="410" stroke="#41506b" stroke-width="2"/>
            <!-- 刻度点 -->
            <circle cx="470" cy="104" r="5" fill="#7aa7f0"/><text x="486" y="108" fill="#bcc9dd" font-size="12.5">1637 郁金香:空气交易一夜流拍</text>
            <circle cx="470" cy="128" r="5" fill="#7aa7f0"/><text x="486" y="132" fill="#bcc9dd" font-size="12.5">1720 南海:股价本身成了利润来源</text>
            <circle cx="470" cy="152" r="5" fill="#7aa7f0"/><text x="486" y="156" fill="#bcc9dd" font-size="12.5">1929 大萧条:道指 -89%,25 年才回本</text>
            <circle cx="470" cy="176" r="5" fill="#f0c96a"/><text x="486" y="180" fill="#bcc9dd" font-size="12.5">1987 黑色星期一:程序化自救的踩踏</text>
            <circle cx="470" cy="200" r="5" fill="#f0c96a"/><text x="486" y="204" fill="#bcc9dd" font-size="12.5">1990 日本:抵押品循环被加息截断</text>
            <circle cx="470" cy="224" r="5" fill="#f0c96a"/><text x="486" y="228" fill="#bcc9dd" font-size="12.5">1997 亚洲:做空一个国家的完整手册</text>
            <circle cx="470" cy="248" r="5" fill="#e87878"/><text x="486" y="252" fill="#bcc9dd" font-size="12.5">2000 互联网:思科有利润也跌 -89%</text>
            <circle cx="470" cy="272" r="5" fill="#e87878"/><text x="486" y="276" fill="#bcc9dd" font-size="12.5">2008 次贷:相关性假设值一万亿美元</text>
            <circle cx="470" cy="296" r="5" fill="#e87878"/><text x="486" y="300" fill="#bcc9dd" font-size="12.5">2010 欧债:没有最后贷款人的货币联盟</text>
            <circle cx="470" cy="320" r="5" fill="#8fb37a"/><text x="486" y="324" fill="#bcc9dd" font-size="12.5">2015 A 股:两融 2.27 万亿与千股跌停</text>
            <circle cx="470" cy="344" r="5" fill="#8fb37a"/><text x="486" y="348" fill="#bcc9dd" font-size="12.5">2020/2022:抢现金与反身性死亡螺旋</text>
            <circle cx="470" cy="368" r="5" fill="#8fb37a"/><text x="486" y="372" fill="#bcc9dd" font-size="12.5">2023 SVB/瑞信:单日挤兑 420 亿美元</text>
            <text x="640" y="404" text-anchor="middle" fill="#8499bd" font-size="12.5">点火时间不可测,顺序永远一致。</text>"""
    return concept_figure(body, "0 0 900 440",
        "危机四步骨架:叙事、杠杆、点火、规则重写,右侧十二场危机的时间线从 1637 郁金香排到 2023 硅谷银行",
        "四步永远按同一顺序发生:叙事先把价格抬离锚,杠杆把错配堆到极限,点火只需一根火柴,灭火靠的是规则被临时重写。危机无法预测,但每一步都有可监测的仪表盘。")


def _fig_j10_mismatch():
    """ch10:期限错配的梯子——90 天滚动负债养 3 年资产。"""
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">期限错配:用 90 天的钱养 3 年的资产</text>
            <!-- 负债端:90 天滚动四段 -->
            <text x="70" y="84" fill="#a8c6ff" font-size="14" font-weight="800">负债端:投资者的钱,90 天一轮回</text>
            <rect x="70" y="96" width="172" height="46" rx="8" fill="rgba(122,167,240,0.30)" stroke="#7aa7f0"/><text x="156" y="124" text-anchor="middle" fill="#a8c6ff" font-size="12">第 1 轮 90 天</text>
            <rect x="250" y="96" width="172" height="46" rx="8" fill="rgba(122,167,240,0.30)" stroke="#7aa7f0"/><text x="336" y="124" text-anchor="middle" fill="#a8c6ff" font-size="12">第 2 轮 90 天</text>
            <rect x="430" y="96" width="172" height="46" rx="8" fill="rgba(122,167,240,0.30)" stroke="#7aa7f0"/><text x="516" y="124" text-anchor="middle" fill="#a8c6ff" font-size="12">第 3 轮 90 天</text>
            <rect x="610" y="96" width="172" height="46" rx="8" fill="rgba(122,167,240,0.30)" stroke="#7aa7f0"/><text x="696" y="124" text-anchor="middle" fill="#a8c6ff" font-size="12">第 4 轮 90 天…</text>
            <!-- 资产端:一条 3 年 -->
            <text x="70" y="190" fill="#f0c96a" font-size="14" font-weight="800">资产端:借给地产商的贷款,3 年才到期,收益 5%</text>
            <rect x="70" y="202" width="712" height="46" rx="8" fill="rgba(240,201,106,0.18)" stroke="#f0c96a"/>
            <text x="426" y="230" text-anchor="middle" fill="#ffe6a8" font-size="12">3 年 × 5% ——第 1095 天晚上 12 点之前,一分钱拿不回来</text>
            <!-- 利差赚取区 -->
            <text x="70" y="282" fill="#8fb37a" font-size="13" font-weight="800">平时赚什么:借 3.2%、贷 5%,一年躺赚 1.8% 价差</text>
            <!-- 断裂点 -->
            <line x1="426" y1="300" x2="426" y2="380" stroke="#e87878" stroke-width="2" stroke-dasharray="6 6"/>
            <path d="M 412 380 L 426 396 L 440 380 Z" fill="#e87878"/>
            <rect x="200" y="400" width="452" height="64" rx="10" fill="rgba(232,120,120,0.16)" stroke="#e87878"/>
            <text x="216" y="426" fill="#ffb4b4" font-size="13" font-weight="800">某一天,第 N 轮 90 天到期的钱不肯续了</text>
            <text x="216" y="448" fill="#bcc9dd" font-size="12">资产还剩 2 年才到期——要么折价卖、要么求谁借钱。1997 / 2008 / 2023 都是这一天。</text>
            <text x="450" y="490" text-anchor="middle" fill="#8499bd" font-size="12.5">左侧滚动的每一格都不是新钱,是旧钱的"再借一次"。滚动断掉的那天,账面上的盈利模型只剩一句话:谁能借我钱?</text>"""
    return concept_figure(body, "0 0 900 515",
        "期限错配示意:上方负债端四个 90 天滚动块,下方资产端一条 3 年长方块,中间是 1.8% 的利差,底部红色区域标记滚动断裂点",
        "影子银行与正规银行共用同一台发动机:滚动短钱,放长期资产,吃利差。1997 年是央行储备续不上,2008 年是回购市场续不上,2023 年硅谷银行是储户续不上——点火处不同,断的是同一根轴。")


def _fig_j11_trilemma():
    """ch11:不可能三角。"""
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">不可能三角:三样东西,只能选两样</text>
            <!-- 三角形 -->
            <path d="M 450 110 L 170 380 L 730 380 Z" fill="rgba(18,29,49,0.55)" stroke="#41506b" stroke-width="2"/>
            <!-- 顶点 -->
            <circle cx="450" cy="110" r="9" fill="#f0c96a"/>
            <text x="450" y="86" text-anchor="middle" fill="#ffe6a8" font-size="15" font-weight="800">独立的货币政策</text>
            <text x="450" y="134" text-anchor="middle" fill="#bcc9dd" font-size="11.5">自己定利率,想加就加</text>
            <circle cx="170" cy="380" r="9" fill="#7aa7f0"/>
            <text x="170" y="414" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">资本自由流动</text>
            <text x="170" y="436" text-anchor="middle" fill="#bcc9dd" font-size="11.5">钱想来就来,想走就走</text>
            <circle cx="730" cy="380" r="9" fill="#8fb37a"/>
            <text x="730" y="414" text-anchor="middle" fill="#b8d6a3" font-size="15" font-weight="800">汇率稳定</text>
            <text x="730" y="436" text-anchor="middle" fill="#bcc9dd" font-size="11.5">盯住美元或一篮子</text>
            <!-- 三边:选法与代价 -->
            <rect x="60" y="180" width="230" height="86" rx="10" fill="rgba(122,167,240,0.14)" stroke="rgba(122,167,240,0.5)"/>
            <text x="76" y="206" fill="#a8c6ff" font-size="13" font-weight="800">美国:选 ①+②</text>
            <text x="76" y="228" fill="#bcc9dd" font-size="12">放弃汇率稳定——美元自由浮动,</text>
            <text x="76" y="248" fill="#bcc9dd" font-size="12">涨跌都认,换完整政策主权</text>
            <rect x="610" y="180" width="230" height="86" rx="10" fill="rgba(143,183,122,0.14)" stroke="rgba(143,183,122,0.5)"/>
            <text x="626" y="206" fill="#b8d6a3" font-size="13" font-weight="800">中国香港:选 ②+③</text>
            <text x="626" y="228" fill="#bcc9dd" font-size="12">放弃货币政策——联系汇率下,</text>
            <text x="626" y="248" fill="#bcc9dd" font-size="12">美联储加息香港只能跟加</text>
            <rect x="335" y="470" width="230" height="86" rx="10" fill="rgba(240,201,106,0.14)" stroke="rgba(240,201,106,0.5)"/>
            <text x="351" y="496" fill="#ffe6a8" font-size="13" font-weight="800">中国内地:选 ①+③</text>
            <text x="351" y="518" fill="#bcc9dd" font-size="12">放弃资本自由流动——资本管制,</text>
            <text x="351" y="538" fill="#bcc9dd" font-size="12">才有自己的利率与汇率节奏</text>
            <text x="450" y="330" text-anchor="middle" fill="#eef4f8" font-size="13" font-weight="800">1992 英镑、1997 泰铢:</text>
            <text x="450" y="352" text-anchor="middle" fill="#eef4f8" font-size="13" font-weight="800">都是想三个全要,被市场投票出局</text>"""
    return concept_figure(body, "0 0 900 575",
        "不可能三角:三个顶点分别是独立的货币政策、资本自由流动、汇率稳定,三条边外各标注美国的选法、香港的选法、中国内地的选法",
        "三角形的三个顶点不能同时占有,每个国家只是选了放弃哪一样。所有伟大的汇率危机——1992 英镑、1997 泰铢、2015 瑞郎——都发生在“我全要”的那一侧。")


PATCH_J = {
    6: [("敲进敲出的四条命", _fig_j6_snowball)],
    9: [("危机的同一根脊柱", _fig_j9_spine)],
    10: [("用 90 天的钱养 3 年的资产", _fig_j10_mismatch)],
    11: [("三样东西,只能选两样", _fig_j11_trilemma)],
}



def _fig_k6_waterfall():
    """ch06:CDO 分层瀑布——现金流自上而下,损失自下而上。"""
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">CDO 的瀑布:现金流从上往下浇,损失从下往上烧</text>
            <!-- 三层塔 -->
            <rect x="120" y="80" width="360" height="66" rx="8" fill="rgba(122,167,240,0.30)" stroke="#7aa7f0"/>
            <text x="300" y="106" text-anchor="middle" fill="#a8c6ff" font-size="14" font-weight="800">AAA 优先层 80%</text>
            <text x="300" y="130" text-anchor="middle" fill="#bcc9dd" font-size="11.5">先吃饭:贷款回款先付它,票息最低</text>
            <rect x="120" y="146" width="360" height="66" rx="8" fill="rgba(240,201,106,0.24)" stroke="#f0c96a"/>
            <text x="300" y="172" text-anchor="middle" fill="#ffe6a8" font-size="14" font-weight="800">夹层 BBB~A 15%</text>
            <text x="300" y="196" text-anchor="middle" fill="#bcc9dd" font-size="11.5">排队吃:优先级吃饱才轮它,票息居中</text>
            <rect x="120" y="212" width="360" height="66" rx="8" fill="rgba(232,120,120,0.22)" stroke="#e87878"/>
            <text x="300" y="238" text-anchor="middle" fill="#ffb4b4" font-size="14" font-weight="800">股权层(最先死)5%</text>
            <text x="300" y="262" text-anchor="middle" fill="#bcc9dd" font-size="11.5">收缴碗:所有损失先砸它,票息最肥</text>
            <!-- 现金流箭头(自上而下) -->
            <path d="M 540 70 L 540 260" stroke="#8fb37a" stroke-width="3" fill="none"/>
            <path d="M 532 70 L 548 70 L 540 56 Z" fill="#8fb37a"/>
            <text x="566" y="110" fill="#b8d6a3" font-size="12.5" font-weight="700">现金流向下浇:</text>
            <text x="566" y="132" fill="#bcc9dd" font-size="12">100 万月供先进来,</text>
            <text x="566" y="152" fill="#bcc9dd" font-size="12">AAA 拿走它的那份,</text>
            <text x="566" y="172" fill="#bcc9dd" font-size="12">剩下的才浇下一层</text>
            <!-- 损失箭头(自下而上) -->
            <path d="M 720 260 L 720 76" stroke="#e87878" stroke-width="3" fill="none"/>
            <path d="M 712 78 L 728 78 L 720 64 Z" fill="#e87878"/>
            <text x="620" y="290" fill="#ffb4b4" font-size="12.5" font-weight="700">违约损失往上烧:</text>
            <text x="620" y="310" fill="#bcc9dd" font-size="12">平均违约率 7% 时,股权层烧光、</text>
            <text x="620" y="330" fill="#bcc9dd" font-size="12">夹层带血,AAA 岿然不动;</text>
            <text x="620" y="350" fill="#bcc9dd" font-size="12">2008 年各地违约一起跳到 25%——</text>
            <text x="620" y="370" fill="#bcc9dd" font-size="12">AAA 的"安全"原来是相关性假设</text>
            <!-- 底部 -->
            <text x="450" y="416" text-anchor="middle" fill="#eef4f8" font-size="13.5" font-weight="800">分层不减风险,只重排风险的座位:总损失 = 各层损失相加,一层都省不了。</text>
            <text x="450" y="444" text-anchor="middle" fill="#8499bd" font-size="12.5">2008 年的发明不是分层,是把一群"相关性 0.2"的假设卖掉、再按"相关性 1"的现实定价</text>"""
    return concept_figure(body, "0 0 900 470",
        "CDO 三层塔自上而下:AAA 优先层、夹层、股权层;左侧绿色箭头现金流自上而下,右侧红色箭头违约损失自下而上",
        "瀑布的本质是队列,不是魔法:上游 AAA 先吃饭,下游股权层先替所有人收碗。2008 年大家发现,只要各地房价一起跌,AAA 的'安全'只是建在相关性 0.2 的假设上。")


def _fig_k9_doubleplay():
    """ch09:1997 香港双击——做空港元 + 做空恒指期货。"""
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">1997 香港双击:哪条腿赚钱,我都赢</text>
            <!-- 左:第一腿 做空港元 -->
            <rect x="60" y="76" width="350" height="110" rx="10" fill="rgba(122,167,240,0.16)" stroke="rgba(122,167,240,0.5)"/>
            <text x="80" y="104" fill="#a8c6ff" font-size="14" font-weight="800">腿 ①:做空港元</text>
            <text x="80" y="128" fill="#bcc9dd" font-size="12">借入港元,市场上抛港元换美元</text>
            <text x="80" y="148" fill="#bcc9dd" font-size="12">赌联系汇率守不住,一旦改浮,</text>
            <text x="80" y="168" fill="#bcc9dd" font-size="12">港元贬 30%,借出还入赚价差</text>
            <!-- 右:第二腿 做空恒指期货 -->
            <rect x="490" y="76" width="350" height="110" rx="10" fill="rgba(232,120,120,0.14)" stroke="rgba(232,120,120,0.5)"/>
            <text x="510" y="104" fill="#ffb4b4" font-size="14" font-weight="800">腿 ②:做空恒生指数期货</text>
            <text x="510" y="128" fill="#bcc9dd" font-size="12">预先卖空恒指</text>
            <text x="510" y="148" fill="#bcc9dd" font-size="12">赌央行保汇率必须加息,一加息,</text>
            <text x="510" y="168" fill="#bcc9dd" font-size="12">股市崩、期货空头赚翻</text>
            <!-- 中央:港府的选项 -->
            <text x="450" y="222" text-anchor="middle" fill="#eef4f8" font-size="14" font-weight="800">金管局只有两种反应,两种都被算计</text>
            <path d="M 235 186 L 380 232 L 380 246" stroke="#41506b" fill="none" stroke-width="2"/>
            <path d="M 665 186 L 520 232 L 520 246" stroke="#41506b" fill="none" stroke-width="2"/>
            <rect x="140" y="252" width="300" height="86" rx="10" fill="rgba(18,29,49,0.70)" stroke="rgba(240,201,106,0.5)"/>
            <text x="160" y="280" fill="#ffe6a8" font-size="13" font-weight="800">若弃守:联系汇率浮动</text>
            <text x="160" y="304" fill="#bcc9dd" font-size="12">腿 ①赚:港元贬值兑现</text>
            <text x="160" y="324" fill="#bcc9dd" font-size="12">腿 ②平仓,结局=泰铢模式</text>
            <rect x="460" y="252" width="300" height="86" rx="10" fill="rgba(18,29,49,0.70)" stroke="rgba(240,201,106,0.5)"/>
            <text x="480" y="280" fill="#ffe6a8" font-size="13" font-weight="800">若死守:隔夜 HIBOR 拉到 280%</text>
            <text x="480" y="304" fill="#bcc9dd" font-size="12">腿 ②赚:恒指四天 -23%(1997.10)</text>
            <text x="480" y="324" fill="#bcc9dd" font-size="12">腿 ①平仓,结局=汇率守住股市崩</text>
            <!-- 底部结局 -->
            <rect x="140" y="362" width="620" height="64" rx="10" fill="rgba(143,183,122,0.12)" stroke="rgba(143,183,122,0.5)"/>
            <text x="450" y="388" text-anchor="middle" fill="#b8d6a3" font-size="13" font-weight="800">1998.8 港府第三反应:外汇基金直接买入 1200 亿港元恒指成分股,托住期货结算价</text>
            <text x="450" y="414" text-anchor="middle" fill="#bcc9dd" font-size="12">1999 年打包成盈富基金退出,还盈利约 300 亿港元——防守方第一次用了空头没想到的招</text>"""
    return concept_figure(body, "0 0 900 450",
        "1997 香港双击结构:左框做空港元、右框做空恒指期货,中间金管局的两种反应各喂饱一条腿,底部港府直接入市的反击",
        "双击的精髓:两条腿方向正交、情景互补,无论央行如何选择,总有一条腿在收钱。对抗它的唯一方式是打在它的算式之外:直接买入它的对手盘。")


def _fig_k10_repo():
    """ch10:回购市场挤兑螺旋——折扣率与价格互相咬尾。"""
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">回购市场怎么挤兑:折扣率和价格互相咬尾</text>
            <!-- 螺旋五步循环 -->
            <ellipse cx="450" cy="250" rx="300" ry="150" fill="none" stroke="#41506b" stroke-width="2" stroke-dasharray="6 5"/>
            <rect x="330" y="70" width="240" height="52" rx="8" fill="rgba(18,29,49,0.85)" stroke="#e87878"/>
            <text x="450" y="102" text-anchor="middle" fill="#ffb4b4" font-size="13" font-weight="800">① 风声:MBS 开始跌</text>
            <rect x="580" y="180" width="250" height="52" rx="8" fill="rgba(18,29,49,0.85)" stroke="#e87878"/>
            <text x="705" y="212" text-anchor="middle" fill="#ffb4b4" font-size="13" font-weight="800">② 折扣率 2% → 40%</text>
            <rect x="580" y="300" width="250" height="52" rx="8" fill="rgba(18,29,49,0.85)" stroke="#e87878"/>
            <text x="705" y="332" text-anchor="middle" fill="#ffb4b4" font-size="13" font-weight="800">③ 同样的抵押,借到的钱少了</text>
            <rect x="70" y="300" width="250" height="52" rx="8" fill="rgba(18,29,49,0.85)" stroke="#e87878"/>
            <text x="195" y="332" text-anchor="middle" fill="#ffb4b4" font-size="13" font-weight="800">④ 被迫抛售资产补保证金</text>
            <rect x="70" y="180" width="250" height="52" rx="8" fill="rgba(18,29,49,0.85)" stroke="#e87878"/>
            <text x="195" y="212" text-anchor="middle" fill="#ffb4b4" font-size="13" font-weight="800">⑤ 价格跌更狠 → 回到 ①</text>
            <!-- 中央标注 -->
            <text x="450" y="238" text-anchor="middle" fill="#eef4f8" font-size="14" font-weight="800">融资流动性螺旋</text>
            <text x="450" y="262" text-anchor="middle" fill="#bcc9dd" font-size="12">Brunnermeier–Pedersen</text>
            <text x="450" y="282" text-anchor="middle" fill="#bcc9dd" font-size="12">每一圈都要抵押品管加一遍</text>
            <!-- 底部对照 -->
            <text x="450" y="430" text-anchor="middle" fill="#8499bd" font-size="12.5">2008 年 9 月,这个螺旋用四天走完贝尔斯登三个月的路:没有门口排队,只有回购单上以小时计的折扣率上调。</text>
            <text x="450" y="456" text-anchor="middle" fill="#eef4f8" font-size="13" font-weight="800">存款有存款保险,回购没有。</text>"""
    return concept_figure(body, "0 0 900 480",
        "回购市场挤兑的五步咬尾循环:MBS 跌、折扣率从 2% 涨到 40%、借款能力缩水、被迫抛售、价格再跌,中央标注融资流动性螺旋",
        "影子银行的挤兑不排队,在抵押品的折扣率上发生:昨天 98 元抵押能借 96,今天只能借 60,差额必须用卖资产补——卖出本身让价格再跌,拧紧下一圈。")


def _fig_k11_curve():
    """ch11:收益率曲线与倒挂——长短期利率打架的信号。"""
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">收益率曲线:平时上坡,危险时倒着挂</text>
            <!-- 坐标区 -->
            <line x1="90" y1="330" x2="810" y2="330" stroke="#41506b" stroke-width="2"/>
            <line x1="90" y1="330" x2="90" y2="70" stroke="#41506b" stroke-width="2"/>
            <text x="66" y="200" fill="#8499bd" font-size="12">利率</text>
            <text x="816" y="334" fill="#8499bd" font-size="12">期限</text>
            <!-- 正常曲线(上行) -->
            <path d="M 100 280 Q 300 200 800 120" stroke="#8fb37a" stroke-width="3" fill="none"/>
            <text x="640" y="104" fill="#b8d6a3" font-size="13" font-weight="800">正常形态:期限越长,利息越高</text>
            <text x="640" y="128" fill="#bcc9dd" font-size="11.5">短借长贷有利差,银行开心</text>
            <!-- 倒挂曲线(下行) -->
            <path d="M 100 130 Q 300 220 800 290" stroke="#e87878" stroke-width="3" fill="none"/>
            <text x="120" y="118" fill="#ffb4b4" font-size="13" font-weight="800">倒挂:短端比长端贵</text>
            <text x="120" y="142" fill="#bcc9dd" font-size="11.5">央行加息把短端顶上去了,连 5 年期都不愿给这么高</text>
            <!-- 倒挂的含义 -->
            <rect x="120" y="356" width="660" height="86" rx="10" fill="rgba(232,120,120,0.12)" stroke="rgba(232,120,120,0.5)"/>
            <text x="140" y="384" fill="#ffb4b4" font-size="13" font-weight="800">倒挂交易的是"央行的未来认输"</text>
            <text x="140" y="410" fill="#bcc9dd" font-size="12">长端利率 = 未来平均短期利率的市场预期。倒挂 = 市场赌央行很快就会降息,</text>
            <text x="140" y="430" fill="#bcc9dd" font-size="12">而此时降息的理由通常只有一个:经济衰退要来了。</text>
            <text x="450" y="474" text-anchor="middle" fill="#eef4f8" font-size="13" font-weight="800">历史样本:2 年-10 年倒挂后,衰退从未缺席过——只是不知道什么时候来。</text>
            <text x="450" y="500" text-anchor="middle" fill="#8499bd" font-size="12.5">用法:它是一个状态变量,带不来择时,但当它出现时,每一张多头仓位都该重新审一遍。</text>"""
    return concept_figure(body, "0 0 900 525",
        "收益率曲线坐标图:绿色正常曲线上坡,红色倒挂曲线下坡,底部框注明倒挂的含义是市场赌央行即将降息",
        "曲线的形状是央行之手与市场预期的合力。倒挂时,曲线的两端在打架:短端说'我现在紧',长端说'我知道你不会一直紧'——历史告诉我们,长端常常是对的.")


PATCH_K = {
    6: [("一栋房子卖出一百份保险", _fig_k6_waterfall)],
    9: [("做空一个国家的完整手册", _fig_k9_doubleplay)],
    10: [("挤兑的队伍排在回购市场上", _fig_k10_repo)],
    11: [("长短期利率打架的信号", _fig_k11_curve)],
}



def _fig_l8_stairs():
    """ch08:中等收入陷阱的楼梯图:红利耗尽后的两条路。"""
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">中等收入陷阱:楼梯爬到一半,梯子撤了</text>
            <!-- 楼梯 -->
            <rect x="80" y="330" width="160" height="40" rx="6" fill="rgba(122,167,240,0.25)" stroke="#7aa7f0"/>
            <text x="160" y="355" text-anchor="middle" fill="#a8c6ff" font-size="13" font-weight="800">农业起步</text>
            <rect x="240" y="280" width="160" height="40" rx="6" fill="rgba(122,167,240,0.35)" stroke="#7aa7f0"/>
            <text x="320" y="305" text-anchor="middle" fill="#a8c6ff" font-size="13" font-weight="800">出口代工</text>
            <rect x="400" y="230" width="160" height="40" rx="6" fill="rgba(240,201,106,0.3)" stroke="#f0c96a"/>
            <text x="480" y="255" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">中等收入(卡壳高发区)</text>
            <rect x="640" y="180" width="160" height="40" rx="6" fill="rgba(143,179,122,0.3)" stroke="#8fb37a"/>
            <text x="720" y="205" text-anchor="middle" fill="#b5d3a0" font-size="13" font-weight="800">高收入</text>
            <!-- 断梯 -->
            <line x1="560" y1="280" x2="640" y2="190" stroke="#ee8877" stroke-width="4" stroke-dasharray="10 8"/>
            <text x="600" y="160" text-anchor="middle" fill="#ee8877" font-size="13" font-weight="800">梯子撤了:工资涨了,廉价优势没了</text>
            <!-- 两条路 -->
            <path d="M 480 230 Q 560 150 700 128" fill="none" stroke="#8fb37a" stroke-width="4"/>
            <text x="620" y="120" text-anchor="middle" fill="#b5d3a0" font-size="13" font-weight="800">A:技术升级接上去(日韩)</text>
            <path d="M 480 272 Q 560 320 700 330" fill="none" stroke="#ee8877" stroke-width="4"/>
            <text x="620" y="352" text-anchor="middle" fill="#ffb4b4" font-size="13" font-weight="800">B:靠借债和老本打转(拉美)</text>
            <text x="450" y="400" text-anchor="middle" fill="#bcc9dd" font-size="12.5">判断看点:工人工资涨得比效率快,债务堆得比技术快,就是 B 路线的前兆</text>"""
    return concept_figure(body, "0 0 900 430",
        "中等收入陷阱楼梯图:农业起步、出口代工、中等收入三级台阶,通向高收入的梯子断掉,一条绿色路线升级接上去,一条红色路线原地打转",
        "爬楼前半段靠的是便宜劳动力和出口代工,谁都能爬;难的是工资涨起来之后那一级——梯子(廉价优势)撤了,要么靠技术升级接上去(日韩路线),要么靠借债在原地打转(拉美路线)。判断前兆就看两条:工资涨得比效率快、债务堆得比技术快。")


def _fig_l23_pipeline():
    """ch23:量化项目从原始数据到研究报告的分层流水线。"""
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">量化项目流水线:每一层只管自己的事</text>
            <!-- 六层管道 -->
            <rect x="40" y="70" width="120" height="56" rx="8" fill="rgba(18,29,49,0.8)" stroke="#7aa7f0"/>
            <text x="100" y="94" text-anchor="middle" fill="#a8c6ff" font-size="13" font-weight="800">原始数据</text>
            <text x="100" y="114" text-anchor="middle" fill="#bcc9dd" font-size="11">只读,不改</text>
            <rect x="190" y="70" width="120" height="56" rx="8" fill="rgba(18,29,49,0.8)" stroke="#7aa7f0"/>
            <text x="250" y="94" text-anchor="middle" fill="#a8c6ff" font-size="13" font-weight="800">清洗</text>
            <text x="250" y="114" text-anchor="middle" fill="#bcc9dd" font-size="11">对齐·去重·补缺</text>
            <rect x="340" y="70" width="120" height="56" rx="8" fill="rgba(240,201,106,0.2)" stroke="#f0c96a"/>
            <text x="400" y="94" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">特征/因子</text>
            <text x="400" y="114" text-anchor="middle" fill="#bcc9dd" font-size="11">每个有定义</text>
            <rect x="490" y="70" width="120" height="56" rx="8" fill="rgba(18,29,49,0.8)" stroke="#8fb37a"/>
            <text x="550" y="94" text-anchor="middle" fill="#b5d3a0" font-size="13" font-weight="800">训练</text>
            <text x="550" y="114" text-anchor="middle" fill="#bcc9dd" font-size="11">只用历史段</text>
            <rect x="640" y="70" width="100" height="56" rx="8" fill="rgba(18,29,49,0.8)" stroke="#ee8877"/>
            <text x="690" y="94" text-anchor="middle" fill="#ffb4b4" font-size="13" font-weight="800">预测</text>
            <text x="690" y="114" text-anchor="middle" fill="#bcc9dd" font-size="11">滚到样本外</text>
            <rect x="770" y="70" width="110" height="56" rx="8" fill="rgba(18,29,49,0.8)" stroke="#ee8877"/>
            <text x="825" y="94" text-anchor="middle" fill="#ffb4b4" font-size="13" font-weight="800">回测/报告</text>
            <text x="825" y="114" text-anchor="middle" fill="#bcc9dd" font-size="11">自动生成</text>
            <!-- 箭头 -->
            <line x1="160" y1="98" x2="188" y2="98" stroke="#8499bd" stroke-width="2.5"/>
            <line x1="310" y1="98" x2="338" y2="98" stroke="#8499bd" stroke-width="2.5"/>
            <line x1="460" y1="98" x2="488" y2="98" stroke="#8499bd" stroke-width="2.5"/>
            <line x1="610" y1="98" x2="638" y2="98" stroke="#8499bd" stroke-width="2.5"/>
            <line x1="740" y1="98" x2="768" y2="98" stroke="#8499bd" stroke-width="2.5"/>
            <!-- 数据不可回流红线 -->
            <path d="M 690 128 Q 550 190 400 168" fill="none" stroke="#ee8877" stroke-width="3" stroke-dasharray="8 6"/>
            <line x1="380" y1="160" x2="420" y2="176" stroke="#ee8877" stroke-width="3"/>
            <line x1="380" y1="176" x2="420" y2="160" stroke="#ee8877" stroke-width="3"/>
            <text x="545" y="186" text-anchor="middle" fill="#ffb4b4" font-size="12.5" font-weight="800">禁止:未来信息回流训练——一跨线就是前视偏差</text>
            <!-- 底部三栏口诀 -->
            <rect x="60" y="220" width="240" height="90" rx="10" fill="rgba(18,29,49,0.7)" stroke="rgba(122,167,240,0.4)"/>
            <text x="80" y="246" fill="#a8c6ff" font-size="13" font-weight="800">配置外置</text>
            <text x="80" y="270" fill="#bcc9dd" font-size="12">路径·参数全进配置文件</text>
            <text x="80" y="292" fill="#bcc9dd" font-size="12">代码里不许硬编码</text>
            <rect x="330" y="220" width="240" height="90" rx="10" fill="rgba(18,29,49,0.7)" stroke="rgba(240,201,106,0.4)"/>
            <text x="350" y="246" fill="#f0c96a" font-size="13" font-weight="800">失败也留档</text>
            <text x="350" y="270" fill="#bcc9dd" font-size="12">跑挂的实验记参数和报错</text>
            <text x="350" y="292" fill="#bcc9dd" font-size="12">失败的坑只值记一次</text>
            <rect x="600" y="220" width="240" height="90" rx="10" fill="rgba(18,29,49,0.7)" stroke="rgba(238,136,119,0.4)"/>
            <text x="620" y="246" fill="#ffb4b4" font-size="13" font-weight="800">测试断言守门</text>
            <text x="620" y="270" fill="#bcc9dd" font-size="12">因子值域、收益单位、</text>
            <text x="620" y="292" fill="#bcc9dd" font-size="12">截面覆盖率,进 CI 每天查</text>
            <text x="450" y="352" text-anchor="middle" fill="#bcc9dd" font-size="12.5">工程骨架的正确性不看代码多聪明,看三条纪律:数据单向流、配置全外置、结果可复现</text>"""
    return concept_figure(body, "0 0 920 385",
        "量化项目分层流水线图:原始数据、清洗、特征因子、训练、预测、回测报告六个方框单向排列,训练到因子之间画红色禁止回流线和叉号,下方三栏口诀分别为配置外置、失败也留档、测试断言守门",
        "量化项目的正确性靠的是三条纪律而不是代码聪明:数据只能从原始层一路单向流到报告层,训练绝不允许偷看样本外(一跨线就是前视偏差);路径参数全部外置到配置文件;跑挂的实验也要留档,同样的坑只值记一次。")


def _fig_m8_export():
    """ch08:出口造血循环:外汇怎么变成工资和工厂。"""
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">拿出口给自己造血:一个国家的造血循环</text>
            <!-- 中心循环四个节点 -->
            <rect x="360" y="70" width="180" height="56" rx="8" fill="rgba(122,167,240,0.25)" stroke="#7aa7f0"/>
            <text x="450" y="94" text-anchor="middle" fill="#a8c6ff" font-size="13" font-weight="800">开工厂接订单</text>
            <text x="450" y="114" text-anchor="middle" fill="#bcc9dd" font-size="11">先把东西卖出去</text>
            <rect x="640" y="196" width="180" height="56" rx="8" fill="rgba(143,179,122,0.25)" stroke="#8fb37a"/>
            <text x="730" y="220" text-anchor="middle" fill="#b5d3a0" font-size="13" font-weight="800">外汇流进来</text>
            <text x="730" y="240" text-anchor="middle" fill="#bcc9dd" font-size="11">美元/欧元落袋</text>
            <rect x="360" y="320" width="180" height="56" rx="8" fill="rgba(240,201,106,0.25)" stroke="#f0c96a"/>
            <text x="450" y="344" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">结汇变本币</text>
            <text x="450" y="364" text-anchor="middle" fill="#bcc9dd" font-size="11">央行/银行系统放大</text>
            <rect x="80" y="196" width="180" height="56" rx="8" fill="rgba(238,136,119,0.2)" stroke="#ee8877"/>
            <text x="170" y="220" text-anchor="middle" fill="#ffb4b4" font-size="13" font-weight="800">发工资扩内需</text>
            <text x="170" y="240" text-anchor="middle" fill="#bcc9dd" font-size="11">工人有钱再消费</text>
            <!-- 循环箭头 -->
            <path d="M 540 100 Q 660 130 716 192" fill="none" stroke="#8499bd" stroke-width="3" marker-end="url(#arrowM)"/>
            <path d="M 700 252 Q 620 306 544 336" fill="none" stroke="#8499bd" stroke-width="3"/>
            <path d="M 360 350 Q 240 320 190 256" fill="none" stroke="#8499bd" stroke-width="3"/>
            <path d="M 200 196 Q 260 130 356 104" fill="none" stroke="#8499bd" stroke-width="3"/>
            <defs><marker id="arrowM" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#8499bd"/></marker></defs>
            <!-- 循环中心 -->
            <circle cx="450" cy="212" r="46" fill="rgba(18,29,49,0.9)" stroke="#f0c96a" stroke-width="2"/>
            <text x="450" y="208" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">造血机</text>
            <text x="450" y="228" text-anchor="middle" fill="#bcc9dd" font-size="11">越转越壮</text>
            <text x="450" y="412" text-anchor="middle" fill="#bcc9dd" font-size="12.5">循环一旦转起来,工人变消费者,消费者养活更多工厂;反之订单一断,整个环跟着收缩</text>"""
    return concept_figure(body, "0 0 900 440",
        "出口造血循环图:开工厂接订单、外汇流进来、结汇变本币、发工资扩内需四个方框围成顺时针循环,中心圆写造血机越转越壮",
        "一个国家拿出口给自己造血的完整循环:开工厂接订单,外汇流进来,结汇变成本币,发工资扩内需,工人变消费者再养活更多工厂——越转越壮。反过来,订单一断,整个环跟着收缩。")


def _fig_m23_dirs():
    """ch23:量化项目目录分层:原始层只读,特征层可算,报告层只产。"""
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">把目录当地层:每一层只许干一件事</text>
            <!-- 三层地层,像地质剖面 -->
            <rect x="80" y="70" width="740" height="84" rx="8" fill="rgba(122,167,240,0.15)" stroke="#7aa7f0"/>
            <text x="110" y="102" fill="#a8c6ff" font-size="14" font-weight="800">data/raw 原始层</text>
            <text x="110" y="128" fill="#bcc9dd" font-size="12">落地之后一个字都不许改——改坏了没人知道,所有脏活留给下一层</text>
            <rect x="80" y="166" width="740" height="84" rx="8" fill="rgba(240,201,106,0.15)" stroke="#f0c96a"/>
            <text x="110" y="198" fill="#f0c96a" font-size="14" font-weight="800">data/features 特征层</text>
            <text x="110" y="224" fill="#bcc9dd" font-size="12">清洗、对齐、算因子全在这里;每个因子一张登记表:定义、公式、值域、频率</text>
            <rect x="80" y="262" width="740" height="84" rx="8" fill="rgba(238,136,119,0.13)" stroke="#ee8877"/>
            <text x="110" y="294" fill="#ffb4b4" font-size="14" font-weight="800">reports 报告层</text>
            <text x="110" y="320" fill="#bcc9dd" font-size="12">回测曲线、指标表、报错日志只从这里出;截图从贴自动生成,杜绝手工美图</text>
            <!-- 层间箭头:只许向下 -->
            <line x1="450" y1="156" x2="450" y2="164" stroke="#8499bd" stroke-width="3"/>
            <line x1="450" y1="252" x2="450" y2="260" stroke="#8499bd" stroke-width="3"/>
            <text x="470" y="161" fill="#8499bd" font-size="11">只许向下读</text>
            <text x="470" y="257" fill="#8499bd" font-size="11">只许向下写</text>
            <!-- 右侧红线:禁止反向 -->
            <path d="M 800 330 Q 860 220 800 100" fill="none" stroke="#ee8877" stroke-width="3" stroke-dasharray="8 6"/>
            <line x1="786" y1="88" x2="814" y2="112" stroke="#ee8877" stroke-width="3"/>
            <line x1="786" y1="112" x2="814" y2="88" stroke="#ee8877" stroke-width="3"/>
            <text x="450" y="388" text-anchor="middle" fill="#bcc9dd" font-size="12.5">吃过亏的项目最后都长成一个样:原始层只读、特征层可算、报告层只产,箭头一律向下</text>"""
    return concept_figure(body, "0 0 900 415",
        "量化项目目录三层图:raw 原始层只读、features 特征层可算、reports 报告层只产,层间只允许向下读写,右侧红色虚线表示禁止反向回流",
        "把目录当地质层:data/raw 落地后一个字不许改;data/features 负责清洗和算因子,每个因子都有登记表;reports 只负责产出回测曲线和报错日志。吃亏的项目最后都长成一个样——箭头一律向下,谁也不许反向回流。")


PATCH_M = {
    8: [("拿出口给自己造血", _fig_m8_export)],
    28: [("目录结构先分层", _fig_m23_dirs)],
}

def _fig_n12_pool():
    """ch12:风险汇聚池:百人凑五条鱼,翻船赔两百条。"""
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">风险汇聚池:每人交确定的 5 条,翻船拿保底 200</text>
            <!-- 左:100个渔民 -->
            <text x="180" y="80" text-anchor="middle" fill="#a8c6ff" font-size="13" font-weight="800">100 个渔民,各交</text>
            <g fill="#7aa7f0">
              <circle cx="100" cy="120" r="12"/><circle cx="150" cy="120" r="12"/><circle cx="200" cy="120" r="12"/><circle cx="250" cy="120" r="12"/>
              <circle cx="100" cy="160" r="12"/><circle cx="150" cy="160" r="12"/><circle cx="200" cy="160" r="12"/><circle cx="250" cy="160" r="12"/>
              <circle cx="100" cy="200" r="12"/><circle cx="150" cy="200" r="12"/><circle cx="200" cy="200" r="12"/><circle cx="250" cy="200" r="12"/>
            </g>
            <text x="180" y="240" text-anchor="middle" fill="#bcc9dd" font-size="12">每年 5 条鱼(确定的小损失)</text>
            <!-- 汇聚箭头 -->
            <path d="M 300 150 Q 370 150 400 175" fill="none" stroke="#8499bd" stroke-width="3" marker-end="url(#arrowN)"/>
            <!-- 中:公共仓 -->
            <rect x="400" y="130" width="140" height="90" rx="10" fill="rgba(240,201,106,0.2)" stroke="#f0c96a"/>
            <text x="470" y="162" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">公共仓</text>
            <text x="470" y="184" text-anchor="middle" fill="#bcc9dd" font-size="12">收 500 条/年</text>
            <text x="470" y="203" text-anchor="middle" fill="#bcc9dd" font-size="12">大数定律:出险≈2 条船</text>
            <!-- 下:翻转宿 -->
            <path d="M 540 205 Q 620 250 660 240" fill="none" stroke="#8fb37a" stroke-width="3" marker-end="url(#arrowN)"/>
            <rect x="640" y="200" width="200" height="70" rx="10" fill="rgba(143,179,122,0.2)" stroke="#8fb37a"/>
            <text x="740" y="228" text-anchor="middle" fill="#b5d3a0" font-size="13" font-weight="800">谁家翻了船</text>
            <text x="740" y="250" text-anchor="middle" fill="#bcc9dd" font-size="12">一次赔 200 条(扛两年难关)</text>
            <!-- 账本 -->
            <rect x="60" y="290" width="780" height="90" rx="10" fill="rgba(18,29,49,0.7)" stroke="rgba(240,201,106,0.45)"/>
            <text x="84" y="318" fill="#f0c96a" font-size="13" font-weight="800">全年账本</text>
            <text x="84" y="342" fill="#bcc9dd" font-size="12">进:100 人 × 5 = 500 条;出:2 人翻船 × 200 条 = 400 条;结余 100 条是安全边际</text>
            <text x="84" y="364" fill="#bcc9dd" font-size="12">若某年翻了 5 条船赔 1000 条,缺口 500 条就要预警信号——那叫偿付能力压力</text>
            <defs><marker id="arrowN" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#8499bd"/></marker></defs>
            <text x="450" y="412" text-anchor="middle" fill="#8499bd" font-size="12.5">保险不消灭灾难,只是把“一人塌天”改写成“众人凑手”</text>"""
    return concept_figure(body, "0 0 900 440",
        "风险汇聚池图:一百个渔民每人五条的确定缴费汇入公共仓,翻船家庭一次获赔两百条,账本显示收五百赔四百,结余是安全边际",
        "保险原始模型:一百个渔民每年各交确定的 5 条鱼,谁家翻船就从公共仓领 200 条。大数定律让收赔两端都可预算——500 进、约 400 出,多出来的 100 条就是保险公司的生存缝隙。")


def _fig_n12_diffs():
    """ch12:三差三口袋:死差费差利各自从哪里来。"""
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">三差三口袋:保险公司的利润来自哪里</text>
            <!-- 三口袋扇形排部 -->
            <rect x="60" y="90" width="240" height="150" rx="12" fill="rgba(122,167,240,0.2)" stroke="#7aa7f0"/>
            <text x="180" y="120" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">死差(表损差)</text>
            <text x="180" y="146" text-anchor="middle" fill="#bcc9dd" font-size="12">预计赔 100 例</text>
            <text x="180" y="168" text-anchor="middle" fill="#bcc9dd" font-size="12">实际只赔 90 例</text>
            <text x="180" y="196" text-anchor="middle" fill="#8fb37a" font-size="13" font-weight="800">差价 = 承保利润</text>
            <text x="180" y="220" text-anchor="middle" fill="#8499bd" font-size="11">手艺口袋:长期寿险圭臬</text>
            <rect x="330" y="90" width="240" height="150" rx="12" fill="rgba(240,201,106,0.2)" stroke="#f0c96a"/>
            <text x="450" y="120" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">费差</text>
            <text x="450" y="146" text-anchor="middle" fill="#bcc9dd" font-size="12">预算费用 1 亿</text>
            <text x="450" y="168" text-anchor="middle" fill="#bcc9dd" font-size="12">实际花 8000 万</text>
            <text x="450" y="196" text-anchor="middle" fill="#8fb37a" font-size="13" font-weight="800">节约 = 运营利润</text>
            <text x="450" y="220" text-anchor="middle" fill="#8499bd" font-size="11">治理口袋:各公司经营分水岭</text>
            <rect x="600" y="90" width="240" height="150" rx="12" fill="rgba(238,136,119,0.15)" stroke="#ee8877"/>
            <text x="720" y="120" text-anchor="middle" fill="#ffb4b4" font-size="15" font-weight="800">利差</text>
            <text x="720" y="146" text-anchor="middle" fill="#bcc9dd" font-size="12">合同约定 2.5%</text>
            <text x="720" y="168" text-anchor="middle" fill="#bcc9dd" font-size="12">实际投资 4.5%</text>
            <text x="720" y="196" text-anchor="middle" fill="#8fb37a" font-size="13" font-weight="800">差额 = 投资利润(久期长×规模大=大头)</text>
            <text x="720" y="220" text-anchor="middle" fill="#8499bd" font-size="11">利率口袋:利率下行期变利差损</text>
            <!-- 底部竖线 -->
            <text x="450" y="288" text-anchor="middle" fill="#bcc9dd" font-size="13">利率长期下行时,口袋三会从利润反转成亏损 —— 这是日本 90 年代与中国 2020 年代共同的保险剧本</text>
            <text x="450" y="316" text-anchor="middle" fill="#8499bd" font-size="12.5">记住:死差和费差管“技术”,利差管“行情”;真正决定一家保险公司四十年的,是它敢不敢把利率假设定得保守</text>"""
    return concept_figure(body, "0 0 900 350",
        "三差三口袋图:死差靠赔付低于预期、费差靠费用结余、利差靠投资收益超过假设利率,利差部分标为利率口袋,注明利率下行会变成利差损",
        "保险公司的利润有三口:死差靠赔得比预想得少,费差靠花得比预算少,利差靠投资赚得比定价假设多。长险里大头是利差——所以利率长期下行,口袋三会从利润反转成利差损,输入一个行业轮回。")


def _fig_n13_paygo():
    """ch13:现收现付:下一代缴的钱今天发给上一代。"""
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">现收现付:今天缴的钱,今晚就在别人碗里</text>
            <!-- 左:在职年轻人 -->
            <rect x="60" y="90" width="220" height="200" rx="12" fill="rgba(122,167,240,0.2)" stroke="#7aa7f0"/>
            <text x="170" y="120" text-anchor="middle" fill="#a8c6ff" font-size="14" font-weight="800">现在缴费的年轻人</text>
            <text x="170" y="148" text-anchor="middle" fill="#bcc9dd" font-size="12">月薪一万,养老年月缴 800</text>
            <text x="170" y="170" text-anchor="middle" fill="#bcc9dd" font-size="12">单位再缴 1600</text>
            <text x="170" y="196" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">每月合计 2400 元</text>
            <text x="170" y="222" text-anchor="middle" fill="#8499bd" font-size="11">不存进你的储蓄罐,直接进入</text>
            <text x="170" y="240" text-anchor="middle" fill="#8499bd" font-size="11">当年的统筹资金池</text>
            <!-- 箭头 -->
            <path d="M 282 180 Q 370 175 410 190" fill="none" stroke="#8499bd" stroke-width="3" marker-end="url(#arrowN2)"/>
            <!-- 中:统筹池 -->
            <rect x="415" y="140" width="150" height="100" rx="10" fill="rgba(240,201,106,0.2)" stroke="#f0c96a"/>
            <text x="490" y="168" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">统筹池</text>
            <text x="490" y="192" text-anchor="middle" fill="#bcc9dd" font-size="12">现收现付制度</text>
            <text x="490" y="212" text-anchor="middle" fill="#bcc9dd" font-size="12">当年收 = 当年支</text>
            <!-- 箭头发到退休者 -->
            <path d="M 568 190 Q 640 190 700 180" fill="none" stroke="#8fb37a" stroke-width="3" marker-end="url(#arrowN2)"/>
            <!-- 右:退休者 -->
            <rect x="705" y="90" width="160" height="200" rx="12" fill="rgba(143,179,122,0.2)" stroke="#8fb37a"/>
            <text x="785" y="120" text-anchor="middle" fill="#b5d3a0" font-size="14" font-weight="800">当前的退休者</text>
            <text x="785" y="148" text-anchor="middle" fill="#bcc9dd" font-size="12">月领 4000 元</text>
            <text x="785" y="170" text-anchor="middle" fill="#bcc9dd" font-size="12">由今天 2 亿多缴费者</text>
            <text x="785" y="190" text-anchor="middle" fill="#bcc9dd" font-size="12">现收现付支撑</text>
            <!-- 底部日复循环 -->
            <text x="490" y="288" text-anchor="middle" fill="#bcc9dd" font-size="12">你的个人账户里只是一个“记账数”,不是现金存钱罐——等你退休,</text>
            <text x="490" y="310" text-anchor="middle" fill="#bcc9dd" font-size="12">再由下一代缴费者,按同样的逻辑发给你</text>
            <defs><marker id="arrowN2" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#8499bd"/></marker></defs>
            <text x="450" y="352" text-anchor="middle" fill="#8499bd" font-size="12.5">制度稳不稳,关键就看“缴费者不足、领者渐多”的抚养比——整套系统的呼吸口</text>"""
    return concept_figure(body, "0 0 900 395",
        "现收现付流程图:年轻人每月缴费进入统筹池,同月发给当前的退休者,个人账户只是记账数,底部说明抚养比是制度呼吸口",
        "现收现付的本质:你缴的养老钱不存进你的专属小金库,而是当月就付给父辈的退休金;你的退休金同理,取决于下一代。人口抚养比——缴费者与领取者之比——是整个制度的呼吸口。")


def _fig_n13_pillars():
    """ch13:养老三支柱:国家底、企业腰、自己顶。"""
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">养老三支柱:国家打底、企业加成、自己补顶</text>
            <!-- 三根柱子 -->
            <rect x="90" y="130" width="200" height="200" rx="10" fill="rgba(122,167,240,0.25)" stroke="#7aa7f0"/>
            <text x="190" y="158" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">第一支柱</text>
            <text x="190" y="182" text-anchor="middle" fill="#bcc9dd" font-size="12">基本养老保险</text>
            <text x="190" y="204" text-anchor="middle" fill="#bcc9dd" font-size="12">强制+现收现付</text>
            <text x="190" y="226" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">替代率约 50%</text>
            <text x="190" y="252" text-anchor="middle" fill="#8499bd" font-size="11">保底:饿不死</text>
            <rect x="350" y="130" width="200" height="200" rx="10" fill="rgba(240,201,106,0.2)" stroke="#f0c96a"/>
            <text x="450" y="158" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">第二支柱</text>
            <text x="450" y="182" text-anchor="middle" fill="#bcc9dd" font-size="12">企业/职业年金</text>
            <text x="450" y="204" text-anchor="middle" fill="#bcc9dd" font-size="12">单位主导+自愿</text>
            <text x="450" y="226" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">覆盖率&lt;10%</text>
            <text x="450" y="252" text-anchor="middle" fill="#8499bd" font-size="11">加码:过得还行</text>
            <rect x="610" y="130" width="200" height="200" rx="10" fill="rgba(238,136,119,0.15)" stroke="#ee8877"/>
            <text x="710" y="158" text-anchor="middle" fill="#ffb4b4" font-size="15" font-weight="800">第三支柱</text>
            <text x="710" y="182" text-anchor="middle" fill="#bcc9dd" font-size="12">个人养老金账户</text>
            <text x="710" y="204" text-anchor="middle" fill="#bcc9dd" font-size="12">完全市场+自愿</text>
            <text x="710" y="226" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">年上限 1.2 万</text>
            <text x="710" y="252" text-anchor="middle" fill="#8499bd" font-size="11">补顶:要活得体面</text>
            <!-- 底线台重 -->
            <rect x="60" y="335" width="780" height="32" rx="6" fill="rgba(18,29,49,0.7)" stroke="rgba(132,153,189,0.4)"/>
            <text x="450" y="356" text-anchor="middle" fill="#bcc9dd" font-size="12">退休目标替代率国际线 ≈ 70%,第一支柱不够,二点五根必须齐上</text>
            <text x="450" y="390" text-anchor="middle" fill="#8499bd" font-size="12.5">支柱框架你不是被动等:第一支柱资格优先别断缴,第三支柱用足税优,超出的部分再用市场工具</text>"""
    return concept_figure(body, "0 0 900 415",
        "养老三支柱图:第一支柱基本养老保险替代率约五十,第二支柱企业年金覆盖率小于十,第三支柱个人养老金年上限一万二,底部标注国际线百分之七十",
        "三支柱的记忆法:第一支柱保你饿不死(替代率约五成),第二支柱看单位有没有福利心,第三支柱看你自己是不是精明。国际线:退休后收入要达到退休前的七成,三根柱子缺一不可。")


PATCH_N = {
    12: [("保险公司为什么敢接你的灾难", _fig_n12_pool),
         ("保险公司靠什么赚钱", _fig_n12_diffs)],
    13: [("你的养老金其实不在你的账户里", _fig_n13_paygo),
         ("国家、企业、自己各扛一部分", _fig_n13_pillars)],
}

def _fig_r30_checklist():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">上线前的回测-实盘一致性检查</text>
            <rect x="60" y="80" width="360" height="260" rx="12" fill="rgba(238,136,119,0.15)" stroke="#ee8877"/>
            <text x="240" y="108" text-anchor="middle" fill="#ffb4b4" font-size="15" font-weight="800">七条硬检验(任一答“不确定”就停)</text>
            <text x="85" y="140" fill="#bcc9dd" font-size="12">① 数据是同一家供应商、同一个更新时点吗</text>
            <text x="85" y="166" fill="#bcc9dd" font-size="12">② 时间线是逻辑时序对齐的吗</text>
            <text x="85" y="192" fill="#bcc9dd" font-size="12">③ 股票池是历史时点的名单吗</text>
            <text x="85" y="218" fill="#bcc9dd" font-size="12">④ 交易规则(涨跌停/停牌/最小手数)被完整包含了吗</text>
            <text x="85" y="244" fill="#bcc9dd" font-size="12">⑤ 成本估算里滑点跟清仓精度按压线测过吗</text>
            <text x="85" y="270" fill="#bcc9dd" font-size="12">⑥ 因子是否单独出过单因子报告</text>
            <text x="85" y="296" fill="#bcc9dd" font-size="12">⑦ 基准模型和假定的简单基线比较过了吗</text>
            <rect x="480" y="80" width="360" height="260" rx="12" fill="rgba(240,201,106,0.15)" stroke="#f0c96a"/>
            <text x="660" y="108" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">稳态运营的三块长期检查</text>
            <text x="505" y="140" fill="#bcc9dd" font-size="12">⑧ 组合约束跟仓位上限跟风险预算一致吗</text>
            <text x="505" y="166" fill="#bcc9dd" font-size="12">⑨ 同一行报告,两周以后你还能复现出来吗</text>
            <text x="505" y="192" fill="#bcc9dd" font-size="12">⑩ 模拟盘至少跑过两周且有正当收益你才能上实盘吗</text>
            <text x="505" y="226" fill="#ee8877" font-size="13" font-weight="800">清单写进代码,不写进脑子</text>
            <text x="505" y="254" fill="#bcc9dd" font-size="12">每次上线前跑一遍 PYTHON 脚本,</text>
            <text x="505" y="278" fill="#bcc9dd" font-size="12">任何一项没过就不允许 git commit</text>
            <text x="505" y="308" fill="#bcc9dd" font-size="12">这不是要让机器聪明,是让制度顽固</text>"""
    return concept_figure(body, "0 0 900 365",
        "上线前十问检查图:从数据时间线股池规则成本到因子基线模拟全盘的一盘检测清单",
        "上线检查清单不是安慰品,是制度化的不相信——既有信心不敬重'我相信是有料的',而是制度让'上线看好不我不相信'。七条硬检验加三块长期检查,过不了的就不允许提交。")


def _fig_r31_five():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">读研究报告的第一件事:先问五个问题,再看结论</text>
            <text x="80" y="70" fill="#8499bd" font-size="12" font-weight="800">哪点子数据不在于你看到丽性 —— 而在于你问对了什么</text>
            <text x="80" y="108" fill="#f0c96a" font-size="13" font-weight="800">① 它要证明的核心命题是什么?</text>
            <text x="120" y="130" fill="#bcc9dd" font-size="12">看不懂要证明什么就别跟着看结果—先弄懂假设与结论的逻辑.</text>
            <text x="80" y="168" fill="#f0c96a" font-size="13" font-weight="800">② 数据从哪里来,时间窗多长,中爻巴克?</text>
            <text x="120" y="190" fill="#bcc9dd" font-size="12">数据口径、历史时段、修正方向都会影响结论,必须透出来.</text>
            <text x="80" y="228" fill="#f0c96a" font-size="13" font-weight="800">③ 股票池是什么,跟谁比?</text>
            <text x="120" y="250" fill="#bcc9dd" font-size="12">与沪深 300 比跟与创业板比,完全是两种结论.</text>
            <text x="80" y="288" fill="#f0c96a" font-size="13" font-weight="800">④ 成本被算完了吗?冲击成本、滑点、容量上边上足过吗?</text>
            <text x="120" y="310" fill="#bcc9dd" font-size="12">单纯的低换手高阿尔法,往往在放大执行成本后被砸裸奔.</text>
            <text x="80" y="348" fill="#f0c96a" font-size="13" font-weight="800">⑤ 样本外令人满意吗?作者又赚不到这里提到的钱?</text>
            <text x="120" y="370" fill="#bcc9dd" font-size="12">如果作者的基金早已把钱从这里赚走了,这一笔能被一分钱留给你吗?</text>
            <text x="450" y="410" text-anchor="middle" fill="#bcc9dd" font-size="12.5">回答这五个问题之前,漂亮结论越多越警惕——它们往往不是诱你跳过这五问的廚化剂</text>"""
    return concept_figure(body, "0 0 900 435",
        "阅读研究报告五问清单:命题、数据、对比、成本容量、样本外",
        "真正能防御假研究的,是看之前先问五个问题。报告里没填这五个空的,圧石头有心写多长,或很多结论都是给你看的“添油堵反”。")


PATCH_R7 = {
    30: [("别让两套代码各跑各的", _fig_r30_checklist)],
    31: [("它到底想证明什么", _fig_r31_five)],
}



def _fig_r38_eyefund():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">招募书先看这五行,不看宣传册</text>
            <rect x="80" y="80" width="740" height="48" rx="8" fill="rgba(122,167,240,0.15)" stroke="rgba(122,167,240,0.5)"/>
            <text x="104" y="110" fill="#a8c6ff" font-size="13" font-weight="800">① 投资范围:能买什么、比例多少、有没有“可投其他工具”的活口</text>
            <rect x="80" y="138" width="740" height="48" rx="8" fill="rgba(240,201,106,0.12)" stroke="rgba(240,201,106,0.45)"/>
            <text x="104" y="168" fill="#f0c96a" font-size="13" font-weight="800">② 申购赎回:开放日、最低赎回额、管理人是否有权暂停赎回</text>
            <rect x="80" y="196" width="740" height="48" rx="8" fill="rgba(143,179,122,0.15)" stroke="rgba(143,179,122,0.5)"/>
            <text x="104" y="226" fill="#b5d3a0" font-size="13" font-weight="800">③ 风控线:预警线、止损线、清盘线分别设在净值多少</text>
            <rect x="80" y="254" width="740" height="48" rx="8" fill="rgba(238,136,119,0.12)" stroke="rgba(238,136,119,0.4)"/>
            <text x="104" y="284" fill="#ffb4b4" font-size="13" font-weight="800">④ 费率结构:申购/赎回/管理/托管/销售服务费,合计一年要被吃掉多少</text>
            <rect x="80" y="312" width="740" height="48" rx="8" fill="rgba(132,153,189,0.12)" stroke="rgba(132,153,189,0.4)"/>
            <text x="104" y="342" fill="#bcc9dd" font-size="13">⑤ 基金经理:从业年限、在任多久、之前的代表作业绩</text>
            <text x="450" y="392" text-anchor="middle" fill="#bcc9dd" font-size="12.5">读完这五处再决定要不要看宣传图——顺序不能反</text>"""
    return concept_figure(body, "0 0 900 415",
        "招募说明书五处必看:投资范围、申购赎回、风控线、费率、基金经理",
        "两百页招募书里,能决定一款产品能不能买的,就是五处的条款。不用苦算数据,也不用看完所有报表——把这五处看透,你已跑赢大多数被广告糊弄的人。")


def _fig_r39_small():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">小资金实盘纪律:先把亏损的上限写死</text>
            <rect x="70" y="80" width="360" height="260" rx="12" fill="rgba(122,167,240,0.18)" stroke="#7aa7f0"/>
            <text x="250" y="108" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">三条资金上限</text>
            <text x="250" y="142" text-anchor="middle" fill="#bcc9dd" font-size="12">本金上限:5 万元封顶</text>
            <text x="250" y="170" text-anchor="middle" fill="#bcc9dd" font-size="12">单笔亏损上限:每笔最多 -1%本金</text>
            <text x="250" y="198" text-anchor="middle" fill="#bcc9dd" font-size="12">日内总亏损上限:-2% 强制关单收工</text>
            <text x="250" y="226" text-anchor="middle" fill="#ee8877" font-size="13" font-weight="800">连续亏 3 天,当天不许再开新仓</text>
            <text x="250" y="254" text-anchor="middle" fill="#bcc9dd" font-size="12">周末必须做一次对账</text>
            <text x="250" y="300" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">在第一步是习惯而不是收益</text>
            <rect x="470" y="80" width="360" height="260" rx="12" fill="rgba(240,201,106,0.15)" stroke="#f0c96a"/>
            <text x="650" y="108" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">四个周期信号</text>
            <text x="650" y="142" text-anchor="middle" fill="#bcc9dd" font-size="12">月度亏损超 10%:仓位减半</text>
            <text x="650" y="170" text-anchor="middle" fill="#bcc9dd" font-size="12">月度收益超 20%:手数减半</text>
            <text x="650" y="198" text-anchor="middle" fill="#bcc9dd" font-size="12">连续 4 周横盘:微调参数不追加资金</text>
            <text x="650" y="226" text-anchor="middle" fill="#bcc9dd" font-size="12">4 周以上不回撤:可加一档资金</text>
            <text x="650" y="254" text-anchor="middle" fill="#bcc9dd" font-size="12">任意信号之间不许同情绪交易</text>
            <text x="650" y="300" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">规则写下来才可信,搭讪日拱一卒</text>
            <text x="450" y="376" text-anchor="middle" fill="#bcc9dd" font-size="12.5">每一条都是用来跟自己交朋友:趁自己没在市场里虚惊时先把规则写好——真实情绪来的时候,不会听你从容的道理</text>"""
    return concept_figure(body, "0 0 900 400",
        "小资金实盘规则图:本金上限五万,单笔亏一百分点,连亏三日强制收工",
        "实盘亏的不只是钱,是心态。小资金的真正价值是练纪律——上限的目的不是顾虑亏损,是给你在最想加杠杆时,一个按得住自己的理由。")


def _fig_r40_two_lists():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">最终清单的两列:能说明白才算懂</text>
            <rect x="70" y="80" width="360" height="265" rx="12" fill="rgba(122,167,240,0.18)" stroke="#7aa7f0"/>
            <text x="250" y="108" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">金融直觉列</text>
            <text x="250" y="138" text-anchor="middle" fill="#bcc9dd" font-size="12">钱和财富的区别</text>
            <text x="250" y="166" text-anchor="middle" fill="#bcc9dd" font-size="12">银行为什么又脆弱又有用</text>
            <text x="250" y="194" text-anchor="middle" fill="#bcc9dd" font-size="12">股票与债券的风险结构差异</text>
            <text x="250" y="222" text-anchor="middle" fill="#bcc9dd" font-size="12">基金与 ETF 的基本结构</text>
            <text x="250" y="250" text-anchor="middle" fill="#bcc9dd" font-size="12">收益风险指标到底反映什么</text>
            <text x="250" y="278" text-anchor="middle" fill="#bcc9dd" font-size="12">有效市场与行为偏差的关系</text>
            <text x="250" y="310" text-anchor="middle" fill="#8499bd" font-size="12">口舌讲不明白的就是没掌握</text>
            <rect x="470" y="80" width="360" height="265" rx="12" fill="rgba(240,201,106,0.15)" stroke="#f0c96a"/>
            <text x="650" y="108" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">工程纪律列</text>
            <text x="650" y="138" text-anchor="middle" fill="#bcc9dd" font-size="12">股票池必须点时确定</text>
            <text x="650" y="166" text-anchor="middle" fill="#bcc9dd" font-size="12">回测必须包含真实成本</text>
            <text x="650" y="194" text-anchor="middle" fill="#bcc9dd" font-size="12">因子必须单独出具报告</text>
            <text x="650" y="222" text-anchor="middle" fill="#bcc9dd" font-size="12">模型必须和田农药基线对比</text>
            <text x="650" y="250" text-anchor="middle" fill="#bcc9dd" font-size="12">组合必须有明确的约束</text>
            <text x="650" y="278" text-anchor="middle" fill="#bcc9dd" font-size="12">报告必须能被复现</text>
            <text x="650" y="310" text-anchor="middle" fill="#8499bd" font-size="12">没写出来的不允许操作</text>
            <text x="450" y="378" text-anchor="middle" fill="#bcc9dd" font-size="12.5">能写下来就是能证明,能说服小白就是能讲透——从这个列开始一步步推进到最后的仓位和决策</text>"""
    return concept_figure(body, "0 0 900 400",
        "最终清单双列:金融直觉说人话,工程纪律写代码式约束",
        "毕业考试不是背定义,是把它们写给你不看行不辿;工程侧同理:把规则说得出来才算真的理解,讲得出来就要拿模拟盘认证。")


def _fig_r41_overfit():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">判断题里最容易翻车的四道</text>
            <rect x="70" y="80" width="360" height="195" rx="12" fill="rgba(238,136,119,0.15)" stroke="#ee8877"/>
            <text x="250" y="108" text-anchor="middle" fill="#ffb4b4" font-size="14" font-weight="800">题A:钱多了,社会一定更富?</text>
            <text x="250" y="140" text-anchor="middle" fill="#bcc9dd" font-size="12">错误直觉:多一个零就是财富加量</text>
            <text x="250" y="168" text-anchor="middle" fill="#ee8877" font-size="13" font-weight="800">✗</text>
            <text x="250" y="200" text-anchor="middle" fill="#bcc9dd" font-size="12">钱只是调动真实财富的工具,</text>
            <text x="250" y="228" text-anchor="middle" fill="#bcc9dd" font-size="12">池子不宽,水位再涨也只是表面热闹</text>
            <rect x="470" y="80" width="360" height="195" rx="12" fill="rgba(238,136,119,0.15)" stroke="#ee8877"/>
            <text x="650" y="108" text-anchor="middle" fill="#ffb4b4" font-size="14" font-weight="800">题B:债券一定比股票安全?</text>
            <text x="650" y="140" text-anchor="middle" fill="#bcc9dd" font-size="12">错误直觉:情歌一样稳的债比股票保险</text>
            <text x="650" y="168" text-anchor="middle" fill="#ee8877" font-size="13" font-weight="800">✗</text>
            <text x="650" y="200" text-anchor="middle" fill="#bcc9dd" font-size="12">利率上涨时债价下跌,违约能蚀损的是票面,</text>
            <text x="650" y="228" text-anchor="middle" fill="#bcc9dd" font-size="12">美债负责涨收益不负责保本金</text>
            <rect x="70" y="290" width="360" height="120" rx="12" fill="rgba(240,201,106,0.15)" stroke="#f0c96a"/>
            <text x="250" y="318" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">题C:高胜率策略 = 好策略?</text>
            <text x="250" y="346" text-anchor="middle" fill="#bcc9dd" font-size="12">错误直觉:稳赢的对</text>
            <text x="250" y="374" text-anchor="middle" fill="#bcc9dd" font-size="12">正确的区别:期望值与回撤组合</text>
            <text x="250" y="398" text-anchor="middle" fill="#bcc9dd" font-size="12">99 次小赚 vs 1 次大亏是高胜率低 EV</text>
            <rect x="470" y="290" width="360" height="120" rx="12" fill="rgba(240,201,106,0.15)" stroke="#f0c96a"/>
            <text x="650" y="318" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">题D:回测曲线好 ⇒ 能实盘?</text>
            <text x="650" y="346" text-anchor="middle" fill="#bcc9dd" font-size="12">错误直觉:谷仓曲线 = 能力</text>
            <text x="650" y="374" text-anchor="middle" fill="#bcc9dd" font-size="12">史论速率不清仓生产、成本、样本外</text>
            <text x="650" y="398" text-anchor="middle" fill="#bcc9dd" font-size="12">实盘跟排练完全不同</text>
            <text x="450" y="450" text-anchor="middle" fill="#bcc9dd" font-size="12.5">这四道题不是用来考的,是用来在你每一次要下手前重新对一次答案</text>"""
    return concept_figure(body, "0 0 900 475",
        "四道最易翻车判断题:钱多不一定富、债券不一定稳赢、胜率高不一定好、回测好不等于实盘",
        "把它们做对,比会做 100 道计算题更难——因为收益曲线是冷冰冰的,而直觉是热的。")


def _fig_r42_lifecycle():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">一个稳妥个人量化项目的成长路径:八步闭环</text>
            <circle cx="450" cy="230" r="160" fill="rgba(122,167,240,0.1)" stroke="#7aa7f0" stroke-width="2"/>
            <text x="450" y="225" text-anchor="middle" fill="#a8c6ff" font-size="14" font-weight="800">你 · 主理人</text>
            <text x="450" y="247" text-anchor="middle" fill="#bcc9dd" font-size="12">外界的问题:下一步去哪儿?</text>
            <!-- 环绕的八步 -->
            <g font-size="12.5" font-weight="800">
              <text x="90" y="80" fill="#f0c96a">① 问题足够小</text>
              <text x="300" y="46" fill="#a8c6ff">② 先做数据检查</text>
              <text x="560" y="46" fill="#8fb37a">③ 做最简单基线</text>
              <text x="760" y="80" fill="#ee8877">④ 单因子报告</text>
              <text x="790" y="240" fill="#ee8877">⑤ 他如何判断下一步</text>
              <text x="70" y="240" fill="#f0c96a">⑥ 小资金半自动</text>
              <text x="300" y="420" fill="#a8c6ff">⑦ 样本外与模拟盘</text>
              <text x="560" y="420" fill="#f0c96a">⑧ 多因子组合</text>
            </g>
            <text x="450" y="462" text-anchor="middle" fill="#bcc9dd" font-size="12.5">圈不是闭环,是循环——走在第八步时,又回到第一步问自己“这个新问题能不能再压小一点”</text>"""
    return concept_figure(body, "0 0 900 490",
        "量化项目八步闭环:小问题、数据检查、基线、单因子、组合、样本外模拟、小资金半自动、再提问——循环运行",
        "这是一张闭环图:问题变小→查数据→做基线→出单因子→组合→模拟盘→小实盘→再问下一个更小的问题。终点不存在,每一圈都是一次被修炼。")


def _fig_r43_checkpaper():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">附录这张纸不是讲知识,是上手前要问到位的口语化检查</text>
            <rect x="60" y="80" width="780" height="120" rx="10" fill="rgba(122,167,240,0.15)" stroke="rgba(122,167,240,0.5)"/>
            <text x="84" y="108" fill="#a8c6ff" font-size="14" font-weight="800">研究前(动理念)</text>
            <text x="84" y="134" fill="#bcc9dd" font-size="12">① 这个问题是不是小到一周之内能给个答案?</text>
            <text x="84" y="158" fill="#bcc9dd" font-size="12">② 最坏情况是亏钱 -2% 还是 -10% 或 -50%?</text>
            <text x="84" y="182" fill="#bcc9dd" font-size="12">③ 这一次的核算成本,是不是认真算过印花税和滑点?</text>
            <rect x="60" y="220" width="780" height="100" rx="10" fill="rgba(240,201,106,0.12)" stroke="rgba(240,201,106,0.45)"/>
            <text x="84" y="248" fill="#f0c96a" font-size="14" font-weight="800">回测前(动机器)</text>
            <text x="84" y="274" fill="#bcc9dd" font-size="12">④ 在那个历史时点,我到底有没有看到要用到的数据?</text>
            <text x="84" y="298" fill="#bcc9dd" font-size="12">⑤ 这套代码跟我后面模拟盘运行的是不是同一套?</text>
            <rect x="60" y="340" width="780" height="90" rx="10" fill="rgba(238,136,119,0.12)" stroke="rgba(238,136,119,0.4)"/>
            <text x="84" y="368" fill="#ffb4b4" font-size="14" font-weight="800">实盘前(动钱包)</text>
            <text x="84" y="394" fill="#bcc9dd" font-size="12">⑥ 策略疯起来(或者静下来)我能不能马上停,且机身和弹药都还在手里?</text>"""
    return concept_figure(body, "0 0 900 450",
        "启动前六问图:研究三问、回测两问、实盘一问",
        "这张纸不是给你背下来的,是给你每次动手前要问到位的——六问里有任意一问答不出来,就先不要下手。")


PATCH_R6 = {
    38: [("招募说明书先翻五处", _fig_r38_eyefund)],
    39: [("先定资金上限", _fig_r39_small)],
    40: [("能管住自己的资金边界", _fig_r40_two_lists)],
    41: [("高胜率策略一定好吗", _fig_r41_overfit)],
    42: [("问题很小", _fig_r42_lifecycle)],
    43: [("研究前先问问题是否足够小", _fig_r43_checkpaper)],
}



def _fig_r32_drawdown():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">回撤不对称:跌 50% 要涨 100% 才能回本</text>
            <line x1="80" y1="300" x2="820" y2="300" stroke="#8499bd" stroke-width="2"/>
            <line x1="80" y1="60" x2="80" y2="300" stroke="#8499bd" stroke-width="2"/>
            <text x="92" y="66" fill="#bcc9dd" font-size="12">净值</text>
            <path d="M 85 200 Q 200 170 330 190 Q 420 200 450 205 Q 500 285 620 275 Q 740 260 815 220" fill="none" stroke="#a8c6ff" stroke-width="3"/>
            <circle cx="85" cy="200" r="5" fill="#8fb37a"/>
            <text x="85" y="188" fill="#8fb37a" font-size="12" font-weight="800">起点 1.0</text>
            <circle cx="450" cy="205" r="5" fill="#f0c96a"/>
            <text x="450" y="193" fill="#f0c96a" font-size="12" font-weight="800">高点 1.2</text>
            <circle cx="620" cy="275" r="5" fill="#ee8877"/>
            <text x="620" y="295" fill="#ee8877" font-size="12" font-weight="800">谷底 0.6(-50%)</text>
            <line x1="450" y1="205" x2="810" y2="205" stroke="#8fb37a" stroke-width="2" stroke-dasharray="8 6"/>
            <text x="810" y="200" fill="#8fb37a" font-size="12">得回到 1.2 才算回本</text>
            <text x="450" y="338" text-anchor="middle" fill="#bcc9dd" font-size="12.5">数学只有一句:1.2 → 0.6 是 -50%,0.6 → 1.2 是 +100%;从深坑里爬出的代价比你想象贵上一倍——这就是止损要卡的死死的原因</text>"""
    return concept_figure(body, "0 0 900 365",
        "回撤不对称复原图:净值从 1.2 跌到 0.6 又是怎么必须再涨 100% 才能回本",
        "跌 50% 不是利润的一半失去,是必须再赚 100% 才回得来。同哲学只能弥补的是止损和仓位——越往下亏,能回到起点的天数越长,这就是何时控制的设置在绝对值上。")


def _fig_r33_tenlayer():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">量化十层金字塔:底下坏一点,上面就动一片</text>
            <path d="M 60 400 L 840 400 L 790 340 L 110 340 Z" fill="rgba(122,167,240,0.12)" stroke="rgba(122,167,240,0.4)"/>
            <text x="450" y="378" text-anchor="middle" fill="#bcc9dd" font-size="13">① 真实财富与生产力 · ② 信用与时间 · ③ 权利与资产</text>
            <path d="M 110 340 L 790 340 L 740 280 L 160 280 Z" fill="rgba(122,167,240,0.18)" stroke="rgba(122,167,240,0.45)"/>
            <text x="450" y="318" text-anchor="middle" fill="#bcc9dd" font-size="13">④ 市场制度 · ⑤ 数据可见性</text>
            <path d="M 160 280 L 740 280 L 690 220 L 210 220 Z" fill="rgba(122,167,240,0.25)" stroke="rgba(122,167,240,0.5)"/>
            <text x="450" y="258" text-anchor="middle" fill="#bcc9dd" font-size="13">⑥ 因子与模型 · ⑦ 回测与验证</text>
            <path d="M 210 220 L 690 220 L 640 160 L 260 160 Z" fill="rgba(240,201,106,0.2)" stroke="rgba(240,201,106,0.5)"/>
            <text x="450" y="198" text-anchor="middle" fill="#bcc9dd" font-size="13">⑧ 组合与风险 · ⑨ 交易与实盘</text>
            <path d="M 260 160 L 640 160 L 590 100 L 310 100 Z" fill="rgba(238,136,119,0.2)" stroke="rgba(238,136,119,0.5)"/>
            <text x="450" y="138" text-anchor="middle" fill="#bcc9dd" font-size="13">⑩ 人和纪律</text>
            <path d="M 310 100 L 590 100 L 450 40 Z" fill="rgba(240,201,106,0.3)" stroke="#f0c96a"/>
            <text x="450" y="76" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">你自己的决策</text>
            <text x="450" y="438" text-anchor="middle" fill="#bcc9dd" font-size="12.5">这不是组织架构图,是知识依赖图——底座塔基稍微不稳,上面那些数据、意外与模型都会跟着晃</text>"""
    return concept_figure(body, "0 0 900 465",
        "十层金字塔图:真实财富、信用、制度、数据、因子、组合、执行,塔顶是人的纪律",
        "这本书的全部内容可以画成一座十层金字塔。底下几层日暮存心,上面三层人人都盯屏幕。当你看到模型失效时,要检查的不是模型,是底下九层之一。“技术要求”的它本身没问题。”")


def _fig_r34_portfolio():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">量化职业三线的技能栈与性格匹配</text>
            <rect x="70" y="80" width="240" height="250" rx="12" fill="rgba(122,167,240,0.2)" stroke="#7aa7f0"/>
            <text x="190" y="108" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">① 开发(QD)</text>
            <text x="190" y="136" text-anchor="middle" fill="#bcc9dd" font-size="12">交易系统、回测框架</text>
            <text x="190" y="158" text-anchor="middle" fill="#bcc9dd" font-size="12">负责写工具,不写信号</text>
            <text x="190" y="186" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">指标的低压/可复现性</text>
            <text x="190" y="214" text-anchor="middle" fill="#bcc9dd" font-size="12">压力与变动相对低</text>
            <text x="190" y="242" text-anchor="middle" fill="#bcc9dd" font-size="12">对代码热爱的人</text>
            <text x="190" y="268" text-anchor="middle" fill="#8499bd" font-size="12">年限上率先久远</text>
            <text x="190" y="296" text-anchor="middle" fill="#8fb37a" font-size="12.5">上下限最优法工程师</text>
            <rect x="330" y="80" width="240" height="250" rx="12" fill="rgba(240,201,106,0.15)" stroke="#f0c96a"/>
            <text x="450" y="108" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">② 研究(QR)</text>
            <text x="450" y="136" text-anchor="middle" fill="#bcc9dd" font-size="12">因子、数据、模型</text>
            <text x="450" y="158" text-anchor="middle" fill="#bcc9dd" font-size="12">负责写信号与策略</text>
            <text x="450" y="186" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">IC 与统计严谨性</text>
            <text x="450" y="214" text-anchor="middle" fill="#bcc9dd" font-size="12">对 PNL 功绩直负责</text>
            <text x="450" y="242" text-anchor="middle" fill="#bcc9dd" font-size="12">对学术推理更敏感</text>
            <text x="450" y="268" text-anchor="middle" fill="#8499bd" font-size="12">入门难度最高</text>
            <text x="450" y="296" text-anchor="middle" fill="#8fb37a" font-size="12.5">上下限最高</text>
            <rect x="600" y="80" width="240" height="250" rx="12" fill="rgba(238,136,119,0.15)" stroke="#ee8877"/>
            <text x="720" y="108" text-anchor="middle" fill="#ffb4b4" font-size="15" font-weight="800">③ 交易(QT)</text>
            <text x="720" y="136" text-anchor="middle" fill="#bcc9dd" font-size="12">盯盘、仓位、风险恶化</text>
            <text x="720" y="158" text-anchor="middle" fill="#bcc9dd" font-size="12">负责运行与决断</text>
            <text x="720" y="186" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">成交叉和天天 PNL</text>
            <text x="720" y="214" text-anchor="middle" fill="#bcc9dd" font-size="12">压力下坚持与服纪律</text>
            <text x="720" y="242" text-anchor="middle" fill="#bcc9dd" font-size="12">对市场直觉和执行力</text>
            <text x="720" y="268" text-anchor="middle" fill="#8499bd" font-size="12">最像运动成绩</text>
            <text x="720" y="296" text-anchor="middle" fill="#8fb37a" font-size="12.5">成长中魔术点最多</text>
            <text x="450" y="358" text-anchor="middle" fill="#bcc9dd" font-size="12.5">三个角色需要的不是同一颗脑袋不是级别阶梯,而是性格岔置;不是先升 QR 再升 QT,是先看你愿意文思、写码、还是执手实盘</text>"""
    return concept_figure(body, "0 0 900 390",
        "量化职业三路线对比:开发缺代码,研究缺信号,交易缺决断",
        "三条路线哪个上下限高,全看你口里的 PnL 挂的是谁:开发挂系统年资、研究挂因子技能、交易挂执行心态。天个岗位必备的技能栈完全不同。")


def _fig_r35_terms():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">术语地图:按你要做的事拉出来,不是按字母背</text>
            <text x="80" y="70" fill="#8499bd" font-size="12" font-weight="800">不竖书里的“只要被背什么”顺序;而是拉进工作时想用就能捡哪种场景</text>
            <text x="80" y="110" fill="#f0c96a" font-size="13" font-weight="800">入门看病(市场结构)</text>
            <text x="200" y="110" fill="#bcc9dd" font-size="12">货币、信用、利率、通胀、股债基等基本利差</text>
            <text x="80" y="160" fill="#f0c96a" font-size="13" font-weight="800">买之前(行情基础)</text>
            <text x="200" y="160" fill="#bcc9dd" font-size="12">股票、债券、基金、ETF、期货、期权的基本是怎么样的</text>
            <text x="80" y="210" fill="#f0c96a" font-size="13" font-weight="800">做模型之前(机器思维)</text>
            <text x="200" y="210" fill="#bcc9dd" font-size="12">Alpha、Beta、因子、IC、RankIC、回测</text>
            <text x="80" y="260" fill="#f0c96a" font-size="13" font-weight="800">执行时(成本与误差)</text>
            <text x="200" y="260" fill="#bcc9dd" font-size="12">滑点、容量、跟踪误差、归因、风险、风控</text>
            <text x="80" y="310" fill="#f0c96a" font-size="13" font-weight="800">谁错了说什么(复盘)</text>
            <text x="200" y="310" fill="#bcc9dd" font-size="12">真实成交价差、未来函数、幸存者偏差、过拟合、样本外</text>
            <text x="450" y="350" text-anchor="middle" fill="#bcc9dd" font-size="12.5">这章不是一个表,而是按「我现在多做什么事」准出问题;字母表是字典顺序,场景序是查词顺序</text>"""
    return concept_figure(body, "0 0 900 375",
        "术语按交易场景分组:入门看病、买之前、做模型之前、执行时、复盘问题,各用一个对应主题",
        "别按字母背术语——按$$面处境去查:在选股前,在看策略时,在准备做执行时,在复盘的时候。口诀多了不佑,但每一个都要在你能使用它们的时候,保伪证明你能召回。")


def _fig_r36_account():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">开户首页的三个框框:不管你用哪家券商,这三个读法稳定</text>
            <rect x="70" y="80" width="240" height="200" rx="12" fill="rgba(122,167,240,0.2)" stroke="#7aa7f0"/>
            <text x="190" y="108" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">① 总资产 VS 可用 VS 可取</text>
            <text x="190" y="144" text-anchor="middle" fill="#bcc9dd" font-size="12">总资产 = 持仓市值 + 现金</text>
            <text x="190" y="166" text-anchor="middle" fill="#bcc9dd" font-size="12">可用 = 今天能下单动用的</text>
            <text x="190" y="188" text-anchor="middle" fill="#bcc9dd" font-size="12">可取 = 能从证券转回银行卡的</text>
            <text x="190" y="216" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">三个别混为一谈</text>
            <text x="190" y="244" text-anchor="middle" fill="#8499bd" font-size="12">差额是还在途的钱:刚才挂单、在途道来未走峻</text>
            <rect x="340" y="80" width="240" height="200" rx="12" fill="rgba(240,201,106,0.15)" stroke="#f0c96a"/>
            <text x="460" y="108" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">② 成本价 VS 当前价</text>
            <text x="460" y="144" text-anchor="middle" fill="#bcc9dd" font-size="12">成本价是你当时买的均价</text>
            <text x="460" y="166" text-anchor="middle" fill="#bcc9dd" font-size="12">当前价是今天最新的全市场成交</text>
            <text x="460" y="188" text-anchor="middle" fill="#bcc9dd" font-size="12">两者之差是浮盈浮亏</text>
            <text x="460" y="216" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">把成本价看成心理也会错</text>
            <text x="460" y="244" text-anchor="middle" fill="#8499bd" font-size="12">所谓“套着”是错觉而已——持仓未来下一步到哪里,不能以成交价格为判断标准</text>
            <rect x="610" y="80" width="240" height="200" rx="12" fill="rgba(238,136,119,0.15)" stroke="#ee8877"/>
            <text x="730" y="108" text-anchor="middle" fill="#ffb4b4" font-size="15" font-weight="800">③ 今日收益 VS 累计收益</text>
            <text x="730" y="144" text-anchor="middle" fill="#bcc9dd" font-size="12">今日收益只今天的变动</text>
            <text x="730" y="166" text-anchor="middle" fill="#bcc9dd" font-size="12">累计收益是总盈亏的总额</text>
            <text x="730" y="188" text-anchor="middle" fill="#bcc9dd" font-size="12">两个数字不要混看就好</text>
            <text x="730" y="216" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">同样当日涨零点零、累计收益可以是高点落半里</text>
            <text x="730" y="244" text-anchor="middle" fill="#8499bd" font-size="12">分两个表看才不会把今天惘因为当天暴跌说明起点壤里</text>
            <text x="450" y="322" text-anchor="middle" fill="#bcc9dd" font-size="12.5">除此三框之外:成交额、换手率、震幅,都是辅助理解今天市场活跃程度的旁证——你也可以拒絕它们扰晄交易成本与费用</text>"""
    return concept_figure(body, "0 0 900 360",
        "账户创世纪首页阅读规范:总资产/可用/可取、成本价/当前价、今日收益/累计收益",
        "开户首页六态:三对概念不要混,熟悉希望的读法对每一家券商都是稳定如一的。否则你会把浮亏当成已经亏、把今日涨幅当成总收益。")


def _fig_r37_datasanity():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">回测第一天的四个数据坑:你踩过的四大不会被版</text>
            <rect x="70" y="80" width="360" height="130" rx="10" fill="rgba(238,136,119,0.15)" stroke="#ee8877"/>
            <text x="250" y="108" text-anchor="middle" fill="#ffb4b4" font-size="14" font-weight="800">坑1:幸存者偏差</text>
            <text x="250" y="134" text-anchor="middle" fill="#bcc9dd" font-size="12">取今日 SP500 成分股去测 2015-2019 年数据</text>
            <text x="250" y="156" text-anchor="middle" fill="#bcc9dd" font-size="12">等于把当年退市股票自动剔除</text>
            <text x="250" y="186" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">存活偏向导致回测很好看</text>
            <rect x="470" y="80" width="360" height="130" rx="10" fill="rgba(238,136,119,0.15)" stroke="#ee8877"/>
            <text x="650" y="108" text-anchor="middle" fill="#ffb4b4" font-size="14" font-weight="800">坑2:未来信息泄漏</text>
            <text x="650" y="134" text-anchor="middle" fill="#bcc9dd" font-size="12">构造因子引用了今天收盘后才发布的报表</text>
            <text x="650" y="156" text-anchor="middle" fill="#bcc9dd" font-size="12">也是变量时点(PIT)不同步</text>
            <text x="650" y="186" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">处理时间线时不能苟同</text>
            <rect x="70" y="220" width="360" height="130" rx="10" fill="rgba(240,201,106,0.15)" stroke="#f0c96a"/>
            <text x="250" y="248" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">坑3:交易成本估低</text>
            <text x="250" y="274" text-anchor="middle" fill="#bcc9dd" font-size="12">1 万元以下股票要加涨 3 万一计</text>
            <text x="250" y="296" text-anchor="middle" fill="#bcc9dd" font-size="12">大笔多股换成小规模仓库还要考虑冲击成本</text>
            <text x="250" y="326" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">小资金大单交换流动性会被打</text>
            <rect x="470" y="220" width="360" height="130" rx="10" fill="rgba(240,201,106,0.15)" stroke="#f0c96a"/>
            <text x="650" y="248" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">坑4:过度拟合</text>
            <text x="650" y="274" text-anchor="middle" fill="#bcc9dd" font-size="12">反复调参数直到 2018-2022 年表现最好</text>
            <text x="650" y="296" text-anchor="middle" fill="#bcc9dd" font-size="12">等于是把这几年背诵下来,不是预测出行情</text>
            <text x="650" y="326" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">样本外测试不能只算业绩指标,也要看容量</text>
            <text x="450" y="372" text-anchor="middle" fill="#bcc9dd" font-size="12.5">这四个坑每一个具体是怎么发生的,都放在本书关于回溯实例的第一章节里起来了——今天的遇见,是明天多写一行断言的依据</text>"""
    return concept_figure(body, "0 0 900 400",
        "回测四坑:幸存者偏差、未来泄漏、低事成本、过度拟合,都梁在第一天写回测",
        "第一天写回测最容易缺的不是代码工整,是这四个认知坑——今天在上面避免,明天就是一个断言、一个校验、一个拉平板模式的写真。")


PATCH_R5 = {
    32: [("回撤里最容易做错决定", _fig_r32_drawdown)],
    33: [("人和纪律", _fig_r33_tenlayer)],
    34: [("先分清岗位", _fig_r34_portfolio)],
    35: [("通胀", _fig_r35_terms)],
    36: [("总资产不是可花的钱", _fig_r36_account)],
    37: [("数据没有按时到", _fig_r37_datasanity)],
}



def _fig_r25_neutral():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">Beta 对冲:把大盘的潮水拉平成溪流</text>
            <line x1="80" y1="300" x2="820" y2="300" stroke="#8499bd" stroke-width="2"/>
            <line x1="80" y1="60" x2="80" y2="300" stroke="#8499bd" stroke-width="2"/>
            <text x="92" y="66" fill="#bcc9dd" font-size="12">净值</text>
            <text x="820" y="318" fill="#bcc9dd" font-size="12">时间</text>
            <path d="M 85 200 Q 200 260 330 240 Q 450 210 550 250 Q 650 285 810 230" fill="none" stroke="#ee8877" stroke-width="3"/>
            <text x="220" y="260" fill="#ee8877" font-size="12" font-weight="800">裸仓做多(整轮波谷浪拍下来)</text>
            <line x1="85" y1="170" x2="810" y2="170" stroke="#8fb37a" stroke-width="3.5"/>
            <text x="220" y="162" fill="#8fb37a" font-size="12" font-weight="800">对冲后 + 股指期货做空(贴近水平)</text>
            <rect x="100" y="360" width="740" height="85" rx="10" fill="rgba(18,29,49,0.7)" stroke="rgba(240,201,106,0.45)"/>
            <text x="124" y="386" fill="#f0c96a" font-size="13" font-weight="800">对冲的账</text>
            <text x="124" y="414" fill="#bcc9dd" font-size="12">多头组合的收益 = α(选股的磨炼) + β(大盘的浪)——加上反向股指期货,β 被对冲,剩下的只有 α</text>
            <text x="124" y="436" fill="#bcc9dd" font-size="12">代价是空头端的基差和资金成本——所以中性产品的收益,通常比纯多头低两三个百分点,但回撤也小一大截</text>"""
    return concept_figure(body, "0 0 900 460",
        "Beta 对冲效果图:大盘浪线起伏明显,对冲后近似水平,屏蔽 Beta 只留 Alpha",
        "中性策略不是神秘术,是用股指期货把大盘水位抽走,让每次涨跌的原因只剩“你选的股能不能跑赢平均”;代价是要付对冲成本,长期通常拿回 Alpha 减 2-3% 对冲费。")


def _fig_r26_pairs():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">配对交易:两只同行的股,只赌价差收敛</text>
            <line x1="80" y1="300" x2="820" y2="300" stroke="#8499bd" stroke-width="2"/>
            <line x1="80" y1="60" x2="80" y2="300" stroke="#8499bd" stroke-width="2"/>
            <text x="92" y="66" fill="#bcc9dd" font-size="12">价格</text>
            <text x="820" y="318" fill="#bcc9dd" font-size="12">时间</text>
            <path d="M 85 100 Q 200 120 320 110 Q 450 100 590 130 Q 700 150 815 120" fill="none" stroke="#a8c6ff" stroke-width="3"/>
            <text x="830" y="125" fill="#a8c6ff" font-size="12">股 A(银行)</text>
            <path d="M 85 140 Q 210 170 330 150 Q 460 140 600 170 Q 710 190 815 150" fill="none" stroke="#ee8877" stroke-width="3"/>
            <text x="830" y="155" fill="#ee8877" font-size="12">股 B(银行)</text>
            <ellipse cx="240" cy="145" rx="50" ry="40" fill="none" stroke="#f0c96a" stroke-width="3" stroke-dasharray="6 4"/>
            <text x="240" y="212" text-anchor="middle" fill="#f0c96a" font-size="12" font-weight="800">价差异常拉开:做空 A,买入 B</text>
            <ellipse cx="560" cy="150" rx="50" ry="40" fill="none" stroke="#8fb37a" stroke-width="3" stroke-dasharray="6 4"/>
            <text x="560" y="217" text-anchor="middle" fill="#8fb37a" font-size="12" font-weight="800">价差收敛至正常:平仓</text>
            <text x="450" y="338" text-anchor="middle" fill="#bcc9dd" font-size="12.5">同行业两只股价长期高度正相关。只有当价差拉到历史均值±2σ之外才出手;回到区间内就收工——赌的是相关性回归,不是股票涨跌</text>"""
    return concept_figure(body, "0 0 900 365",
        "配对交易图:跟踪同行两股的价差,拉到异常区间就做空高开买低收,恢复正常就收手",
        "统计学套利的原型:同行业的股票走势通常同步;当价差落到历史正常区间外,就有价值修复的机会。你赚的是价差回归的那一块,不是牛熊方向。")


def _fig_r27_fees():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">基金费用的两层:看得见的收费和看不见的成本</text>
            <rect x="70" y="80" width="360" height="130" rx="10" fill="rgba(122,167,240,0.2)" stroke="#7aa7f0"/>
            <text x="250" y="108" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">看得见的四笔(写在合同里)</text>
            <text x="250" y="136" text-anchor="middle" fill="#bcc9dd" font-size="12">认购费/申购费 0.15%-1.5%</text>
            <text x="250" y="158" text-anchor="middle" fill="#bcc9dd" font-size="12">赎回费 0%-1.5%(持有时间越长越低)</text>
            <text x="250" y="180" text-anchor="middle" fill="#bcc9dd" font-size="12">管理费 0.2%-1.5%/年</text>
            <text x="250" y="202" text-anchor="middle" fill="#bcc9dd" font-size="12">托管费 0.05%-0.25%/年</text>
            <rect x="470" y="80" width="360" height="130" rx="10" fill="rgba(238,136,119,0.18)" stroke="#ee8877"/>
            <text x="650" y="108" text-anchor="middle" fill="#ffb4b4" font-size="15" font-weight="800">看不见的两块(从你的收益里悄悄拿走)</text>
            <text x="650" y="136" text-anchor="middle" fill="#bcc9dd" font-size="12">交易佣金 + 手续费—自己开仓时付交易对手</text>
            <text x="650" y="158" text-anchor="middle" fill="#bcc9dd" font-size="12">冲击成本/滑点—大单买小票会移动价格</text>
            <text x="650" y="180" text-anchor="middle" fill="#bcc9dd" font-size="12">换手率越高,这两块越重</text>
            <text x="650" y="202" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">总量能占到管理费的 30%-100%</text>
            <rect x="80" y="240" width="760" height="100" rx="10" fill="rgba(18,29,49,0.7)" stroke="rgba(240,201,106,0.45)"/>
            <text x="104" y="268" fill="#f0c96a" font-size="13" font-weight="800">长期持有的累计影响</text>
            <text x="104" y="294" fill="#bcc9dd" font-size="12">假设基金年化 8%:总费用率是 1%,十年后是 2.16 倍;费用率 3%,十年后只有 1.85 倍——一年差 2%,十年差掉 15% 的累计财富</text>
            <text x="104" y="318" fill="#bcc9dd" font-size="12">这就是“一年看收益,十年看费用”这句话为什么在每次长期选择里都重新一堆人取</text>"""
    return concept_figure(body, "0 0 900 360",
        "基金费用的两层结构:合同可见费四项,隐性摩擦两块,长期费用吞噬累计收益牢不可破",
        "决定你十年后收益的,不只是年化这几个点,还有每年被悄悄加收的总费用率。市场宣传时一定会把总费用率裁下来,所以在签署前请一定会主动把它的每一层加总起来。")


def _fig_r29_units():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">指数增强的最小回测:八步流水</text>
            <g>
              <rect x="60" y="80" width="170" height="70" rx="8" fill="rgba(122,167,240,0.22)" stroke="#7aa7f0"/>
              <text x="145" y="106" text-anchor="middle" fill="#a8c6ff" font-size="13" font-weight="800">① 数据入库</text>
              <text x="145" y="128" text-anchor="middle" fill="#bcc9dd" font-size="11.5">股票池、历史 K 线、成分股权重表;</text>
              <text x="145" y="146" text-anchor="middle" fill="#bcc9dd" font-size="11.5">特别强调:必须是点时可见版本</text>
              <rect x="250" y="80" width="170" height="70" rx="8" fill="rgba(122,167,240,0.22)" stroke="#7aa7f0"/>
              <text x="335" y="106" text-anchor="middle" fill="#a8c6ff" font-size="13" font-weight="800">② 写因子</text>
              <text x="335" y="128" text-anchor="middle" fill="#bcc9dd" font-size="11.5">选一两个简单因子比如 20 日动量</text>
              <text x="335" y="146" text-anchor="middle" fill="#bcc9dd" font-size="11.5">先写一个,再多写</text>
              <rect x="440" y="80" width="170" height="70" rx="8" fill="rgba(240,201,106,0.2)" stroke="#f0c96a"/>
              <text x="525" y="106" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">③ 打分</text>
              <text x="525" y="128" text-anchor="middle" fill="#bcc9dd" font-size="11.5">把因子值标准化后加起来,</text>
              <text x="525" y="146" text-anchor="middle" fill="#bcc9dd" font-size="11.5">给每只股票算总分</text>
              <rect x="630" y="80" width="170" height="70" rx="8" fill="rgba(240,201,106,0.2)" stroke="#f0c96a"/>
              <text x="715" y="106" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">④ 调仓名单</text>
              <text x="715" y="128" text-anchor="middle" fill="#bcc9dd" font-size="11.5">选出高分股前100名</text>
              <text x="715" y="146" text-anchor="middle" fill="#bcc9dd" font-size="11.5">按权重排比例</text>
              <!-- 第二行 -->
              <rect x="60" y="200" width="170" height="70" rx="8" fill="rgba(238,136,119,0.15)" stroke="#ee8877"/>
              <text x="145" y="226" text-anchor="middle" fill="#ffb4b4" font-size="13" font-weight="800">⑧ 复盘结论</text>
              <text x="145" y="248" text-anchor="middle" fill="#bcc9dd" font-size="11.5">把结果告诉下一步要修正的部分,</text>
              <text x="145" y="266" text-anchor="middle" fill="#bcc9dd" font-size="11.5">形成报告</text>
              <rect x="250" y="200" width="170" height="70" rx="8" fill="rgba(238,136,119,0.15)" stroke="#ee8877"/>
              <text x="335" y="226" text-anchor="middle" fill="#ffb4b4" font-size="13" font-weight="800">⑦ 出报告</text>
              <text x="335" y="248" text-anchor="middle" fill="#bcc9dd" font-size="11.5">净值、年化、夏普、最大回撤</text>
              <text x="335" y="266" text-anchor="middle" fill="#bcc9dd" font-size="11.5">按指标出</text>
              <rect x="440" y="200" width="170" height="70" rx="8" fill="rgba(143,179,122,0.15)" stroke="#8fb37a"/>
              <text x="525" y="226" text-anchor="middle" fill="#b5d3a0" font-size="13" font-weight="800">⑥ 扣成本</text>
              <text x="525" y="248" text-anchor="middle" fill="#bcc9dd" font-size="11.5">双边佣金 + 滑点 + 印花,</text>
              <text x="525" y="266" text-anchor="middle" fill="#bcc9dd" font-size="11.5">合在一起算总成本</text>
              <rect x="630" y="200" width="170" height="70" rx="8" fill="rgba(143,179,122,0.15)" stroke="#8fb37a"/>
              <text x="715" y="226" text-anchor="middle" fill="#b5d3a0" font-size="13" font-weight="800">⑤ 模拟调仓</text>
              <text x="715" y="248" text-anchor="middle" fill="#bcc9dd" font-size="11.5">日频推进,不过未来的数据,</text>
              <text x="715" y="266" text-anchor="middle" fill="#bcc9dd" font-size="11.5">形成串行序列</text>
            </g>
            <!-- 箭头 -->
            <line x1="232" y1="115" x2="248" y2="115" stroke="#8499bd" stroke-width="2"/>
            <line x1="422" y1="115" x2="438" y2="115" stroke="#8499bd" stroke-width="2"/>
            <line x1="612" y1="115" x2="628" y2="115" stroke="#8499bd" stroke-width="2"/>
            <line x1="715" y1="152" x2="715" y2="198" stroke="#8499bd" stroke-width="2"/>
            <line x1="715" y1="235" x2="612" y2="235" stroke="#8499bd" stroke-width="2"/>
            <line x1="422" y1="235" x2="438" y2="235" stroke="#8499bd" stroke-width="2" stroke-dasharray="3 3" opacity="0"/>
            <line x1="438" y1="235" x2="422" y2="235" stroke="#8499bd" stroke-width="2"/>
            <line x1="248" y1="235" x2="232" y2="235" stroke="#8499bd" stroke-width="2"/>
            <text x="450" y="310" text-anchor="middle" fill="#bcc9dd" font-size="12.5">数据→因子→打分→名单→模拟→成本→报告→复盘——少任何一步,结论都能被某个隐藏的坑拆掉</text>"""
    return concept_figure(body, "0 0 900 340",
        "指数增强最小回测流水线:数据入库→写因子→打分→生成名单→模拟调仓→扣成本→出报告→复盘结论",
        "最小回测不是一段代码精灵,是八个环节的传导链。数据到结论全对一条龙才有意义,中间断掉任何一环都可能变成“模型很好但那只是没上纲上线”。")


PATCH_RMID = {
    25: [("Beta 对冲的直觉", _fig_r25_neutral)],
    26: [("配对交易", _fig_r26_pairs)],
    27: [("费用结构会吃掉收益", _fig_r27_fees)],
    29: [("先把项目目标和边界钉死", _fig_r29_units)],
}



def _fig_r16_index():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">市值加权:大公司涨 1%,比小公司涨 10% 更厉害</text>
            <!-- 指数的三个代表权 -->
            <rect x="90" y="90" width="200" height="200" rx="14" fill="rgba(122,167,240,0.3)" stroke="#7aa7f0"/>
            <text x="190" y="118" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">成分 1</text>
            <text x="190" y="146" text-anchor="middle" fill="#bcc9dd" font-size="12">市值 1000 亿</text>
            <text x="190" y="168" text-anchor="middle" fill="#bcc9dd" font-size="12">权重 50%</text>
            <rect x="330" y="110" width="120" height="160" rx="12" fill="rgba(240,201,106,0.2)" stroke="#f0c96a"/>
            <text x="390" y="138" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">成分 2</text>
            <text x="390" y="166" text-anchor="middle" fill="#bcc9dd" font-size="12">市值 600 亿</text>
            <text x="390" y="188" text-anchor="middle" fill="#bcc9dd" font-size="12">权重 30%</text>
            <rect x="490" y="140" width="90" height="130" rx="10" fill="rgba(238,136,119,0.2)" stroke="#ee8877"/>
            <text x="535" y="168" text-anchor="middle" fill="#ffb4b4" font-size="15" font-weight="800">成分 3</text>
            <text x="535" y="196" text-anchor="middle" fill="#bcc9dd" font-size="12">市值 400 亿</text>
            <text x="535" y="218" text-anchor="middle" fill="#bcc9dd" font-size="12">权重 20%</text>
            <!-- 箭头与数字 -->
            <text x="670" y="130" fill="#bcc9dd" font-size="13">成分1 涨 1%</text>
            <text x="670" y="156" fill="#f0c96a" font-size="15" font-weight="800">→ 指数涨 0.50 点</text>
            <text x="670" y="188" fill="#bcc9dd" font-size="13">成分2 涨 1%</text>
            <text x="670" y="210" fill="#f0c96a" font-size="15" font-weight="800">→ 指数涨 0.30 点</text>
            <text x="670" y="244" fill="#bcc9dd" font-size="13">成分3 涨 10%</text>
            <text x="670" y="266" fill="#f0c96a" font-size="15" font-weight="800">→ 指数只涨 0.20 点</text>
            <rect x="60" y="310" width="780" height="80" rx="10" fill="rgba(18,29,49,0.7)" stroke="rgba(240,201,106,0.45)"/>
            <text x="84" y="334" fill="#f0c96a" font-size="13" font-weight="800">结论</text>
            <text x="84" y="360" fill="#bcc9dd" font-size="12">宽基指数(上证50/沪深300)头部效应极强;不是“市场”听投票多少,是大公司方向决定主方向。要读“市场宽度”得看涨跌家数,不能只看指数曲线</text>"""
    return concept_figure(body, "0 0 900 400",
        "市值加权示意图:三巨头权重 50/30/20,大公司 1% 变动比小公司 10% 变动对指数影响更大",
        "市值加权的含义:尽管指数看起来是数理平均,实际是“大公司说话更大声”。当你听说“指数涨了”,决定答案的大部分是前二十大成分股,不是大多数公司。")


def _fig_r18_overconfidence():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">过度自信的四个典型陷阱:你以为领先,其实平均</text>
            <rect x="70" y="80" width="350" height="120" rx="10" fill="rgba(122,167,240,0.2)" stroke="#7aa7f0"/>
            <text x="245" y="108" text-anchor="middle" fill="#a8c6ff" font-size="14" font-weight="800">陷阱1:频繁换手</text>
            <text x="245" y="134" text-anchor="middle" fill="#bcc9dd" font-size="12">散户研究显示:交易频率与净收益反相关,</text>
            <text x="245" y="156" text-anchor="middle" fill="#bcc9dd" font-size="12">涨手最快的人群年化最低</text>
            <text x="245" y="186" text-anchor="middle" fill="#ee8877" font-size="13" font-weight="800">自信的代价常常是磨损</text>
            <rect x="480" y="80" width="350" height="120" rx="10" fill="rgba(240,201,106,0.15)" stroke="#f0c96a"/>
            <text x="655" y="108" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">陷阱2:选股传奇</text>
            <text x="655" y="134" text-anchor="middle" fill="#bcc9dd" font-size="12">“我去年赚到了 XX” 一旦指数上升,</text>
            <text x="655" y="156" text-anchor="middle" fill="#bcc9dd" font-size="12">归因到能力还在,归因到市场不存在</text>
            <text x="655" y="186" text-anchor="middle" fill="#ee8877" font-size="13" font-weight="800">这是跑偏的典型信号</text>
            <rect x="70" y="230" width="350" height="120" rx="10" fill="rgba(238,136,119,0.15)" stroke="#ee8877"/>
            <text x="245" y="258" text-anchor="middle" fill="#ffb4b4" font-size="14" font-weight="800">陷阱3:绝佳择时</text>
            <text x="245" y="284" text-anchor="middle" fill="#bcc9dd" font-size="12">同一股票同一天同価决断,同一人也不一定能连续做对</text>
            <text x="245" y="306" text-anchor="middle" fill="#bcc9dd" font-size="12">“稍快或稍慢也它都不灵”不是真技能</text>
            <text x="245" y="336" text-anchor="middle" fill="#ee8877" font-size="13" font-weight="800">自信里用户凯转机在开仓位</text>
            <rect x="480" y="230" width="350" height="120" rx="10" fill="rgba(143,179,122,0.2)" stroke="#8fb37a"/>
            <text x="655" y="258" text-anchor="middle" fill="#b5d3a0" font-size="14" font-weight="800">陷阱4:大户牛托</text>
            <text x="655" y="284" text-anchor="middle" fill="#bcc9dd" font-size="12">股市赚钱时说“我看对了”,春耕东渐;</text>
            <text x="655" y="306" text-anchor="middle" fill="#bcc9dd" font-size="12">亏钱时“今天消息”或“今天不灵”</text>
            <text x="655" y="336" text-anchor="middle" fill="#ee8877" font-size="13" font-weight="800">这叫自己说谎,归因偏差</text>
            <text x="450" y="382" text-anchor="middle" fill="#f0c96a" font-size="12.5">把这四条做成检查清单交易前核一遍,发现其中一条就要停手</text>"""
    return concept_figure(body, "0 0 900 410",
        "过度自信四陷阱图:过度换手、选股全能、绝佳择时、事帮他人的归因偏差",
        "过度自信不是雄心,是系统性装修——越自信的部分越是成本。最好的手艺人的共同点是把自己的交易频率压得低,把仓位上限定压。")


def _fig_r19_buckets():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">先分桶,再钱讨——三个桶都被同一份收入打败</text>
            <path d="M 90 100 L 100 280 Q 190 300 280 280 L 290 100 Z" fill="rgba(122,167,240,0.22)" stroke="#7aa7f0"/>
            <text x="190" y="130" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">桶① 生活费与应急金</text>
            <text x="190" y="158" text-anchor="middle" fill="#bcc9dd" font-size="12">6 个月刚性支出</text>
            <text x="190" y="180" text-anchor="middle" fill="#bcc9dd" font-size="12">货基/活期 确保随时可用</text>
            <text x="190" y="208" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">优先级最高</text>
            <text x="190" y="234" text-anchor="middle" fill="#8499bd" font-size="12">破裂:有急用钱会逼你斩仓</text>
            <path d="M 350 100 L 360 280 Q 455 300 550 280 L 560 100 Z" fill="rgba(240,201,106,0.2)" stroke="#f0c96a"/>
            <text x="455" y="130" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">桶② 风险对冲(保险)</text>
            <text x="455" y="158" text-anchor="middle" fill="#bcc9dd" font-size="12">家庭支柱定寿 + 全家重疾 + 百万医疗</text>
            <text x="455" y="180" text-anchor="middle" fill="#bcc9dd" font-size="12">一年保费 ≈ 年收入 3-8%</text>
            <text x="455" y="208" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">“怕什么”的钱罐</text>
            <text x="455" y="234" text-anchor="middle" fill="#8499bd" font-size="12">破裂:风险要步宽,躲闪不了责任</text>
            <path d="M 620 100 L 630 280 Q 700 300 770 280 L 780 100 Z" fill="rgba(238,136,119,0.15)" stroke="#ee8877"/>
            <text x="700" y="130" text-anchor="middle" fill="#ffb4b4" font-size="15" font-weight="800">桶③ 长期增值</text>
            <text x="700" y="158" text-anchor="middle" fill="#bcc9dd" font-size="12">宽基指数、股票、多类资产定投</text>
            <text x="700" y="180" text-anchor="middle" fill="#bcc9dd" font-size="12">目标是跑赢通胀 3-6%</text>
            <text x="700" y="208" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">五年以上不动</text>
            <text x="700" y="234" text-anchor="middle" fill="#8499bd" font-size="12">破裂:货股两难,先法上法</text>
            <text x="450" y="330" text-anchor="middle" fill="#bcc9dd" font-size="12.5">你不能同时进行住“急用 $$ 取出生活”和“这三年亏还能赚”——挑一个优先主调</text>"""
    return concept_figure(body, "0 0 900 360",
        "家庭资产三桶图:生活应急、保险对冲、长期增值按优先级分桶负责",
        "投资的次序永远不是先挑股票。先有 6 个月生活备付,再把家里突发风险付掉,剩下闲钱才有资格进股海。三桶顺序翻铺一次,混乱是以十年兆的。")


def _fig_r20_factor_ic():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">IC:每颗因子技能摆一条？检验一切是否“态一致”</text>
            <!-- 排序 VS 下月收益坐标;正相关散开 -->
            <rect x="80" y="80" width="380" height="300" rx="10" fill="rgba(122,167,240,0.12)" stroke="rgba(122,167,240,0.5)"/>
            <text x="270" y="106" text-anchor="middle" fill="#a8c6ff" font-size="14" font-weight="800">IC 的秒定义</text>
            <text x="270" y="132" text-anchor="middle" fill="#bcc9dd" font-size="12">因子按分数给全市场若干股排队;</text>
            <text x="270" y="154" text-anchor="middle" fill="#bcc9dd" font-size="12">看上个月谁最后;</text>
            <text x="270" y="176" text-anchor="middle" fill="#bcc9dd" font-size="12">计算两个名次表的相关系数</text>
            <text x="270" y="206" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">IC = {-1 ~ +1 的相关数}</text>
            <text x="270" y="234" text-anchor="middle" fill="#bcc9dd" font-size="12">+ 表示分数高能涨(买高分好)</text>
            <text x="270" y="256" text-anchor="middle" fill="#bcc9dd" font-size="12">- 表示分数高能跌(低分好)</text>
            <text x="270" y="278" text-anchor="middle" fill="#bcc9dd" font-size="12">0 表示因子不预测未来</text>
            <text x="270" y="308" text-anchor="middle" fill="#8499bd" font-size="12">行业经验:稳定的 IC 在 0.03~0.05 尤属珍贵</text>
            <!-- 右边 曲线 -->
            <text x="630" y="90" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">IC 为什么要滚一个季度到一年</text>
            <line x1="500" y1="330" x2="820" y2="330" stroke="#8499bd" stroke-width="2"/>
            <line x1="500" y1="130" x2="500" y2="330" stroke="#8499bd" stroke-width="2"/>
            <path d="M 505 210 Q 560 200 620 220 Q 680 240 740 200 Q 790 170 820 190" fill="none" stroke="#a8c6ff" stroke-width="3"/>
            <line x1="505" y1="235" x2="820" y2="235" stroke="#f0c96a" stroke-width="2" stroke-dasharray="8 6"/>
            <text x="820" y="232" fill="#f0c96a" font-size="12">均值的均值</text>
            <text x="820" y="330" fill="#bcc9dd" font-size="12">月份</text>
            <text x="510" y="140" fill="#bcc9dd" font-size="12">IC(+)/-</text>
            <text x="650" y="362" text-anchor="middle" fill="#bcc9dd" font-size="12">任何单月可能都正,但趋势摆动围绕“均值的均值”上下;真正信号看 IC 摊平后的水平是否稳定轩抬高位</text>"""
    return concept_figure(body, "0 0 900 385",
        "IC 曲线图:因子排序与未来收益的相关性起伏,需要看一年摊平后才能判断有没有资产质量",
        "IC 是量化界的成绩单——波动大是常态,稳定上斜才是真迹。单月出来一个 0.2 不能保证是真因子,一年的平均 IC 0.03-0.05 才能写进策略池。")


def _fig_r22_greek():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">风险模型在算哪三件事</text>
            <rect x="90" y="90" width="220" height="230" rx="12" fill="rgba(122,167,240,0.2)" stroke="#7aa7f0"/>
            <text x="200" y="118" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">① 波动率</text>
            <text x="200" y="146" text-anchor="middle" fill="#bcc9dd" font-size="12">每只个股或资产自然波动多大</text>
            <text x="200" y="168" text-anchor="middle" fill="#bcc9dd" font-size="12">窗口滞后的历史扰动</text>
            <text x="200" y="196" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">方差 / 标准差</text>
            <text x="200" y="224" text-anchor="middle" fill="#bcc9dd" font-size="12">它是绝对风险的上限付罗</text>
            <text x="200" y="252" text-anchor="middle" fill="#8499bd" font-size="12">高波动 · 高风险</text>
            <text x="200" y="280" text-anchor="middle" fill="#8499bd" font-size="12">模型理解也被这块表所影响</text>
            <rect x="340" y="90" width="220" height="230" rx="12" fill="rgba(240,201,106,0.15)" stroke="#f0c96a"/>
            <text x="450" y="118" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">② 相关系数</text>
            <text x="450" y="146" text-anchor="middle" fill="#bcc9dd" font-size="12">股和股之间起落有多同步</text>
            <text x="450" y="168" text-anchor="middle" fill="#bcc9dd" font-size="12">不同行业不同景度</text>
            <text x="450" y="196" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">协方差矩阵</text>
            <text x="450" y="224" text-anchor="middle" fill="#bcc9dd" font-size="12">它是分散的杠杆——</text>
            <text x="450" y="246" text-anchor="middle" fill="#bcc9dd" font-size="12">相关性越高,收益越像</text>
            <text x="450" y="274" text-anchor="middle" fill="#8499bd" font-size="12">极度时她完全不分散</text>
            <rect x="590" y="90" width="220" height="230" rx="12" fill="rgba(238,136,119,0.15)" stroke="#ee8877"/>
            <text x="700" y="118" text-anchor="middle" fill="#ffb4b4" font-size="15" font-weight="800">③ 暴露程度</text>
            <text x="700" y="146" text-anchor="middle" fill="#bcc9dd" font-size="12">你持有的小整组合</text>
            <text x="700" y="168" text-anchor="middle" fill="#bcc9dd" font-size="12">对某个因子的平均评价</text>
            <text x="700" y="196" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">行业暴露 * 风格暴露</text>
            <text x="700" y="224" text-anchor="middle" fill="#bcc9dd" font-size="12">它是你在赌什么——</text>
            <text x="700" y="246" text-anchor="middle" fill="#bcc9dd" font-size="12">赌价值,赌成长,赌消费</text>
            <text x="700" y="274" text-anchor="middle" fill="#8499bd" font-size="12">过度集中就是赌注过巫</text>
            <text x="450" y="360" text-anchor="middle" fill="#bcc9dd" font-size="12.5">风险不是一个总数,是这三个维度的题项之合;这三个合在一起才叫卫刻风险献</text>"""
    return concept_figure(body, "0 0 900 385",
        "风险模型三维度图:波动率、相关系数(协方差)、因子暴露,分别描述绝对风险、分散程度、赌博方向",
        "说“这个组合风险大”没有意义;要说“哪个维度”的风险大。先看波动、再看关联、最后看暴露——三层都过了,才算真正把风险看透了。")


def _fig_r23_career():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">量化研究员 ≠ 量化工程师 ≠ 交易员</text>
            <rect x="70" y="80" width="240" height="250" rx="12" fill="rgba(240,201,106,0.18)" stroke="#f0c96a"/>
            <text x="190" y="108" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">研究员</text>
            <text x="190" y="136" text-anchor="middle" fill="#bcc9dd" font-size="12">每天:读论文、算数据</text>
            <text x="190" y="158" text-anchor="middle" fill="#bcc9dd" font-size="12">写因子、试模型</text>
            <text x="190" y="186" text-anchor="middle" fill="#8fb37a" font-size="13" font-weight="800">产出:信号和因子</text>
            <text x="190" y="214" text-anchor="middle" fill="#8499bd" font-size="12">核心能力:统计学+金融理解</text>
            <text x="190" y="242" text-anchor="middle" fill="#bcc9dd" font-size="12">指标: IC, RankIC</text>
            <text x="190" y="270" text-anchor="middle" fill="#bcc9dd" font-size="12">假设定理与实验设计</text>
            <text x="190" y="298" text-anchor="middle" fill="#8499bd" font-size="11.5">工资净累,压力重寝发</text>
            <rect x="340" y="80" width="240" height="250" rx="12" fill="rgba(122,167,240,0.2)" stroke="#7aa7f0"/>
            <text x="460" y="108" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">工程师</text>
            <text x="460" y="136" text-anchor="middle" fill="#bcc9dd" font-size="12">每天:设工具、搭开仓</text>
            <text x="460" y="158" text-anchor="middle" fill="#bcc9dd" font-size="12">优化延迟、提架构</text>
            <text x="460" y="186" text-anchor="middle" fill="#8fb37a" font-size="13" font-weight="800">产出:高效的执现环境</text>
            <text x="460" y="214" text-anchor="middle" fill="#8499bd" font-size="12">核心能力:代码质量+系统御决</text>
            <text x="460" y="242" text-anchor="middle" fill="#bcc9dd" font-size="12">指标: 延迟、成熟度</text>
            <text x="460" y="270" text-anchor="middle" fill="#bcc9dd" font-size="12">如何低延迟不堑误</text>
            <text x="460" y="298" text-anchor="middle" fill="#8499bd" font-size="11.5">高级语言与异恈工程语言</text>
            <rect x="610" y="80" width="240" height="250" rx="12" fill="rgba(238,136,119,0.15)" stroke="#ee8877"/>
            <text x="730" y="108" text-anchor="middle" fill="#ffb4b4" font-size="15" font-weight="800">交易员</text>
            <text x="730" y="136" text-anchor="middle" fill="#bcc9dd" font-size="12">每天:盯盘、改仓位</text>
            <text x="730" y="158" text-anchor="middle" fill="#bcc9dd" font-size="12">监控风险、调整策略</text>
            <text x="730" y="186" text-anchor="middle" fill="#8fb37a" font-size="13" font-weight="800">产出: 盘中仓位与决断</text>
            <text x="730" y="214" text-anchor="middle" fill="#8499bd" font-size="12">核心能力:市场直觉+备压</text>
            <text x="730" y="242" text-anchor="middle" fill="#bcc9dd" font-size="12">指标: PnL, 成交量实现</text>
            <text x="730" y="270" text-anchor="middle" fill="#bcc9dd" font-size="12">执行与微结构决策</text>
            <text x="730" y="298" text-anchor="middle" fill="#8499bd" font-size="11.5">执行心理负载最大</text>
            <text x="450" y="358" text-anchor="middle" fill="#bcc9dd" font-size="12.5">三个人殊不等于三个级别,同级别但天天处理的是完全不同的对象</text>"""
    return concept_figure(body, "0 0 900 385",
        "量化行业三岗位对比:研究员产出因子、工程师产出系统、交易员产出决断,三种不同的工作对象",
        "三种技能栈完全不同:一个读学术找信号,一个写代码跟微秒赛跑,一个盯盘压手。你选哪个方向,先看你爱处理的是符号、系统还是决策者。")


PATCH_R3 = {
    16: [("大公司说话更大声", _fig_r16_index)],
    18: [("九成司机自认为中上水平", _fig_r18_overconfidence)],
    19: [("先分桶,不是先选股", _fig_r19_buckets)],
    20: [("因子排序和未来收益是否同向", _fig_r20_factor_ic)],
    22: [("风险模型在估计什么", _fig_r22_greek)],
    23: [("量化机构不是只有研究员", _fig_r23_career)],
}



def _fig_r10_run():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">挤兑的速度档位:批发清算比零售存款快上百倍</text>
            <rect x="60" y="80" width="230" height="155" rx="10" fill="rgba(143,179,122,0.2)" stroke="#8fb37a"/>
            <text x="175" y="108" text-anchor="middle" fill="#b5d3a0" font-size="14" font-weight="800">零售存款挤兑</text>
            <text x="175" y="134" text-anchor="middle" fill="#bcc9dd" font-size="12">居民在营业点ATM排队</text>
            <text x="175" y="156" text-anchor="middle" fill="#bcc9dd" font-size="12">存款保险让他们不必太快</text>
            <text x="175" y="184" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">酝酿来要几天到几周</text>
            <rect x="335" y="80" width="230" height="155" rx="10" fill="rgba(240,201,106,0.15)" stroke="#f0c96a"/>
            <text x="450" y="108" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">同业拆借挤兑</text>
            <text x="450" y="134" text-anchor="middle" fill="#bcc9dd" font-size="12">机构之间“今天别再借给它了”</text>
            <text x="450" y="156" text-anchor="middle" fill="#bcc9dd" font-size="12">瞬时的通知,没有门铃</text>
            <text x="450" y="184" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">几小时就完成断流</text>
            <rect x="610" y="80" width="230" height="155" rx="10" fill="rgba(238,136,119,0.2)" stroke="#ee8877"/>
            <text x="725" y="108" text-anchor="middle" fill="#ffb4b4" font-size="14" font-weight="800">批发回购挤兑</text>
            <text x="725" y="134" text-anchor="middle" fill="#bcc9dd" font-size="12">对方从“押品抽责”开始:</text>
            <text x="725" y="156" text-anchor="middle" fill="#bcc9dd" font-size="12">原来的折扣率 2% → 45%</text>
            <text x="725" y="178" text-anchor="middle" fill="#bcc9dd" font-size="12">等于抵押品瞬间被折价一半</text>
            <text x="725" y="206" text-anchor="middle" fill="#ee8877" font-size="13" font-weight="800">按小时-日日落实,分钟里有生死</text>
            <rect x="60" y="260" width="780" height="100" rx="10" fill="rgba(18,29,49,0.7)" stroke="rgba(240,201,106,0.45)"/>
            <text x="84" y="288" fill="#f0c96a" font-size="13" font-weight="800">这就是 2008 年雷曼的死法</text>
            <text x="84" y="314" fill="#bcc9dd" font-size="12">雷曼需要的“明天开运”资金是靠回购融资。回购对手一旦在它身上加码新折扣率、或要求追加抵押,雷曼的钱立刻不够付到期的账单——结果 48 小时就场倒闭</text>
            <text x="84" y="338" fill="#bcc9dd" font-size="12">存款保险是零售预防挤兑的疫苗;批发机构挤兑至今靠壮机构互相“不要廷同时逼债”这种非正式愿望,脆弱得多</text>"""
    return concept_figure(body, "0 0 900 385",
        "挤兑三级速度图:零售几天几月、同业几小时、批发回购分钟级,雷曼 48 小时倒闭",
        "同样是挤兑,批发机构之间的速度比居民排队快上三个数量级。2008 年雷曼之所以两天就死,根源正是它被回购市场瞬间断水。")


def _fig_r11_corridor():
    """ch11:利率走廊,锚“货币政策三件套: 政策利率、准备金率、公开市场操作”。"""
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">利率走廊:央行不是出一个点数,是画一条通道</text>
            <!-- 走廊 -->
            <rect x="120" y="90" width="660" height="220" rx="10" fill="rgba(122,167,240,0.1)" stroke="rgba(122,167,240,0.5)"/>
            <line x1="120" y1="140" x2="780" y2="140" stroke="#ee8877" stroke-width="2.5" stroke-dasharray="8 5"/>
            <text x="130" y="132" fill="#ee8877" font-size="13" font-weight="800">上限:贴现利率/紧急贷款利率(央行贷款给你的价格)</text>
            <line x1="120" y1="250" x2="780" y2="250" stroke="#8fb37a" stroke-width="2.5" stroke-dasharray="8 5"/>
            <text x="130" y="270" fill="#8fb37a" font-size="13" font-weight="800">下限:超额准备金利率(银行闲钱存央行的价格)</text>
            <!-- 政策利率 -->
            <line x1="120" y1="195" x2="780" y2="195" stroke="#f0c96a" stroke-width="3"/>
            <text x="130" y="188" fill="#f0c96a" font-size="13" font-weight="800">目标:政策利率(联邦基金利率/七天逆回购)</text>
            <!-- 市场利率游荡 -->
            <path d="M 200 210 Q 300 170 400 195 Q 500 220 600 185 Q 700 165 760 195" fill="none" stroke="#a8c6ff" stroke-width="3"/>
            <text x="560" y="168" fill="#a8c6ff" font-size="12">市场利率(Shibor/同业存单利率)</text>
            <!-- 说明 -->
            <rect x="80" y="330" width="740" height="70" rx="10" fill="rgba(18,29,49,0.7)" stroke="rgba(132,153,189,0.4)"/>
            <text x="104" y="354" fill="#bcc9dd" font-size="12">走廊比点数重要:上限是让市场知道利率再贵也不超过这条线,下限是让市场知道钱再便宜央行也不让它跌穿。两层线一变,市场利率自然就会容许在中间游荡</text>
            <text x="104" y="378" fill="#bcc9dd" font-size="12">美联储加息 = 整条走廊上移;QE/缩表 = 央行直接买/卖资产把走廊内的市场利率压缩到底,两种是不同工具</text>"""
    return concept_figure(body, "0 0 900 420",
        "利率走廊图:上下限两条虚线夹着政策利率,市场利率在其中游荡,人民银行用走廊来控制资金价格",
        "理解央行的加息/降息不要记“数字变几点”,要看走廊整体搬上了几条台阶——墙根动了、普通利率就会跟随加动上限/下限的位移。")


def _fig_r12_solvency():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">偿付能力充足率:保险公司的救生衣气压表</text>
            <rect x="90" y="80" width="330" height="110" rx="10" fill="rgba(122,167,240,0.2)" stroke="#7aa7f0"/>
            <text x="255" y="108" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">分子:实际资本</text>
            <text x="255" y="134" text-anchor="middle" fill="#bcc9dd" font-size="12">经审计认可的净资产 + 认可资产价值</text>
            <text x="255" y="156" text-anchor="middle" fill="#bcc9dd" font-size="12">减掉风险折价以上,这就是缓冲底</text>
            <text x="255" y="182" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">它是一块保险气录,要在风险中发现</text>
            <rect x="480" y="80" width="330" height="110" rx="10" fill="rgba(238,136,119,0.15)" stroke="#ee8877"/>
            <text x="645" y="108" text-anchor="middle" fill="#ffb4b4" font-size="15" font-weight="800">分母:最低资本</text>
            <text x="645" y="134" text-anchor="middle" fill="#bcc9dd" font-size="12">监管按你的保单风险、资产风险算出的最低要求</text>
            <text x="645" y="156" text-anchor="middle" fill="#bcc9dd" font-size="12">风险越大 → 分母越高 → 充足率越低</text>
            <text x="645" y="182" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">它是风险大小,不是风险的绝对开销</text>
            <text x="450" y="224" text-anchor="middle" fill="#f0c96a" font-size="17" font-weight="800">充足率 = 实际资本 / 最低资本</text>
            <rect x="90" y="252" width="220" height="110" rx="10" fill="rgba(143,179,122,0.2)" stroke="#8fb37a"/>
            <text x="200" y="280" text-anchor="middle" fill="#b5d3a0" font-size="15" font-weight="800">&gt;150%</text>
            <text x="200" y="304" text-anchor="middle" fill="#bcc9dd" font-size="12">监管信任的监督级别</text>
            <text x="200" y="328" text-anchor="middle" fill="#8fb37a" font-size="12">允许加大分红和新产品</text>
            <rect x="340" y="252" width="220" height="110" rx="10" fill="rgba(240,201,106,0.15)" stroke="#f0c96a"/>
            <text x="450" y="280" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">100% - 150%</text>
            <text x="450" y="304" text-anchor="middle" fill="#bcc9dd" font-size="12">开始被“屯促管”</text>
            <text x="450" y="328" text-anchor="middle" fill="#bcc9dd" font-size="12">规范新增资产和新保单</text>
            <rect x="590" y="252" width="220" height="110" rx="10" fill="rgba(238,136,119,0.2)" stroke="#ee8877"/>
            <text x="700" y="280" text-anchor="middle" fill="#ffb4b4" font-size="15" font-weight="800">&lt;100%</text>
            <text x="700" y="304" text-anchor="middle" fill="#bcc9dd" font-size="12">监管可以直接接管</text>
            <text x="700" y="328" text-anchor="middle" fill="#ee8877" font-size="12">公司被视为有问题</text>
            <text x="450" y="398" text-anchor="middle" fill="#bcc9dd" font-size="12.5">看充足率别只记百分比,要看“与 100% 的距离”;距离越小,你买的保险听起来越安心,但承受突然赔款的工作能力越糟</text>"""
    return concept_figure(body, "0 0 900 420",
        "偿付能力公式与门槛图:实际资本除以最低资本,临界值 50%、100%、150%",
        "偿付能力充足率就是保险公司的资本密度表:低于 100% 监管有权接管,150% 以上是舒服区。买长期险前一眼这栏,高于看条款的遗漏收集。")


def _fig_r13_pillars3():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">养老三支柱,你在哪根上</text>
            <rect x="70" y="80" width="240" height="230" rx="12" fill="rgba(122,167,240,0.2)" stroke="#7aa7f0"/>
            <text x="190" y="110" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">①国家底:基本养老</text>
            <text x="190" y="138" text-anchor="middle" fill="#bcc9dd" font-size="12">现收现付、覆盖面广</text>
            <text x="190" y="160" text-anchor="middle" fill="#bcc9dd" font-size="12">你只要缴朋雷城就累积</text>
            <text x="190" y="188" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">替代率 ≈ 50%</text>
            <text x="190" y="216" text-anchor="middle" fill="#8499bd" font-size="12">按就业期的姬蓝文化序列绂押</text>
            <text x="190" y="244" text-anchor="middle" fill="#8499bd" font-size="12">越多越多交,退休长缴费</text>
            <text x="190" y="272" text-anchor="middle" fill="#8fb37a" font-size="12.5">饿不死</text>
            <rect x="350" y="80" width="240" height="230" rx="12" fill="rgba(240,201,106,0.15)" stroke="#f0c96a"/>
            <text x="470" y="110" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">②单位加:企业/职业年金</text>
            <text x="470" y="138" text-anchor="middle" fill="#bcc9dd" font-size="12">单位自愿搭配</text>
            <text x="470" y="160" text-anchor="middle" fill="#bcc9dd" font-size="12">覆盖率 &lt; 10%(中国)</text>
            <text x="470" y="188" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">贡献 ~10-20%</text>
            <text x="470" y="216" text-anchor="middle" fill="#8499bd" font-size="12">招比直接配套本单位才有</text>
            <text x="470" y="244" text-anchor="middle" fill="#8499bd" font-size="12">国家给税优</text>
            <text x="470" y="272" text-anchor="middle" fill="#f0c96a" font-size="12.5">过得还行</text>
            <rect x="630" y="80" width="240" height="230" rx="12" fill="rgba(238,136,119,0.15)" stroke="#ee8877"/>
            <text x="750" y="110" text-anchor="middle" fill="#ffb4b4" font-size="15" font-weight="800">③个人搂:个人养老金</text>
            <text x="750" y="138" text-anchor="middle" fill="#bcc9dd" font-size="12">自愿·税延·合出</text>
            <text x="750" y="160" text-anchor="middle" fill="#bcc9dd" font-size="12">年上限 12000 元</text>
            <text x="750" y="188" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">你的决定权重夷一块</text>
            <text x="750" y="216" text-anchor="middle" fill="#8499bd" font-size="12">可以买养老目标基金/存款/保险</text>
            <text x="750" y="244" text-anchor="middle" fill="#8499bd" font-size="12">三十年久期复利主场</text>
            <text x="750" y="272" text-anchor="middle" fill="#ee8877" font-size="12.5">活得体面</text>
            <text x="450" y="330" text-anchor="middle" fill="#bcc9dd" font-size="12.5">日本、美国、欧洲的叠加:①+②还不够,得③补上;别等老后才发现那道缺口</text>
            <text x="450" y="355" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">自测:你的工资之外,还存了多少你自己不动声色的离退休金?这才是宝素</text>"""
    return concept_figure(body, "0 0 900 385",
        "养老三支柱对比图:国家基础、单位年金、个人养老金,替代率分别50%、10-20%、自负",
        "三支柱分工拆开:国家保证不饿死,单位决定你能不能活得还行,个人养老金决定你老后能不能活出选择适合自己的生活方式。中国 70% 替代率的缺口,头一个要补的就是第三根柱。")


def _fig_r14_bidask():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">盘口簿:买几档卖几档,谁排在前面</text>
            <text x="200" y="76" fill="#eef4f8" font-size="14" font-weight="800">买单(从优到次)</text>
            <rect x="60" y="86" width="280" height="44" rx="6" fill="rgba(143,179,122,0.32)" stroke="#8fb37a"/>
            <text x="80" y="114" fill="#b5d3a0" font-size="13" font-weight="800">买1: 10.50 元 × 5000 股</text>
            <rect x="60" y="134" width="280" height="44" rx="6" fill="rgba(143,179,122,0.18)" stroke="#8fb37a"/>
            <text x="80" y="162" fill="#8fb37a" font-size="13">买2: 10.49 元 × 2000 股</text>
            <rect x="60" y="182" width="280" height="44" rx="6" fill="rgba(143,179,122,0.1)" stroke="#8fb37a"/>
            <text x="80" y="210" fill="#8fb37a" font-size="13">买3: 10.48 元 × 9000 股</text>
            <text x="200" y="244" fill="#8499bd" font-size="11.5">价高者排前——出价力最强的先成交</text>
            <text x="640" y="76" fill="#eef4f8" font-size="14" font-weight="800">卖单(从优到次)</text>
            <rect x="560" y="86" width="280" height="44" rx="6" fill="rgba(238,136,119,0.32)" stroke="#ee8877"/>
            <text x="580" y="114" fill="#ffb4b4" font-size="13" font-weight="800">卖1: 10.51 元 × 1000 股</text>
            <rect x="560" y="134" width="280" height="44" rx="6" fill="rgba(238,136,119,0.18)" stroke="#ee8877"/>
            <text x="580" y="162" fill="#ee8877" font-size="13">卖2: 10.52 元 × 3000 股</text>
            <rect x="560" y="182" width="280" height="44" rx="6" fill="rgba(238,136,119,0.1)" stroke="#ee8877"/>
            <text x="580" y="210" fill="#ee8877" font-size="13">卖3: 10.55 元 × 2500 股</text>
            <text x="640" y="244" fill="#8499bd" font-size="11.5">价低者排前</text>
            <text x="450" y="118" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">撮合规则钳</text>
            <text x="450" y="148" text-anchor="middle" fill="#bcc9dd" font-size="12">买1 价 ≥ 卖1 价?</text>
            <text x="450" y="170" text-anchor="middle" fill="#bcc9dd" font-size="12">是 → 配对成交(以先斩到的价格为准)</text>
            <text x="450" y="192" text-anchor="middle" fill="#bcc9dd" font-size="12">否 → 一起待着,价差就自己保留</text>
            <text x="450" y="222" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">同价?先到的先成交(时间优先)</text>
            <text x="450" y="250" text-anchor="middle" fill="#8499bd" font-size="12">你下单后只是进入这条队伍,不一定立刻成交;流动性浅的股,两个买1卖1差的可能超过你想象的宽度</text>"""
    return concept_figure(body, "0 0 900 280",
        "订单簿双列排布图:买单从高到低排列、卖单从低到高排列,价格优先同价时间优先",
        "盘口的两条队伍:买的一边价高者优先,卖的一边价低者优先。你下的单子只是被系统挂在某个格子上排队,“我喊到了这个价”还远远不等于“我就能成交”。")


def _fig_r15_broken():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">退市三条触发门:财务、交易、重大违法</text>
            <rect x="60" y="90" width="240" height="185" rx="10" fill="rgba(122,167,240,0.2)" stroke="#7aa7f0"/>
            <text x="180" y="118" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">财务指标门</text>
            <text x="180" y="146" text-anchor="middle" fill="#bcc9dd" font-size="12">连续两年亏损 + 营收 &lt; 1 亿</text>
            <text x="180" y="168" text-anchor="middle" fill="#bcc9dd" font-size="12">净资产为负</text>
            <text x="180" y="196" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">先看真是小账</text>
            <text x="180" y="224" text-anchor="middle" fill="#8499bd" font-size="11">扣非后的业绩才算数</text>
            <text x="180" y="252" text-anchor="middle" fill="#8499bd" font-size="11">“脱胎换骨”前科要退市</text>
            <rect x="330" y="90" width="240" height="185" rx="10" fill="rgba(238,136,119,0.15)" stroke="#ee8877"/>
            <text x="450" y="118" text-anchor="middle" fill="#ffb4b4" font-size="15" font-weight="800">交易指标门</text>
            <text x="450" y="146" text-anchor="middle" fill="#bcc9dd" font-size="12">连续 20 个交易日收盘价 &lt; 1 元</text>
            <text x="450" y="168" text-anchor="middle" fill="#bcc9dd" font-size="12">总市值 &lt; 3 亿元</text>
            <text x="450" y="196" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">“市场用脚投票”这条最直接</text>
            <text x="450" y="224" text-anchor="middle" fill="#8499bd" font-size="11">2023-2024 年最后的主流退市入口</text>
            <rect x="600" y="90" width="240" height="185" rx="10" fill="rgba(143,179,122,0.15)" stroke="#8fb37a"/>
            <text x="720" y="118" text-anchor="middle" fill="#b5d3a0" font-size="15" font-weight="800">重大违法门</text>
            <text x="720" y="146" text-anchor="middle" fill="#bcc9dd" font-size="12">财务造假主业务收入金额大</text>
            <text x="720" y="168" text-anchor="middle" fill="#bcc9dd" font-size="12">欺诈发行被追刑责</text>
            <text x="720" y="196" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">一眼就踢出沒商议</text>
            <text x="720" y="224" text-anchor="middle" fill="#8499bd" font-size="11">触发即停牌 → 终止上市</text>
            <text x="450" y="316" text-anchor="middle" fill="#bcc9dd" font-size="12.5">三条门加起来的结果:2019-2024 年年均退市数是注册制前的几倍——“上市就不是质保铭牌,上市也不是永生”</text>"""
    return concept_figure(body, "0 0 900 350",
        "退市三条门示意图:财务指标、交易指标、重大违法,注册制后门都打开了",
        "戴帽不是结束、退市才是一致结果。注册制把“进来”的门放宽,必须把“出去”的门也打开——这就是我为什么要盯涨跌幅红线为什么警惕。")


PATCH_R2 = {
    10: [("挤兑的队伍排在回购市场上", _fig_r10_run)],
    11: [("政策利率、准备金率、公开市场操作", _fig_r11_corridor)],
    12: [("保险公司自己的救生衣", _fig_r12_solvency)],
    13: [("国家、企业、自己各扛一部分", _fig_r13_pillars3)],
    14: [("价格优先和时间优先", _fig_r14_bidask)],
    15: [("戴帽、*ST 与强制退出的三条路", _fig_r15_broken)],
}



def _fig_r02_clearing():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">成交只是承诺,交收才算完成</text>
            <rect x="60" y="80" width="230" height="130" rx="10" fill="rgba(122,167,240,0.2)" stroke="#7aa7f0"/>
            <text x="175" y="108" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">T 日 · 撮合成交</text>
            <text x="175" y="134" text-anchor="middle" fill="#bcc9dd" font-size="12">交易所确认:谁买谁卖</text>
            <text x="175" y="156" text-anchor="middle" fill="#bcc9dd" font-size="12">双方价格锁定</text>
            <text x="175" y="184" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">合同成立,钱货未动</text>
            <rect x="335" y="80" width="230" height="130" rx="10" fill="rgba(240,201,106,0.15)" stroke="#f0c96a"/>
            <text x="450" y="108" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">T+1 日 · 清算</text>
            <text x="450" y="134" text-anchor="middle" fill="#bcc9dd" font-size="12">中国结算做净额轧算</text>
            <text x="450" y="156" text-anchor="middle" fill="#bcc9dd" font-size="12">算清每户净该收/付多少</text>
            <text x="450" y="184" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">证券、资金都在划拨途中</text>
            <rect x="610" y="80" width="230" height="130" rx="10" fill="rgba(143,179,122,0.2)" stroke="#8fb37a"/>
            <text x="725" y="108" text-anchor="middle" fill="#b5d3a0" font-size="15" font-weight="800">T+1 日 · 交收</text>
            <text x="725" y="134" text-anchor="middle" fill="#bcc9dd" font-size="12">股票划到买方证券账户</text>
            <text x="725" y="156" text-anchor="middle" fill="#bcc9dd" font-size="12">现金划到卖方资金账户</text>
            <text x="725" y="184" text-anchor="middle" fill="#8fb37a" font-size="13" font-weight="800">此刻才算真正持有</text>
            <line x1="292" y1="145" x2="333" y2="145" stroke="#8499bd" stroke-width="3" marker-end="url(#arrR1)"/>
            <line x1="567" y1="145" x2="608" y2="145" stroke="#8499bd" stroke-width="3" marker-end="url(#arrR1)"/>
            <defs><marker id="arrR1" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#8499bd"/></marker></defs>
            <rect x="60" y="240" width="780" height="100" rx="10" fill="rgba(18,29,49,0.7)" stroke="rgba(240,201,106,0.45)"/>
            <text x="84" y="268" fill="#f0c96a" font-size="13" font-weight="800">为什么先过账的规则不可逆</text>
            <text x="84" y="294" fill="#bcc9dd" font-size="12">交易所要求券商先冻结资金与证券再挂单,是把“打白条”的风险挡在交易系统之外;A 股之所以 T+1,是要给中央对手方留出清算窗口</text>
            <text x="84" y="318" fill="#bcc9dd" font-size="12">看懂这三步,后面讲停牌、交割日期、甚至国债期货的交割规则,全都是这一条逻辑的延伸</text>"""
    return concept_figure(body, "0 0 900 365",
        "成交、清算、交收三步流程图:T 日撮合合同成立,T+1 轧算划拨,此刻才算持有",
        "成交只是合同锁价,清算是按净额算账,交收才是真正把钱和票过户。A 股 T+1 的本质,是让中央对手方有一天时间核对完账本。")


def _fig_r04_convert():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">可转债 = 一张普通债券 + 一个认购期权</text>
            <rect x="70" y="90" width="360" height="110" rx="10" fill="rgba(122,167,240,0.22)" stroke="#7aa7f0"/>
            <text x="250" y="118" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">债底(纯债价值)</text>
            <text x="250" y="144" text-anchor="middle" fill="#bcc9dd" font-size="12">公司正常还本付息,它就该值多少钱</text>
            <text x="250" y="166" text-anchor="middle" fill="#bcc9dd" font-size="12">例如面值 100 元的转债,纯债底约 95 元</text>
            <text x="250" y="190" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">下跌有底,提供安全边际</text>
            <rect x="470" y="90" width="360" height="110" rx="10" fill="rgba(238,136,119,0.18)" stroke="#ee8877"/>
            <text x="650" y="118" text-anchor="middle" fill="#ffb4b4" font-size="15" font-weight="800">期权顶(转股价值)</text>
            <text x="650" y="144" text-anchor="middle" fill="#bcc9dd" font-size="12">按转股价转成股票后能值多少</text>
            <text x="650" y="166" text-anchor="middle" fill="#bcc9dd" font-size="12">正股涨 30%,它按比例跟涨</text>
            <text x="650" y="190" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">上方收益不设限</text>
            <path d="M 250 205 Q 450 268 650 205" fill="none" stroke="#8fb37a" stroke-width="3"/>
            <text x="450" y="258" text-anchor="middle" fill="#b5d3a0" font-size="14" font-weight="800">转债市价 = 债底 + 期权溢价</text>
            <rect x="70" y="290" width="760" height="80" rx="10" fill="rgba(18,29,49,0.7)" stroke="rgba(132,153,189,0.4)"/>
            <text x="94" y="316" fill="#f0c96a" font-size="13" font-weight="800">用它判断贵贱</text>
            <text x="94" y="340" fill="#bcc9dd" font-size="12">先看债底能兜住多少(下方保护有多厚),再看转股溢价率(上方买股票饭要加多少钱);两个数都合理,这张转债才算便宜</text>"""
    return concept_figure(body, "0 0 900 395",
        "可转债结构拆解图:债底提供下行保护,转股权提供上行弹性,价格是两份之和",
        "先看债底给不给你兜,再看期权溢价替波动买了多少单。这样看转债的贵贱,就不只是一个百分比涨跌的事。")


def _fig_r06_greeks():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">期权做市商桌上的四块表</text>
            <rect x="70" y="80" width="360" height="125" rx="10" fill="rgba(122,167,240,0.2)" stroke="#7aa7f0"/>
            <text x="250" y="108" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">Delta · 标的价格每变 1 元</text>
            <text x="250" y="134" text-anchor="middle" fill="#bcc9dd" font-size="12">买平值看涨时 Delta ≈ 0.5:标涨 1 元,期权约赚 0.5</text>
            <text x="250" y="156" text-anchor="middle" fill="#bcc9dd" font-size="12">看跌在 -1~0 之间</text>
            <text x="250" y="188" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">对冲要用它调仓位</text>
            <rect x="470" y="80" width="360" height="125" rx="10" fill="rgba(238,136,119,0.18)" stroke="#ee8877"/>
            <text x="650" y="108" text-anchor="middle" fill="#ffb4b4" font-size="15" font-weight="800">Gamma · 行情的加速度</text>
            <text x="650" y="134" text-anchor="middle" fill="#bcc9dd" font-size="12">标的价格每变一格,Delta 自身变多少</text>
            <text x="650" y="156" text-anchor="middle" fill="#bcc9dd" font-size="12">临近到期、平值附近的 Gamma 最大</text>
            <text x="650" y="188" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">大 Gamma 意味着仓位会越错越快</text>
            <rect x="70" y="220" width="360" height="125" rx="10" fill="rgba(240,201,106,0.15)" stroke="#f0c96a"/>
            <text x="250" y="248" text-anchor="middle" fill="#f0c96a" font-size="15" font-weight="800">Vega · 波动率预期每变 1%</text>
            <text x="250" y="274" text-anchor="middle" fill="#bcc9dd" font-size="12">隐含波动率不是历史波动,是大家对未来的定价</text>
            <text x="250" y="296" text-anchor="middle" fill="#bcc9dd" font-size="12">恐慌时 IV 上冲,期权价格被动抬升</text>
            <text x="250" y="328" text-anchor="middle" fill="#8499bd" font-size="12">做市商对冲它,就要卖进买保险</text>
            <rect x="470" y="220" width="360" height="125" rx="10" fill="rgba(143,179,122,0.2)" stroke="#8fb37a"/>
            <text x="650" y="248" text-anchor="middle" fill="#b5d3a0" font-size="15" font-weight="800">Theta · 每天时间价值衰减多少</text>
            <text x="650" y="274" text-anchor="middle" fill="#bcc9dd" font-size="12">到期越近,沙漏漏得越快</text>
            <text x="650" y="296" text-anchor="middle" fill="#bcc9dd" font-size="12">买方每天都在输 Theta,卖方每天都在收</text>
            <text x="650" y="328" text-anchor="middle" fill="#8499bd" font-size="12">最后一个月衰减最快</text>
            <text x="450" y="372" text-anchor="middle" fill="#bcc9dd" font-size="12.5">方向、加速度、波动、时间——期权的全部价格行为,疏散成这四块表就够了</text>"""
    return concept_figure(body, "0 0 900 400",
        "期权四希腊字母表:Delta 管方向、Gamma 管加速度、Vega 管波动预期、Theta 管时间流逝",
        "期权的复杂不在名字,在维度——方向、加速度、波动预期、时间衰减各占一块。把四块钱读懂,希腊字母就不再是密室术语。")


def _fig_r07_roe():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">杜邦拆解:ROE = 利润率 × 周转率 × 杠杆</text>
            <rect x="360" y="70" width="180" height="80" rx="10" fill="rgba(240,201,106,0.25)" stroke="#f0c96a" stroke-width="2"/>
            <text x="450" y="100" text-anchor="middle" fill="#f0c96a" font-size="17" font-weight="800">ROE 18%</text>
            <text x="450" y="124" text-anchor="middle" fill="#bcc9dd" font-size="12">净利润 / 股东权益</text>
            <rect x="70" y="200" width="230" height="110" rx="10" fill="rgba(143,179,122,0.2)" stroke="#8fb37a"/>
            <text x="185" y="228" text-anchor="middle" fill="#b5d3a0" font-size="14" font-weight="800">① 净利润率</text>
            <text x="185" y="254" text-anchor="middle" fill="#bcc9dd" font-size="12">每 100 元收入净赚多少</text>
            <text x="185" y="276" text-anchor="middle" fill="#bcc9dd" font-size="12">刀刃是经营水准</text>
            <text x="185" y="300" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">利润驱动型公司</text>
            <rect x="335" y="200" width="230" height="110" rx="10" fill="rgba(122,167,240,0.2)" stroke="#7aa7f0"/>
            <text x="450" y="228" text-anchor="middle" fill="#a8c6ff" font-size="14" font-weight="800">② 资产周转率</text>
            <text x="450" y="254" text-anchor="middle" fill="#bcc9dd" font-size="12">一块资产一年转销出多少收入</text>
            <text x="450" y="276" text-anchor="middle" fill="#bcc9dd" font-size="12">刀刃是运营效率</text>
            <text x="450" y="300" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">效率驱动型公司</text>
            <rect x="600" y="200" width="230" height="110" rx="10" fill="rgba(238,136,119,0.18)" stroke="#ee8877"/>
            <text x="715" y="228" text-anchor="middle" fill="#ffb4b4" font-size="14" font-weight="800">③ 杠杆倍数</text>
            <text x="715" y="254" text-anchor="middle" fill="#bcc9dd" font-size="12">总资产 / 股东权益</text>
            <text x="715" y="276" text-anchor="middle" fill="#bcc9dd" font-size="12">刀刃是财务风险</text>
            <text x="715" y="300" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">杠杆驱动型公司</text>
            <path d="M 400 152 Q 300 178 250 196" fill="none" stroke="#8499bd" stroke-width="2.5"/>
            <path d="M 450 152 Q 450 178 450 196" fill="none" stroke="#8499bd" stroke-width="2.5"/>
            <path d="M 500 152 Q 580 178 680 196" fill="none" stroke="#8499bd" stroke-width="2.5"/>
            <rect x="70" y="340" width="760" height="90" rx="10" fill="rgba(18,29,49,0.7)" stroke="rgba(240,201,106,0.45)"/>
            <text x="94" y="366" fill="#f0c96a" font-size="13" font-weight="800">同 ROE ≠ 同质</text>
            <text x="94" y="390" fill="#bcc9dd" font-size="12">A: 18% 利润率 × 1 周转 × 1 杠杆 = 18%,凭经营;B: 3% 利润率 × 1.2 周转 × 5 杠杆 = 18%,凭负债</text>
            <text x="94" y="412" fill="#bcc9dd" font-size="12">两种 18 一旦利率上行表现完全相反——这就是必须拆开看的原因</text>"""
    return concept_figure(body, "0 0 900 450",
        "杜邦三联拆解图:ROE拆成利润率、资产周转率、杠杆倍数,同 ROE 不同质,经营型与杠杆型天差地别",
        "ROE 的数字好看不代表质量好——先拆开看是挣钱挣的、效率挣的,还是负债堆的。只有能拆开的 ROE,才是撑得住下行的 ROE。")


def _fig_r08_demographic():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">人口从红利走向老龄化,资产定价规则就被重写</text>
            <line x1="80" y1="200" x2="820" y2="200" stroke="#8499bd" stroke-width="2"/>
            <text x="92" y="224" fill="#8499bd" font-size="11">1980</text>
            <text x="280" y="224" fill="#8499bd" font-size="11">2000</text>
            <text x="480" y="224" fill="#8499bd" font-size="11">2015</text>
            <text x="680" y="224" fill="#8499bd" font-size="11">2030+</text>
            <rect x="80" y="70" width="220" height="110" rx="10" fill="rgba(143,179,122,0.22)" stroke="#8fb37a"/>
            <text x="190" y="96" text-anchor="middle" fill="#b5d3a0" font-size="14" font-weight="800">人口红利期</text>
            <text x="190" y="122" text-anchor="middle" fill="#bcc9dd" font-size="12">劳动力充足廉价,储蓄率高</text>
            <text x="190" y="144" text-anchor="middle" fill="#bcc9dd" font-size="12">资金持续涌入生产性资产</text>
            <text x="190" y="172" text-anchor="middle" fill="#8fb37a" font-size="13" font-weight="800">股票、工厂、房产各自受益</text>
            <rect x="350" y="70" width="220" height="110" rx="10" fill="rgba(240,201,106,0.15)" stroke="#f0c96a"/>
            <text x="460" y="96" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">人口拐点(刘易斯拐点)</text>
            <text x="460" y="122" text-anchor="middle" fill="#bcc9dd" font-size="12">农村廉价劳力被吸尽</text>
            <text x="460" y="144" text-anchor="middle" fill="#bcc9dd" font-size="12">中国大约 2004-2010 跨过</text>
            <text x="460" y="172" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">工资开始加速上涨</text>
            <rect x="620" y="70" width="220" height="110" rx="10" fill="rgba(238,136,119,0.18)" stroke="#ee8877"/>
            <text x="730" y="96" text-anchor="middle" fill="#ffb4b4" font-size="14" font-weight="800">老龄化承重期</text>
            <text x="730" y="122" text-anchor="middle" fill="#bcc9dd" font-size="12">领养老金的人 ≥ 缴费人口的一半</text>
            <text x="730" y="144" text-anchor="middle" fill="#bcc9dd" font-size="12">财富持有重心转移</text>
            <text x="730" y="172" text-anchor="middle" fill="#ee8877" font-size="13" font-weight="800">债券、现金、保险需求上升</text>
            <rect x="80" y="260" width="760" height="100" rx="10" fill="rgba(18,29,49,0.7)" stroke="rgba(132,153,189,0.4)"/>
            <text x="104" y="288" fill="#f0c96a" font-size="14" font-weight="800">两大长期后果</text>
            <text x="104" y="314" fill="#bcc9dd" font-size="12">利率中枢被压低:庞大储蓄人群争抢固定收益资产,长期债价被持续买高;养老金权益仓位减轻:大量退休人口同时抛售股票换生活费,股市长期承压</text>
            <text x="104" y="336" fill="#bcc9dd" font-size="12">看利率下行别只怪央行——人口结构本身就是汪洋里那股最深的水流</text>"""
    return concept_figure(body, "0 0 900 385",
        "人口周期三阶段图:红利→拐点→老龄化,资产偏好从股票房产转向债券现金保险",
        "刘易斯拐点一过,全社会从“赚工资”切成“领退休金”,债券和保险被推起来,股票被长期拖住。人口不是远问题,是利率每天跳动后面那只看不见的手。")


def _fig_r09_leverage_run():
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">2015 A 股杠杆清算:从杠杆最高的那层开始向下挤</text>
            <text x="80" y="66" fill="#8499bd" font-size="12" font-weight="800">层级越高越安全,越低越最先被迫卖;清算顺序不是你选的,是合同替你选的</text>
            <rect x="80" y="80" width="740" height="48" rx="6" fill="rgba(143,179,122,0.2)" stroke="#8fb37a"/>
            <text x="100" y="111" fill="#b5d3a0" font-size="13" font-weight="800">① 自有资金大仓位</text>
            <text x="440" y="111" fill="#bcc9dd" font-size="12">没有利息、没有平仓线 → 可以穿越周期等回资产价值</text>
            <rect x="80" y="136" width="740" height="48" rx="6" fill="rgba(240,201,106,0.2)" stroke="#f0c96a"/>
            <text x="100" y="167" fill="#f0c96a" font-size="13" font-weight="800">② 两融仓位(券商融资)</text>
            <text x="440" y="167" fill="#bcc9dd" font-size="12">维持担保比例不足而不补仓 → 券商依法强平</text>
            <rect x="80" y="192" width="740" height="48" rx="6" fill="rgba(238,136,119,0.2)" stroke="#ee8877"/>
            <text x="100" y="223" fill="#ffb4b4" font-size="13" font-weight="800">③ 场外配资(5-10 倍杠杆)</text>
            <text x="440" y="223" fill="#bcc9dd" font-size="12">月息 1.5-2%,只要标的跌 5-10% 就触发平仓</text>
            <rect x="80" y="248" width="740" height="48" rx="6" fill="rgba(238,136,119,0.4)" stroke="#ee8877"/>
            <text x="100" y="279" fill="#ee8877" font-size="13" font-weight="800">④ 结构化优先级/高度聚集的多策略产品</text>
            <text x="440" y="279" fill="#ee8877" font-size="12">市场一反,同一位置上的杠杆全部指向同一出口</text>
            <text x="450" y="332" text-anchor="middle" fill="#bcc9dd" font-size="12.5"></text>
            <text x="450" y="332" text-anchor="middle" fill="#bcc9dd" font-size="12.5">清算一旦连锁,无杠杆的① 也会被③④ 拖跌——因为价格本身已经被强平卖压砸穿了</text>"""
    return concept_figure(body, "0 0 900 360",
        "2015 A股杠杆清算顺序图:自有资金最安全,场外配资最先被迫卖,连锁溃败会把自信资金连坐拖垮",
        "清算的层级不是好的坏的排而是资金结构深浅。在连锁强平里,哪怕你没加杠杆,只要你也持有同样资产,价格也会被别人的平仓砸下来。")


PATCH_R1 = {
    2: [("成交不是终点,后面还有清算和交收", _fig_r02_clearing)],
    4: [("可转债为什么复杂", _fig_r04_convert)],
    6: [("做市商桌上的四块表", _fig_r06_greeks)],
    7: [("股东的钱赚得怎么样", _fig_r07_roe)],
    8: [("红利、拐点、老龄化", _fig_r08_demographic)],
    9: [("杠杆的清算顺序踩死流动性", _fig_r09_leverage_run)],
}



def _fig_p15_ipo():
    """ch15:打新从红包到技术活的前后对比。"""
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">打新经济学:从制度红包到技术活</text>
            <!-- 两根柱子:核准 vs 注册 -->
            <rect x="120" y="90" width="240" height="170" rx="10" fill="rgba(143,179,122,0.2)" stroke="#8fb37a"/>
            <text x="240" y="118" text-anchor="middle" fill="#b5d3a0" font-size="16" font-weight="800">核准制时代</text>
            <text x="240" y="146" text-anchor="middle" fill="#bcc9dd" font-size="13">23 倍 PE 隐形上限</text>
            <text x="240" y="170" text-anchor="middle" fill="#bcc9dd" font-size="13">首日涨跌 ≤ 44%</text>
            <text x="240" y="198" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">破发率 ≈ 0</text>
            <text x="240" y="228" text-anchor="middle" fill="#8fb37a" font-size="13" font-weight="800">两只门缝的免费彩票</text>
            <rect x="540" y="90" width="240" height="170" rx="10" fill="rgba(238,136,119,0.15)" stroke="#ee8877"/>
            <text x="660" y="118" text-anchor="middle" fill="#ffb4b4" font-size="16" font-weight="800">注册制时代(2023.4 起)</text>
            <text x="660" y="146" text-anchor="middle" fill="#bcc9dd" font-size="13">询价制,贴近二级价</text>
            <text x="660" y="170" text-anchor="middle" fill="#bcc9dd" font-size="13">前五日不设涨跌幅</text>
            <text x="660" y="198" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">破发率 10-20%+</text>
            <text x="660" y="228" text-anchor="middle" fill="#ee8877" font-size="13" font-weight="800">要读招股书的技术活</text>
            <path d="M 370 170 Q 450 130 530 170" fill="none" stroke="#8499bd" stroke-width="3" stroke-dasharray="8 6"/>
            <text x="450" y="120" text-anchor="middle" fill="#8499bd" font-size="12">制度差价消失了</text>
            <text x="450" y="308" text-anchor="middle" fill="#bcc9dd" font-size="12.5">免费彩票变调研题之后,你的本钱路线和机会成本才受到正视</text>"""
    return concept_figure(body, "0 0 900 340",
        "打新制度对比图:左列核准制时代隐形上限23倍PE、首日涨跌44%、破发率近零;右列注册制询价,破发率10%以上",
        "核准制下打新是制度红包,注册制把红包收回变成技术活。这不是制度变坏了,定价权交回市场了——免费午餐一收摊,你赚不赚钱只能靠自己读东西。")


def _fig_p15_delist():
    """ch15:上市与退市两条门扇,才能优胜劣汏。"""
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">一只门的上市和另一只门的退市</text>
            <!-- 左:上市门 -->
            <path d="M 80 300 L 80 130 Q 200 100 320 130 L 320 300 Z" fill="rgba(122,167,240,0.12)" stroke="#7aa7f0" stroke-width="2"/>
            <text x="200" y="150" text-anchor="middle" fill="#a8c6ff" font-size="15" font-weight="800">发行端(进门)</text>
            <text x="200" y="178" text-anchor="middle" fill="#bcc9dd" font-size="12">注册制:审核只查披露</text>
            <text x="200" y="200" text-anchor="middle" fill="#bcc9dd" font-size="12">监管不再实质把关</text>
            <text x="200" y="228" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">门变宽:更多公司能进</text>
            <!-- 右:退市门 -->
            <path d="M 580 300 L 580 130 Q 700 100 820 130 L 820 300 Z" fill="rgba(238,136,119,0.12)" stroke="#ee8877" stroke-width="2"/>
            <text x="700" y="150" text-anchor="middle" fill="#ffb4b4" font-size="15" font-weight="800">退市端(出门)</text>
            <text x="700" y="178" text-anchor="middle" fill="#bcc9dd" font-size="12">交易指标:面值1元/市值3亿红线</text>
            <text x="700" y="200" text-anchor="middle" fill="#bcc9dd" font-size="12">财务违法指标:连年亏损/造假</text>
            <text x="700" y="228" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">门变宽:壳价值丢多</text>
            <!-- 中间的池 -->
            <ellipse cx="450" cy="215" rx="95" ry="55" fill="rgba(240,201,106,0.15)" stroke="#f0c96a"/>
            <text x="450" y="210" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">二级市场水池</text>
            <text x="450" y="232" text-anchor="middle" fill="#bcc9dd" font-size="12">进得出才健康</text>
            <!-- 循环箭头 -->
            <path d="M 320 215 Q 355 210 355 215" fill="none" stroke="#8499bd" stroke-width="3" marker-end="url(#arrowP)"/>
            <path d="M 545 215 Q 580 210 580 215" fill="none" stroke="#8499bd" stroke-width="3" marker-end="url(#arrowP)"/>
            <defs><marker id="arrowP" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#8499bd"/></marker></defs>
            <text x="450" y="328" text-anchor="middle" fill="#8499bd" font-size="12.5">美国一年退几百家,中国个位数时代刚结束;两扇门一起拉开,水洼才会流转</text>"""
    return concept_figure(body, "0 0 900 360",
        "上市与退市两扇门夹着二级市场水池:发行端注册制门宽、退市端指标红线下沉,两门同开水才会錯转",
        "注册制打开了进水口,退市常态化打开了出水口。只有进没有出,水池变渊;只出不进,市场变成存量屠宰场。两头都活络,市场才完成天然的汰换。")


def _fig_p18_scurve():
    """ch18:前景理论 S 曲线:左半比右半陡。"""
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">卡尼曼 S 曲线:同一个 100 元,亏的时候疼一倍</text>
            <!-- 数轴 -->
            <line x1="100" y1="200" x2="800" y2="200" stroke="#8499bd" stroke-width="2"/>
            <line x1="450" y1="70" x2="450" y2="330" stroke="#8499bd" stroke-width="2"/>
            <text x="785" y="224" text-anchor="middle" fill="#bcc9dd" font-size="12">客观盈亏</text>
            <text x="462" y="86" fill="#bcc9dd" font-size="12">主观感受</text>
            <circle cx="450" cy="200" r="6" fill="#f0c96a"/>
            <text x="450" y="224" text-anchor="middle" fill="#f0c96a" font-size="12" font-weight="800">参照点(你买入价)</text>
            <!-- S 曲线 -->
            <path d="M 160 300 Q 300 290 400 230 Q 440 205 450 200 Q 460 195 500 170 Q 600 110 740 100" fill="none" stroke="#a8c6ff" stroke-width="4"/>
            <text x="210" y="320" text-anchor="middle" fill="#ee8877" font-size="13" font-weight="800">亏损侧(陡)</text>
            <text x="690" y="90" text-anchor="middle" fill="#8fb37a" font-size="13" font-weight="800">盈利侧(平)</text>
            <!-- 拼装标 ↓ 收入 -->
            <path d="M 380 285 L 520 115" stroke="#f0c96a" stroke-width="2" stroke-dasharray="6 4"/>
            <text x="460" y="205" fill="#f0c96a" font-size="11.5">斜率≈2-2.5倍</text>
            <text x="450" y="352" text-anchor="middle" fill="#bcc9dd" font-size="12.5">含义:同样 100 元,当它离开你时,你的难受程度是它进来时的两倍</text>"""
    return concept_figure(body, "0 0 900 385",
        "前景理论S形曲线:横轴客观盈亏纵轴主观感受,原点是你买入价,左半亏损侧陡于右半盈利侧,斜率差约两倍",
        "前景理论的图式记法:人不是按绝对财富作判断,是按相对参照点作判断;亏损侧比盈利侧陡一倍,所以丢 100 的疼需要赚 200 才能抹平。这是处置效应、回本执念、死扛不换仓的总源头。")


def _fig_p18_disposition():
    """ch18:处置效应:两只票你会先卖哪只。"""
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">处置效应:为什么你会留下错的那只</text>
            <!-- 两条持仓条 -->
            <rect x="100" y="90" width="320" height="110" rx="10" fill="rgba(143,179,122,0.2)" stroke="#8fb37a"/>
            <text x="260" y="118" text-anchor="middle" fill="#b5d3a0" font-size="14" font-weight="800">股票 A:+18%</text>
            <text x="260" y="144" text-anchor="middle" fill="#bcc9dd" font-size="12">浮盈,心里复古的想法:</text>
            <text x="260" y="166" text-anchor="middle" fill="#bcc9dd" font-size="12">“赶紧卖了,怕回吐!”</text>
            <text x="260" y="192" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">卖出概率高</text>
            <rect x="480" y="90" width="320" height="110" rx="10" fill="rgba(238,136,119,0.15)" stroke="#ee8877"/>
            <text x="640" y="118" text-anchor="middle" fill="#ffb4b4" font-size="14" font-weight="800">股票 B:-25%</text>
            <text x="640" y="144" text-anchor="middle" fill="#bcc9dd" font-size="12">浮亏,心里复古的想法:</text>
            <text x="640" y="166" text-anchor="middle" fill="#bcc9dd" font-size="12">“只要不卖,就不算输”</text>
            <text x="640" y="192" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">持有概率高</text>
            <!-- 不合理之处 -->
            <text x="450" y="240" text-anchor="middle" fill="#ee8877" font-size="14" font-weight="800">全世界散户加起来做了同一个动作——把未来会涨的票卖了,抱着未来还在跌的票不放手</text>
            <text x="450" y="270" text-anchor="middle" fill="#bcc9dd" font-size="12.5">不是谁比谁脏,是损失厌恶+S形曲线写了同一道出厂程序</text>
            <!-- 健康的相反动作 -->
            <rect x="60" y="295" width="780" height="60" rx="10" fill="rgba(18,29,49,0.7)" stroke="rgba(122,167,240,0.4)"/>
            <text x="84" y="320" fill="#a8c6ff" font-size="13" font-weight="800">量化纪律恰恰相反</text>
            <text x="84" y="344" fill="#bcc9dd" font-size="12">止损失败的方向(截断错误),加码成功的方向(让浮盈延伸) ——对人性用力气,对出厂设置拆阀门,比技术分析的点金术要高级。</text>"""
    return concept_figure(body, "0 0 900 385",
        "处置效应两票对比图:股票A浮盈18%卖出概率高、股票B浮亏25%持有概率高;卖出猛涨持有还跌的,与量化纪律恰好相反",
        "同一个时间的两个按钮:你心里会按键的顺序,与市场赢钱的顺序恰好相反。截断失败、放大成功这种量化纪律,不是逆着运,是逆着出厂设置。")


def _fig_p19_iceberg():
    """ch19:家庭资产冰山:保障性水位舄茅看不到。"""
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">家庭配置的冰山:水面上是投资,水面下是底盘</text>
            <!-- 水面 -->
            <line x1="100" y1="160" x2="800" y2="160" stroke="#8499bd" stroke-width="3" stroke-dasharray="10 6"/>
            <text x="782" y="148" text-anchor="end" fill="#8499bd" font-size="12">水面</text>
            <!-- 水面上的小金子 -->
            <path d="M 370 120 L 530 120 L 500 160 L 400 160 Z" fill="rgba(240,201,106,0.9)" stroke="#f0c96a"/>
            <text x="450" y="148" text-anchor="middle" fill="#eef4f8" font-size="13" font-weight="800">大家看到的那块:股票/基金仓位</text>
            <!-- 水下的大冰床 -->
            <path d="M 400 160 L 500 160 L 620 330 L 280 330 Z" fill="rgba(122,167,240,0.15)" stroke="#7aa7f0"/>
            <text x="450" y="210" text-anchor="middle" fill="#a8c6ff" font-size="13" font-weight="800">水面下:应急资金(3-6 个月刚性支出)</text>
            <text x="450" y="236" text-anchor="middle" fill="#a8c6ff" font-size="13" font-weight="800">重疾险 / 医疗险 / 定期寿险</text>
            <text x="450" y="262" text-anchor="middle" fill="#a8c6ff" font-size="13" font-weight="800">养老金(第一二三支柱分跑)</text>
            <text x="450" y="294" text-anchor="middle" fill="#bcc9dd" font-size="12">只谈水面上的仓位,水花一大缝就直接沉底</text>
            <text x="450" y="362" text-anchor="middle" fill="#bcc9dd" font-size="12.5">顺序:现金垫→风险垫→长期投资,任何一步翻墙都会被生活血腥教学</text>"""
    return concept_figure(body, "0 0 900 390",
        "家庭资产冰山图:水面上是金尖股票基金仓位,水面下是应急金、保险保障、养老金",
        "家庭配置是冰山:水面上的金尖人人都看得见,水面下的应急、保障、养老才是决定你沉不沉的部分。把水下那三层先铸实,再谈金尖的成色。")


def _fig_p19_buckets():
    """ch19:三个桶顺序图。"""
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">家庭资产按用途分三个桶:次序不可逆</text>
            <!-- 桶① -->
            <path d="M 90 130 L 100 300 Q 165 320 230 300 L 240 130 Z" fill="rgba(122,167,240,0.2)" stroke="#7aa7f0"/>
            <text x="165" y="160" text-anchor="middle" fill="#a8c6ff" font-size="14" font-weight="800">桶① 现金桶</text>
            <text x="165" y="190" text-anchor="middle" fill="#bcc9dd" font-size="11.5">3-6 个月刚性支出</text>
            <text x="165" y="212" text-anchor="middle" fill="#bcc9dd" font-size="11.5">货币基金/活期/短债</text>
            <text x="165" y="240" text-anchor="middle" fill="#f0c96a" font-size="12" font-weight="800">要稳不要多</text>
            <!-- 桶② -->
            <path d="M 355 130 L 365 300 Q 430 320 495 300 L 505 130 Z" fill="rgba(240,201,106,0.15)" stroke="#f0c96a"/>
            <text x="430" y="160" text-anchor="middle" fill="#f0c96a" font-size="14" font-weight="800">桶② 保障桶</text>
            <text x="430" y="190" text-anchor="middle" fill="#bcc9dd" font-size="11.5">重疾险→医疗险→寿险</text>
            <text x="430" y="212" text-anchor="middle" fill="#bcc9dd" font-size="11.5">保费 ≤ 年收入 3-8%</text>
            <text x="430" y="240" text-anchor="middle" fill="#ee8877" font-size="12" font-weight="800">保险不做理财</text>
            <!-- 桶③ -->
            <path d="M 620 130 L 630 300 Q 695 320 760 300 L 770 130 Z" fill="rgba(238,136,119,0.12)" stroke="#ee8877"/>
            <text x="695" y="160" text-anchor="middle" fill="#ffb4b4" font-size="14" font-weight="800">桶③ 增值桶</text>
            <text x="695" y="190" text-anchor="middle" fill="#bcc9dd" font-size="11.5">宽基指数/债券组合</text>
            <text x="695" y="212" text-anchor="middle" fill="#bcc9dd" font-size="11.5">3-5 年以上不动的钱</text>
            <text x="695" y="240" text-anchor="middle" fill="#8fb37a" font-size="12" font-weight="800">股债 60/40 起步</text>
            <!-- 箭头 -->
            <path d="M 240 210 Q 295 210 350 210" fill="none" stroke="#8499bd" stroke-width="2.5" marker-end="url(#arrowP2)"/>
            <path d="M 505 210 Q 560 210 615 210" fill="none" stroke="#8499bd" stroke-width="2.5" marker-end="url(#arrowP2)"/>
            <defs><marker id="arrowP2" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#8499bd"/></marker></defs>
            <text x="450" y="352" text-anchor="middle" fill="#bcc9dd" font-size="12.5">桶②和桶③ 位置泄露,桶③ 波动首先震倒没有现金和保障的家庭</text>"""
    return concept_figure(body, "0 0 900 385",
        "三桶图:桶一是现金桶应急,桶二是保障桶保险,桶三是增值桶资产配置,三桶必须按顺序装",
        "把家里的钱装进三个桶:现金桶保证你能活,保障桶保证你能今晚安睡,增值桶才谈得上赚多少。你常踩的每一个坑,几乎都是桶②和桶③没装好就冲去装点桶③。")


def _fig_p38_reading():
    """ch38:一个产品的三份文件,阅读顺序与各自责任。"""
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">产品文件三层:合同是地基,报告是例行体检</text>
            <!-- 三层 -->
            <rect x="90" y="80" width="720" height="70" rx="10" fill="rgba(122,167,240,0.15)" stroke="#7aa7f0"/>
            <text x="120" y="108" fill="#a8c6ff" font-size="14" font-weight="800">第一层 地基(一次性)</text>
            <text x="120" y="132" fill="#bcc9dd" font-size="12">基金招募书 / 产品说明书——写清楚能买什么、什么价可以买、什么价必须止损</text>
            <rect x="90" y="170" width="720" height="70" rx="10" fill="rgba(240,201,106,0.12)" stroke="#f0c96a"/>
            <text x="120" y="198" fill="#f0c96a" font-size="14" font-weight="800">第二层 体检(每季度)</text>
            <text x="120" y="222" fill="#bcc9dd" font-size="12">定期报告:超额收益、份额变化、重仓集中度——超过三层信号都在这份文件里</text>
            <rect x="90" y="260" width="720" height="70" rx="10" fill="rgba(238,136,119,0.12)" stroke="#ee8877"/>
            <text x="120" y="288" fill="#ffb4b4" font-size="14" font-weight="800">第三层 生死状(结构化)</text>
            <text x="120" y="312" fill="#bcc9dd" font-size="12">确认书:敲出/敲入/票息/观察频率/期限——这五个数决定你到底买了什么中间可以的结局</text>
            <text x="450" y="362" text-anchor="middle" fill="#bcc9dd" font-size="12.5">所有事项权重都在文档里,任何“销售说”的话却都不成立</text>"""
    return concept_figure(body, "0 0 900 390",
        "产品文件三层图:招募书地基、定期报告体检、确认书生死状,各写一行对应你要顶的指标",
        "产品文件分列三层:地基是一次性体检(招募书),例行体检是季报,生死状是结构化条款清单。每层你只看自己负责的指标。黑字永远压倒言语。")


def _fig_p38_fivesnowball():
    """ch38:雪球确认书五处必看。"""
    body = """            <text x="450" y="34" text-anchor="middle" fill="#eef4f8" font-size="19" font-weight="800">雪球确认书的五个词</text>
            <!-- 五个框 -->
            <rect x="40" y="90" width="150" height="130" rx="10" fill="rgba(122,167,240,0.2)" stroke="#7aa7f0"/>
            <text x="115" y="118" text-anchor="middle" fill="#a8c6ff" font-size="13" font-weight="800">① 敲出价</text>
            <text x="115" y="144" text-anchor="middle" fill="#bcc9dd" font-size="11">涨的门槛</text>
            <text x="115" y="166" text-anchor="middle" fill="#bcc9dd" font-size="11">期初 × 100-105%</text>
            <rect x="210" y="90" width="150" height="130" rx="10" fill="rgba(238,136,119,0.15)" stroke="#ee8877"/>
            <text x="285" y="118" text-anchor="middle" fill="#ffb4b4" font-size="13" font-weight="800">② 敲入价</text>
            <text x="285" y="144" text-anchor="middle" fill="#bcc9dd" font-size="11">跌的陷阱</text>
            <text x="285" y="166" text-anchor="middle" fill="#bcc9dd" font-size="11">期初 × 70-80%</text>
            <rect x="380" y="90" width="150" height="130" rx="10" fill="rgba(240,201,106,0.15)" stroke="#f0c96a"/>
            <text x="455" y="118" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">③ 票息率</text>
            <text x="455" y="144" text-anchor="middle" fill="#bcc9dd" font-size="11">承诺的年票息</text>
            <text x="455" y="166" text-anchor="middle" fill="#bcc9dd" font-size="11">15%-20%是拉客价</text>
            <rect x="550" y="90" width="150" height="130" rx="10" fill="rgba(143,179,122,0.15)" stroke="#8fb37a"/>
            <text x="625" y="118" text-anchor="middle" fill="#b5d3a0" font-size="13" font-weight="800">④ 观察频率</text>
            <text x="625" y="144" text-anchor="middle" fill="#bcc9dd" font-size="11">每日 / 每月</text>
            <text x="625" y="166" text-anchor="middle" fill="#bcc9dd" font-size="11">错颗粒度会错估概率</text>
            <rect x="720" y="90" width="150" height="130" rx="10" fill="rgba(132,153,189,0.15)" stroke="#8499bd"/>
            <text x="795" y="118" text-anchor="middle" fill="#bcc9dd" font-size="13" font-weight="800">⑤ 期限</text>
            <text x="795" y="144" text-anchor="middle" fill="#bcc9dd" font-size="11">有多长</text>
            <text x="795" y="166" text-anchor="middle" fill="#bcc9dd" font-size="11">长期票息更高但风险更长</text>
            <text x="450" y="266" text-anchor="middle" fill="#f0c96a" font-size="13" font-weight="800">这五个数拼起来就是你买的东西;丢了任何一个,你都不知买的是什么</text>
            <text x="450" y="300" text-anchor="middle" fill="#bcc9dd" font-size="12.5">回程资金账:敲入触发后,票息补不回敲入的下跌;前文已把四条命拆解过了</text>"""
    return concept_figure(body, "0 0 920 330",
        "雪球确认书五关键词:敲出价、敲入价、票息率、观察频率、期限,五框匀排",
        "雪球这类结构化产品的阅读绝不复杂:只要五处数字你能在确认书里找到,你就知道买了什么。腿不净判读不叫节省工夫,叫按运气发牌。")


PATCH_P = {
    15: [("从制度红包到智力活动", _fig_p15_ipo),
         ("发行与退市是同一部机器的两半", _fig_p15_delist)],
    18: [("所有苦乐都看参照点", _fig_p18_scurve),
         ("为什么你总把赚钱的卖了", _fig_p18_disposition)],
    19: [("先给自己留一条能呼吸的缝", _fig_p19_iceberg),
         ("先分桶,不是先选股", _fig_p19_buckets)],
    38: [("一切口头的承诺都不算数", _fig_p38_reading),
         ("雪球确认书逐词拆", _fig_p38_fivesnowball)],
}



PATCH_L = {
    8: [("卡在不高不低的那一档", _fig_l8_stairs)],
    28: [("训练、预测和回测不要混", _fig_l23_pipeline)],
}


def _merge_figures(base, patch):
    """按章合并锚点列表,不覆盖既有条目"""
    for k, v in patch.items():
        base.setdefault(k, []).extend(v)

_merge_figures(CONCEPT_FIGURES, CONCEPT_FIGURES_FREE)
_merge_figures(CONCEPT_FIGURES, PATCH_C)
_merge_figures(CONCEPT_FIGURES, PATCH_D)
_merge_figures(CONCEPT_FIGURES, PATCH_E)
_merge_figures(CONCEPT_FIGURES, PATCH_F)
_merge_figures(CONCEPT_FIGURES, PATCH_G)
_merge_figures(CONCEPT_FIGURES, PATCH_H)
_merge_figures(CONCEPT_FIGURES, PATCH_I)
_merge_figures(CONCEPT_FIGURES, PATCH_J)
_merge_figures(CONCEPT_FIGURES, PATCH_K)
_merge_figures(CONCEPT_FIGURES, PATCH_L)
_merge_figures(CONCEPT_FIGURES, PATCH_M)
_merge_figures(CONCEPT_FIGURES, PATCH_N)
_merge_figures(CONCEPT_FIGURES, PATCH_R1)
_merge_figures(CONCEPT_FIGURES, PATCH_R2)
_merge_figures(CONCEPT_FIGURES, PATCH_R3)
_merge_figures(CONCEPT_FIGURES, PATCH_RMID)
_merge_figures(CONCEPT_FIGURES, PATCH_R5)
_merge_figures(CONCEPT_FIGURES, PATCH_R6)
_merge_figures(CONCEPT_FIGURES, PATCH_R7)
_merge_figures(CONCEPT_FIGURES, PATCH_P)


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
# 3. 术语表中的金融术语 -> 天青点线链接,每小节同一术语只链接第一次;
# 4. 数值+单位(46 亿美元/3%/20 倍...) -> 金色数字 .num(做全书里的视觉锚点)。
_GLOSSARY_LINK_TARGETS = {term: term for term, _ in GLOSSARY}
_GLOSSARY_LINK_TARGETS.update({
    "ROE": "净资产收益率(ROE)",
    "净资产收益率": "净资产收益率(ROE)",
    "PE": "市盈率(PE)",
    "市盈率": "市盈率(PE)",
    "PB": "市净率(PB)",
    "市净率": "市净率(PB)",
    "夏普": "夏普比率",
    "IR": "信息比率",
    "RankIC": "IC",
    "alpha": "Alpha",
    "beta": "Beta",
    "升水": "升水/贴水",
    "贴水": "升水/贴水",
    "动量": "动量因子",
})
_LEGACY_ENRICH_TERMS = {
    "RankIC", "REIT", "REITs", "IPO", "T+0", "IR", "ROE", "PE", "PB",
    "夏普", "超额收益", "年化收益", "股指期货", "保证金", "杠杆",
    "动量", "反转", "沪深 300", "中证 500",
}
_ENRICH_TERM_LABELS = sorted(
    set(_GLOSSARY_LINK_TARGETS) | _LEGACY_ENRICH_TERMS,
    key=lambda item: (-len(item), item),
)
_ENRICH_TERMS_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:"
    + "|".join(re.escape(term) for term in _ENRICH_TERM_LABELS)
    + r")(?![A-Za-z0-9])"
)
_ENRICH_NUM_RE = re.compile(
    r"(?<![0-9A-Za-z#])(-?\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?\s*(?:亿美元|万元|亿元|万美元|万|亿|%|倍|个基点|bp|"
    r"个百分点|年|个月|月|个交易日|交易日|日|天|股|手|张|点|元|次|分钟|小时))(?![0-9A-Za-z「」])"
)


def _enrich_terms_nums(inner: str, linked_glossary_targets: set[str]) -> str:
    """处理纯文本片段；跳过链接和代码，避免嵌套或误改代码示例。"""
    parts = re.split(r"(<[^>]+>)", inner)
    blocked_depth = 0
    for i in range(len(parts)):
        seg = parts[i]
        if not seg:
            continue
        if seg.startswith("<"):
            tag = re.match(r"<\s*(/?)\s*([A-Za-z0-9]+)", seg)
            if tag:
                closing, name = tag.groups()
                name = name.lower()
                if name in {"a", "code"}:
                    if closing:
                        blocked_depth = max(0, blocked_depth - 1)
                    elif not seg.rstrip().endswith("/>"):
                        blocked_depth += 1
            continue
        if blocked_depth:
            continue

        def _term(m):
            label = m.group(0)
            target = _GLOSSARY_LINK_TARGETS.get(label)
            if target is None:
                return f'<span class="term">{esc(label)}</span>'
            if target in linked_glossary_targets:
                if label in _LEGACY_ENRICH_TERMS:
                    return f'<span class="term">{esc(label)}</span>'
                return esc(label)
            linked_glossary_targets.add(target)
            anchor = f"g-{slugify(target)}"
            return (
                f'<a class="term term-link" href="glossary.html#{anchor}" '
                f'title="查看术语：{esc(target)}">{esc(label)}</a>'
            )

        seg = _ENRICH_TERMS_RE.sub(_term, seg)
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


def enrich_body(
    htmltext: str,
    linked_glossary_targets: set[str] | None = None,
) -> str:
    """对单个小节 body 做富文本增强(不改原文文字,只加包装)。

    手稿 body 由 p(...) + ... 直接拼接,段落之间没有换行,因此按 <p>...</p>
    边界切分;含 figure/pre/table/svg 的复合块保持原样。
    """
    parts = re.split(r"(<p>[\s\S]*?</p>)", htmltext)
    out = []
    if linked_glossary_targets is None:
        linked_glossary_targets = set()
    for seg in parts:
        if not (seg.startswith("<p>") and seg.endswith("</p>")) or any(tag in seg for tag in ("<pre", "<figure", "<table", "<svg", "<ol", "<ul", "code-walk")):
            out.append(seg)
            continue
        inner = seg[3:-4]
        plain = re.sub(r"<[^>]+>", "", inner)
        # 1) 标志词段落升级成 callout
        kw, style, title = _marker_title(plain)
        if kw and len(plain) <= 260:
            out.append(f'<div class="callout callout--{style} reveal"><span class="callout__title">{esc(title)}</span><p>{_enrich_terms_nums(inner, linked_glossary_targets)}</p></div>')
            continue
        # 2) 双引号短语高亮(避免已含标签的片段错乱)
        def _hl(m):
            return f'<span class="hl">“{m.group(1)}”</span>'
        new_inner = re.sub(r"“([^”<>]{2,18})”", _hl, inner)
        # 3) 术语与数字标注:对已含 <span class="hl"> 的嵌套安全(split 按标签切)
        new_inner = _enrich_terms_nums(new_inner, linked_glossary_targets)
        out.append(f"<p>{new_inner}</p>")
    return "".join(out)


FIGURE_SOURCE_OVERRIDES = {
    # 旧章同时包含策略全景和指数增强专题;总览图留在策略全景,
    # 其余两个锚点会自然匹配到指数增强专题。
    (24, "指数增强"): 29,
}


def figure_anchors_for_chapter(ch: dict) -> list:
    """把旧公开章号登记的概念图按小节锚点迁回源单元。"""
    by_num = {item["num"]: item for item in SOURCE_CHAPTERS}
    wanted = set(ch["source_nums"])
    result = []
    for legacy_num, anchors in CONCEPT_FIGURES.items():
        legacy_sources = LEGACY_CHAPTER_GROUPS[legacy_num]
        for keyword, maker in anchors:
            owners = []
            for source_num in legacy_sources:
                source = by_num[source_num]
                titles = [clean_section_title(title) for title, _ in source["sections"]]
                if any(keyword in title for title in titles):
                    owners.append(source_num)
            owner = FIGURE_SOURCE_OVERRIDES.get(
                (legacy_num, keyword), owners[0] if owners else legacy_sources[0]
            )
            if owner in wanted:
                result.append((keyword, maker))
    return result


def render_chapter_context(ch: dict) -> str:
    current = ch["part_chapter_index"] + 1
    total = ch["part_chapter_count"]
    note = "可独立选读,不影响后续量化主线。" if ch["part_kind"] == "special" else ""
    if ch["part_kind"] == "appendix":
        note = "工具型内容,需要时回来查。"
    return f"""
        <section class="chapter-context chapter-context--{esc(ch['part_kind'])}">
          <div class="chapter-context__meta">
            <span class="chapter-context__badge">{esc(ch['part_badge'])}</span>
            <span>本部分第 {current} / {total} 章</span>
          </div>
          <p><strong>本部分的问题:</strong>{esc(ch['part_question'])}</p>
          <p class="chapter-context__outcome">{esc(ch['part_outcome'])} {esc(note)}</p>
        </section>
"""


def render_handoff(ch: dict) -> str:
    idx = ch["num"]
    if idx == len(CHAPTERS) - 1:
        return """
        <section class="chapter-handoff">
          <span class="chapter-handoff__label">读到这里</span>
          <h2>工具箱到此结束</h2>
          <p>回到全书目录,按你的问题重新进入对应部分;这本书不要求一次记住所有内容。</p>
          <a class="xref" href="index.html">返回全书路线图 →</a>
        </section>
"""

    next_ch = CHAPTERS[idx + 1]
    if next_ch["part_kind"] == "special" and ch["part_kind"] == "main":
        main_target = next(item for item in CHAPTERS[idx + 1:] if item["part_kind"] == "main")
        return f"""
        <section class="chapter-handoff chapter-handoff--choice">
          <span class="chapter-handoff__label">接下来有两条路</span>
          <h2>先补个人安全底盘,或继续量化主线</h2>
          <p>专题篇不承担后续前置知识。想先处理保险和家庭现金流,顺序阅读;想直接进入研究生产线,可以跳过。</p>
          <div class="chapter-handoff__actions">
            <a class="xref" href="{chapter_file(next_ch['num'])}">专题选读: {esc(next_ch['title'])} →</a>
            <a class="xref" href="{chapter_file(main_target['num'])}">继续主线: {esc(main_target['title'])} →</a>
          </div>
        </section>
"""

    if next_ch["part_kind"] == "appendix" and ch["part_kind"] == "main":
        label = "正文已经收束"
        heading = "下面是随时回来查的工具箱"
        body = "术语、公式和最终检查表不再承担新的叙事任务,可以按需阅读。"
    elif next_ch["part"] != ch["part"]:
        label = "下一步"
        heading = f"进入{next_ch['part']}"
        body = next_ch["part_question"]
    else:
        label = "下一章为什么接在这里"
        heading = next_ch["title"]
        body = next_ch["desc"]
    return f"""
        <section class="chapter-handoff">
          <span class="chapter-handoff__label">{esc(label)}</span>
          <h2>{esc(heading)}</h2>
          <p>{esc(body)}</p>
        </section>
"""


CASE_SECTION_LABELS = (
    ("金融现场｜", "金融现场"),
    ("概念现场｜", "概念现场"),
)


def split_case_section_title(title: str) -> tuple[str | None, str]:
    for prefix, label in CASE_SECTION_LABELS:
        if title.startswith(prefix):
            return label, title.removeprefix(prefix)
    return None, title


def render_chapter(ch: dict) -> str:
    idx = ch["num"]
    # 概念图按锚点关键词挂到对应小节后面
    anchors = figure_anchors_for_chapter(ch)
    used = [False] * len(anchors)

    def attach_figures(title: str, out: list):
        for ai, (keyword, maker) in enumerate(anchors):
            if not used[ai] and keyword in title:
                out.append(maker())
                used[ai] = True

    units = ch.get("units") or []
    sections = []
    recap_rows = []
    linked_glossary_targets = set()
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
                case_label, display_title = split_case_section_title(title)
                if case_label:
                    sections.append(f"""
        <section class="case-study reveal">
          <span class="case-study__label">{case_label}</span>
          <h3>{ui}.{si}. {esc(display_title)}</h3>
{enrich_body(body.rstrip(), linked_glossary_targets)}
        </section>
""")
                else:
                    sections.append(f"""
        <h3>{ui}.{si}. {esc(title)}</h3>
{enrich_body(body.rstrip(), linked_glossary_targets)}
""")
                recap_rows.append((f"{ui}.{si}.", display_title))
                attach_figures(title, sections)
    else:
        rendered_sections = prepare_sections(ch["sections"])
        for n, (title, body) in enumerate(rendered_sections, 1):
            case_label, display_title = split_case_section_title(title)
            if case_label:
                sections.append(f"""
        <section class="case-study reveal">
          <span class="case-study__label">{case_label}</span>
          <h2>{n}. {esc(display_title)}</h2>
{enrich_body(body.rstrip(), linked_glossary_targets)}
        </section>
""")
            else:
                sections.append(f"""
        <h2>{n}. {esc(title)}</h2>
{enrich_body(body.rstrip(), linked_glossary_targets)}
""")
            recap_rows.append((f"{n}.", display_title))
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
{render_chapter_context(ch)}
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
{render_handoff(ch)}
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
                cards.append("        </div>\n      </section>\n")
            last_part = ch["part"]
            cards.append(f"""      <section class="toc-part-block toc-part-block--{esc(ch['part_kind'])}" id="part-{ch['part_index']}">
        <div class="toc-part-header">
          <span class="toc-part-badge">{esc(ch['part_badge'])}</span>
          <h2>{esc(last_part)}</h2>
          <p class="toc-part-question">{esc(ch['part_question'])}</p>
          <p>{esc(ch['part_outcome'])}</p>
        </div>
        <div class="toc-grid">
""")
        cards.append(f"""        <a class="toc-card reveal" href="{chapter_file(ch['num'])}">
          <span class="toc-card__num">第 {ch['num']} 章</span>
          <span class="toc-card__title">{esc(ch['title'])}</span>
          <span class="toc-card__desc">{esc(ch['desc'])}</span>
        </a>
""")
    cards.append("        </div>\n      </section>\n")

    roadmap_cards = []
    for part_index, part in enumerate(BOOK_STRUCTURE):
        if part["kind"] != "main":
            continue
        roadmap_cards.append(f"""        <a class="roadmap-card" href="#part-{part_index}">
          <span>{esc(part['badge'])}</span>
          <strong>{esc(part['title'].split('·', 1)[-1].strip())}</strong>
          <small>{esc(part['question'])}</small>
        </a>
""")

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
          一本写给计算机背景金融小白的路线书。沿着“真实财富 → 金融权利 → 市场价格与数据 →
          研究假设 → 回测验证 → 组合交易 → 项目复盘”,一步步走到可信的量化研究。
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
      <section class="book-roadmap reveal" aria-labelledby="roadmap-title">
        <p class="book-roadmap__eyebrow">建议先看路线,再进目录</p>
        <h2 id="roadmap-title">整本书只走一条主线</h2>
        <p>先理解金融为什么存在,再认识资产、市场与宏观;随后把金融问题变成可验证研究,最后让策略穿过产品、项目和人的边界。专题篇可以跳过,附录按需查阅。</p>
        <div class="roadmap-grid">
{''.join(roadmap_cards)}        </div>
        <div class="book-roadmap__aside">
          <a class="xref" href="#part-4">专题选读:个人金融的安全底盘</a>
          <a class="xref" href="#part-9">工具箱:术语、公式与最终检查表</a>
        </div>
      </section>
      <div class="toc-heading">
        <p class="book-roadmap__eyebrow">共 {len(CHAPTERS)} 章</p>
        <h2>全书目录</h2>
        <p>主线部分建议顺序阅读。每一章只回答一个核心问题;多单元章会在章内明确分层。</p>
      </div>
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
          全书 {len(CHAPTERS)} 章,正文全部手写,配 {sum(len(items) for items in CONCEPT_FIGURES.values())} 张解释概念的手绘 SVG 图。内容尽量做到通俗又不失专业,
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
.book-roadmap {
  margin-bottom: 3.5rem;
  padding: 1.5rem;
  border: 1px solid rgba(122, 167, 240, 0.28);
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(122, 167, 240, 0.11), rgba(240, 201, 106, 0.06));
}
.book-roadmap > p { max-width: 58rem; color: var(--text-soft); }
.book-roadmap__eyebrow {
  margin: 0 0 0.25rem;
  color: var(--accent);
  font-size: 0.82rem;
  font-weight: 850;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.roadmap-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.7rem;
  margin-top: 1.25rem;
}
.roadmap-card {
  display: grid;
  gap: 0.3rem;
  min-height: 10rem;
  padding: 0.9rem;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  background: rgba(12, 18, 29, 0.48);
  color: var(--text);
}
.roadmap-card:hover { text-decoration: none; border-color: rgba(240, 201, 106, 0.45); }
.roadmap-card span { color: var(--primary); font-size: 0.78rem; font-weight: 850; }
.roadmap-card strong { line-height: 1.35; }
.roadmap-card small { color: var(--text-dim); line-height: 1.55; }
.book-roadmap__aside { display: flex; flex-wrap: wrap; gap: 1rem; margin-top: 1rem; }
.toc-heading { margin-bottom: 2rem; }
.toc-heading > p:last-child { color: var(--text-soft); }
.toc-part-block { margin: 0 0 3.5rem; scroll-margin-top: calc(var(--header-height) + 1.5rem); }
.toc-part-header {
  margin-bottom: 1rem;
  padding: 1rem 1.1rem;
  border-left: 3px solid var(--primary);
  background: rgba(255,255,255,0.025);
}
.toc-part-header h2 { margin: 0.2rem 0 0.45rem; font-size: 1.65rem; }
.toc-part-header p { margin: 0.25rem 0; color: var(--text-soft); }
.toc-part-header .toc-part-question { color: var(--text); font-weight: 720; }
.toc-part-badge { color: var(--primary); font-size: 0.8rem; font-weight: 850; }
.toc-part-block--special .toc-part-header { border-left-color: var(--accent); }
.toc-part-block--special .toc-part-badge { color: var(--accent); }
.toc-part-block--appendix .toc-part-header { border-left-color: var(--text-dim); }
.toc-part-block--appendix .toc-part-badge { color: var(--text-dim); }
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
.chapter-context {
  margin: -0.8rem 0 2rem;
  padding: 1rem 1.1rem;
  border: 1px solid rgba(122, 167, 240, 0.24);
  border-left: 3px solid var(--accent);
  border-radius: 10px;
  background: rgba(122, 167, 240, 0.06);
}
.chapter-context p { margin: 0.45rem 0; }
.chapter-context__meta { display: flex; flex-wrap: wrap; gap: 0.75rem; color: var(--text-dim); font-size: 0.84rem; }
.chapter-context__badge { color: var(--accent); font-weight: 850; }
.chapter-context__outcome { font-size: 0.95rem; }
.chapter-context--special { border-left-color: var(--primary); background: rgba(240, 201, 106, 0.055); }
.chapter-context--special .chapter-context__badge { color: var(--primary); }
.chapter-context--appendix { border-left-color: var(--text-dim); background: rgba(255,255,255,0.03); }
.chapter-context--appendix .chapter-context__badge { color: var(--text-dim); }
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
.case-study {
  margin: 2.6rem 0;
  padding: 1.2rem 1.25rem 1.25rem;
  border: 1px solid rgba(240, 201, 106, 0.24);
  border-left: 4px solid var(--primary);
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(240, 201, 106, 0.09), rgba(122, 167, 240, 0.045));
}
.case-study__label {
  display: inline-flex;
  padding: 0.2rem 0.52rem;
  border-radius: 999px;
  background: rgba(240, 201, 106, 0.15);
  color: var(--primary);
  font-size: 0.76rem;
  font-weight: 850;
  letter-spacing: 0.08em;
}
.case-study h2,
.case-study h3 {
  margin-top: 0.65rem;
  padding-top: 0;
  border-top: 0;
}
.case-study p:last-child { margin-bottom: 0; }
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
.term-link {
  text-decoration: none;
  text-underline-offset: 0.18em;
}
.term-link:hover {
  color: #a9c8ff;
  border-bottom-style: solid;
  text-decoration: none;
}
.term-link:focus-visible {
  border-radius: 3px;
  outline: 2px solid var(--primary);
  outline-offset: 3px;
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
.chapter-handoff {
  margin: 3rem 0 0;
  padding: 1.2rem 1.3rem;
  border: 1px solid rgba(122, 167, 240, 0.28);
  border-radius: 12px;
  background: rgba(122, 167, 240, 0.065);
}
.chapter-handoff h2 { margin: 0.2rem 0 0.5rem; padding: 0; border: 0; font-size: 1.35rem; }
.chapter-handoff p { margin: 0.45rem 0 0.75rem; }
.chapter-handoff__label { color: var(--accent); font-size: 0.8rem; font-weight: 850; }
.chapter-handoff__actions { display: flex; flex-wrap: wrap; gap: 0.7rem 1.1rem; }
.chapter-handoff--choice { border-color: rgba(240, 201, 106, 0.3); background: rgba(240, 201, 106, 0.06); }
.chapter-handoff--choice .chapter-handoff__label { color: var(--primary); }

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
  scroll-margin-top: calc(var(--header-height) + 1.5rem);
}
.glossary-list li:target {
  margin-inline: -0.75rem;
  padding-inline: 0.75rem;
  border-radius: 8px;
  background: rgba(240, 201, 106, 0.1);
  box-shadow: inset 3px 0 0 var(--primary);
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
  .toc-grid, .map-grid, .roadmap-grid { grid-template-columns: 1fr; }
  .book-roadmap { padding: 1.1rem; }
  .roadmap-card { min-height: auto; }
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
  // 公开结构已经整体重排。使用新键避免把旧章号进度误映射到不同主题。
  var STORAGE_LAST = "financebook:last:v2";
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
    if (target.matches && target.matches(".glossary-list li[id^='g-']")) {
      scrollHeadingIntoView(target, smooth);
      return;
    }
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
