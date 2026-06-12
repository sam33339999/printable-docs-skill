#!/usr/bin/env python3
"""把 HTML 裡的 SVG 佔位符替換成檔案內容（agent 不必讀 SVG 本體）。

用法：
    python3 embed-svg.py 檔.html              # 就地替換
    python3 embed-svg.py 檔.html -o 成品.html  # 保留佔位符原稿另存

HTML 佔位符寫法（路徑相對於 HTML 檔所在目錄，或絕對路徑）：
    <figure><!--SVG: 圖.svg--></figure>

設計原因：SVG 動輒數十 KB，agent 把內容 cat 進上下文再寫回 HTML
會撐爆視窗。正確流程是 make-svg.py 產檔 → HTML 只寫佔位符 →
本腳本在磁碟上替換。外層 CSS 記得加
figure svg { width:100%; height:auto; max-height:110mm; }（缺了會警告）。
"""
import argparse, re, sys
from pathlib import Path

PLACEHOLDER = re.compile(r"<!--\s*SVG:\s*(.+?)\s*-->")


def main():
    ap = argparse.ArgumentParser(description="替換 HTML 內的 <!--SVG: 檔--> 佔位符")
    ap.add_argument("html", help="含佔位符的 HTML 檔")
    ap.add_argument("-o", "--output", help="輸出路徑（預設就地替換）")
    args = ap.parse_args()

    src = Path(args.html)
    html = src.read_text(encoding="utf-8")

    refs = PLACEHOLDER.findall(html)
    if not refs:
        sys.exit(f"{src.name} 找不到任何 <!--SVG: 檔--> 佔位符——"
                 "先在 HTML 裡寫佔位符再跑本腳本，不要手貼 SVG 內容。")

    missing, bad = [], []
    svgs = {}
    for ref in dict.fromkeys(refs):
        p = Path(ref) if Path(ref).is_absolute() else src.parent / ref
        if not p.is_file():
            missing.append(ref)
            continue
        body = p.read_text(encoding="utf-8").strip()
        if not body.startswith("<svg"):
            bad.append(ref)
            continue
        svgs[ref] = body
    if missing or bad:
        msg = []
        if missing:
            msg.append("找不到檔案：" + "、".join(missing))
        if bad:
            msg.append("內容不是 <svg> 開頭（確定是 make-svg.py 產物？）：" + "、".join(bad))
        sys.exit("embed error: " + "；".join(msg))

    out_html = PLACEHOLDER.sub(lambda m: svgs[m.group(1)], html)

    if "max-height" not in html:
        print("警告：HTML 沒看到 max-height——直式版型 SVG 會放大溢出頁面，"
              "外層 CSS 要加 figure svg { width:100%; height:auto; max-height:110mm; }",
              file=sys.stderr)

    dst = Path(args.output) if args.output else src
    dst.write_text(out_html, encoding="utf-8")
    print(f"已嵌入 {len(refs)} 個 SVG（{len(svgs)} 個檔案）→ {dst}")


if __name__ == "__main__":
    main()
