/*
 * labs.js — 书里的可交互"实验台"(搬自《从神经元到大模型》的同名模式)。
 * 用法: 在章节里放 <div data-lab="xxx">, 本脚本自动往里塞结构并接好交互。
 * 支持: compound(复利/折现) | ic(因子IC散点) | cost(成本敏感) | hedge(Beta对冲)
 */
(function () {
  "use strict";

  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html !== undefined) e.innerHTML = html;
    return e;
  }
  function fmt(v, digits) {
    return Number(v).toLocaleString("zh-CN", { maximumFractionDigits: digits === undefined ? 2 : digits });
  }
  function slider(label, min, max, step, val, unit) {
    var wrap = el("div", "lab__ctl");
    var lab = el("label", "lab__lab");
    var span = el("span", "lab__val", fmt(val) + unit);
    lab.textContent = label;
    var input = document.createElement("input");
    input.type = "range";
    input.min = min; input.max = max; input.step = step; input.value = val;
    input.className = "lab__range";
    input.addEventListener("input", function () { span.textContent = fmt(this.value) + unit; });
    wrap.appendChild(lab); wrap.appendChild(span); wrap.appendChild(input);
    wrap._input = input;
    return wrap;
  }
  function svgWrap(w, h) {
    var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 " + w + " " + h);
    svg.setAttribute("class", "lab__chart");
    return svg;
  }
  function txt(x, y, s, color, anchor, size) {
    var t = document.createElementNS("http://www.w3.org/2000/svg", "text");
    t.setAttribute("x", x); t.setAttribute("y", y);
    t.setAttribute("text-anchor", anchor || "middle");
    t.setAttribute("fill", color || "#bcc9dd");
    t.setAttribute("font-size", size || 12);
    t.textContent = s;
    return t;
  }
  function rect(x, y, w, h, fill, rx) {
    var r = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    r.setAttribute("x", x); r.setAttribute("y", y);
    r.setAttribute("width", w); r.setAttribute("height", h);
    r.setAttribute("fill", fill); if (rx) r.setAttribute("rx", rx);
    return r;
  }
  function line(x1, y1, x2, y2, stroke, dash) {
    var l = document.createElementNS("http://www.w3.org/2000/svg", "line");
    l.setAttribute("x1", x1); l.setAttribute("y1", y1);
    l.setAttribute("x2", x2); l.setAttribute("y2", y2);
    l.setAttribute("stroke", stroke); l.setAttribute("stroke-width", 1.5);
    if (dash) l.setAttribute("stroke-dasharray", dash);
    return l;
  }
  function tip(text) { return el("p", "lab__tip", text); }

  /* =============== 1. 复利 / 折现(货币与利率主题)=============== */
  function buildCompound(root) {
    var cP = slider("本金 P", 10000, 1000000, 10000, 100000, " 元");
    var cR = slider("年利率 r", 1, 12, 0.5, 5, " %");
    var cN = slider("年数 n", 1, 30, 1, 10, " 年");
    var cI = slider("通胀 i", 0, 6, 0.5, 2, " %");
    var out = el("div", "lab__out");
    var chart = svgWrap(600, 230);
    root.appendChild(el("div", "lab__title", "复利计算器:今天的钱,值明天的多少钱"));
    root.appendChild(cP); root.appendChild(cR); root.appendChild(cN); root.appendChild(cI);
    root.appendChild(chart); root.appendChild(out);
    root.appendChild(tip("把本金、利率、年数换成你自己的数;通胀滑上去,就能看到“名义变多、购买力缩水”这个书里的核心场景。"));

    function render() {
      var P = +cP._input.value, r = +cR._input.value / 100;
      var n = +cN._input.value, inf = +cI._input.value / 100;
      var F = P * Math.pow(1 + r, n);                       // 终值
      var real = P * Math.pow((1 + r) / (1 + inf), n);      // 购买力
      var PV = F / Math.pow(1 + r, n);                      // n 年后 F 的现值(=P,展示公式)
      // 曲线: 每年末值
      while (chart.firstChild) chart.removeChild(chart.firstChild);
      var maxV = F, minV = P;
      var pad = 30, W = 600, H = 230;
      for (var t = 0; t <= n; t++) {
        var v = P * Math.pow(1 + r, t);
        var rv = P * Math.pow((1 + r) / (1 + inf), t);
        var x = pad + (W - 2 * pad) * t / n;
        chart.appendChild(rect(x - 3, H - 24 - (H - 50) * (v - minV) / (maxV - minV + 1), 6, (H - 50) * (v - minV) / (maxV - minV + 1) || 2, "rgba(240,201,106,0.75)", 2));
        if (t === 0 || t === n || t === Math.floor(n / 2)) {
          chart.appendChild(txt(x, H - 8, "第" + t + "年", "#8b9cb4", "middle", 11));
        }
        if (t === n) {
          chart.appendChild(txt(x - 4, H - 34 - (H - 50) * (maxV - minV) / (maxV - minV + 1), "名义 " + fmt(F, 0), "#ffd97a", "end", 12));
          chart.appendChild(txt(x - 4, H - 20 - (H - 50) * (real - minV) / (maxV - minV + 1), "购买力 " + fmt(real, 0), "#7aa7f0", "end", 12));
        }
      }
      out.innerHTML =
        "<div class='lab__row'><span>终值 P·(1+r)ⁿ</span><strong>" + fmt(F, 0) + " 元</strong></div>" +
        "<div class='lab__row'><span>扣通胀后,购买力只剩</span><strong class='lab__accent'>" + fmt(real, 0) + " 元</strong></div>" +
        "<div class='lab__row lab__hint'><span>反过来: n 年后的 " + fmt(F, 0) + " 元,今天值 P = " + fmt(PV, 0) + " 元 (折现)</span></div>";
    }
    [cP, cR, cN, cI].forEach(function (c) { c._input.addEventListener("input", render); });
    render();
  }

  /* =============== 2. IC 因子相关(因子研究主题)=============== */
  function buildIC(root) {
    var cC = slider("相关性强度 ρ", -0.5, 0.8, 0.05, 0.3, "");
    var out = el("div", "lab__out");
    var chart = svgWrap(600, 300);
    root.appendChild(el("div", "lab__title", "IC 散点:因子分数和未来收益,到底走不走到一起"));
    root.appendChild(cC); root.appendChild(chart); root.appendChild(out);
    root.appendChild(tip("每一点是一只股票:横坐标是因子分,纵坐标是下一个月收益。把 ρ 从 0 往上推,看散点从“一团雾”变成“一条斜线”——这就是 IC 在量化的意义。"));

    // 固定随机种子,保证每次刷新布局一致
    var seed = 42;
    function rnd() { seed = (seed * 9301 + 49297) % 233280; return seed / 233280; }
    function render() {
      seed = 42;
      var rho = +cC._input.value;
      var N = 120, pts = [];
      for (var i = 0; i < N; i++) {
        // 建相关 pair: y = rho * x + sqrt(1-rho^2) * z
        var x = 2 * rnd() - 1;
        var z = 2 * rnd() - 1;
        var y = rho * x + Math.sqrt(Math.max(0, 1 - rho * rho)) * z;
        pts.push([x, y]);
      }
      while (chart.firstChild) chart.removeChild(chart.firstChild);
      var W = 600, H = 300, pad = 40;
      chart.appendChild(line(pad, H / 2, W - pad, H / 2, "#46587a"));
      chart.appendChild(line(W / 2, 20, W / 2, H - 24, "#46587a"));
      chart.appendChild(txt(W - pad, H / 2 - 8, "下月收益 →", "#8b9cb4", "end", 11));
      chart.appendChild(txt(W / 2 + 10, 22, "因子分 →", "#8b9cb4", "start", 11));
      pts.forEach(function (p) {
        var cx = W / 2 + p[0] * (W / 2 - pad - 4);
        var cy = H / 2 - p[1] * (H / 2 - 40);
        var dot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        dot.setAttribute("cx", cx); dot.setAttribute("cy", cy);
        dot.setAttribute("r", 3.4);
        dot.setAttribute("fill", p[1] > 0 ? "rgba(240,201,106,0.65)" : "rgba(122,167,240,0.65)");
        chart.appendChild(dot);
      });
      var ic = rho;
      out.innerHTML =
        "<div class='lab__row'><span>IC ≈ ρ = </span><strong class='" + (ic > 0.05 ? "lab__accent" : "") + "'>" + ic.toFixed(2) + "</strong></div>" +
        "<div class='lab__row lab__hint'><span>" +
        (ic > 0.3 ? "这么强的 IC,真实市场基本只在教科书里存在" :
         ic > 0.05 ? "已经比多数实盘因子强了——能稳定站 0.03-0.05 就可拿去用" :
         ic > -0.05 ? "跟纯噪声没啥区别,换一个因子吧" :
         "负相关……把排序倒过来用,就变成了正因子") + "</span></div>";
    }
    cC._input.addEventListener("input", render);
    render();
  }

  /* =============== 3. 成本敏感(指数增强实战)=============== */
  function buildCost(root) {
    var cG = slider("年化毛收益 g", 5, 30, 1, 15, " %");
    var cT = slider("双边换手倍数", 1, 30, 1, 10, " 倍/年");
    var cC = slider("双边成本率 c", 0.02, 0.3, 0.01, 0.13, " %");
    var out = el("div", "lab__out");
    var chart = svgWrap(600, 220);
    root.appendChild(el("div", "lab__title", "成本敏感性:同样的策略,成本翻几倍,你还赚钱吗"));
    root.appendChild(cG); root.appendChild(cT); root.appendChild(cC);
    root.appendChild(chart); root.appendChild(out);
    root.appendChild(tip("净收益 ≈ 毛收益 - 换手×成本。把换手推到 20 倍,成本再推到 0.2%,看金条还剩多少——这是对冲/高频/量化回测都要写的敏感性测试,书上叫“照妖镜”。"));

    function render() {
      var g = +cG._input.value, t = +cT._input.value, c = +cC._input.value;
      var drag = t * c;      // 简化: 每年拖拽损失 = 双边换手倍数 × 双边成本率
      var net = g - drag;
      while (chart.firstChild) chart.removeChild(chart.firstChild);
      var W = 600, H = 220, pad = 40, maxV = Math.max(g, 30);
      var gh = (H - 60) * g / maxV, nh = (H - 60) * Math.max(net, 0) / maxV;
      chart.appendChild(rect(pad + 30, H - 30 - gh, 130, gh, "rgba(240,201,106,0.75)", 8));
      chart.appendChild(txt(pad + 95, H - 34 - gh, "毛收益 " + g + "%", "#ffd97a", "middle", 12));
      chart.appendChild(txt(pad + 95, H - 8, "策略能赚", "#8b9cb4", "middle", 11));
      chart.appendChild(rect(pad + 230, H - 30 - nh, 130, nh, net > 0 ? "rgba(122,167,240,0.75)" : "rgba(238,136,119,0.75)", 8));
      chart.appendChild(txt(pad + 295, H - 34 - nh, (net > 0 ? "净收益 " + net.toFixed(1) + "%" : "已亏: " + net.toFixed(1) + "%"), net > 0 ? "#a8c6ff" : "#ffb4b4", "middle", 12));
      chart.appendChild(txt(pad + 295, H - 8, "到手的钱", "#8b9cb4", "middle", 11));
      // 被成本吃掉那部分
      chart.appendChild(rect(pad + 430, H - 30 - (H - 60) * Math.max(drag, 0) / maxV, 110, (H - 60) * Math.max(drag, 0) / maxV, "rgba(238,136,119,0.5)", 8));
      chart.appendChild(txt(pad + 485, H - 34 - (H - 60) * Math.max(drag, 0) / maxV, "被吃 " + drag.toFixed(1) + "%", "#ffb4b4", "middle", 11));
      chart.appendChild(txt(pad + 485, H - 8, "成本吞掉", "#8b9cb4", "middle", 11));
      out.innerHTML =
        "<div class='lab__row'><span>拖拽 = 换手 × 成本 = " + t + " × " + c + "% = </span><strong>" + drag.toFixed(2) + "%</strong></div>" +
        "<div class='lab__row lab__hint'><span>" +
        (net <= 0 ? "成本把整段策略吞了——回测再美,落地也得缩水甚至反亏" :
         net / g < 0.5 ? "一大半利润交给市场了——不是“赚到”,是“替市场打工”" :
         net / g < 0.8 ? "扣掉三成多,可以接受但别得意:这就是书里要把成本× 0/1/2/3 报告的原因" :
         "这条策略对成本不敏感,继续持有;可以顺手切一下换手再跑一次") + "</span></div>";
    }
    [cG, cT, cC].forEach(function (c) { c._input.addEventListener("input", render); });
    render();
  }

  /* =============== 4. Beta 对冲(市场中性模拟盘)=============== */
  function buildHedge(root) {
    var cB = slider("多头组合 Beta", 0.5, 2.0, 0.1, 1.0, "");
    var cH = slider("对冲比例 h(名义/多头)", 0, 1.2, 0.1, 1.0, "");
    var out = el("div", "lab__out");
    var chart = svgWrap(600, 240);
    root.appendChild(el("div", "lab__title", "Beta 对冲:组合还差多少暴露在大盘上"));
    root.appendChild(cB); root.appendChild(cH);
    root.appendChild(chart); root.appendChild(out);
    root.appendChild(tip("净暴露 = Beta × (1 - h)。把对冲比例推到 1,看组合波动被压成什么样;再推过头(h &gt; 1)看反转做空。书上说的“对冲比例是道算术题”。"));

    function render() {
      var b = +cB._input.value, h = +cH._input.value;
      var netBeta = b * (1 - h);                 // 净 Beta
      var netExp = netBeta;                      // 净暴露(名义)
      // 波动率示意: 市场 16% 年化,净 Sigma 趋势 = |netBeta| × 16%(粗口径,跳Special性另想)
      var sig = Math.abs(netBeta) * 16;
      while (chart.firstChild) chart.removeChild(chart.firstChild);
      var W = 600, H = 240, pad = 40;
      // X 轴: h 从 0 到 1.2 的波动率曲线(当前 b 下)
      chart.appendChild(line(pad, H - 30, W - pad, H - 30, "#46587a"));
      chart.appendChild(line(pad, 20, pad, H - 30, "#46587a"));
      chart.appendChild(txt(W - pad + 4, H - 22, "h →", "#8b9cb4", "start", 11));
      chart.appendChild(txt(pad - 4, 22, "σ", "#8b9cb4", "end", 11));
      var maxSig = 40;
      var pts = [];
      for (var i = 0; i <= 60; i++) {
        var hh = 0.02 * i;
        var sg = Math.abs(b * (1 - hh)) * 16;
        var px = pad + (W - 2 * pad) * hh / 1.2;
        var py = H - 30 - (H - 56) * sg / maxSig;
        pts.push(px + "," + py);
      }
      var pl = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
      pl.setAttribute("points", pts.join(" "));
      pl.setAttribute("fill", "none"); pl.setAttribute("stroke", "#7aa7f0"); pl.setAttribute("stroke-width", 2);
      chart.appendChild(pl);
      // 当前点位
      var cx = pad + (W - 2 * pad) * h / 1.2;
      var cy = H - 30 - (H - 56) * Math.min(sig, maxSig) / maxSig;
      var dot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      dot.setAttribute("cx", cx); dot.setAttribute("cy", cy); dot.setAttribute("r", 7);
      dot.setAttribute("fill", "#f0c96a"); dot.setAttribute("stroke", "#101420"); dot.setAttribute("stroke-width", 2);
      chart.appendChild(dot);
      chart.appendChild(txt(cx, cy - 14, "当前 " + sig.toFixed(1) + "%", "#ffd97a", "middle", 12));
      // h=1 位置竖虚线 (全对冲)
      var x1 = pad + (W - 2 * pad) * 1 / 1.2;
      chart.appendChild(line(x1, 20, x1, H - 30, "rgba(240,201,106,0.35)", "4 4"));
      chart.appendChild(txt(x1, H - 8, "h=1 全对冲", "#8b9cb4", "middle", 11));
      out.innerHTML =
        "<div class='lab__row'><span>净暴露 Beta×(1-h) = </span><strong class='" + (Math.abs(netExp) < 0.15 ? "lab__accent" : "") + "'>" + netExp.toFixed(2) + "</strong></div>" +
        "<div class='lab__row lab__hint'><span>" +
        (Math.abs(netExp) < 0.1 ? "贴得很好——基本不随大盘动,吃的是选股那点 alpha" :
         Math.abs(netExp) < 0.3 ? "可以了,残余这点暴露实盘能接受;再追 0 用保证金倒逼反而亏" :
         netExp > 0 ? "还是净多头,大盘一跌还是跟着肉痛——加对冲或降仓位" :
         "反手拿空了,行情一涨就踩踏——对冲过头和不对冲一样危险") + "</span></div>";
    }
    [cB, cH].forEach(function (c) { c._input.addEventListener("input", render); });
    render();
  }

  var builders = {
    "compound": buildCompound,
    "ic": buildIC,
    "cost": buildCost,
    "hedge": buildHedge
  };

  function boot() {
    document.querySelectorAll("[data-lab]").forEach(function (node) {
      if (node._built) return;
      var name = node.getAttribute("data-lab");
      var factory = builders[name];
      if (!factory) return;
      node._built = true;
      node.classList.add("lab");
      var head = el("div", "lab__head", "<span class='lab__head-tag'>◈ 实验台</span><span class='lab__head-name'>" + name + "</span>");
      node.appendChild(head);
      factory(node);
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
