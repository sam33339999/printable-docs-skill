# printable-docs — 可列印中文 HTML 文件 Skill

產出「HTML → Cmd+P → PDF」的中文 A4 文件：報告、報價單、合約、會議記錄、
表單、履歷、簡報、學習用表，並可在文件裡內嵌資訊圖表（infographic）。

這是一個 [Claude Code Skill](https://docs.claude.com/en/docs/claude-code)，
也可以不靠 AI、直接手動複製模板使用。所有模板都是**單檔自包含**的 HTML，
中文字型已設定為可嵌入 PDF——不會再發生「螢幕正常、印出來中文整段消失」的問題。

## 為什麼需要這個

macOS 上 Chrome 列印 PDF 時**無法嵌入系統中文字型 PingFang**。
任何字型鏈落到 `system-ui`、`-apple-system` 或裸 `sans-serif` 的中文，
螢幕上看起來都正常，但印成 PDF 後會整段消失。

本庫所有模板與 SVG 產製工具都已內建解法——明確指定可嵌入的字型鏈：

```css
font-family: 'Noto Sans TC', 'Heiti TC', 'Arial Unicode MS', 'Microsoft JhengHei', sans-serif;
```

這也是全庫唯一的鐵則：**`<head>` 內的字型設定一個字都不能動。**

## 內容物

```
printable-docs/
├── SKILL.md                 # Claude Code skill 定義（AI 的工作流程與鐵則）
├── templates/               # 39 張 A4 中文模板（31 張通用 + 8 張學習用表）
│   ├── README.md            # 模板總目錄、用法、列印設定
│   └── memory/              # 記憶法系列（康乃爾筆記、錯題本、字卡⋯⋯）
└── infographic/             # 165 個已測試的資訊圖表模組（AntV Infographic）
    ├── catalog.md           # 取用指南、分類表、硬規則
    ├── templates.json       # 機器可讀模板清單（name／category／data_shape）
    ├── make-svg.py          # syntax → 乾淨 SVG 的產製工具
    ├── preview.html         # 165 個模板的視覺總覽（瀏覽器開）
    └── vendor/infographic.min.js  # 本地渲染 bundle（MIT）
```

## 快速開始

### 用法一：當 Claude Code Skill 用

把本目錄放到 skills 路徑（如 `~/.claude/skills/printable-docs/`），
然後直接對 Claude 說需求即可，例如：

> 幫我做一份「××系統導入評估報告」，要能印成 A4 PDF

> 用報價單模板產一份報價，項目是……，最後加一張時程圖

觸發詞：印成 PDF、A4 文件、Cmd+P、報價單、週報、infographic、
「列印 PDF 中文消失」。AI 會自動選模板、改內容、產圖、實印驗證。

### 用法二：手動複製模板

1. 從 `templates/` 複製最接近需求的模板（目錄表見
   [`templates/README.md`](templates/README.md)），改檔名。
2. 每個檔案開頭的 `<!-- ... -->` 註解說明了哪些區塊可以增刪複製。
3. 只改內容，不動 `<head>` 字型設定。
4. Chrome 開啟 → Cmd+P → 另存為 PDF（記得勾「背景圖形」、
   取消「頁首及頁尾」）。

## 模板總覽（39 張）

完整目錄表與列印設定見 [`templates/README.md`](templates/README.md)，分組摘要：

| 分組 | 模板 |
|---|---|
| 報告・文件 | report（技術報告）、proposal（提案／SOW）、spec（PRD／SRS）、uat（驗收測試）、postmortem（事故報告）、8d（問題改善）、esg（永續報告）、sop（標準作業程序） |
| 商務・財務 | quote（報價單）、expense（報銷單）、budget（預算表）、mou（備忘錄／簡式合約）、letter（公函）、press（新聞稿） |
| 會議・專案 | minutes（會議記錄）、agenda（議程）、signin（簽到表）、status（週進度）、worklog（工作日誌）、handover（交接清單） |
| 人資 | resume（履歷）、jd（職位說明書）、interview（面試評估）、review（績效考核）、bullying（職場不法侵害申訴） |
| 分析・圖表式 | swot（SWOT＋TOWS）、bmc（商業模式圖）、iso45001（風險評估矩陣） |
| 其他版面 | slides-16x9（簡報）、certificate（證書／獎狀，橫式） |
| 學習用表 | study-plan（讀書計劃）＋ `memory/` 記憶法系列：review-cycle（遺忘曲線）、mistakes（錯題本）、cornell（康乃爾筆記）、recall（主動回憶）、flashcards（萊特納字卡）、feynman（費曼技巧）、loci（記憶宮殿）、sq3r（SQ3R 閱讀法） |

沒有完全對應的需求，就選結構最接近的模板改——**永遠從現成模板複製，
不從零寫 HTML**，字型、分頁、版面的坑都已踩平。

## Infographic：在 A4 文件裡放資訊圖表

`infographic/` 收錄 165 個基於 [AntV Infographic](https://github.com/antvis)
的圖表模板，全數通過渲染回歸測試。流程是**預渲染 SVG 後內嵌**進 HTML——
不用 runtime JS，成品仍是單檔自包含、離線可印。

### 三步驟

**1. 查表選模板**：讀 [`infographic/catalog.md`](infographic/catalog.md)
與 `templates.json`，依分類挑 `name`、照 `data_shape` 組資料。
也可以直接用瀏覽器開 `preview.html` 視覺挑選。

| 類別 | 數量 | 代表版型 | 適用場景 |
|---|---|---|---|
| sequence | 68 | steps、timeline、roadmap、funnel、pyramid | 流程、里程碑、時程、漏斗 |
| list | 37 | row、column、grid、waterfall、zigzag | 職責清單、交付物 |
| compare | 24 | binary（vs／fold）、quadrant、swot | 方案比較、四象限 |
| chart | 15 | bar、column、line、pie、wordcloud | 預算、佔比、統計 |
| hierarchy | 14 | mindmap、structure、tree | 組織圖、知識架構 |
| relation | 7 | dagre-flow、network、circle | 因果鏈、系統架構 |

**2. 寫 syntax、產 SVG**：

```
infographic sequence-steps-simple
data
  title 導入時程
  lists
    - label 需求訪談
      desc 確認範圍
    - label 撰寫初稿
      desc 套用模板
theme
  colorPrimary #1e4e79
```

```bash
python3 infographic/make-svg.py 檔案.syntax -o 圖.svg
```

`make-svg.py` 會自動把 SVG 內的字型換成可嵌入的 Noto Sans TC 字型鏈
（避開 PingFang PDF 坑），並移除編輯器雜訊。

**3. 內嵌進 HTML**：SVG 直接貼進模板，外層 CSS 必加：

```css
figure svg { width: 100%; height: auto; max-height: 110mm; }
```

### 硬規則（踩過坑的）

- **不要跳過 `make-svg.py`**——手抽的 SVG 寫死了不存在的字型，
  印 PDF 中文會消失。
- **直式版型（timeline、roadmap-vertical 等）必加 `max-height`**，
  否則會放大溢出頁面。
- **正式文件選 `-simple`／`-plain-text` 變體**或用 `theme` 改主色
  `#1e4e79`——預設主題是鮮豔漸層，與模板庫的編輯式風格衝突。
- compare-binary 系列內容要寫在 children；icon 欄位需要連外 API，
  離線或正式交付不要用。

完整規則與各模板註記見 [`infographic/catalog.md`](infographic/catalog.md)。

## 交付前驗證

別只看螢幕，實印一份 PDF 確認：

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --no-pdf-header-footer \
  --print-to-pdf=/tmp/check.pdf "file:///絕對路徑/檔案.html"
open /tmp/check.pdf
```

檢查三件事：**中文完整**（文字可選取）、**頁數正確**（單頁模板印出
兩頁＝內容溢出，先刪內容、收間距，縮字級是最後手段）、
**表格沒被攔腰切**。注意 sips／截圖只看得到第一頁——溢出永遠在最後一頁，
要逐頁看。

## 設計原則

- **單檔自包含**：一個 HTML 就是一份文件，不依賴外部 CSS／JS
  （僅 Google Fonts 需首次連網，離線會落到 Heiti TC 仍可印）。
- **克制的編輯式風格**：不加漸層、emoji、圓角卡片；沿用模板既有樣式。
- **列印優先**：`@page` 已寫好紙張與邊界，簡報檔自動橫式，
  不需手動調整列印方向。

## 維護

開發源頭在 `html-demo` repo（含 `batch-test.py` 回歸測試），
本目錄是發行副本。同步方式見 [`SKILL.md`](SKILL.md) 的「維護」一節
（注意 `catalog.md` 的路徑已改寫成相對引用，不可直接覆蓋）。
