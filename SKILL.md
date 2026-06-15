---
name: printable-docs
description: Use when 要產出可列印成 PDF 的中文 HTML 文件（報告、報價單、合約、會議記錄、表單、履歷、簡報、學習用表）、要在 A4 文件裡加資訊圖表／infographic／流程圖／時間軸，或遇到「列印 PDF 中文消失」問題。觸發詞：印成 PDF、A4 文件、Cmd+P、報價單、週報、infographic。
---

# 可列印中文文件（printable-docs）

## Overview

資產隨附在**本 skill 目錄**（SKILL.md 所在資料夾，以下稱 `<skill>`）：
`<skill>/templates/` 39 張 A4 中文模板、`<skill>/infographic/` 165 個
已測試的資訊圖表模組。核心原則：**永遠從現成模板複製改內容，
不從零寫 HTML**——字型、分頁、版面的坑都已踩平。
（開發源頭在 `/Users/yaxin/html-demo`，若該 repo 存在且較新，
以 repo 為準。）

## 工作流程

### 第零步（最先做）：判斷要不要拆頁

**在選模板、寫任何 HTML 之前**先問這兩個問題：

| 問題 | 是 → |
|---|---|
| 需求裡有「幾頁」「多頁」「季報」「年報」「多章節」「之後還要更新」？ | 直接走拆頁工作流 |
| 內容段落 ≥ 5 個，或明顯會超過 3 頁？ | 直接走拆頁工作流 |

符合任一條件就**立即建 `_shell.html` + `pages/` 目錄**，不要先
產單檔再事後拆。事後拆等於雙倍工作，而且漏的機率很高。

單頁或明確說「一頁」才走下方步驟 1–6。

---

1. **選模板**：讀 `<skill>/templates/README.md` 的目錄表（含
   `memory/` 學習用表分組），選最接近的模板。任務是週報→
   `status-a4`、報價→`quote-a4`、SWOT→`swot-a4`……沒有完全
   對應的也選結構最近的改。
   - **走拆頁工作流時**：把模板的 `<head>` 完整複製到 `_shell.html`，
     body 留 `<!-- PAGES -->` 佔位，頁面內容寫到 `pages/` 裡。
2. **複製改內容**：每個模板開頭的 HTML 註解寫了「給 AI 的指示」，
   照做。**`<head>` 內字型設定一個字都不能動。**
3. **需要多欄版面才做這步**：在 `<style>` 結尾加入格線系統 CSS
   （見下方「格線系統」章節），然後用 `.cols-2`、`.cols-3` 等 class
   包住要並排的內容。
4. **要圖表才做這步**：讀 `<skill>/infographic/catalog.md`，查
   `templates.json` 選模板名，寫 syntax 後跑
   `python3 <skill>/infographic/make-svg.py 檔.syntax -o 圖.svg`。
   內嵌用佔位符，**不要讀 SVG 內容**（多圖會撐爆上下文）：HTML 裡寫
   `<figure><!--SVG: 圖.svg--></figure>`，再跑
   `python3 <skill>/infographic/embed-svg.py 檔.html` 就地替換
   （外層 CSS 必加 `max-height: 110mm`，腳本缺了會警告）。
   chart 類 label 寫在 8 個全形字內；make-svg.py 會量測文字
   相撞，報 layout error 就縮短 label 或換模板（別硬調尺寸，
   內部版面是固定座標）。
5. **走拆頁工作流時**：所有 pages/ 寫完後跑組裝：
   ```bash
   python3 /Users/yaxin/html-demo/assemble.py 專案目錄/
   python3 <skill>/infographic/embed-svg.py 專案目錄/output.html
   ```
   詳見下方「多頁拆頁工作流」章節。
