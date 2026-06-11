# AntV Infographic 模組目錄（agent 取用指南）

165 個模板已全數通過標準資料形狀渲染測試（2026-06-11，`batch-test.py` 產出）。
agent 要在文件裡放資訊圖表時，照以下三步取用。

## 取用三步驟

1. **查表選模板**：讀 `templates.json`，依 `category` 與用途挑 `name`，
   照 `data_shape` 欄組資料；有 `note` 欄的模板先讀註記。
2. **產 SVG**：寫 syntax 檔後執行
   ```bash
   python3 make-svg.py 檔案.syntax -o 圖.svg
   ```
3. **內嵌進 A4 模板**：SVG 直接貼進 HTML（單檔自包含、離線可印），
   外層必加：
   ```css
   figure svg { width: 100%; height: auto; max-height: 110mm; }
   ```

## syntax 速查

```
infographic <模板名>            ← 第一行，模板名查 templates.json
data
  title 圖表標題                ← 兩空格縮排
  lists
    - label 項目名
      desc 描述文字             ← chart 類改用 value 數值
      children                  ← hierarchy／compare 類用
        - label 子項
theme                           ← 可選；正式文件建議自訂色
  colorPrimary #1e4e79
```

## 分類與選用建議（165 個，6 類）

| 類別 | 數量 | 基礎版型 | 文件對應 |
|---|---|---|---|
| sequence | 68 | steps、timeline、roadmap-vertical、funnel、snake-steps、circular、stairs-3d、mountain、filter-mesh、pyramid | SOP 流程、status 里程碑、proposal 時程、report 漏斗 |
| list | 37 | row、column、grid、pyramid、sector、waterfall、zigzag | jd 職責、handover 清單、proposal 交付物 |
| compare | 24 | binary-horizontal（vs／fold／arrow）、quadrant、swot、hierarchy-left-right | swot、proposal 方案比較 |
| chart | 15 | bar、column、line、pie、pie-donut、wordcloud | budget 數據、esg 佔比、report 統計 |
| hierarchy | 14 | mindmap（branch／level 各 5 變體）、structure、structure-mirror、tree | 組織圖、study-plan 知識架構 |
| relation | 7 | dagre-flow、network、circle | postmortem／8d 因果、系統架構 |

## 硬規則（踩過坑的）

1. **不要跳過 make-svg.py 的字型替換**。SVG 原生寫死
   `Alibaba PuHuiTi`，拔掉 runtime 後該字型不存在，macOS 會
   fallback 到 PingFang → 列印 PDF 中文整段消失。
2. **直式版型必加 max-height**（timeline、roadmap-vertical、
   list-column 等）：viewBox 窄高，`width:100%` 會放大到溢出頁面。
3. **compare-binary 系列頂層 label 不顯示**，內容要寫在
   children（label＋desc）；`compare-hierarchy-left-right` 實測
   只渲染根節點，要做左右對照樹改用 `hierarchy-structure-mirror`。
4. **正式 A4 文件選 `-simple`／`-plain-text` 變體**。預設主題是
   鮮豔漸層，與模板庫的編輯式風格衝突；或用 theme 把主色改
   `#1e4e79`。
5. icon 欄位會打 `weavefox.cn` API，離線或正式交付不要用。

## 本目錄檔案

| 檔案 | 用途 |
|---|---|
| `templates.json` | 機器可讀模板清單（name／category／data_shape／note） |
| `make-svg.py` | syntax → 乾淨 SVG 的產製工具 |
| `batch-test.py` | 全量回歸測試（升級 bundle 後重跑） |
| `preview.html` | 165 個模板的視覺總覽（瀏覽器開） |
| `a4-embed.html` | 內嵌 A4 的驗證成品（6 圖、已過列印測試） |
| `vendor/infographic.min.js` | 本地 bundle v0.2.x（MIT） |
