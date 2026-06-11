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

1. **選模板**：讀 `<skill>/templates/README.md` 的目錄表（含
   `memory/` 學習用表分組），選最接近的模板。任務是週報→
   `status-a4`、報價→`quote-a4`、SWOT→`swot-a4`……沒有完全
   對應的也選結構最近的改。
2. **複製改內容**：每個模板開頭的 HTML 註解寫了「給 AI 的指示」，
   照做。**`<head>` 內字型設定一個字都不能動。**
3. **要圖表才做這步**：讀 `<skill>/infographic/catalog.md`，查
   `templates.json` 選模板名，寫 syntax 後跑
   `python3 <skill>/infographic/make-svg.py 檔.syntax`，
   產出的 SVG 內嵌進 HTML（外層 CSS 必加 `max-height: 110mm`）。
4. **實印驗證（必做，grep 不算驗證）**：
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
| 風格加漸層、emoji、圓角卡片 | 本庫是克制的編輯式風格，沿用模板既有樣式 |

## 維護：與開發 repo 同步

資產有兩份：`/Users/yaxin/html-demo` 是開發測試場（含 batch-test.py
回歸測試），本 skill 目錄是發行副本。在 repo 新增模板、升級 bundle
或重跑批次測試後，執行同步：

```bash
cp -R /Users/yaxin/html-demo/templates/ ~/.claude/skills/printable-docs/templates/
cp /Users/yaxin/html-demo/antv-test/{make-svg.py,templates.json,preview.html} ~/.claude/skills/printable-docs/infographic/
cp /Users/yaxin/html-demo/antv-test/vendor/infographic.min.js ~/.claude/skills/printable-docs/infographic/vendor/
```

**`catalog.md` 不可直接覆蓋**——skill 內這份的路徑已改寫成相對引用
（`antv-test/make-svg.py` → `make-svg.py`）。repo 版有內容更新時，
複製過來後需重做同樣的路徑替換。
