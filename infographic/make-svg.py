#!/usr/bin/env python3
"""AntV Infographic syntax → 乾淨可內嵌的 SVG（agent 取用入口）。

用法：
  python3 make-svg.py input.syntax              # 輸出 input.svg
  python3 make-svg.py input.syntax -o out.svg
  echo "infographic ..." | python3 make-svg.py - -o out.svg
  python3 make-svg.py input.syntax --width 760 --height 460

syntax 檔範例（模板名查 templates.json，資料形狀看 data_shape 欄）：
  infographic sequence-steps-simple
  data
    lists
      - label 需求訪談
        desc 確認範圍
      - label 撰寫初稿
        desc 套用模板

產出的 SVG 已做三件事（缺一不可，原因見 catalog.md）：
  1. 字型由 Alibaba PuHuiTi 換成 Noto Sans TC 字型鏈（避開 PingFang PDF 坑）
  2. 移除編輯器按鈕 defs
  3. 版面檢查：量測文字真實矩形，相撞時若是 plain-text 標籤換行溢出
     會自動加 lineNumber 重渲染（stderr 印 auto-fit 通知）；修不了
     就帶明細報錯退出——此時請縮短 label（chart 類 ≤ 8 個全形字）
內嵌進 A4 時記得：figure svg { width:100%; height:auto; max-height:110mm; }
回歸測試：python3 tests/test-overlap.py（獨立量測產出物，新增案例丟 tests/*.syntax）
"""
import argparse, html, json, re, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
BUNDLE = HERE / "vendor/infographic.min.js"
FONT = "'Noto Sans TC', 'Heiti TC', 'Arial Unicode MS', 'Microsoft JhengHei', sans-serif"

# 渲染後在頁內量測文字真實矩形是否相撞／溢出畫布。
# 標籤（foreignObject）宣告框是固定的（如 chart 類 120x20、overflow:visible），
# 長標籤換行會外溢壓到下一列——所以用 Range 量實際行框，不能信宣告框。
# 可修時自動以模板原 item props + lineNumber 重渲染（列高隨 item 高度撐開）。
PAGE_JS = r"""
const SYNTAX = __SYNTAX__;
function render(design) {
  const old = document.getElementById('c');
  if (old) old.remove();
  const div = document.createElement('div');
  div.id = 'c';
  div.style.width = '__W__px';
  div.style.height = '__H__px';
  document.body.prepend(div);
  const opts = {container: '#c', width: '100%', height: '100%'};
  if (design) opts.design = design;
  try {
    new AntVInfographic.Infographic(opts).render(SYNTAX);
  } catch (e) { document.getElementById('err').textContent = String(e); }
}
function measure() {
  const svg = document.querySelector('#c svg');
  if (!svg) return null;
  const boxes = [];
  for (const t of svg.querySelectorAll('text')) {
    const r = t.getBoundingClientRect();
    if (r.width > 0 && r.height > 0)
      boxes.push({r, s: (t.textContent || '').trim().slice(0, 18)});
  }
  const labels = [];
  for (const fo of svg.querySelectorAll('foreignObject')) {
    const span = fo.firstElementChild;
    if (!span || !(span.textContent || '').trim()) continue;
    const rg = document.createRange();
    rg.selectNodeContents(span);
    const r = rg.getBoundingClientRect();
    if (r.width > 0 && r.height > 0)
      boxes.push({r, s: span.textContent.trim().slice(0, 18)});
    if (fo.getAttribute('data-element-type') === 'item-label') {
      const h = parseFloat(fo.getAttribute('height')) || 0;
      const fs = parseFloat(getComputedStyle(span).fontSize) || 14;
      labels.push({over: span.scrollHeight > h + 2,
                   need: Math.max(2, Math.round(span.scrollHeight / (fs * 1.4)))});
    }
  }
  const bad = [];
  for (let i = 0; i < boxes.length; i++)
    for (let j = i + 1; j < boxes.length; j++) {
      const a = boxes[i].r, b = boxes[j].r;
      const w = Math.min(a.right, b.right) - Math.max(a.left, b.left);
      const h = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
      if (w <= 0 || h <= 0) continue;
      if (w * h > 0.2 * Math.min(a.width * a.height, b.width * b.height))
        bad.push(boxes[i].s + ' ⊗ ' + boxes[j].s);
    }
  const over = labels.filter(l => l.over);
  return {bad, needLines: over.length ? Math.max(...over.map(l => l.need)) : 0};
}
const out = {ok: false, fix: null, bad: []};
function finish(m) {
  out.ok = !!m && m.bad.length === 0;
  out.bad = m ? m.bad : ['render failed'];
  document.getElementById('check').textContent = JSON.stringify(out);
}
render(null);
setTimeout(() => {
  const m = measure();
  if (!m || m.bad.length === 0 || m.needLines < 2) { finish(m); return; }
  const name = (SYNTAX.match(/^\s*infographic\s+(\S+)/m) || [])[1];
  const tpl = name && AntVInfographic.getTemplate(name);
  const base = tpl && tpl.design &&
    (tpl.design.item || (tpl.design.items || [])[0]);
  if (!base || base.type !== 'plain-text') { finish(m); return; }
  out.fix = {lineNumber: m.needLines};
  render({item: Object.assign({}, base, {lineNumber: m.needLines})});
  setTimeout(() => finish(measure()), 2500);
}, 2500);
"""


