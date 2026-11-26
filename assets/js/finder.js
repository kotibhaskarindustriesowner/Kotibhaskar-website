/* Kotibhaskar Industries — homepage Material Handling Solution Finder.
   A plain, rule-based matcher (no AI, no server): it reads the load, height, operation and product
   type from the customer's words and compares them with the documented configurations in
   /assets/data/finder.json (built by tools/build_finder.py from the same data as the product pages).
   It only suggests a product when a documented configuration meets every figure the customer gave;
   otherwise it asks one question or offers to send the requirement to the sales team. */
(function () {
  'use strict';
  var form = document.getElementById('sf-form');
  if (!form) return;
  var input = document.getElementById('sf-input');
  var out = document.getElementById('sf-results');
  var me = document.currentScript || document.querySelector('script[data-finder-data]');
  var DATA_URL = me && me.getAttribute('data-finder-data');
  var SITE = 'https://kotibhaskarindustries.com';
  var CFG = window.ENQUIRY || {};
  var EP = CFG.endpoint || 'https://api.web3forms.com/submit';
  var KEY = CFG.accessKey;
  var WA = CFG.whatsapp || '919822413252';
  var PHONE = CFG.phone || '+919822413252';
  var PHONE_LABEL = CFG.phoneLabel || '+91 98224 13252';

  var state = { orig: '', clar: [], asked: {}, pick: null, items: null, sending: false, lastSig: '' };
  var dataP = null;
  function loadData() {
    if (!dataP) {
      dataP = fetch(DATA_URL, { credentials: 'same-origin' })
        .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
        .then(function (d) { d.items.forEach(function (it, i) { it.i = i; }); return d.items; })
        .catch(function (e) { dataP = null; throw e; });
    }
    return dataP;
  }
  input.addEventListener('focus', function () { loadData().catch(function () {}); }, { once: true });

  function esc(t) {
    return String(t).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; });
  }
  function fmtH(mm) { return mm >= 1000 ? (+(mm / 1000).toFixed(2)) + ' m' : mm + ' mm'; }
  function fmtKg(kg) { return kg.toLocaleString('en-IN') + ' kg'; }
  function uniq(a) { return a.filter(function (x, i) { return x != null && a.indexOf(x) === i; }); }

  /* ---------------------------------------------------------------- reading the requirement */
  var T = [   // [regex, product types it names] — specific phrases first
    [/high[\s-]*lift|scissor\s*pallet/, ['pallet-truck-highlift']],
    [/pallet\s*(truck|jack|trolley|mover|lifter)|hand\s*pallet|\bhpt\b/, ['pallet-truck', 'pallet-truck-highlift']],
    [/stacker|fork[\s-]*lift(er)?\b|forklift/, ['stacker', 'stacker-cage', 'stacker-jib']],
    [/floor\s*crane|engine\s*(crane|hoist)|shop\s*crane|hydraulic\s*crane|\bcranes?\b|\bboom\b/, ['floor-crane']],
    [/gantr(y|ies)|a[\s-]frame|chain\s*pulley|\bhoist\b/, ['gantry']],
    [/scissor|lift(ing)?\s*table|table\s*lift|platform\s*lift|lifting\s*platform|hydraulic\s*table/, ['scissor-mobile', 'scissor-pit']],
    [/order\s*picker|\bpicking\b|stock\s*picker|operator\s*(cage|platform)|work(ing)?\s*at\s*height/, ['order-picker']],
    [/material\s*(lifter|tilter)|hopper|tipp(er|ing)|pour(ing)?\s*(material|powder|granules)/, ['material-tilter']],
    [/dock\s*level+er|\bdock\b|loading\s*bay|truck\s*bed|container\s*loading|loading\s*ramp/, ['dock-leveller']],
    [/goods\s*lift|freight\s*lift|\belevator\b|between\s*floors|upper\s*floor|first\s*floor|mezzanine|lifting\s*cage/, ['goods-lift', 'lifting-cage']],
    [/shel(f|ves)\s*trolley|shelf\s*cart|\b(2|3|5|two|three|five)[\s-]*shel(f|ves)/, ['trolley-two-shelf-trolley', 'trolley-three-shelf-trolley', 'trolley-five-shelf-trolley']],
    [/industrial\s*shelving|\bshelving\b|\bracks?\b|racking|storage\s*rack/, ['shelving']],
    [/conveyor|roller\s*(line|track|bed)/, ['conveyor']],
    [/\bsacks?\b|gunny|\bbags?\b|cement/, ['trolley-sack-trolley']],
    [/barrow/, ['trolley-double-wheel-barrow']],
    [/\bchips?\b|swarf|\bscrap\b/, ['trolley-chip-trolley']],
    [/coolant/, ['trolley-coolant-feeding-trolley']],
    [/\bcnc\b|tool\s*(holder|trolley|pockets?)/, ['trolley-cnc-tool-trolley-600x5', 'trolley-cnc-tool-trolley-600x7', 'trolley-cnc-tool-trolley-900x5', 'trolley-cnc-tool-trolley-900x7']],
    [/work\s*-?\s*(table|bench)/, ['trolley-industrial-work-table-a', 'trolley-industrial-work-table-b']],
    [/\bbins?\b/, ['trolley-bin-trolley-single-sided', 'trolley-bin-trolley-double-sided']],
    [/access\s*steps|\bsteps\b|ladder/, ['trolley-mobile-access-steps']],
    [/(steel|metal|\bms\b|m\.s\.|iron|industrial)\s*pallets?/, ['trolley-industrial-steel-pallet-plain', 'trolley-industrial-steel-pallet-sheet', 'trolley-industrial-steel-pallet-wiremesh']],
    [/turn\s*-?table|steering\s*trolley/, ['trolley-turntable-platform-trolley', 'trolley-turntable-platform-truck', 'trolley-turntable-workshop-trolley-sheet']],
    [/platform\s*(trolley|truck|cart)|flat\s*(bed\s*)?trolley|workshop\s*trolley|push\s*cart|hand\s*cart/, ['trolley-platform-trolley', 'trolley-workshop-trolley-sheet', 'trolley-workshop-trolley-wiremesh']],
    [/multi[\s-]*utility/, ['trolley-multi-utility-trolley']]
  ];
  // what is carried (only used when no product type is named)
  var BOXES = /cartons?|\bboxes\b|\bbox\b|parcels?|packages?/;
  var BOX_TYPES = ['trolley-multi-utility-trolley', 'trolley-platform-trolley', 'trolley-turntable-platform-trolley'];
  var DRUM = /\bdrums?\b|barrels?/;
  var TROLLEY_GENERIC = /trolle(y|ys)|\bcarts?\b|hand\s*truck/;
  var TROLLEY_DEFAULT = ['trolley-platform-trolley', 'trolley-multi-utility-trolley', 'trolley-turntable-platform-trolley', 'trolley-workshop-trolley-sheet'];
  var LIFT_POOL = ['stacker', 'floor-crane', 'gantry', 'scissor-mobile', 'scissor-pit', 'goods-lift', 'lifting-cage', 'pallet-truck-highlift'];
  var MOVE_POOL = ['pallet-truck', 'trolley-platform-trolley', 'trolley-turntable-platform-truck', 'trolley-turntable-platform-trolley'];
  var LIFT_VERB = /\blift(s|ed|ing)?\b|\braise|\bhoist|\belevat|\bstack(ing)?\b|\bload(ing)? (on|onto|into)\b|\bhigher\b|\bheight\b/;
  var MOVE_VERB = /\bmov(e|es|ing)\b|transport|\bshift(ing)?\b|\bcarry|\bpush|\bpull|\bhaul/;
  var CONTEXT = /factory|warehouse|workshop|godown|plant|industr|store|shop\s*floor|production|material|handling|lift|move|load|heavy|equipment|machine/;

  function parse(text) {
    var s = (' ' + text + ' ').toLowerCase().replace(/[–—]/g, '-').replace(/(\d),(\d{3})\b/g, '$1$2').replace(/×/g, 'x');
    var r = { s: s, kg: null, perWheel: false, mm: null, op: null, types: [], inferred: false, wheel: null, pallet: false, custom: false };
    // ---- load (kg / tonnes); "per wheel/castor", "per shelf" and "per metre" are kept apart
    var m, re = /(\d+(?:\.\d+)?)\s*(kgs?|kilo(?:gram)?s?|kilos|tonnes?|tons?|mt|t)\b(\s*(?:\/|per|each)\s*(wheels?|castors?|casters?|shel(?:f|ves)|metres?|meters?|mtrs?|m)\b)?/g;
    var kgs = [];
    while ((m = re.exec(s))) {
      var v = parseFloat(m[1]) * (/^(t|mt|tons?|tonnes?)$/.test(m[2]) ? 1000 : 1);
      var per = m[4] || '';
      if (/wheel|castor|caster/.test(per)) { r.perWheel = true; kgs.push(v); }
      else if (!per) kgs.push(v);
    }
    if (/(each|per|every)\s*(wheel|castor|caster)/.test(s)) r.perWheel = true;
    if (kgs.length) r.kg = Math.max.apply(null, kgs);
    // ---- height (m / mm / cm / ft); sizes such as "1200 x 1000 mm" and lengths are not heights
    var hs = [];
    re = /(\d+(?:\.\d+)?)\s*(mm|cm|metres?|meters?|mtrs?|m|ft|feet|foot)\b/g;
    while ((m = re.exec(s))) {
      var before = s.slice(Math.max(0, m.index - 40), m.index), after = s.slice(m.index + m[0].length, m.index + m[0].length + 14);
      if (/x\s*$/.test(before) || /^\s*x\s*\d/.test(after)) continue;                       // a dimension
      if (/(long|length|width|wide|distance|away|span|across|travel)\b[^.]{0,12}$/.test(before) || /^\s*(long|wide|in length|away)/.test(after)) continue;
      var u = m[2], val = parseFloat(m[1]);
      var mm = /^(mm)$/.test(u) ? val : /^cm$/.test(u) ? val * 10 : /^(ft|feet|foot)$/.test(u) ? val * 304.8 : val * 1000;
      if (/^(mm|cm)$/.test(u) && !/height|high|lift|raise|level|up\s*to|upto|to a|stack|elevat/.test(before)) continue;
      hs.push(Math.round(mm));
    }
    if (hs.length) r.mm = Math.max.apply(null, hs);
    // ---- operation
    if (/fully?\s*-?\s*electric|completely\s*electric|electric\s*(drive|travel|movement|traction)|battery[\s-]*(operated|powered)\s*(drive|travel)|self[\s-]*propelled/.test(s)) r.op = 'fully';
    else if (/\bdc\b/.test(s)) r.op = 'dc';
    else if (/battery|24\s*v\b/.test(s)) r.op = 'battery';      // semi-electric DC or fully electric
    else if (/\bac\b|440\s*v|415\s*v|3[\s-]*phase|three[\s-]*phase|\bmains\b/.test(s)) r.op = 'ac';
    else if (/semi[\s-]*electric/.test(s)) r.op = 'semi';
    else if (/\belectric(al|ally)?\b|motori[sz]ed|powered/.test(s)) r.op = 'electric';
    else if (/\bmanual(ly)?\b|hand[\s-]*(operated|pump)|without\s*(power|electricity)|no\s*(power|electricity)/.test(s)) r.op = 'manual';
    r.custom = /custom|special|\bspm\b|tailor|made\s*to\s*order|bespoke/.test(s);
    r.pallet = /\bpallets?\b/.test(s);
    // ---- wheels & castors: "castor", or "wheels/rollers for ..." means the wheels themselves are wanted
    var wheelWord = /castors?|casters?/.test(s) || /\b(wheels?|rollers?)\s+(for|on|to\s*suit|to\s*fit)\b/.test(s) ||
                    (/\b(wheels?|rollers?)\b/.test(s) && !/trolley|truck|stacker|crane|barrow|lift|conveyor/.test(s.replace(/(wheels?|rollers?)\s+(for|on)\s+[a-z ]+$/, '')));
    if (wheelWord) {
      var w = [];
      if (/uhmw|polyethylene|hard\s*polymer|\bnylon\b/.test(s)) w.push('wheel-uhmw');
      if (/\bpu\b|polyurethane|pu-?ci|puci/.test(s)) w.push('wheel-puci');
      if (/cast\s*iron|\bci\b/.test(s)) w.push('wheel-ci');
      if (/pallet\s*truck|pallet\s*jack/.test(s)) w = ['wheel-pallet-truck'];
      if (/track|\brail|groove|flange/.test(s)) w = ['wheel-ms-track'];
      r.wheel = w.length ? w : ['wheel-uhmw', 'wheel-puci', 'wheel-ci'];
      r.types = r.wheel.slice();
      return r;
    }
    // ---- product types named in the text
    var rest = s;
    T.forEach(function (t) {
      if (t[0].test(rest)) { r.types = r.types.concat(t[1]); rest = rest.replace(t[0], ' '); }
    });
    // gas cylinders: the LPG trolley and the O2 / CO2 / N2 / argon trolley are different products
    var lpg = /\blpg\b/.test(s), ind = /oxygen|\bo2\b|\bco2\b|nitrogen|argon/.test(s);
    var two = /two\s*cylinders|double\s*(gas\s*)?cylinder|2\s*cylinders|\bboth\b/.test(s);
    if (lpg || ind || /cylinders?|\bgas\b/.test(s)) {
      var g = [];
      if (two || (lpg && ind)) g.push('trolley-gas-cylinder-trolley-double');
      if (ind && !two && !lpg) g.push('trolley-gas-cylinder-trolley-single');
      if (lpg && !ind && !two) g.push('trolley-gas-cylinder-trolley-lpg');
      if (!g.length) g = ['trolley-gas-cylinder-trolley-single', 'trolley-gas-cylinder-trolley-lpg', 'trolley-gas-cylinder-trolley-double'];
      r.types = r.types.concat(g);
    }
    if (DRUM.test(s)) {
      if (/tilt|pour|rotat|empty|decant/.test(s)) r.types.push('drum-tilter');
      else if (/grip|clamp|automatic|auto\b/.test(s)) r.types.push('drum-gripper');
      else if (/trolley|\bmove|transport|shift|roll/.test(s) && !LIFT_VERB.test(s)) r.types.push('trolley-drum-trolley');
      else r.types.push('drum-tilter', 'drum-gripper', 'trolley-drum-trolley');
    }
    // stackers: standard fork stackers unless the cage or jib-hook version is asked for
    if (r.types.indexOf('stacker') >= 0) {
      var other = r.types.filter(function (t) { return !/^stacker/.test(t); });
      r.types = (/\bjib\b|\bhook\b/.test(s) ? ['stacker-jib'] : /\bcage\b|person|operator/.test(s) ? ['stacker-cage'] : ['stacker']).concat(other);
    }
    if (BOXES.test(s) && (!r.types.length || (r.types.length && TROLLEY_GENERIC.test(s) && r.types.every(function (t) { return /^trolley-/.test(t); }))))
      r.types = BOX_TYPES.concat(r.types);
    if (!r.types.length && TROLLEY_GENERIC.test(s)) r.types = TROLLEY_DEFAULT.slice();
    // ---- nothing named: infer from what is being lifted or moved
    if (!r.types.length) {
      r.inferred = true;
      var lift = LIFT_VERB.test(s) || (r.mm != null && r.mm >= 300);
      if (r.pallet) r.types = lift ? (r.mm != null && r.mm <= 800 ? ['stacker', 'pallet-truck-highlift'] : ['stacker']) : (MOVE_VERB.test(s) ? ['pallet-truck'] : ['pallet-truck', 'stacker']);
      else if (/engine|motor|machine|\bdies?\b|mou?ld|gearbox|component|heavy\s*parts|container/.test(s) && lift) r.types = ['floor-crane', 'gantry'];
      else if (lift && (r.kg != null || /lifting|lift/.test(s))) r.types = LIFT_POOL.slice();
      else if (MOVE_VERB.test(s) && r.kg != null) r.types = MOVE_POOL.slice();
    }
    r.types = uniq(r.types);
    return r;
  }

  /* ---------------------------------------------------------------- matching against documented data */
  function opOk(itemOp, op) {
    if (!op) return true;
    if (!itemOp || /push/i.test(itemOp)) return false;          // wheels & trolleys have no powered option
    if (op === 'manual') return itemOp === 'Manual';
    if (op === 'ac') return /\bAC\b/.test(itemOp);
    if (op === 'dc') return /\bDC\b/.test(itemOp);
    if (op === 'battery') return /\bDC\b/.test(itemOp) || itemOp === 'Fully Electric';
    if (op === 'fully') return itemOp === 'Fully Electric';
    if (op === 'semi') return /^Semi-Electric/.test(itemOp);
    return itemOp !== 'Manual' && /Electric|Electro/.test(itemOp);   // 'electric'
  }
  function fit(it, q) {
    var c = it.cfg.slice(), checked = false;
    if (q.kg != null) {
      if (it.unit === 'per-caster') {
        // a wheel rating is per wheel: only compared when the customer gave a per-wheel load
        if (q.perWheel) { c = c.filter(function (x) { return x[0] >= q.kg; }); checked = true; }
      } else if (it.unit !== 'total' || !c.length) return null;               // cannot verify the load
      else { c = c.filter(function (x) { return x[0] >= q.kg; }); checked = true; }
    }
    if (q.mm != null) {
      if (!it.hl) return null;                                                 // no documented lifting height
      c = c.filter(function (x) { return x[1] != null && x[1] >= q.mm; });
      checked = true;
    }
    if (checked) {
      if (!c.length) return null;
      c.sort(function (a, b) { return (a[0] - b[0]) || ((a[1] || 0) - (b[1] || 0)); });
    }
    return { it: it, best: checked ? c[0] : null };
  }
  function match(items, q) {
    var pool;
    if (q.wheel && q.perWheel && q.kg != null) {
      // a per-wheel load: individual wheel sizes (smallest that carries it), or the whole range where sizes aren't listed
      pool = items.filter(function (it) {
        return q.wheel.some(function (w) { return it.t === w.replace('wheel-', 'wheelsize-'); }) ||
          (q.wheel.indexOf(it.t) >= 0 && /pallet-truck|ms-track/.test(it.t));
      });
    } else {
      pool = items.filter(function (it) {
        return q.types.indexOf(it.t) >= 0 && !(it.spm && !q.custom);   // built-to-order variants only when asked for
      });
    }
    var byOp = pool.filter(function (it) { return opOk(it.op, q.op); });
    var fits = byOp.map(function (it) { return fit(it, q); }).filter(Boolean);
    fits.sort(function (a, b) {
      var ra = a.best && q.kg ? a.best[0] / q.kg : 1, rb = b.best && q.kg ? b.best[0] / q.kg : 1;
      var ha = a.best && q.mm ? a.best[1] / q.mm : 1, hb = b.best && q.mm ? b.best[1] / q.mm : 1;
      return (q.types.indexOf(a.it.t) - q.types.indexOf(b.it.t)) * (q.inferred ? 1 : 0) || (ra - rb) || (ha - hb) || (a.it.i - b.it.i);
    });
    // up to three, spread across operating types (or product types) before repeating one
    var exactOp = q.op === 'manual' || q.op === 'ac' || q.op === 'dc' || q.op === 'fully';
    var key = function (f) { return exactOp || !f.it.op || /push/.test(f.it.op) ? f.it.t : f.it.op; };
    var picked = [], seen = {};
    fits.forEach(function (f) { if (picked.length < 3 && !seen[key(f)]) { seen[key(f)] = 1; picked.push(f); } });
    fits.forEach(function (f) { if (picked.length < 3 && picked.indexOf(f) < 0) picked.push(f); });
    return { pool: pool, byOp: byOp, fits: fits, picked: picked };
  }

  /* ---------------------------------------------------------------- one follow-up question, when it matters */
  var OP_CHIPS = [['Manual', 'manual operation'], ['Semi-electric AC', 'semi-electric AC operation'], ['Semi-electric DC (battery)', 'semi-electric DC operation'], ['Fully electric', 'fully electric operation']];
  function question(q, res) {
    var f = res.picked;
    var lifting = f.some(function (x) { return x.it.lift; });
    var ops = uniq(f.map(function (x) { return x.it.op; }).filter(function (o) { return o && !/push/.test(o); }));
    var hgts = uniq([].concat.apply([], f.map(function (x) { return x.it.cfg.map(function (c) { return c[1]; }); })));
    if (q.wheel && !(q.kg != null && q.perWheel)) return { k: 'wheel', q: 'What load should each wheel or castor carry?', ph: 'e.g. 300 kg per wheel' };
    if (q.kg == null && (lifting || f.some(function (x) { return x.it.c === 'trolley' || /pallet-truck/.test(x.it.t); })))
      return { k: 'kg', q: f.some(function (x) { return x.it.c === 'trolley'; }) ? 'What total load must the trolley carry?' : 'What load capacity do you require?', ph: 'e.g. 500 kg' };
    if (q.mm == null && lifting && hgts.length > 1) return { k: 'mm', q: 'What lifting height do you need?', ph: 'e.g. 2.5 m' };
    if (!q.op && ops.length > 1) return { k: 'op', q: 'Do you require manual or electric operation?', chips: OP_CHIPS };
    if (/^(electric|semi|battery)$/.test(q.op || '') && ops.length > 1)
      return { k: 'op', q: 'Which type of electric operation do you need?', chips: OP_CHIPS.slice(1) };
    return null;
  }

  /* ---------------------------------------------------------------- rendering */
  function specLine(it) {
    var kgs = uniq(it.cfg.map(function (c) { return c[0]; })).sort(function (a, b) { return a - b; });
    var hs = uniq(it.cfg.map(function (c) { return c[1]; })).sort(function (a, b) { return a - b; });
    var p = [];
    if (it.unit === 'per-caster') p.push('Load per wheel: ' + (it.range ? kgs[0] + '–' + fmtKg(kgs[kgs.length - 1]) : fmtKg(kgs[0])));
    else if (kgs.length) p.push('Capacity: ' + kgs.join(' / ') + ' kg');
    else if (it.ct) p.push('Capacity: ' + it.ct);
    if (hs.length && it.hl) p.push(it.hl.charAt(0).toUpperCase() + it.hl.slice(1) + ': ' + hs.map(fmtH).join(' / '));
    if (it.op && !/push/.test(it.op)) p.push(it.op);
    return p.join(' · ');
  }
  function why(f, q) {
    var it = f.it, b = f.best, t = [];
    if (b && it.unit === 'per-caster') t.push((it.range ? 'This range includes sizes rated up to ' : 'Rated ') + fmtKg(b[0]) + ' per wheel — meets the ' + fmtKg(q.kg) + ' per wheel you mentioned.');
    else if (b) {
      var all = uniq(it.cfg.map(function (c) { return c[0]; }));
      t.push('Documented configuration: ' + fmtKg(b[0]) + (b[1] && it.hl && q.mm != null ? ' with ' + fmtH(b[1]) + ' ' + it.hl : '') +
        ' — meets the ' + [q.kg != null ? fmtKg(q.kg) + ' load' : '', q.mm != null ? fmtH(q.mm) + ' height' : ''].filter(Boolean).join(' and ') + ' you mentioned.');
      if (q.kg != null && all.length === 1 && b[0] > q.kg) t.push('Offered in ' + fmtKg(b[0]) + ' capacity only.');
    } else t.push('Matches the type of equipment you described.');
    if (it.unit === 'per-caster' && !q.perWheel) t.push('Ratings are per wheel or castor, not for the whole trolley.');
    return t.join(' ');
  }
  function card(f, i, q) {
    var it = f.it;
    return '<article class="sf-card">' +
      (it.img ? '<img src="' + esc(it.img) + '" alt="" width="84" height="84" loading="lazy">' : '<span class="sf-noimg" aria-hidden="true"></span>') +
      '<div class="sf-card-body"><h3>' + esc(it.n) + '</h3><p class="sf-spec">' + esc(specLine(it)) + '</p>' +
      '<p class="sf-why">' + esc(why(f, q)) + '</p>' +
      '<div class="sf-acts"><a class="sf-view" href="' + esc(it.u) + '">View product &rarr;</a>' +
      '<button type="button" class="sf-enq-btn" data-pick="' + i + '">Enquire now</button></div></div></article>';
  }
  function contactBar(lead) {
    return '<div class="sf-contact">' + (lead ? '<p>' + lead + '</p>' : '') +
      '<div class="sf-contact-btns"><button type="button" class="sf-send" data-send>Send my requirement</button>' +
      '<a class="sf-wa" href="' + esc(waLink()) + '" target="_blank" rel="noopener">WhatsApp our team</a></div></div>';
  }
  function askHtml(qn) {
    if (!qn) return '';
    return '<div class="sf-ask"><p class="sf-ask-q">' + esc(qn.q) + '</p>' +
      (qn.chips ? '<div class="sf-chips">' + qn.chips.map(function (c) { return '<button type="button" data-clar="' + esc(c[1]) + '">' + esc(c[0]) + '</button>'; }).join('') + '</div>' :
        '<form class="sf-clar" data-k="' + qn.k + '"><input type="text" maxlength="120" placeholder="' + esc(qn.ph || '') + '" aria-label="' + esc(qn.q) + '"><button type="submit">Update</button></form>') +
      '<p class="sf-ask-skip">Or skip this and send your requirement to our team below.</p></div>';
  }
  var NOMATCH = "We couldn't identify an exact match from our online catalogue. Please share your requirement with our team, and we'll review it to confirm whether we can help.";

  function maxOf(items, types) {
    var m = 0;
    items.forEach(function (it) { if (types.indexOf(it.t) >= 0 && it.unit === 'total') it.cfg.forEach(function (c) { if (c[0] > m) m = c[0]; }); });
    return m;
  }

  function run() {
    var text = [state.orig].concat(state.clar).join('. ');
    var q = parse(text);
    state.pick = null;
    state.view = null;
    var items = state.items, html = '', res = null;
    var head = '<p class="sf-for">Your requirement: <q>' + esc(state.orig) + '</q>' +
      (state.clar.length ? ' <span>+ ' + esc(state.clar.join('; ')) + '</span>' : '') + '</p>';
    if (!q.types.length) {
      if (CONTEXT.test(q.s) || q.kg != null) {
        html = head + askHtml({ k: 'what', q: 'What do you need to lift or move — for example pallets, drums, machine parts or boxes — and roughly how heavy is it?', ph: 'e.g. 800 kg machine parts' }) + contactBar('');
        state.view = 'clarify';
      } else {
        html = head + '<div class="sf-none"><p>' + esc(NOMATCH) + '</p></div>' + contactBar('');
        state.view = 'none';
      }
    } else {
      res = match(items, q);
      state.res = res;
      if (!res.picked.length) {
        var hint = '';
        var mx = maxOf(items, q.types);
        var mh = 0;
        items.forEach(function (it) { if (q.types.indexOf(it.t) >= 0 && it.hl) it.cfg.forEach(function (c) { if (c[1] > mh) mh = c[1]; }); });
        if (q.kg != null && mx && mx < q.kg && !q.wheel) hint = ' For reference, the highest documented capacity for this type of equipment in our online catalogue is ' + fmtKg(mx) + '.';
        else if (q.mm != null && mh && mh < q.mm) hint = ' For reference, the highest documented lifting height for this type of equipment in our online catalogue is ' + fmtH(mh) + '.';
        html = head + '<div class="sf-none"><p>' + esc(NOMATCH + hint) + '</p></div>' + contactBar('');
        state.view = 'none';
      } else {
        var qn = question(q, res);
        if (qn && state.asked[qn.k]) qn = null;             // never ask the same question twice
        if (qn) state.asked[qn.k] = 1;
        html = head + '<h3 class="sf-h">Suggested products</h3><div class="sf-cards">' + res.picked.map(function (f, i) { return card(f, i, q); }).join('') + '</div>' +
          '<p class="sf-disclaimer">These are suggestions based on the specifications in our online catalogue and the details you gave &mdash; not a confirmation of engineering suitability. Our team will confirm the right model and configuration for your application.</p>' +
          askHtml(qn) + contactBar('Not sure, or need something different? Our team will review your requirement.');
        state.view = 'match';
      }
    }
    out.innerHTML = html + '<div class="sf-enq-slot"></div>';
    out.hidden = false;
    state.q = q;
  }

  function show(msgHtml) { out.innerHTML = msgHtml; out.hidden = false; }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var t = input.value.replace(/\s+/g, ' ').trim();
    if (t.length < 3) { input.focus(); return; }
    state.orig = input.value.trim();
    state.clar = []; state.asked = {}; state.lastSig = '';
    show('<p class="sf-loading">Checking our catalogue&hellip;</p>');
    loadData().then(function (items) {
      state.items = items;
      run();
    }).catch(function () {
      state.items = [];
      show('<p class="sf-for">Your requirement: <q>' + esc(state.orig) + '</q></p><div class="sf-none"><p>The product finder could not load just now. Please share your requirement with our team and we will review it.</p></div>' + contactBar('') + '<div class="sf-enq-slot"></div>');
    });
    out.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  });
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); form.requestSubmit ? form.requestSubmit() : form.dispatchEvent(new Event('submit', { cancelable: true })); }
  });

  out.addEventListener('click', function (e) {
    var b = e.target.closest('button');
    if (!b) return;
    if (b.hasAttribute('data-clar')) { state.clar.push(b.getAttribute('data-clar')); run(); return; }
    if (b.hasAttribute('data-pick')) { state.pick = state.res.picked[+b.getAttribute('data-pick')].it; openEnq(); return; }
    if (b.hasAttribute('data-send')) { state.pick = null; openEnq(); return; }
  });
  out.addEventListener('submit', function (e) {
    var f = e.target;
    if (f.classList.contains('sf-clar')) {
      e.preventDefault();
      var v = f.querySelector('input').value.trim();
      if (!v) return;
      state.clar.push(v);
      run();
    } else if (f.classList.contains('sf-enq')) { e.preventDefault(); sendEnq(f); }
  });

  /* ---------------------------------------------------------------- WhatsApp & enquiry (Web3Forms) */
  function waText() {
    var t = 'Hello Kotibhaskar Industries, I have a material handling requirement (from kotibhaskarindustries.com):\n' + state.orig;
    if (state.clar.length) t += '\nMore details: ' + state.clar.join('; ');
    if (state.pick) t += '\nProduct I am interested in: ' + state.pick.n + ' (' + SITE + state.pick.u + ')';
    return t;
  }
  function waLink() { return 'https://wa.me/' + WA + '?text=' + encodeURIComponent(waText()); }

  function openEnq() {
    var slot = out.querySelector('.sf-enq-slot');
    var keep = {};
    var old = slot.querySelector('form');
    if (old) ['name', 'phone', 'email', 'company', 'city'].forEach(function (n) { keep[n] = old.elements[n].value; });
    slot.innerHTML = '<form class="sf-enq" novalidate>' +
      '<h3 class="sf-h">Send your requirement to our team</h3>' +
      '<p class="sf-enq-sum"><b>Requirement:</b> ' + esc(state.orig) + (state.clar.length ? '<br><b>More details:</b> ' + esc(state.clar.join('; ')) : '') +
      (state.pick ? '<br><b>Product:</b> ' + esc(state.pick.n) : '') + '</p>' +
      '<div class="sf-grid">' +
      fld('name', 'Your name', 'text', true, 'name') + fld('phone', 'Phone number', 'tel', true, 'tel') +
      fld('email', 'Email address', 'email', true, 'email') + fld('company', 'Company name (optional)', 'text', false, 'organization') +
      fld('city', 'Delivery city / location (optional)', 'text', false, 'address-level2') + '</div>' +
      '<input type="checkbox" name="botcheck" class="sf-hp" tabindex="-1" autocomplete="off" aria-hidden="true">' +
      '<div class="sf-enq-row"><button type="submit" class="sf-submit">Send requirement</button>' +
      '<a class="sf-wa" href="' + esc(waLink()) + '" target="_blank" rel="noopener">WhatsApp instead</a></div>' +
      '<p class="sf-status" role="status" aria-live="polite"></p></form>';
    var f = slot.querySelector('form');
    Object.keys(keep).forEach(function (n) { f.elements[n].value = keep[n]; });
    // keep every WhatsApp link in the results in step with the chosen product
    out.querySelectorAll('a.sf-wa').forEach(function (a) { a.href = waLink(); });
    f.elements.name.focus({ preventScroll: true });
    f.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
  function fld(n, label, type, req, ac) {
    return '<label class="sf-f"><span>' + label + (req ? ' <i aria-hidden="true">*</i>' : '') + '</span>' +
      '<input name="' + n + '" type="' + type + '" autocomplete="' + ac + '"' + (req ? ' required' : '') + ' maxlength="120"></label>';
  }
  function status(f, html, err) { var s = f.querySelector('.sf-status'); s.innerHTML = html; s.className = 'sf-status show' + (err ? ' error' : ''); }

  function sendEnq(f) {
    if (state.sending) return;
    var v = function (n) { return f.elements[n].value.trim(); };
    var d = { name: v('name'), phone: v('phone'), email: v('email'), company: v('company'), city: v('city') };
    f.querySelectorAll('.invalid').forEach(function (el) { el.classList.remove('invalid'); });
    var digits = d.phone.replace(/\D/g, ''), bad = null;
    if (d.name.length < 2) bad = ['name', 'Please enter your name.'];
    else if (!/^[+()\d\s\-]{7,25}$/.test(d.phone) || digits.length < 7 || digits.length > 15) bad = ['phone', 'Please enter a valid phone number (with country code if outside India).'];
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(d.email)) bad = ['email', 'Please enter a valid email address so we can reply to you.'];
    if (bad) { f.elements[bad[0]].classList.add('invalid'); f.elements[bad[0]].focus(); status(f, esc(bad[1]), true); return; }
    if (f.elements.botcheck.checked) return;
    if (!KEY) { status(f, failHtml(), true); return; }
    var sig = [d.name, d.phone, d.email, state.orig, state.clar.join(';'), state.pick ? state.pick.u : ''].join('|');
    if (sig === state.lastSig) { status(f, 'This requirement has already been sent. Our team will contact you shortly.', false); return; }
    var q = state.q || {};
    var summary = state.view === 'match' ? 'Suggested: ' + state.res.picked.map(function (x) { return x.it.n; }).join(', ') :
      state.view === 'clarify' ? 'Finder asked for more details' : 'No catalogue match found by the finder';
    var payload = {
      access_key: KEY,
      subject: 'Website Requirement (Solution Finder): ' + (state.pick ? state.pick.n : state.orig.slice(0, 60)) + ' — ' + d.name + (d.company ? ' (' + d.company + ')' : ''),
      from_name: 'Kotibhaskar Website — Solution Finder',
      replyto: d.email,
      name: d.name, email: d.email, phone: d.phone, company: d.company || '—', delivery_location: d.city || '—',
      requirement_as_entered: state.orig,
      clarification: state.clar.length ? state.clar.join('; ') : '—',
      suggested_product: state.pick ? state.pick.n : '—',
      product_page: state.pick ? SITE + state.pick.u : '—',
      finder_result: summary,
      understood: [q.kg != null ? 'load ' + fmtKg(q.kg) + (q.perWheel ? ' per wheel' : '') : '', q.mm != null ? 'height ' + fmtH(q.mm) : '', q.op ? 'operation: ' + q.op : ''].filter(Boolean).join(', ') || '—',
      message: 'Requirement (as entered): ' + state.orig + (state.clar.length ? '\nMore details: ' + state.clar.join('; ') : '') +
        (state.pick ? '\nProduct selected: ' + state.pick.n + ' — ' + SITE + state.pick.u : '') + (d.city ? '\nDelivery location: ' + d.city : ''),
      submitted_at: new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' }) + ' IST',
      sent_from: location.origin + location.pathname + ' (Solution Finder)',
      botcheck: false
    };
    var btn = f.querySelector('.sf-submit'), label = btn.innerHTML;
    state.sending = true; btn.disabled = true; btn.innerHTML = 'Sending&hellip;';
    status(f, 'Sending your requirement&hellip;', false);
    var ctrl = 'AbortController' in window ? new AbortController() : null;
    var timer = setTimeout(function () { if (ctrl) ctrl.abort(); }, CFG.timeoutMs || 20000);
    fetch(EP, { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(payload), signal: ctrl ? ctrl.signal : undefined })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (r) {
        if (r.ok && r.j && r.j.success === true) {          // success ONLY when Web3Forms confirms
          state.lastSig = sig;
          f.outerHTML = '<div class="sf-done" role="status"><b>Thank you, ' + esc(d.name) + '.</b> Your requirement has been received by Kotibhaskar Industries. Our team will contact you at ' + esc(d.email) + ' or ' + esc(d.phone) + '.</div>';
        } else status(f, failHtml(), true);
      })
      .catch(function () { status(f, failHtml(), true); })
      .then(function () { clearTimeout(timer); state.sending = false; if (btn.isConnected) { btn.disabled = false; btn.innerHTML = label; } });
  }
  function failHtml() {
    return '<b>Sorry, your requirement could not be sent right now.</b> Your details are still in the form &mdash; please try again, or ' +
      '<a href="' + esc(waLink()) + '" target="_blank" rel="noopener">send it on WhatsApp</a> or <a href="tel:' + PHONE + '">call ' + PHONE_LABEL + '</a>.';
  }

  // test hook for the build checks (no effect on the page)
  window.__sfParse = parse;
  window.__sfMatch = function (text) { return loadData().then(function (items) { var q = parse(text); return { q: q, r: q.types.length ? match(items, q) : null }; }); };
})();
