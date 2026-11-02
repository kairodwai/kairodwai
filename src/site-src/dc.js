/* ขายรถไว — ตัวแสดงผลหน้าเว็บ (อ่าน template + logic แล้ววาดด้วย Preact) */
(function () {
  var P = window.preact, h = P.h;
  var tplEl = document.getElementById('dc-tpl');
  var logicEl = document.getElementById('dc-logic');
  var root = document.getElementById('root');
  if (!tplEl || !root) return;

  var HOLE = /\{\{\s*([^}]*?)\s*\}\}/g;

  function lookup(path, vals, scope) {
    if (path === 'true') return true;
    if (path === 'false') return false;
    if (path === 'null') return null;
    if (/^-?\d+(\.\d+)?$/.test(path)) return Number(path);
    if (/^(['"]).*\1$/.test(path)) return path.slice(1, -1);
    var parts = path.split('.'), head = parts[0], v;
    if (scope && Object.prototype.hasOwnProperty.call(scope, head)) v = scope[head];
    else v = vals ? vals[head] : undefined;
    for (var i = 1; i < parts.length && v != null; i++) v = v[parts[i]];
    return v;
  }
  function str(v) { return v == null || v === false ? '' : String(v); }

  function build(list, vals, scope, out) {
    for (var i = 0; i < list.length; i++) {
      var c = list[i];
      if (c.k === 't') out.push(c.v);
      else if (c.k === 'x') {
        if (c.parts.length === 1 && typeof c.parts[0] === 'object') out.push(str(lookup(c.parts[0].p, vals, scope)));
        else out.push(c.parts.map(function (p) { return typeof p === 'string' ? p : str(lookup(p.p, vals, scope)); }).join(''));
      } else if (c.k === 'if') { if (lookup(c.p, vals, scope)) build(c.kids, vals, scope, out); }
      else if (c.k === 'for') {
        var arr = lookup(c.p, vals, scope) || [];
        for (var ix = 0; ix < arr.length; ix++) {
          var sc = Object.create(scope || null); sc[c.as] = arr[ix]; sc.$index = ix;
          build(c.kids, vals, sc, out);
        }
      } else if (c.k === 'e') {
        var props = {};
        for (var a = 0; a < c.attrs.length; a++) {
          var at = c.attrs[a];
          if ('v' in at) props[at.n] = at.v;
          else if ('p' in at) props[at.n] = lookup(at.p, vals, scope);
          else props[at.n] = at.s.replace(HOLE, function (_, p) { return str(lookup(p, vals, scope)); });
        }
        var kids = []; build(c.kids, vals, scope, kids);
        out.push(h.apply(null, [c.tag, props].concat(kids)));
      }
    }
    return out;
  }

  var tree = JSON.parse(tplEl.textContent);

  window.DCLogic = function DCLogic(props) { P.Component.call(this, props); };
  window.DCLogic.prototype = Object.create(P.Component.prototype);
  window.DCLogic.prototype.constructor = window.DCLogic;
  window.DCLogic.prototype.render = function () {
    var vals = (this.renderVals && this.renderVals()) || {};
    return h(P.Fragment, null, build(tree, vals, null, []));
  };

  var Comp;
  try {
    var code = logicEl ? logicEl.textContent : 'class Component extends DCLogic { renderVals() { return {}; } }';
    Comp = new Function('DCLogic', code + '\n;return Component;')(window.DCLogic);
  } catch (e) { console.error(e); return; }
  root.textContent = '';
  P.render(h(Comp, {}), root);
  document.documentElement.classList.add('dc-ready');
})();