def render(syntax: str, width: int, height: int) -> str:
    js = (PAGE_JS.replace("__SYNTAX__", json.dumps(syntax))
                 .replace("__W__", str(width)).replace("__H__", str(height)))
    page = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body>
<pre id="err"></pre><pre id="check"></pre>
<script src="{BUNDLE.as_uri()}"></script>
<script>{js}</script></body></html>"""
    tmp = Path(tempfile.mkdtemp()) / "render.html"
    tmp.write_text(page, encoding="utf-8")
    r = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--virtual-time-budget=15000",
         "--dump-dom", tmp.as_uri()],
        capture_output=True, text=True, timeout=120)
    dom = r.stdout
    err = re.search(r'<pre id="err">([^<]+)</pre>', dom, re.S)
    if err:
        sys.exit(f"render error: {err.group(1).strip()}")
    m = re.search(r'<div id="c"[^>]*>.*?(<svg.*</svg>)', dom, re.S)
    if not m:
        sys.exit("render error: no svg produced（檢查模板名是否存在於 templates.json）")
    chk = re.search(r'<pre id="check">(.+?)</pre>', dom, re.S)
    if not chk:
        sys.exit("render error: 版面檢查未回報（virtual-time 不足？）")
    check = json.loads(html.unescape(chk.group(1)))
    if not check["ok"]:
        sys.exit("layout error: 文字相撞／溢出：" + "；".join(check["bad"]) + "\n"
                 "建議：縮短 label（chart 類 ≤ 8 個全形字）、改寫成兩段、或換模板。")
    if check["fix"]:
        print(f"auto-fit: 標籤過長，已自動改為 {check['fix']['lineNumber']} 行高度"
              "（item lineNumber，列距已撐開）", file=sys.stderr)
    svg = m.group(1)
    svg = svg.replace('font-family="Alibaba PuHuiTi"',
                      'font-family="' + FONT.replace("'", "&#39;") + '"')
    svg = re.sub(r'<defs data-element-type="btn-icon-defs">.*?</defs>', '', svg, flags=re.S)
    return svg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="syntax 檔路徑，- 表示 stdin")
    ap.add_argument("-o", "--output", help="輸出 svg 路徑（預設同名 .svg）")
    ap.add_argument("--width", type=int, default=760)
    ap.add_argument("--height", type=int, default=460)
    a = ap.parse_args()

    if a.input == "-":
        syntax = sys.stdin.read()
        out = Path(a.output or "out.svg")
    else:
        syntax = Path(a.input).read_text(encoding="utf-8")
        out = Path(a.output) if a.output else Path(a.input).with_suffix(".svg")

    svg = render(syntax, a.width, a.height)
    out.write_text(svg, encoding="utf-8")
    print(f"written: {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
