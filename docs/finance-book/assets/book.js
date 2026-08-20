
(function () {
  "use strict";
  var CHAPTERS = [
    { num: 0, title: '钱不是财富: 从一座只有鱼的小岛讲起', file: 'chapter-00.html', part: '第一部分 · 金融为什么存在' },
    { num: 1, title: '钱、价格和通胀: 鱼票为什么会缩水', file: 'chapter-01.html', part: '第一部分 · 金融为什么存在' },
    { num: 2, title: '信用、利率和债: 借钱为什么要付利息', file: 'chapter-02.html', part: '第一部分 · 金融为什么存在' },
    { num: 3, title: '银行和央行: 钱不是都躺在保险柜里', file: 'chapter-03.html', part: '第一部分 · 金融为什么存在' },
    { num: 4, title: '金融系统与市场: 钱、风险和证券如何流动', file: 'chapter-04.html', part: '第一部分 · 金融为什么存在' },
    { num: 5, title: '股票与估值: 你买的权利为什么值这个价', file: 'chapter-05.html', part: '第二部分 · 资产如何承载现金流与风险' },
    { num: 6, title: '债券: 确定性更强,但绝不等于没有风险', file: 'chapter-06.html', part: '第二部分 · 资产如何承载现金流与风险' },
    { num: 7, title: '基金、ETF、指数和私募: 把钱交给别人管理意味着什么', file: 'chapter-07.html', part: '第二部分 · 资产如何承载现金流与风险' },
    { num: 8, title: '期货、远期与互换: 把未来价格写进合约', file: 'chapter-08.html', part: '第二部分 · 资产如何承载现金流与风险' },
    { num: 9, title: '期权: 把不对称收益结构变成可交易产品', file: 'chapter-09.html', part: '第二部分 · 资产如何承载现金流与风险' },
    { num: 10, title: '跨资产入门: 外汇、商品与 REITs', file: 'chapter-10.html', part: '第二部分 · 资产如何承载现金流与风险' },
    { num: 11, title: '结构性产品深拆: 收益和风险怎样被切开重卖', file: 'chapter-11.html', part: '第二部分 · 资产如何承载现金流与风险' },
    { num: 12, title: '账户与交易界面: 一笔委托从哪里出发', file: 'chapter-12.html', part: '第三部分 · 市场如何形成价格与数据' },
    { num: 13, title: '股票怎样上市、交易与退市', file: 'chapter-13.html', part: '第三部分 · 市场如何形成价格与数据' },
    { num: 14, title: '行情、K 线、成交量和复权: 先看懂屏幕上的数字', file: 'chapter-14.html', part: '第三部分 · 市场如何形成价格与数据' },
    { num: 15, title: '指数、ETF 和基准: 你到底在和谁比较', file: 'chapter-15.html', part: '第三部分 · 市场如何形成价格与数据' },
    { num: 16, title: '财务报表和基本面因子: 公司赚钱到底看哪里', file: 'chapter-16.html', part: '第三部分 · 市场如何形成价格与数据' },
    { num: 17, title: '收益和风险怎么量化: 年化、波动、回撤和夏普', file: 'chapter-17.html', part: '第三部分 · 市场如何形成价格与数据' },
    { num: 18, title: '资产配置和分散化: 不要把所有判断押在一个地方', file: 'chapter-18.html', part: '第三部分 · 市场如何形成价格与数据' },
    { num: 19, title: '市场为什么难赢: 有效性与行为偏差', file: 'chapter-19.html', part: '第三部分 · 市场如何形成价格与数据' },
    { num: 20, title: '国家为什么有穷有富: 从起飞到中等收入陷阱', file: 'chapter-20.html', part: '第四部分 · 宏观环境如何改变资产' },
    { num: 21, title: '宏观数据和多资产: 利率、通胀、汇率和商品如何连起来', file: 'chapter-21.html', part: '第四部分 · 宏观环境如何改变资产' },
    { num: 22, title: '央行、利率与汇率: 全球资金的水龙头', file: 'chapter-22.html', part: '第四部分 · 宏观环境如何改变资产' },
    { num: 23, title: '世界经济形势: 美元、黄金和全球资金流', file: 'chapter-23.html', part: '第四部分 · 宏观环境如何改变资产' },
    { num: 24, title: '危机四百年: 从郁金香到硅谷银行', file: 'chapter-24.html', part: '第四部分 · 宏观环境如何改变资产' },
    { num: 25, title: '影子银行: 银行不在银行里', file: 'chapter-25.html', part: '第四部分 · 宏观环境如何改变资产' },
    { num: 26, title: '保险: 把扛不住的灾难摊给几千人', file: 'chapter-26.html', part: '专题篇 · 个人金融的安全底盘' },
    { num: 27, title: '社保、养老金与家庭资产配置', file: 'chapter-27.html', part: '专题篇 · 个人金融的安全底盘' },
    { num: 28, title: '从问题到因子: 把投资判断变成可检验假设', file: 'chapter-28.html', part: '第五部分 · 量化研究如何产生可信结论' },
    { num: 29, title: '数据、标签和样本切分: 量化模型从哪里学', file: 'chapter-29.html', part: '第五部分 · 量化研究如何产生可信结论' },
    { num: 30, title: '回测: 在历史里排练,但不要把历史当答案', file: 'chapter-30.html', part: '第五部分 · 量化研究如何产生可信结论' },
    { num: 31, title: '量化里的机器学习: 模型不是越复杂越好', file: 'chapter-31.html', part: '第五部分 · 量化研究如何产生可信结论' },
    { num: 32, title: '从预测到仓位: 组合优化和风险模型', file: 'chapter-32.html', part: '第五部分 · 量化研究如何产生可信结论' },
    { num: 33, title: '交易执行和实盘系统: 策略如何真的下到市场里', file: 'chapter-33.html', part: '第五部分 · 量化研究如何产生可信结论' },
    { num: 34, title: '风险控制和组合监控: 什么时候该减仓、停用和复盘', file: 'chapter-34.html', part: '第五部分 · 量化研究如何产生可信结论' },
    { num: 35, title: '一个量化项目的代码骨架: 从数据到报告怎么组织', file: 'chapter-35.html', part: '第五部分 · 量化研究如何产生可信结论' },
    { num: 36, title: '识别回测幻觉: 错误清单与拆解案例', file: 'chapter-36.html', part: '第五部分 · 量化研究如何产生可信结论' },
    { num: 37, title: '审查量化研究: 从论文到回测报告', file: 'chapter-37.html', part: '第五部分 · 量化研究如何产生可信结论' },
    { num: 38, title: '量化策略全景: 指数增强、市场中性、CTA、套利和高频', file: 'chapter-38.html', part: '第六部分 · 策略如何变成产品' },
    { num: 39, title: '指数增强策略: 在基准附近争取一点点超额', file: 'chapter-39.html', part: '第六部分 · 策略如何变成产品' },
    { num: 40, title: '市场中性策略: 对冲大盘以后还剩什么', file: 'chapter-40.html', part: '第六部分 · 策略如何变成产品' },
    { num: 41, title: 'CTA 和期货趋势: 用规则交易商品、股指和利率', file: 'chapter-41.html', part: '第六部分 · 策略如何变成产品' },
    { num: 42, title: '套利和相对价值: 看起来确定的价差为什么也会亏', file: 'chapter-42.html', part: '第六部分 · 策略如何变成产品' },
    { num: 43, title: '高频交易和市场微观结构: 毫秒里的价格、排队和风险', file: 'chapter-43.html', part: '第六部分 · 策略如何变成产品' },
    { num: 44, title: '读懂量化产品: 净值、报告与合同', file: 'chapter-44.html', part: '第六部分 · 策略如何变成产品' },
    { num: 45, title: '监管、合规和伦理: 技术能力不能越过市场规则', file: 'chapter-45.html', part: '第六部分 · 策略如何变成产品' },
    { num: 46, title: '实战项目一: 从零做一个指数增强回测', file: 'chapter-46.html', part: '第七部分 · 把研究变成可运行项目' },
    { num: 47, title: '市场中性模拟盘: 把策略放进真实时间', file: 'chapter-47.html', part: '第七部分 · 把研究变成可运行项目' },
    { num: 48, title: '从模拟盘到小实盘: 上线前必须检查什么', file: 'chapter-48.html', part: '第七部分 · 把研究变成可运行项目' },
    { num: 49, title: '投资心理和资金管理: 活下来比一次赚快钱重要', file: 'chapter-49.html', part: '第七部分 · 把研究变成可运行项目' },
    { num: 50, title: '两条项目路径: 程序员怎样失败、怎样做稳', file: 'chapter-50.html', part: '第七部分 · 把研究变成可运行项目' },
    { num: 51, title: '量化行业与职业路线: 你适合站在哪个位置', file: 'chapter-51.html', part: '第八部分 · 职业、复盘与长期成长' },
    { num: 52, title: '长期学习路线: 从零到可展示的量化项目', file: 'chapter-52.html', part: '第八部分 · 职业、复盘与长期成长' },
    { num: 53, title: '全书复盘与自检: 从一条鱼到一个量化系统', file: 'chapter-53.html', part: '第八部分 · 职业、复盘与长期成长' },
    { num: 54, title: '结语: 你现在应该带走什么', file: 'chapter-54.html', part: '第八部分 · 职业、复盘与长期成长' },
    { num: 55, title: '概念复盘: 用人话重走金融与量化关键词', file: 'chapter-55.html', part: '附录 · 随时回来查' },
    { num: 56, title: '公式和指标速查: 别背公式,要知道它在问什么', file: 'chapter-56.html', part: '附录 · 随时回来查' },
    { num: 57, title: '最终检查表: 研究、交易和实盘前先读', file: 'chapter-57.html', part: '附录 · 随时回来查' }
  ];
  var BOOK_TITLE = "从金融零基础到量化研究者";
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
