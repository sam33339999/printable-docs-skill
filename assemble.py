#!/usr/bin/env python3
"""
assemble.py — 把 pages/*.html 組裝成單一可列印 HTML

用法：
  python3 assemble.py <專案目錄>          # 輸出 <專案目錄>/output.html
  python3 assemble.py <專案目錄> -o 成果.html

專案目錄結構：
  _shell.html      ← <head> + CSS + <body>，留 <!-- PAGES --> 佔位符
  pages/
    01-cover.html  ← 只有那頁的 HTML 片段（無 <html>/<head>/<body>）
    02-exec.html
    …
  output.html      ← 組裝結果（此腳本產生）

更新單頁：只改 pages/XX-xxx.html，再重跑此腳本即可。
"""
import argparse, sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="把 pages/*.html 組裝進 _shell.html 產出單一 HTML"
    )
    parser.add_argument("project", help="專案目錄（含 _shell.html 和 pages/）")
    parser.add_argument("-o", "--output", default="output.html",
                        help="輸出檔名（預設 output.html）")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    shell_path = project / "_shell.html"
    pages_dir = project / "pages"

    if not shell_path.exists():
        sys.exit(f"找不到 {shell_path}，請先建立 _shell.html")
    if not pages_dir.is_dir():
        sys.exit(f"找不到 {pages_dir}/ 目錄，請先建立 pages/ 並放入頁面片段")

    shell = shell_path.read_text(encoding="utf-8")
    if "<!-- PAGES -->" not in shell:
        sys.exit("_shell.html 內找不到 <!-- PAGES --> 佔位符")

    page_files = sorted(pages_dir.glob("*.html"))
    if not page_files:
        sys.exit(f"{pages_dir}/ 內沒有 .html 檔案")

    parts = []
    for i, f in enumerate(page_files):
        content = f.read_text(encoding="utf-8").strip()
        # 第一頁不加 break-before，後續頁加
        break_attr = ' style="break-before:page"' if i > 0 else ""
        parts.append(
            f'<!-- PAGE: {f.stem} -->\n'
            f'<div class="doc-page"{break_attr}>\n{content}\n</div>\n'
            f'<!-- /PAGE: {f.stem} -->'
        )

    assembled = shell.replace("<!-- PAGES -->", "\n".join(parts))

    out_path = project / args.output
    out_path.write_text(assembled, encoding="utf-8")
    print(f"✓ 組裝完成 → {out_path}  ({len(page_files)} 個頁面片段)")


if __name__ == "__main__":
    main()