6. **實印驗證（必做，grep 不算驗證）**：
   ```bash
   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
     --headless=new --disable-gpu --no-pdf-header-footer \
     --print-to-pdf=/tmp/check.pdf "file:///絕對路徑/檔案.html"
   ```
   兩項都要做，缺一不可：
   - **數頁數**（sips／截圖只看得到第一頁，溢出永遠在最後一頁）：
     ```bash
     python3 -c "import Quartz,CoreFoundation as CF;p=b'/tmp/check.pdf';u=CF.CFURLCreateFromFileSystemRepresentation(None,p,len(p),False);print(Quartz.CGPDFDocumentGetNumberOfPages(Quartz.CGPDFDocumentCreateWithURL(u)))"
     ```
     單頁模板輸出不是 1 就是溢出：先刪內容、收間距，改完重印重數。
   - **每一頁都轉圖目視**：中文完整、表格沒被攔腰切。

## 格線系統

讓任何模板支援多欄版面，只需在 `<style>` 結尾貼入這段 CSS（不動
`<head>` 字型設定，也不改 `@page`）：

```css
/* ── 格線系統：多欄版面（貼進 <style> 結尾） ────────────── */
:root { --gap: 5mm; }
.cols-2   { display: grid; grid-template-columns: 1fr 1fr;     gap: var(--gap); }
.cols-3   { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: var(--gap); }
.cols-4   { display: grid; grid-template-columns: repeat(4,1fr); gap: var(--gap); }
.cols-2-1 { display: grid; grid-template-columns: 2fr 1fr;     gap: var(--gap); }
.cols-1-2 { display: grid; grid-template-columns: 1fr 2fr;     gap: var(--gap); }
.cols-3-1 { display: grid; grid-template-columns: 3fr 1fr;     gap: var(--gap); }
.cols-2, .cols-3, .cols-4,
.cols-2-1, .cols-1-2, .cols-3-1 {
  align-items: start;
  break-inside: avoid;
  margin-bottom: 1.2rem;
}
/* 欄內 section/div 的底部間距 */
.cols-2 > *, .cols-3 > *, .cols-4 > *,
.cols-2-1 > *, .cols-1-2 > *, .cols-3-1 > * { min-width: 0; }
```

**用法範例**：

```html
<!-- 左主體 2/3 + 右側欄 1/3 -->
<div class="cols-2-1">
  <section>
    <h2>主要內容</h2>
    <p>…</p>
  </section>
  <aside>
    <h3>關鍵數字</h3>
    <p>…</p>
  </aside>
</div>

<!-- 三欄 KPI 卡 -->
<div class="cols-3">
  <div><p class="kicker">營收</p><p class="big-num">$2.4M</p></div>
  <div><p class="kicker">成長率</p><p class="big-num">+18%</p></div>
  <div><p class="kicker">客戶數</p><p class="big-num">342</p></div>
</div>
```

**注意**：
- 格線容器加了 `break-inside: avoid`，整塊不會被分頁切斷；若欄位
  內容超過半頁就別用 avoid，改用自然分頁。
- 欄寬以 A4 type area（174mm）為基準，`--gap: 5mm` 在三欄以內都
  夠用；四欄以上建議改 `--gap: 3mm`。
- infographic 圖表放進格線欄時，外層的 `max-height` 要對應欄寬
  縮小（`cols-2` 用 `80mm`，`cols-3` 用 `50mm`）。

## 多頁拆頁工作流

**適用時機**：文件頁數 5 頁以上，且日後需要獨立更新某幾頁。

```
專案目錄/
├── _shell.html          ← <head> + 共用 CSS + <body>，留 <!-- PAGES --> 佔位
├── pages/
│   ├── 01-cover.html    ← 只有封面內容（無 <html>/<head>/<body> 標籤）
│   ├── 02-exec.html     ← 執行摘要
│   ├── 03-financial.html
│   └── …
└── output.html          ← assemble.py 產生，提交 PDF 用
```

**組裝指令**：

```bash
python3 /Users/yaxin/html-demo/assemble.py 專案目錄/
# 輸出 專案目錄/output.html
```

**`_shell.html` 最小結構**：

```html
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8">
  <!-- 從最接近的模板複製整個 <head>，包含字型與 CSS -->
  <!-- 把格線系統 CSS 也貼在這裡 -->
</head>
<body>
<!-- PAGES -->
</body>
</html>
```

