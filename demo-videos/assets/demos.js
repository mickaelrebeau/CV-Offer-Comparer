/* Démos Talento — construction des pages (UI réelle de l'app) et des trois scénarios.
   Tout est déterministe : aucun aléa, aucune horloge, aucun réseau. Les positions sont
   mesurées une seule fois à la construction (caméra à l'identité), puis figées. */
(function () {
  "use strict";

  var W = 1920;
  var H = 1080;
  var CX = W / 2;
  var CY = H / 2;

  // ---------------------------------------------------------------- DOM
  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text != null) node.textContent = text;
    return node;
  }
  function add(parent) {
    for (var i = 1; i < arguments.length; i += 1) if (arguments[i]) parent.appendChild(arguments[i]);
    return parent;
  }
  function put(parent, child) {
    parent.appendChild(child);
    return child;
  }
  function fmt(template, params) {
    return template.replace(/\{(\w+)\}/g, function (_, k) { return params[k]; });
  }
  var ICON = {
    swap: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3 4 7l4 4"/><path d="M4 7h16"/><path d="m16 21 4-4-4-4"/><path d="M20 17H4"/></svg>',
    spin: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 12a9 9 0 1 1-6.2-8.6"/></svg>',
    msg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
    play: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 4v16l13-8z"/></svg>',
    pen: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/></svg>',
    copy: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>',
    check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>',
    down: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m7 10 5 5 5-5"/><path d="M12 15V3"/></svg>',
    arrowL: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5"/><path d="m12 19-7-7 7-7"/></svg>',
    arrowR: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>',
    circleCheck: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>',
    bubble: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
    pointer: '<svg viewBox="0 0 24 24"><path d="M3 2.8 20.6 14 12.8 15.5 9 22 3 2.8Z" fill="#232323" stroke="#f1eee7" stroke-width="1.5" stroke-linejoin="round"/></svg>',
  };
  function btn(label, icon, cls) {
    var b = el("div", "btn" + (cls ? " " + cls : ""));
    b.innerHTML = (icon ? ICON[icon] : "") + "<span></span>";
    b.querySelector("span").textContent = label;
    return b;
  }

  function appWindow(C, activeTab) {
    var U = C.ui;
    var win = el("div", "win");
    var nav = el("div", "app-nav");
    var brand = el("div", "brand");
    brand.innerHTML = '<img src="assets/logo.png" alt=""><span>Talento</span>';
    var tabs = el("div", "tabs");
    [["dash", U["nav.dashboard"]], ["compare", U["nav.compare"]], ["sim", U["nav.simulator"]], ["letter", U["nav.coverLetter"]]].forEach(function (t) {
      add(tabs, el("span", t[0] === activeTab ? "on" : "", t[1]));
    });
    var right = el("div", "right");
    var lang = el("span", "lang");
    lang.innerHTML = C.lang === "fr" ? "<b>fr</b>en" : "fr<b style=\"margin:0 0 0 6px\">en</b>";
    add(right, el("span", "", C.email), el("span", "pill", U["nav.profile"]), el("span", "signout", U["nav.signOut"]), lang);
    add(nav, brand, tabs, right);
    var page = el("div", "page");
    add(win, nav, page);
    return { win: win, page: page };
  }

  function header(page, U, prefix) {
    var nodes = [el("div", "kicker", U[prefix + ".label"]), el("div", "page-title", U[prefix + ".title"]), el("div", "page-desc", U[prefix + ".description"])];
    // Chevauchement uniquement projeté pendant l'entrée / la sortie 3D de la fenêtre
    nodes.forEach(function (n) { n.setAttribute("data-layout-allow-overlap", ""); add(page, n); });
  }

  function textPanel(title, lines, rightSeg) {
    var p = el("div", "panel");
    var h = el("div", "panel-h");
    add(h, el("span", "", title));
    if (rightSeg) {
      var seg = el("div", "seg");
      add(seg, el("span", "", rightSeg[0]), el("span", "on", rightSeg[1]));
      add(h, seg);
    }
    var b = el("div", "panel-b");
    var ta = el("div", "textarea");
    var ls = lines.map(function (l) { return add(ta, el("p", "line", l)).lastChild; });
    add(b, ta);
    add(p, h, b);
    return { panel: p, lines: ls, box: ta };
  }

  function progressBlock() {
    var wrap = el("div", "progress");
    var top = el("div", "progress-top");
    var status = el("div", "status");
    var pct = el("span", "", "0%");
    add(top, status, pct);
    var track = el("div", "track");
    var fill = el("i");
    add(track, fill);
    add(wrap, top, track);
    return { wrap: wrap, status: status, pct: pct, fill: fill };
  }

  function statusLines(statusEl, texts) {
    return texts.map(function (t) { return add(statusEl, el("span", "", t)).lastChild; });
  }

  // ------------------------------------------------------------ mesures
  var rootRect = null;
  function rect(node) {
    var r = node.getBoundingClientRect();
    return { x: r.left - rootRect.left, y: r.top - rootRect.top, w: r.width, h: r.height, cx: r.left - rootRect.left + r.width / 2, cy: r.top - rootRect.top + r.height / 2 };
  }

  // ------------------------------------------------------------ caméra
  function Camera(tl, outer, inner) {
    this.tl = tl;
    this.outer = outer;
    this.inner = inner;
  }
  // Place le point monde p à la position écran (sx, sy) avec l'échelle s (wrappers imbriqués : T = (screen - centre)/s - offset)
  Camera.prototype.solve = function (p, s, sx, sy) {
    return { s: s, x: (sx - CX) / s - (p.x - CX), y: (sy - CY) / s - (p.y - CY) };
  };
  Camera.prototype.set = function (t, p, s, sx, sy) {
    var v = this.solve(p, s, sx == null ? CX : sx, sy == null ? CY : sy);
    this.tl.set(this.outer, { scale: v.s }, t);
    this.tl.set(this.inner, { x: v.x, y: v.y }, t);
  };
  Camera.prototype.to = function (t, dur, p, s, ease, sx, sy) {
    var v = this.solve(p, s, sx == null ? CX : sx, sy == null ? CY : sy);
    this.tl.to(this.outer, { scale: v.s, duration: dur, ease: ease || "power2.inOut" }, t);
    this.tl.to(this.inner, { x: v.x, y: v.y, duration: dur, ease: ease || "power2.inOut" }, t);
  };
  // Zoom-through : on traverse `from`, on atterrit sur `to` (transition principale du film)
  Camera.prototype.zoomThrough = function (T, from, fromS, to, toS, toSx, toSy) {
    var tl = this.tl;
    this.to(T, 0.36, from, fromS * 3.4, "power4.in");
    tl.to(this.outer, { filter: "blur(14px)", duration: 0.3, ease: "power3.in" }, T + 0.06);
    this.set(T + 0.36, to, toS * 2.6, toSx, toSy);
    this.to(T + 0.36, 0.55, to, toS, "power4.out", toSx, toSy);
    tl.to(this.outer, { filter: "blur(0px)", duration: 0.45, ease: "power3.out" }, T + 0.36);
  };

  // ------------------------------------------------------------ curseur
  function makeCursor(world) {
    var c = el("div", "cursor");
    c.innerHTML = ICON.pointer;
    var ring = el("div", "ring");
    add(world, ring, c);
    return { c: c, ring: ring, tipX: 3.75, tipY: 3.5 };
  }
  function cursorTo(tl, cur, t, dur, p, ease) {
    tl.to(cur.c, { x: p.x - cur.tipX, y: p.y - cur.tipY, duration: dur, ease: ease || "power3.out" }, t);
  }
  function cursorSet(tl, cur, t, p) {
    tl.set(cur.c, { x: p.x - cur.tipX, y: p.y - cur.tipY }, t);
  }
  function click(tl, cur, t, p, target) {
    tl.to(cur.c, { scale: 0.84, duration: 0.08, ease: "power2.in", yoyo: true, repeat: 1, transformOrigin: "12% 12%" }, t);
    if (target) tl.to(target, { scale: 0.95, duration: 0.08, ease: "power2.in", yoyo: true, repeat: 1 }, t);
    tl.set(cur.ring, { left: p.x, top: p.y }, t);
    tl.fromTo(cur.ring, { scale: 0.3, opacity: 0.9 }, { scale: 2.6, opacity: 0, duration: 0.6, ease: "power2.out", immediateRender: false }, t + 0.02);
  }

  // ------------------------------------------------------------ callouts
  // Étiquette + filet + point, accrochée à un point du monde ; side = côté où se trouve l'étiquette
  function callout(world, text, anchor, side, opts) {
    opts = opts || {};
    var fs = opts.fontSize || 13;
    var len = opts.line || 56;
    var dotSize = Math.round(fs * 0.95);
    var c = el("div", "callout" + (opts.invert ? " inv" : ""));
    var lbl = el("span", "lbl", text);
    lbl.style.fontSize = fs + "px";
    lbl.style.padding = Math.round(fs * 0.62) + "px " + Math.round(fs * 0.95) + "px";
    var ln = el("span", "ln");
    ln.style.width = len + "px";
    ln.style.height = Math.max(2, Math.round(fs / 7)) + "px";
    var dot = el("span", "dot");
    dot.style.width = dot.style.height = dotSize + "px";
    dot.style.borderWidth = Math.max(2, Math.round(fs / 5)) + "px";
    if (side === "left") { add(c, lbl, ln, dot); ln.style.setProperty("--from", "100%"); }
    else { add(c, dot, ln, lbl); }
    c.style.opacity = "0";
    add(world, c);
    var r = c.getBoundingClientRect();
    var left = side === "left" ? anchor.x - r.width + dotSize / 2 : anchor.x - dotSize / 2;
    c.style.left = left + "px";
    c.style.top = anchor.y - r.height / 2 + "px";
    return { c: c, lbl: lbl, ln: ln, dot: dot, side: side };
  }
  function showCallout(tl, co, t, hideAt) {
    var dx = co.side === "left" ? 24 : -24;
    tl.set(co.c, { opacity: 1 }, t);
    tl.fromTo(co.dot, { scale: 0 }, { scale: 1, duration: 0.22, ease: "power3.out", immediateRender: false }, t);
    tl.fromTo(co.ln, { scaleX: 0 }, { scaleX: 1, duration: 0.28, ease: "power3.out", immediateRender: false }, t + 0.08);
    tl.fromTo(co.lbl, { opacity: 0, x: dx }, { opacity: 1, x: 0, duration: 0.34, ease: "power3.out", immediateRender: false }, t + 0.16);
    if (hideAt != null) tl.to(co.c, { opacity: 0, duration: 0.22, ease: "power1.in" }, hideAt);
  }

  // ------------------------------------------------------------ texte
  function wordsInto(container, text) {
    return text.split(/\s+/).filter(Boolean).map(function (w) {
      var span = add(container, el("span", "w", w)).lastChild;
      span.setAttribute("data-layout-allow-overlap", ""); // l'accroche sort pendant que la fenêtre entre
      return span;
    });
  }
  // Cascade d'arrivée (waterfall-entry) : opacité binaire, mots qui entrent par la droite
  function waterfall(tl, words, t0, opts) {
    opts = opts || {};
    var t = t0;
    words.forEach(function (w, i) {
      var heavy = w.textContent.length > 6;
      var dur = heavy ? 0.26 : 0.2;
      tl.set(w, { opacity: 1, x: opts.dx || (heavy ? 110 : 80) }, t);
      tl.to(w, { x: 0, duration: dur, ease: "power4.out" }, t);
      t += (opts.step || 0.1) + (i === words.length - 2 ? 0.06 : 0);
    });
    return t;
  }
  function typeText(tl, node, text, t, dur) {
    var st = { n: 0 };
    node.textContent = "";
    tl.to(st, { n: text.length, duration: dur, ease: "none", onUpdate: function () { node.textContent = text.slice(0, Math.round(st.n)); } }, t);
  }
  function countTo(tl, node, t, dur, to, format) {
    var st = { v: 0 };
    node.textContent = format(0);
    tl.to(st, { v: to, duration: dur, ease: "power2.out", onUpdate: function () { node.textContent = format(st.v); } }, t);
  }
  function arrive(tl, nodes, t, step, dy) {
    nodes.forEach(function (n, i) {
      tl.fromTo(n, { opacity: 0, y: dy == null ? 10 : dy }, { opacity: 1, y: 0, duration: 0.32, ease: "power3.out", immediateRender: true }, t + i * step);
    });
  }
  function swapText(tl, nodes, times) {
    nodes.forEach(function (n, i) {
      tl.set(n, { opacity: i === 0 ? 1 : 0 }, 0);
      if (i > 0) { tl.set(nodes[i - 1], { opacity: 0 }, times[i]); tl.set(n, { opacity: 1 }, times[i]); }
    });
  }

  // ------------------------------------------------------------ scène commune
  function buildShell(root, C, demo) {
    var stage = put(root, el("div", "stage"));
    var grid = put(stage, el("div", "stage-grid"));
    var vign = put(stage, el("div", "stage-vignette"));
    var ghost = put(stage, el("div", "stage-ghost", { analyse: "01", entretien: "02", lettre: "03" }[demo]));
    ghost.setAttribute("data-layout-ignore", ""); // chiffre fantôme décoratif, en fond perdu
    void vign;
    var hook = put(root, el("div", "hook"));
    var outer = put(root, el("div", "cam-outer"));
    var inner = put(outer, el("div", "cam-inner"));
    var world = put(inner, el("div", "world"));
    var win3d = put(world, el("div", "win3d"));
    var sig = put(root, el("div", "sig"));
    return { stage: stage, grid: grid, ghost: ghost, hook: hook, outer: outer, inner: inner, world: world, win3d: win3d, sig: sig };
  }

  function buildSignature(S, C, ctaLabel) {
    var wm = put(S.sig, el("div", "wm"));
    wm.innerHTML = '<img src="assets/logo.png" alt=""><span>Talento</span>';
    var slogan = put(S.sig, el("div", "slogan"));
    var words = wordsInto(slogan, C.ui["landing.footer.slogan"]);
    var cta = put(S.sig, el("div", "btn cta"));
    cta.textContent = ctaLabel;
    var cur = el("div", "sig-cursor");
    cur.innerHTML = ICON.pointer;
    var ring = el("div", "ring");
    add(S.sig, ring, cur);
    return { wm: wm, words: words, cta: cta, cur: cur, ring: ring };
  }

  // Ouverture (accroche) + 3D reveal de la fenêtre + signature + boucle : communs aux 3 vidéos
  function openAndClose(tl, S, G, hookWords, cam, base) {
    // Plateau : la grille avance d'exactement une case en 18 s (boucle parfaite), le chiffre respire
    tl.fromTo(S.grid, { x: 0, y: 0 }, { x: -96, y: -96, duration: 18, ease: "none" }, 0);
    tl.fromTo(S.ghost, { scale: 1, x: 0 }, { scale: 1.04, x: -30, duration: 9, ease: "sine.inOut", yoyo: true, repeat: 1 }, 0);

    // Accroche
    waterfall(tl, hookWords, 0.1, { step: 0.1 });
    // Transition : l'accroche recule pendant que la fenêtre entre en 3D (accent « 3D reveal »)
    tl.to(hookWords, { opacity: 0, x: -140, filter: "blur(6px)", duration: 0.45, ease: "power3.in", stagger: 0.02 }, 2.2);
    tl.fromTo(S.win3d, { opacity: 0, rotationY: -34, rotationX: 9, x: 760, z: -200, transformPerspective: 2000 },
      { opacity: 1, rotationY: 0, rotationX: 0, x: 0, z: 0, duration: 0.9, ease: "expo.out" }, 2.3);
    cam.set(0, base.p, base.s, base.sx, base.sy);

    // Signature : la fenêtre part à gauche en 3D, la marque se pose
    var T = 14.5;
    tl.to(S.outer, { x: -1500, rotationY: 38, scale: "*=0.55", opacity: 0, transformPerspective: 2400, duration: 0.85, ease: "power3.in" }, T);
    tl.fromTo(G.wm, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }, T + 0.45);
    waterfall(tl, G.words, T + 0.6, { step: 0.12, dx: 120 });
    tl.fromTo(G.cta, { opacity: 0, scale: 0.86 }, { opacity: 1, scale: 1, duration: 0.45, ease: "power3.out" }, T + 1.05);
    var ctaR = rect(G.cta);
    var target = { x: ctaR.cx + 40, y: ctaR.cy + 6 };
    tl.set(G.cur, { x: 1500, y: 1150 }, 0);
    tl.to(G.cur, { x: target.x - 6, y: target.y - 5, duration: 0.7, ease: "power3.out" }, T + 1.35);
    tl.to(G.cur, { scale: 0.84, duration: 0.08, ease: "power2.in", yoyo: true, repeat: 1, transformOrigin: "12% 12%" }, T + 2.1);
    tl.to(G.cta, { scale: 0.95, duration: 0.08, ease: "power2.in", yoyo: true, repeat: 1 }, T + 2.1);
    tl.set(G.ring, { left: target.x, top: target.y }, T + 2.1);
    tl.fromTo(G.ring, { scale: 0.3, opacity: 0.9 }, { scale: 2.4, opacity: 0, duration: 0.6, ease: "power2.out", immediateRender: false }, T + 2.12);
    // Boucle : fondu flouté vers l'état exact de t = 0 (plateau seul) — accent « blur crossfade »
    tl.to(S.sig, { opacity: 0, filter: "blur(16px)", scale: 1.04, duration: 0.7, ease: "sine.inOut" }, 17.2);
  }

  // ============================================================ ANALYSE
  function buildAnalyse(S, C) {
    var U = C.ui;
    var A = appWindow(C, "compare");
    add(S.win3d, A.win);
    header(A.page, U, "compare");
    var two = put(A.page, el("div", "two"));
    var offer = textPanel(U["cvInput.offerHeader"], C.inputs.offer.split("\n"));
    var cv = textPanel(U["cvInput.cvHeader"], C.inputs.cv.split("\n"), [U["common.pdf"], U["common.text"]]);
    add(two, offer.panel, cv.panel);
    var row = put(A.page, el("div", "center-row"));
    var prog = progressBlock();
    add(row, prog.wrap);
    var st = statusLines(prog.status, [C.status.analysisStart, C.status.analysisGemini, C.status.analysisStreaming]);
    var run = put(row, btn(U["comparison.run"], "swap"));
    var spin = put(run, el("span", "spinwrap"));
    spin.innerHTML = ICON.spin;
    spin.style.cssText = "position:absolute;left:24px;display:flex;opacity:0";
    run.style.position = "relative";

    var results = put(A.page, el("div", "results"));
    results.style.marginTop = "40px";
    var stats = put(results, el("div", "stats"));
    var pctFmt = new Intl.NumberFormat(C.lang === "fr" ? "fr-FR" : "en-US", { style: "percent", maximumFractionDigits: 0 });
    var statDefs = [["comparison.stats.matches", 5, "ok"], ["comparison.stats.missing", 3, "ko"], ["comparison.stats.unclear", 2, "mid"], ["comparison.stats.score", 0.5, ""]];
    var statVals = statDefs.map(function (d) {
      var s = put(stats, el("div", "stat"));
      add(s, el("div", "k", U[d[0]]));
      return add(s, el("div", "v " + d[2], "0")).lastChild;
    });
    var dark = put(results, el("div", "dark"));
    dark.style.marginTop = "32px";
    var din = put(dark, el("div", "dark-in"));
    add(din, add(el("div", "dark-h"), el("span", "", U["comparison.report"])));
    var rows = put(din, el("div", "rows"));
    var statusLabel = { match: U["comparison.status.match"], unclear: U["comparison.status.partial"], missing: U["comparison.status.missing"] };
    var statusCls = { match: "ok", unclear: "mid", missing: "ko" };
    var rowEls = C.items.map(function (it) {
      var r = put(rows, el("div", "row"));
      var left = put(r, el("div"));
      left.style.flex = "1";
      var meta = put(left, el("div", "meta"));
      add(meta, el("span", "", it[0]), el("span", "", fmt(U["comparison.confidence"], { value: pctFmt.format(it[1] / 100) })));
      add(left, el("div", "t", it[2]));
      if (it[3]) {
        var x = put(left, el("div", "x"));
        add(x, el("b", "", U["comparison.cvExcerpt"] + " "), document.createTextNode(it[3]));
      }
      var cp = null;
      if (it[5]) {
        var sg = put(left, el("div", "sugg"));
        add(sg, el("div", "k", U["comparison.rewrites"]));
        var l = put(sg, el("div", "l"));
        add(l, el("span", "", it[5]));
        cp = add(l, el("span", "cp")).lastChild;
        add(cp, el("span", "", U["common.copy"]));
      }
      var pill = add(r, el("div", "s " + statusCls[it[4]], statusLabel[it[4]])).lastChild;
      return { row: r, pill: pill, copy: cp };
    });
    return { A: A, offer: offer, cv: cv, run: run, spin: spin, prog: prog, st: st, results: results, statVals: statVals, stats: stats, dark: dark, rows: rowEls, pctFmt: pctFmt };
  }

  function timelineAnalyse(tl, S, C, V, cam, cur, G) {
    var U = C.ui;
    var features = U["dashboard.modules.compare.features"];
    var panels = rect(V.offer.panel.parentNode);
    var runR = rect(V.run);
    var statsR = rect(V.stats);
    var darkR = rect(V.dark);
    var target = V.rows[8];
    var targetR = rect(target.row);
    var copyR = rect(target.copy);

    var offerR = rect(V.offer.panel);
    var base = { p: { x: panels.cx, y: panels.y + 40 }, s: 1.12 };
    var coExtract = callout(S.world, features[1], { x: offerR.x + offerR.w - 18, y: offerR.y + 20 }, "left", { fontSize: 11, line: 26 });
    var coDiag = callout(S.world, features[0], { x: darkR.x + darkR.w - 30, y: darkR.y + 26 }, "left", { fontSize: 11, line: 40, invert: true });
    var rewR = rect(target.copy.parentNode);
    var coRew = callout(S.world, features[2], { x: rewR.x + 420, y: rewR.y - 26 }, "right", { fontSize: 10, line: 22, invert: true });

    openAndClose(tl, S, G, wordsInto(S.hook, U["landing.hero.title"]), cam, base);

    // Saisie : l'offre puis le CV se remplissent
    arrive(tl, V.offer.lines, 2.6, 0.08, 6);
    arrive(tl, V.cv.lines, 3.05, 0.08, 6);
    showCallout(tl, coExtract, 3.0, 4.8);
    cam.to(3.3, 1.8, { x: runR.cx, y: runR.cy - 80 }, 1.55, "power2.inOut");
    cursorSet(tl, cur, 0, { x: runR.cx + 520, y: runR.cy + 260 });
    cursorTo(tl, cur, 3.6, 1.0, { x: runR.cx + 60, y: runR.cy + 6 });

    // La machine travaille
    click(tl, cur, 4.8, { x: runR.cx + 60, y: runR.cy + 6 }, V.run);
    tl.set(V.run, { opacity: 0.5 }, 4.9);
    tl.set(V.run.querySelector("svg"), { opacity: 0 }, 4.9);
    tl.set(V.spin, { opacity: 1 }, 4.9);
    tl.fromTo(V.spin, { rotation: 0 }, { rotation: 720, duration: 1.8, ease: "none" }, 4.9);
    tl.fromTo(V.prog.wrap, { opacity: 0 }, { opacity: 1, duration: 0.2 }, 4.9);
    swapText(tl, V.st, [0, 5.35, 6.25]);
    tl.fromTo(V.prog.fill, { scaleX: 0 }, { scaleX: 0.12, duration: 0.3, ease: "power2.out" }, 4.95);
    tl.to(V.prog.fill, { scaleX: 0.62, duration: 1.3, ease: "power1.inOut" }, 5.3);
    var pctState = { v: 0 };
    tl.to(pctState, { v: 62, duration: 1.6, ease: "power1.inOut", onUpdate: function () { V.prog.pct.textContent = Math.round(pctState.v) + "%"; } }, 4.95);
    cam.to(5.0, 1.65, { x: runR.cx, y: runR.cy - 30 }, 2.35, "power2.in");

    // Zoom-through → résultat (hero)
    cam.zoomThrough(6.65, { x: runR.cx, y: runR.cy }, 2.35, { x: statsR.cx, y: statsR.cy + 120 }, 1.75);
    tl.set(V.results, { opacity: 0 }, 0);
    tl.set(V.results, { opacity: 1 }, 7.0);
    tl.set([V.prog.wrap, V.spin], { opacity: 0 }, 7.0);
    tl.set(V.run, { opacity: 1 }, 7.0);
    tl.set(V.run.querySelector("svg"), { opacity: 1 }, 7.0);
    tl.set(cur.c, { opacity: 0 }, 6.7);
    var fmts = [
      function (v) { return String(Math.round(v)); },
      function (v) { return String(Math.round(v)); },
      function (v) { return String(Math.round(v)); },
      function (v) { return V.pctFmt.format(Math.round(v * 100) / 100); },
    ];
    [5, 3, 2, 0.5].forEach(function (to, i) { countTo(tl, V.statVals[i], 7.2 + i * 0.1, 0.9, to, fmts[i]); });
    // Le rapport se remplit ; la caméra recule puis descend le long du rapport
    V.rows.forEach(function (r, i) {
      tl.fromTo(r.row, { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.32, ease: "power3.out", immediateRender: true }, 8.1 + i * 0.2);
      tl.fromTo(r.pill, { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.3, ease: "power3.out", immediateRender: true }, 8.25 + i * 0.2);
    });
    cam.to(8.0, 0.9, { x: darkR.cx, y: darkR.y + 260 }, 1.42, "power2.inOut");
    showCallout(tl, coDiag, 8.5, 10.9);
    cam.to(9.0, 2.2, { x: darkR.cx, y: targetR.cy - 60 }, 1.42, "power1.inOut");

    // Le détail utile : push-in sur la ligne manquante, clic « Copier », plan tenu
    cam.to(11.2, 0.8, { x: targetR.cx, y: targetR.cy - 30 }, 1.7, "power3.inOut");
    // Mise en valeur (montage) : les autres critères s'estompent pendant le plan tenu
    var others = V.rows.filter(function (r) { return r !== target; }).map(function (r) { return r.row; });
    tl.to(others, { opacity: 0.28, duration: 0.5, ease: "power2.out" }, 11.3);
    showCallout(tl, coRew, 11.8, 14.35);
    cursorSet(tl, cur, 11.9, { x: copyR.cx + 180, y: copyR.cy + 120 });
    tl.set(cur.c, { opacity: 1 }, 11.9);
    cursorTo(tl, cur, 12.0, 0.7, { x: copyR.cx, y: copyR.cy + 2 });
    click(tl, cur, 12.8, { x: copyR.cx, y: copyR.cy + 2 }, target.copy);
  }

  // ============================================================ ENTRETIEN
  function buildEntretien(S, C) {
    var U = C.ui;
    var A = appWindow(C, "sim");
    add(S.win3d, A.win);
    A.page.style.height = "1060px";
    function screen() { var s = put(A.page, el("div", "screen")); s.style.cssText = "position:absolute;left:64px;right:64px;top:56px"; return s; }

    // Écran 1 : saisie
    var s1 = screen();
    header(s1, U, "interview");
    var two = put(s1, el("div", "two"));
    var offer = textPanel(U["cvInput.offerHeader"], C.inputs.offer.split("\n"));
    var cv = textPanel(U["cvInput.cvHeader"], C.inputs.cv.split("\n"), [U["common.pdf"], U["common.text"]]);
    add(two, offer.panel, cv.panel);
    var r1 = put(s1, el("div", "center-row"));
    var gen = put(r1, btn(U["interview.generate"], "msg"));

    // Écran 2 : les questions
    var s2 = screen();
    header(s2, U, "interview");
    var bar = put(s2, el("div", "panel bar-panel"));
    var left = put(bar, el("div"));
    left.style.cssText = "display:flex;gap:12px";
    add(left, btn(U["interview.changeTopic"], "arrowL", "btn-outline"));
    var start = add(left, btn(U["interview.start"], "play")).lastChild;
    start.style.cssText = "height:36px;padding:0 12px;font-size:11px";
    add(bar, el("div", "kicker", fmt(U["interview.estimate"], { minutes: 10, count: 5 })));
    var qCards = C.questions.map(function (q, i) {
      var c = add(s2, el("div", "panel q-card")).lastChild;
      add(c, el("div", "k", fmt(U["interview.questionN"], { n: i + 1 }) + " · " + q[0]), el("div", "q", q[1]));
      return c;
    });

    // Écran 3 : répondre
    var s3 = screen();
    header(s3, U, "interview");
    var bar3 = put(s3, el("div", "panel bar-panel"));
    add(bar3, btn(U["interview.changeTopic"], "arrowL", "btn-outline"), el("div", "kicker", fmt(U["interview.estimate"], { minutes: 10, count: 5 })));
    var dark = put(s3, el("div", "dark"));
    dark.style.marginTop = "24px";
    var din = put(dark, el("div", "dark-in"));
    var dh = put(din, el("div", "dark-h"));
    add(dh, el("span", "", fmt(U["interview.questionOf"], { current: 1, total: 5, category: C.questions[0][0] })));
    var timer = add(dh, el("span", "", "⏱ 0:00")).lastChild;
    timer.style.color = "var(--paper)";
    var body = put(din, el("div", "q-card q-dark"));
    body.style.padding = "24px";
    add(body, el("div", "q", C.questions[0][1]));
    var lab = add(body, el("div", "k", U["interview.answerLabel"])).lastChild;
    lab.style.cssText = "margin-top:20px;color:rgba(241,238,231,.6)";
    var ans = put(body, el("div", "answer"));
    var typed = add(ans, el("span")).lastChild;
    add(ans, el("span", "caret"));
    var navRow = put(body, el("div", "nav-row"));
    navRow.style.marginTop = "20px";
    add(navRow, el("span", "", "‹ " + U["interview.previous"]), el("span", "", U["interview.pause"]));
    var next = add(navRow, el("span", "next", U["interview.next"] + " ›")).lastChild;
    var pr = put(s3, el("div"));
    pr.style.marginTop = "24px";
    var prTop = put(pr, el("div", "progress-top"));
    add(prTop, el("span", "", U["interview.progress"]), el("span", "", C.lang === "fr" ? "20 %" : "20%"));
    var tr = put(pr, el("div", "track"));
    var trFill = add(tr, el("i")).lastChild;
    trFill.style.transform = "scaleX(0.2)";

    // Écran 4 : le rapport
    var s4 = screen();
    header(s4, U, "results");
    var sg = put(s4, el("div", "score-grid"));
    var sc = add(sg, el("div", "stat")).lastChild;
    add(sc, el("div", "k", U["results.globalScore"]));
    var scoreV = add(sc, el("div", "v", "0/10")).lastChild;
    var good = add(sc, el("div", "k", U["results.score.good"])).lastChild;
    good.style.cssText = "color:var(--ok-text);margin-top:6px";
    [[U["results.questions"], "5"], [U["results.duration"], "7:12"]].forEach(function (d) {
      var c = add(sg, el("div", "stat")).lastChild;
      add(c, el("div", "k", d[0]), el("div", "v", d[1]));
    });
    var strengths = add(s4, el("div", "panel list-panel")).lastChild;
    var h1 = add(strengths, el("h4")).lastChild;
    h1.innerHTML = ICON.circleCheck + "<span></span>";
    h1.querySelector("span").textContent = U["results.strengths"];
    var sItems = C.strengths.map(function (t) { return add(strengths, el("div", "good", t)).lastChild; });
    var impr = add(s4, el("div", "panel list-panel")).lastChild;
    var h2 = add(impr, el("h4")).lastChild;
    h2.innerHTML = ICON.bubble + "<span></span>";
    h2.querySelector("span").textContent = U["results.improvements"];
    var iItems = C.improvements.map(function (t) { return add(impr, el("div", "todo", t)).lastChild; });

    return { A: A, s: [s1, s2, s3, s4], offer: offer, cv: cv, gen: gen, start: start, qCards: qCards, dark: dark, timer: timer, typed: typed, next: next, scoreCard: sc, scoreV: scoreV, good: good, sItems: sItems, iItems: iItems, strengths: strengths, bar: bar };
  }

  function timelineEntretien(tl, S, C, V, cam, cur, G) {
    var U = C.ui;
    var features = U["dashboard.modules.interview.features"];
    var genR = rect(V.gen);
    var two = rect(V.offer.panel.parentNode);
    var startR = rect(V.start);
    var qListR = rect(V.qCards[2]);
    var q1R = rect(V.qCards[1]);
    var darkR = rect(V.dark);
    var timerR = rect(V.timer);
    var nextR = rect(V.next);
    var scoreR = rect(V.scoreCard);
    var strR = rect(V.strengths);

    var base = { p: { x: two.cx, y: two.y + 40 }, s: 1.12 };
    var coQ = callout(S.world, features[0], { x: qListR.x + qListR.w - 20, y: qListR.cy }, "left", { fontSize: 12, line: 40 });
    var coT = callout(S.world, features[1], { x: timerR.x - 10, y: timerR.cy }, "left", { fontSize: 10, line: 30 });
    coT.c.style.top = parseFloat(coT.c.style.top) - 46 + "px";
    var coE = callout(S.world, features[2], { x: scoreR.x + scoreR.w - 24, y: scoreR.y + scoreR.h }, "right", { fontSize: 11, line: 34 });

    openAndClose(tl, S, G, wordsInto(S.hook, C.hookInterview), cam, base);
    tl.set([V.s[1], V.s[2], V.s[3]], { opacity: 0 }, 0);

    // Saisie → générer
    cursorSet(tl, cur, 0, { x: genR.cx + 480, y: genR.cy + 240 });
    cam.to(3.0, 1.0, { x: genR.cx, y: genR.cy - 120 }, 1.45, "power2.inOut");
    cursorTo(tl, cur, 2.7, 0.9, { x: genR.cx + 50, y: genR.cy + 4 });
    click(tl, cur, 3.65, { x: genR.cx + 50, y: genR.cy + 4 }, V.gen);
    tl.set(V.gen, { opacity: 0.5 }, 3.75);

    // Les questions arrivent (même page, l'étape change)
    tl.to(V.s[0], { opacity: 0, duration: 0.25, ease: "power1.in" }, 4.05);
    tl.set(V.s[1], { opacity: 1 }, 4.1);
    cam.to(4.05, 0.7, { x: q1R.cx, y: q1R.cy - 40 }, 1.3, "power3.out");
    arrive(tl, [V.bar].concat(V.qCards), 4.1, 0.11, 22);
    showCallout(tl, coQ, 4.6, 6.0);
    cursorTo(tl, cur, 4.9, 0.8, { x: startR.cx + 20, y: startR.cy + 3 });
    click(tl, cur, 5.75, { x: startR.cx + 20, y: startR.cy + 3 }, V.start);

    // Zoom-through → répondre
    cam.zoomThrough(6.0, { x: startR.cx, y: startR.cy }, 1.3, { x: darkR.cx, y: darkR.cy + 20 }, 1.75);
    tl.set(V.s[1], { opacity: 0 }, 6.36);
    tl.set(V.s[2], { opacity: 1 }, 6.36);
    tl.set(cur.c, { opacity: 0 }, 6.1);
    var clock = { s: 0 };
    tl.to(clock, { s: 32, duration: 3.8, ease: "none", onUpdate: function () {
      var s = Math.floor(clock.s);
      V.timer.textContent = "⏱ 0:" + (s < 10 ? "0" : "") + s;
    } }, 6.4);
    showCallout(tl, coT, 6.7, 8.6);
    typeText(tl, V.typed, C.answer, 6.9, 2.9);
    cursorSet(tl, cur, 9.3, { x: nextR.cx + 200, y: nextR.cy + 140 });
    tl.set(cur.c, { opacity: 1 }, 9.3);
    cursorTo(tl, cur, 9.35, 0.65, { x: nextR.cx, y: nextR.cy + 2 });
    click(tl, cur, 10.05, { x: nextR.cx, y: nextR.cy + 2 }, V.next);

    // Zoom-through → le rapport (hero)
    cam.zoomThrough(10.3, { x: nextR.cx, y: nextR.cy }, 1.75, { x: scoreR.cx + 200, y: scoreR.cy + 90 }, 1.55);
    tl.set(V.s[2], { opacity: 0 }, 10.66);
    tl.set(V.s[3], { opacity: 1 }, 10.66);
    tl.set(cur.c, { opacity: 0 }, 10.4);
    countTo(tl, V.scoreV, 10.8, 0.9, 7.6, function (v) { return (Math.round(v * 10) / 10).toFixed(1) + "/10"; });
    tl.fromTo(V.good, { opacity: 0, y: 6 }, { opacity: 1, y: 0, duration: 0.3, ease: "power3.out", immediateRender: true }, 11.6);
    showCallout(tl, coE, 11.5, 14.35);
    arrive(tl, V.sItems, 11.8, 0.16, 12);
    arrive(tl, V.iItems, 12.35, 0.16, 12);
    cam.to(11.9, 1.2, { x: strR.cx, y: strR.cy - 40 }, 1.4, "power2.inOut");
  }

  // ============================================================ LETTRE
  function buildLettre(S, C) {
    var U = C.ui;
    var A = appWindow(C, "letter");
    add(S.win3d, A.win);
    header(A.page, U, "coverLetter");
    var two = put(A.page, el("div", "two"));
    var short = function (txt) { return txt.split("\n").filter(Boolean).slice(0, 4); };
    var offer = textPanel(U["cvInput.offerHeader"], short(C.inputs.offer));
    var cv = textPanel(U["cvInput.cvHeader"], short(C.inputs.cv), [U["coverLetter.cvFile"], U["common.text"]]);
    offer.box.style.minHeight = cv.box.style.minHeight = "150px";
    add(two, offer.panel, cv.panel);

    var style = add(A.page, el("div", "panel")).lastChild;
    style.style.marginTop = "24px";
    add(style, el("div", "panel-h", U["coverLetter.options.header"]));
    var sb = add(style, el("div", "panel-b style-grid")).lastChild;
    var chipsOf = {};
    [["tone", ["professional", "warm", "confident", "formal"], "tones", "professional"],
      ["length", ["short", "standard", "detailed"], "lengths", "standard"],
      ["language", ["auto", "fr", "en"], "languages", "auto"]].forEach(function (g) {
      var col = add(sb, el("div")).lastChild;
      add(col, el("div", "field-label", U["coverLetter.options." + g[0]]));
      var chips = add(col, el("div", "chips")).lastChild;
      chipsOf[g[0]] = {};
      g[1].forEach(function (v) {
        var c = add(chips, el("span", "chip")).lastChild;
        var b = add(c, el("span", "", U["coverLetter." + g[2] + "." + v])).lastChild;
        var f = add(c, el("span", "fill", U["coverLetter." + g[2] + "." + v])).lastChild;
        var on = v === g[3];
        f.style.opacity = on ? "1" : "0";
        b.style.opacity = on ? "0" : "1"; // libellé de base masqué sous la pastille remplie
        chipsOf[g[0]][v] = { chip: c, fill: f, base: b };
      });
    });

    var row = put(A.page, el("div", "center-row"));
    var prog = progressBlock();
    add(row, prog.wrap);
    var st = statusLines(prog.status, [C.status.letterStart, C.status.letterGemini, C.status.letterWriting]);
    var run = put(row, btn(U["coverLetter.run"], "pen"));

    var panel = add(A.page, el("div", "panel")).lastChild;
    panel.style.marginTop = "40px";
    var ph = add(panel, el("div", "panel-h")).lastChild;
    ph.style.height = "auto";
    ph.style.padding = "8px 16px";
    add(ph, el("span", "", U["coverLetter.result"]));
    var tools = add(ph, el("div", "tools")).lastChild;
    var copyB = add(tools, btn(U["common.copy"], "copy", "btn-outline copy-btn")).lastChild;
    var done = add(copyB, el("span", "done")).lastChild;
    done.innerHTML = ICON.check + "<span></span>";
    done.querySelector("span").textContent = U["coverLetter.copied"];
    add(tools, btn(".txt", "down", "btn-outline"), btn(".md", "down", "btn-outline"));
    var lb = add(panel, el("div", "letter-body")).lastChild;
    var L = C.letter;
    var parts = [add(lb, el("p", "subject", L.subject)).lastChild, add(lb, el("p", "", L.greeting)).lastChild, add(lb, el("p", "", L.opening)).lastChild];
    L.body.forEach(function (b) { parts.push(add(lb, el("p", "", b)).lastChild); });
    parts.push(add(lb, el("p", "", L.closing)).lastChild, add(lb, el("p", "", L.signoff)).lastChild, add(lb, el("p", "", L.signature)).lastChild);
    var foot = add(panel, el("div", "letter-foot", U["coverLetter.reviewHint"])).lastChild;

    return { A: A, offer: offer, style: style, chipsOf: chipsOf, run: run, prog: prog, st: st, panel: panel, tools: tools, copyB: copyB, done: done, parts: parts, foot: foot, ph: ph };
  }

  function timelineLettre(tl, S, C, V, cam, cur, G) {
    var U = C.ui;
    var features = U["dashboard.modules.coverLetter.features"];
    var styleR = rect(V.style);
    var warm = V.chipsOf.tone.warm;
    var pro = V.chipsOf.tone.professional;
    var warmR = rect(warm.chip);
    var runR = rect(V.run);
    var panelR = rect(V.panel);
    var p0 = rect(V.parts[0]);
    var pOpen = rect(V.parts[2]);
    var pLast = rect(V.parts[V.parts.length - 1]);
    var copyR = rect(V.copyB);

    var twoR = rect(V.offer.panel.parentNode);
    var base = { p: { x: twoR.cx, y: twoR.y + 40 }, s: 1.12 };
    var coStyle = callout(S.world, features[1], { x: styleR.x + 30, y: styleR.y }, "right", { fontSize: 12, line: 30 });
    coStyle.c.style.top = parseFloat(coStyle.c.style.top) - 34 + "px";
    var coParts = callout(S.world, features[0], { x: pOpen.x - 20, y: pOpen.y + 14 }, "left", { fontSize: 11, line: 40 });
    var coCopy = callout(S.world, features[2], { x: copyR.x - 16, y: copyR.cy }, "left", { fontSize: 10, line: 34 });

    openAndClose(tl, S, G, wordsInto(S.hook, U["coverLetter.title"]), cam, base);

    // Le style : le ton passe sur « Chaleureux »
    cam.to(2.75, 0.8, { x: styleR.cx, y: styleR.cy - 80 }, 1.36, "power2.inOut");
    showCallout(tl, coStyle, 2.9, 4.7);
    cursorSet(tl, cur, 0, { x: warmR.cx + 560, y: warmR.cy + 300 });
    cursorTo(tl, cur, 2.95, 0.75, { x: warmR.cx, y: warmR.cy + 2 });
    click(tl, cur, 3.75, { x: warmR.cx, y: warmR.cy + 2 }, warm.chip);
    tl.to(pro.fill, { opacity: 0, duration: 0.12 }, 3.8);
    tl.to(pro.base, { opacity: 1, duration: 0.12 }, 3.8);
    tl.to(warm.fill, { opacity: 1, duration: 0.12 }, 3.8);
    tl.to(warm.base, { opacity: 0, duration: 0.12 }, 3.8);
    cursorTo(tl, cur, 4.05, 0.6, { x: runR.cx + 50, y: runR.cy + 4 });
    cam.to(3.9, 1.0, { x: runR.cx, y: runR.cy - 60 }, 1.6, "power2.inOut");
    click(tl, cur, 4.7, { x: runR.cx + 50, y: runR.cy + 4 }, V.run);

    // Rédaction : statuts réels
    tl.set(V.run, { opacity: 0.5 }, 4.8);
    tl.fromTo(V.prog.wrap, { opacity: 0 }, { opacity: 1, duration: 0.2 }, 4.8);
    swapText(tl, V.st, [0, 5.1, 5.35]);
    tl.fromTo(V.prog.fill, { scaleX: 0 }, { scaleX: 0.4, duration: 0.6, ease: "power2.out" }, 4.85);
    var pctState = { v: 0 };
    tl.to(pctState, { v: 40, duration: 0.6, ease: "power2.out", onUpdate: function () { V.prog.pct.textContent = Math.round(pctState.v) + "%"; } }, 4.85);
    cam.to(4.8, 0.4, { x: runR.cx, y: runR.cy }, 2.1, "power2.in");

    // Zoom-through → la lettre s'écrit (hero)
    cam.zoomThrough(5.2, { x: runR.cx, y: runR.cy }, 2.1, { x: panelR.cx, y: p0.y + 250 }, 1.62);
    tl.set(cur.c, { opacity: 0 }, 5.25);
    tl.set([V.tools, V.foot], { opacity: 0 }, 0);
    V.parts.forEach(function (p) { tl.set(p, { opacity: 0 }, 0); });
    var times = [5.7, 6.05, 6.4, 7.15, 7.9, 8.65, 9.2, 9.6];
    V.parts.forEach(function (p, i) {
      tl.fromTo(p, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.4, ease: "power3.out", immediateRender: false }, times[i]);
    });
    showCallout(tl, coParts, 6.6, 9.0);
    cam.to(6.9, 3.2, { x: panelR.cx, y: pLast.y - 120 }, 1.5, "power1.inOut");
    tl.set([V.run], { opacity: 1 }, 10.1);
    tl.set(V.prog.wrap, { opacity: 0 }, 10.1);
    tl.fromTo([V.tools, V.foot], { opacity: 0 }, { opacity: 1, duration: 0.3, ease: "power1.out", immediateRender: false }, 10.2);

    // Copier : « Lettre copiée ✓ » (comportement réel du bouton)
    cam.to(10.6, 0.9, { x: copyR.cx - 180, y: copyR.cy + 120 }, 2.05, "power3.inOut");
    showCallout(tl, coCopy, 11.3, 14.35);
    cursorSet(tl, cur, 11.4, { x: copyR.cx + 180, y: copyR.cy + 150 });
    tl.set(cur.c, { opacity: 1 }, 11.4);
    cursorTo(tl, cur, 11.5, 0.7, { x: copyR.cx, y: copyR.cy + 2 });
    click(tl, cur, 12.3, { x: copyR.cx, y: copyR.cy + 2 }, V.copyB);
    tl.fromTo(V.done, { opacity: 0 }, { opacity: 1, duration: 0.15, ease: "power1.out", immediateRender: true }, 12.38);
    // Le bouton change de contenu (comme dans l'app) : l'ancien libellé disparaît
    tl.set([V.copyB.querySelector("svg"), V.copyB.querySelector("span")], { opacity: 0 }, 12.38);
  }

  // ============================================================ entrée
  var DEMOS = {
    analyse: { build: buildAnalyse, run: timelineAnalyse, cta: "landing.nav.analyze" },
    entretien: { build: buildEntretien, run: timelineEntretien, cta: "dashboard.modules.interview.cta" },
    lettre: { build: buildLettre, run: timelineLettre, cta: "dashboard.modules.coverLetter.cta" },
  };

  window.TalentoDemo = {
    build: function (root, demo, lang) {
      var C = Object.assign({ lang: lang }, window.TALENTO_CONTENT[lang]);
      document.documentElement.lang = lang;
      var D = DEMOS[demo];
      var S = buildShell(root, C, demo);
      var V = D.build(S, C);
      var G = buildSignature(S, C, C.ui[D.cta]);
      var cur = makeCursor(S.world);
      return {
        timeline: function () {
          rootRect = root.getBoundingClientRect();
          var tl = gsap.timeline({ paused: true });
          var cam = new Camera(tl, S.outer, S.inner);
          D.run(tl, S, C, V, cam, cur, G);
          return tl;
        },
      };
    },
  };
})();
