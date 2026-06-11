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

產出的 SVG 已做兩件事（缺一不可，原因見 catalog.md）：
  1. 字型由 Alibaba PuHuiTi 換成 Noto Sans TC 字型鏈（避開 PingFang PDF 坑）
  2. 移除編輯器按鈕 defs
內嵌進 A4 時記得：figure svg { width:100%; height:auto; max-height:110mm; }
"""
import argparse, re, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
BUNDLE = HERE / "vendor/infographic.min.js"
FONT = "'Noto Sans TC', 'Heiti TC', 'Arial Unicode MS', 'Microsoft JhengHei', sans-serif"


def render(syntax: str, width: int, height: int) -> str:
    import json
    page = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>#c{{width:{width}px;height:{height}px}}</style></head><body>
<div id="c"></div><pre id="err"></pre>
<script src="{BUNDLE.as_uri()}"></script>
<script>
try {{
  new AntVInfographic.Infographic({{container:'#c',width:'100%',height:'100%'}})
    .render({json.dumps(syntax)});
}} catch (e) {{ document.getElementById('err').textContent = String(e); }}
</script></body></html>"""
    tmp = Path(tempfile.mkdtemp()) / "render.html"
    tmp.write_text(page, encoding="utf-8")
    r = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--virtual-time-budget=15000",
         "--dump-dom", tmp.as_uri()],
        capture_output=True, text=True, timeout=120)
    dom = r.stdout
    err = re.search(r'<pre id="err">(.+?)</pre>', dom, re.S)
    if err:
        sys.exit(f"render error: {err.group(1).strip()}")
    m = re.search(r'<div id="c">.*?(<svg.*</svg>)', dom, re.S)
    if not m:
        sys.exit("render error: no svg produced（檢查模板名是否存在於 templates.json）")
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