**更新單頁流程**：

1. 只改 `pages/02-exec.html`（幾十行，不用讀整份文件）
2. `python3 assemble.py 專案目錄/`
3. 實印 PDF 驗證那幾頁

**注意**：
- 後續頁 assemble 時自動加 `break-before: page`；第一頁不加。
- `_shell.html` 的字型設定照樣不能動，同普通模板規則。
- `output.html` 是生成物，不要手改；要改就改 `pages/` 裡的源頭再重組。

## 鐵則：中文字型（PingFang 坑）

macOS Chrome 列印 PDF 無法嵌入系統字型 PingFang——螢幕正常、PDF
中文整段消失。所有字型鏈必須明確指定可嵌入 fallback：

```css
font-family: 'Noto Sans TC', 'Heiti TC', 'Arial Unicode MS', 'Microsoft JhengHei', sans-serif;
```

禁止 `system-ui`、`-apple-system`、裸 `sans-serif`。內嵌 SVG 同理
（`make-svg.py` 已自動處理，手抽 SVG 要自己換）。

## 常見錯誤

| 錯誤 | 後果／修正 |
|---|---|
| 「需求有點不同，我從零寫比較快」 | 字型分頁全部重踩坑。先複製最近的模板再改 |
| 用 grep／目視 CSS 當驗證 | 不算。必須實印 PDF 開來看 |
| 只看 PDF 第一頁就說「單頁」 | sips 只轉第一頁。先數頁數，再逐頁看 |
| 改動 `<head>` 字型設定 | PDF 中文消失。不能動 |
| 單頁模板印出兩頁就縮字級 | 先刪內容、收間距；字級是最後手段 |
| infographic 用 runtime JS 嵌入 | 破壞單檔自包含。一律預渲染 SVG 內嵌 |
| cat／Read SVG 再貼進 HTML | 多圖撐爆上下文。寫 `<!--SVG: 檔-->` 佔位符後跑 embed-svg.py |
| 風格加漸層、emoji、圓角卡片 | 本庫是克制的編輯式風格，沿用模板既有樣式 |
| 格線容器包超過半頁內容還加 `break-inside:avoid` | 整塊卡住撐出頁面。超過半頁的欄位移除 avoid |
| infographic 放格線欄但沒縮 `max-height` | 圖超寬溢出。cols-2 改 80mm，cols-3 改 50mm |
| 直接改 `output.html` 而非 `pages/` 裡的源頭 | 下次 assemble 蓋掉。只改 pages/ 再重組 |
| 圖表和 table 放同一個 `<section>` | `section { break-inside:avoid }` 把圖＋表整塊鎖住推到下一頁。圖表改用獨立 `<div>`（不套 `<section>`）放在 table 前，讓兩者各自走自然分頁 |
| 直式/漏斗 SVG 在 `cols-2-1` 主欄沒加 inline `max-height` | shell 的 `.cols-2 figure svg { max-height:80mm }` 只管 cols-2，cols-2-1 主欄沒被覆蓋，SVG 等比放大把整欄撐高、note 被推走。每個直式圖的 `<figure>` 加 `style="max-height:XXmm;overflow:hidden"` |

## 維護：與開發 repo 同步

資產有兩份：`/Users/yaxin/html-demo` 是開發源頭（本檔正本在
`skill/SKILL.md`，含 batch-test.py 回歸測試），本 skill 目錄是發行
副本——而且自身是 git repo（remote: sam33339999/printable-docs-skill），
被誤蓋或 git 回退後內容會丟。repo 有更新、或本目錄被打回舊版時，
一鍵同步：

```bash
/Users/yaxin/html-demo/sync-skill.sh
```

腳本會同步 SKILL.md、templates/、infographic 工具鏈與 bundle，
並自動處理 `catalog.md` 的路徑改寫（`antv-test/make-svg.py` →
`make-svg.py`）。**同步後在本目錄 git commit**，之後誤回退也能
從歷史找回。手改本檔等於改到副本，記得回寫 repo 的
`skill/SKILL.md`，否則下次同步會被蓋掉。
