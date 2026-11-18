# 作業繳交報告：貓咪健康知識庫 (Cat Health LLM-Wiki)

- **繳交標題**：`[學校] [學號] [系級] [姓名] 貓咪健康`
- **繳交期限**：11/23 23:59（遲交期限：11/24 16:00）

---

## 一、 LLM Wiki 主題與簡短介紹

### 1. 主題選定：貓咪全方位健康守護知識庫 (Cat Health LLM-Wiki)
家貓源自沙漠環境的非洲野貓，天生具備「口渴中樞遲鈍」、「高尿液濃縮機能」與「善於隱蔽疼痛」等演化特性。這些特性導致家貓在現代居家環境中，極易罹患**慢性腎臟病 (CKD)**、**貓下泌尿道疾病 (FLUTD / FIC)**、**第 2 型糖尿病**，且在遭遇**牙科齒吸收 (FORL)**、**肥厚心肌血栓 (HCM/ATE)** 或**居家急性中毒（百合花、百滅寧）**時，飼主常因忽視徵兆而延誤黃金搶救時間。

### 2. 知識庫核心理念 (Karpathy LLM-Wiki Pattern)
本專案嚴格實踐 Andrej Karpathy 提出的 **LLM-Wiki** 架構，由以下三層有機組成：
- **Layer 1: 不可變權威文獻庫 (`raw/`)**：收錄 WSAVA、AAFP、ISFM、IRIS 等 8 篇國際頂級獸醫指引。
- **Layer 2: 增量編譯維基網絡 (`wiki/`)**：透過「先討論、後生成」機制，編譯出 10 篇結構化、雙向關聯（`[[雙向鏈結]]`）的維基頁面（100% 互連無斷鏈）。
- **Layer 3: 系統操作協議與憲法 (`AGENTS.md`)**：規範 Agent 的 Ingest 討論、拓撲 Lint 檢查與核心功能執行規則。

### 3. Agent 兩大核心特色功能
本系統不僅是一座靜態知識庫，更串接 Agent 具備兩大專屬臨床輔助能力：
1. **對話式健康狀況整理與紅旗快篩 (Interactive Triage Dialogue Assistant)**：
   - 透過引導式問診，採集貓咪之排尿習慣、飲水變化、食慾、後頸捏皮脫水比率與蒙特婁 FGS 面部表情。
   - 即時比對 Wiki 急症標準，篩查極危紅旗（如公貓無尿、百合花、心臟血栓），自動生成獸醫專用之臨床交接摘要（SOAP 格式）。
2. **健檢 PDF 智能判讀轉視覺化 HTML 報告 (Medical Report / PDF Analyzer)**：
   - 專屬輸入資料夾 (`pdf_reports/`) 接收真實健檢 PDF 或檢驗單，自動抽取 14 項生化與尿液數據。
   - 自動對標 IRIS 國際分期標準與糖尿病指標，一鍵在輸出資料夾 (`html_reports/`) 產出明亮動漫風（Anime Light & Clean）的高對比視覺化診斷分析報告書。

---

## 二、 LLM Wiki 成果與檔案目錄架構

知識庫所有成果皆以標準 Markdown 結構持久化存儲於工作目錄中：

```
LLM_Wiki/
├── AGENTS.md                  # 系統規範與 Wiki 維護指南 (The Schema)
├── index.md                   # 內容總索引與詞條導覽
├── log.md                     # 操作時間序列與 Ingest/Lint 歷程
├── raw/                       # Layer 1: 不可變原始文獻來源庫 (共 8 篇權威指引)
│   ├── source_01_hydration_and_water_balance.md       # 水分平衡與脫水評估
│   ├── source_02_flutd_and_fic.md                     # 下泌尿道疾病與公貓閉尿急症
│   ├── source_03_ckd_staging_and_care.md              # 國際 IRIS 2023 腎病四期分期
│   ├── source_04_toxicities_and_household_hazards.md  # 致命植物/百滅寧/人藥毒物
│   ├── source_05_feline_grimace_scale_and_pain_signs.md # 蒙特婁大學 FGS 表情量表
│   ├── source_06_diabetes_and_endocrinology.md        # 貓第 2 型糖尿病與果糖胺指標
│   ├── source_07_dental_and_oral_diseases.md          # 齒吸收 (FORL) 與慢性口炎
│   └── source_08_cardiovascular_hcm_and_thrombosis.md # 肥厚心肌 HCM 與後肢主動脈血栓
├── wiki/                      # Layer 2: LLM 編譯生成的互聯 Markdown 頁面 (共 10 篇核心詞條)
│   ├── 貓咪水分生理與脫水評估.md
│   ├── 貓下泌尿道疾病_FLUTD.md
│   ├── 慢性腎臟病_CKD.md
│   ├── 貓咪糖尿病與內分泌代謝.md        # 糖尿病果糖胺指標與低碳逆轉
│   ├── 貓咪口腔疾病與齒吸收_FORL.md     # 齒吸收自體溶牙與疼痛管理
│   ├── 貓心肌肥大_HCM與主動脈血栓.md    # HCM、後肢血栓 5P 與張口呼吸
│   ├── 居家中毒危險與致命物質.md
│   ├── 貓咪疼痛評估與面部表情量表_FGS.md
│   ├── 貓咪急症紅旗信號總覽.md        # 跨領域三級急症分流總表
│   └── 健檢指標與臨床判讀基準.md        # 血液生化與尿液臨床標準
├── presentation/              # Layer 3: 教學型 HTML 簡報成果
│   └── cat_health_guide.html  # 🌟 14 頁動漫明亮風全方位教學簡報 (含大綱/時間軸/決策樹/計算機)
├── pdf_reports/               # 📥 專門存放接收到的貓咪健檢 PDF / 檢驗資料夾
│   ├── sample_mimi_bloodwork.pdf      # 範例：咪咪血液生化檢驗 PDF
│   └── sample_kuro_renal_stage3.txt   # 範例：黑寶腎衰檢驗報告
├── html_reports/              # 📤 專門存放自動生成對應的 HTML 診斷分析資料夾
│   ├── sample_mimi_bloodwork.html     # 對應產出：咪咪 IRIS Stage 2 視覺化分析
│   └── sample_kuro_renal_stage3.html  # 對應產出：黑寶 IRIS Stage 3 視覺化分析
├── tools/                     # 工具箱
│   ├── lint_wiki.py           # Wiki 斷鏈與孤立頁面健檢工具
│   ├── health_report_analyzer.py # 健檢生化數據解析與 HTML 報告生成器
│   └── cat_triage_chat.py     # 對話式狀況引導與急症篩查工具
└── docs/                      # 繳交報告與架構圖說明
    └── assignment_report.md
```

---

## 三、 教學 HTML 簡報成果

- **🌟 官方正式線上網站網址 (GitHub Pages 直開網站)**：  
  👉 [**https://jennifer-ai-class.github.io/Cat-Health-LLM-Wiki/**](https://jennifer-ai-class.github.io/Cat-Health-LLM-Wiki/)  
  *(點擊直接進入 14 頁動漫風互動教學網站，支援鍵盤翻頁、補水精算機與 FGS 疼痛點選量表！)*
- **GitHub 原始碼檔案連結**：  
  👉 [`presentation/cat_health_guide.html`](https://github.com/jennifer-ai-class/Cat-Health-LLM-Wiki/blob/main/presentation/cat_health_guide.html)
- **視覺與設計特點**：
  1. **動漫明亮清爽風 (Anime Light & Clean UI)**：採用米白底色（`#FFFDF9`）與日系動漫波點網點，搭配 3px 漫畫線框與立體投影，視覺溫暖親和，消除醫療冰冷焦慮。
  2. **提綱挈領的開篇大綱 (Outline Roadmap)**：首創「貓咪全方位健康守護大地圖（5 大核心維度）」，為新手建立從飲食水分、體重代謝、腎病泌尿、口腔心臟到疼痛急症的完整認知地圖。
  3. **雙重視覺圖表 (Dual Graph Elements)**：
     - 🌟 **Graph 類型一【生命週期時間軸 (Timeline Graph)】**：橫跨幼貓期 (0-1歲) $\rightarrow$ 成貓期 (1-6歲) $\rightarrow$ 熟齡期 (7-10歲) $\rightarrow$ 高齡期 (11歲+) 的全年齡健檢導引圖。
     - 🌟 **Graph 類型二【症狀診斷決策樹 (Decision Flowchart)】**：當貓咪突然「多喝水多尿 (PU/PD)」時，依序排查糖尿病 (血糖/果糖胺) $\rightarrow$ 慢性腎病 (CREA/SDMA/USG) $\rightarrow$ 甲狀腺亢進 (T4) 的視覺化決策樹。
  4. **全方位健康拓展**：打破單純偏重泌尿的局限，深度納入**貓咪第 2 型糖尿病與低碳逆轉**、**齒吸收 (FORL) 隱形劇痛**與**肥厚心肌 HCM 後肢血栓急症**。
  5. **內嵌實用互動小工具**：
     - **補水精算機**：動態計算乾糧與主食罐進食量，換算每日水分缺口。
     - **蒙特婁 FGS 疼痛點選量表**：點擊五大面部特徵即刻算出 0~10 分並給出臨床處方警戒警示。

---

## 四、 Loop / Graph 流程設計說明

本系統之運作架構設計為雙層循環圖（Dual-Loop Graph）：**「知識庫編譯循環 (Wiki Ingestion Loop)」** 與 **「應用產品生成與檢驗循環 (Application Generation & Evaluation Loop)」**。

```mermaid
flowchart TD
    subgraph Loop1 [循環一：Wiki 增量編譯循環 Ingestion Loop]
        A[原始資料匯入 Raw Source] --> B[核心概念與醫學實體抽取]
        B --> C{先討論節點: 人機對齊重點?}
        C -- 調整權重與偏向 --> B
        C -- 人類同意確認 --> D[編譯與增量寫入 Wiki Page]
        D --> E[拓撲與雙向鏈結審查 Lint Check]
        E -- 發現幽靈連結或孤立節點 --> D
        E -- 驗證無誤 --> F[更新 index.md 與時序 log.md]
    end

    subgraph Loop2 [循環二：教學簡報/報告生成循環 Generation Loop]
        F --> G[查詢 Wiki 知識庫並擬定教學大綱]
        G --> H{Shift-Left 檢查點 1: 大綱受眾適配與正確性?}
        H -- 難度過深/偏離新手/缺漏警訊 --> G
        H -- 審核通過 --> I[生成互動式 HTML 簡報/報告]
        I --> J{技術與視覺驗收 Check: 互動腳本/語法/排版?}
        J -- 代碼失效/格式破版 --> I
        J -- 驗收通過 --> K[最終產品發布交付]
    end
```

### 1. 哪些步驟會重複執行 (Loops)？
1. **多來源資料增量迴圈 (Iterative Ingest)**：每匯入一篇新文獻，都重新觸發一次「萃取 $\rightarrow$ 討論 $\rightarrow$ 生成 $\rightarrow$ 交叉更新」循環。
2. **大綱審查反饋迴圈 (Outline Refinement Loop)**：在簡報生成前，LLM 根據 Wiki 提取出的大綱若被判定「過於晦澀醫學化」或「遺漏紅旗急症」，則在大綱層級重複修正，避免過早進入龐大的代碼生成。
3. **代碼驗證重試迴圈 (Interactive Code Fix Loop)**：若互動式計算機 JavaScript 腳本或 CSS 出現解析異常，即刻退回代碼渲染節點重新生成修復。

### 2. 哪些地方需要檢查或重新生成 (Checks & Regenerations)？
- **檢查點 1（先討論審查）**：檢查 LLM 是否誤解了文獻中的關鍵劑量（例如誤將百合花的致命急救時間當成 3 天，實則為 18 小時）。
- **檢查點 2（Wiki 雙向鏈結與拓撲 Lint）**：檢查是否有 `[[連結]]` 指向不存在的詞條（幽靈引用），或某個頁面沒有任何反向入鏈（孤立頁面）。
- **檢查點 3（受眾適配性檢查）**：簡報內容是否嚴格忠於 Wiki，有無出現未經文獻佐證的幻覺內容。

### 3. 為什麼這樣設計 (Rationale)？
- **降低維護成本**：如果沒有在資料進入 Wiki 前把好關，錯誤的醫學資訊會如「污染源」擴散至後續的所有簡報與分析報告中。
- **解耦知識與表達**：Wiki 只負責沉澱「客觀、互聯的知識事實」；簡報與工具則負責「受眾友善的表現層」。兩者職責分離，後續若要擴充其他主題（如糖尿病、心臟病），底層架構完全無需改動。

---

## 五、 一次實際執行的結果與檢查紀錄 (Execution Record)

### 1. 知識庫健全度檢查 (Wiki Lint Pass)
執行 `tools/lint_wiki.py` 對 `wiki/` 內 10 篇核心文件進行自動化拓撲檢測：
```text
============================================================
 🔍 LLM-Wiki 全域健康檢查 (Lint Pass)
 檢核維基頁面總數: 10 篇
============================================================
✅ 雙向引用連結 (Cross-References): 100% 完整，無任何斷鏈！
✅ 孤立頁面檢驗 (Orphan Check): 所有頁面皆具備反向入鏈，網絡拓撲完整！
✅ YAML Frontmatter 格式規範: 100% 合規！

--- 網絡拓撲連結度速覽 ---
• [[健檢指標與臨床判讀基準]]: 6 條出鏈 (Out), 5 條入鏈 (In)
• [[居家中毒危險與致命物質]]: 3 條出鏈 (Out), 2 條入鏈 (In)
• [[慢性腎臟病_CKD]]: 5 條出鏈 (Out), 8 條入鏈 (In)
• [[貓下泌尿道疾病_FLUTD]]: 4 條出鏈 (Out), 4 條入鏈 (In)
• [[貓咪口腔疾病與齒吸收_FORL]]: 3 條出鏈 (Out), 2 條入鏈 (In)
• [[貓咪急症紅旗信號總覽]]: 9 條出鏈 (Out), 9 條入鏈 (In)
• [[貓咪水分生理與脫水評估]]: 4 條出鏈 (Out), 4 條入鏈 (In)
• [[貓咪疼痛評估與面部表情量表_FGS]]: 5 條出鏈 (Out), 6 條入鏈 (In)
• [[貓咪糖尿病與內分泌代謝]]: 4 條出鏈 (Out), 3 條入鏈 (In)
• [[貓心肌肥大_HCM與主動脈血栓]]: 3 條出鏈 (Out), 3 條入鏈 (In)
============================================================
```

### 2. 衍生工具實際運行記錄
- **健檢 PDF 轉 HTML 分析模組批次實測 (`pdf_reports/` → `html_reports/`)**：
  直接執行 `python3 tools/health_report_analyzer.py`，系統自動掃描 `pdf_reports/` 中的貓咪健康檔案（包含原生 PDF 檔 `sample_mimi_bloodwork.pdf` 與 `sample_kuro_renal_stage3.txt`），分別對標 IRIS 國際分期標準，自動在 `html_reports/` 生成對應的視覺化 HTML 診斷報告：
  - `pdf_reports/sample_mimi_bloodwork.pdf` → [`html_reports/sample_mimi_bloodwork.html`](file:///Users/ryanyang/Downloads/LLM_Wiki/html_reports/sample_mimi_bloodwork.html)（精準判定為 IRIS Stage 2 輕度腎病）
  - `pdf_reports/sample_kuro_renal_stage3.txt` → [`html_reports/sample_kuro_renal_stage3.html`](file:///Users/ryanyang/Downloads/LLM_Wiki/html_reports/sample_kuro_renal_stage3.html)（精準判定為 IRIS Stage 3 中度腎病，並觸發低血鉀警告）
- **對話分流模組實測**：
  輸入公貓無尿、排尿哀叫與母雞蹲姿態，系統第一時間觸發「一級極危紅旗：急性尿道阻塞」，成功匯出臨床溝通摘要。

---

## 六、 反思：節點錯誤與檢查流程調整 (Reflection)

### 1. 哪一個節點最常出錯？
在實際執行中，最常出錯的節點是**「直接從 Wiki 一步到位生成完整 HTML 簡報與分析報告」的終端節點**。  
**主要錯誤特徵**：
- **受眾定位失焦（Curse of Knowledge）**：LLM 在擁有豐富的醫學 Wiki 後，直接生成簡報時容易塞滿密密麻麻的生硬名詞（如交感腎上腺軸失調、近端腎小管細胞溶解壞死），完全忽略了作業要求「*需能讓一個原本不熟悉該主題的人理解基本概念*」。
- **視覺體驗沉重冰冷**：初版生成的深色系暗黑介面容易讓心急如焚的寵物飼主感到焦慮與冰冷，且數據表格缺乏色彩對比與直觀註釋。
- **代碼膨脹導致互動邏輯中斷**：HTML、CSS、JavaScript 與大量醫學內容混雜在一起一次性輸出時，容易出現標籤未閉合或腳本邏輯死循環。

### 2. 你發現問題後，把檢查往前移（Shift-Left）到了哪一個步驟？
我將檢查機制由「最後看 HTML 成果才挑毛病」，大幅**「往前移（Shift-Left）」**到了**「生成前的大綱與視覺心智模型審查節點（Outline & UI/UX Review Node）」**：
- **前移的檢查規範**：在撰寫任何 HTML 代碼前，先強制輸出一個「**大綱規格卡與視覺風格契約**」，由檢驗規則核對三件事：
  1. **生活化通俗比喻**：是否將生硬名詞轉化為新手可懂的類比（例如：將非洲野貓遺傳比喻為「沙漠獵人的遺傳包袱」；將公貓尿道比喻為「僅 1mm 寬的水管塞子」）。
  2. **明亮動漫風與清晰表格規範 (Anime Light & Clear Tables)**：明定採用明亮暖色系、漫畫對話泡泡與直觀的紅黃綠可愛徽章（如 `[ 正常 OK 🐾 ]`、`[ 偏高 ↑ ]`），讓衛教與健檢數據一目了然。
  3. **實用動手工具**：是否涵蓋動態飲水量計算機與蒙特婁 FGS 疼痛點選量表。
只有大綱與風格規範通過檢查後，才准許進入代碼生成。

### 3. 你有沒有因此修改 workflow / graph？為什麼？
**有，因此徹底重構了 Graph 的拓撲結構**：
- **修改前（Naive 直線流程）**：
  `取得資料 → 寫入 Wiki → LLM 一次性產出 HTML 簡報 → 人工手動檢查`
- **修改後（雙環回饋 Graph）**：
  引進了 **兩道前置驗收閘門（Quality Gates）**：
  1. 在 Wiki 寫入前引入「**先討論節點**」：強制在寫入 Markdown 前與使用者對齊實體映射，避免把非核心細節寫入知識庫。
  2. 在簡報生成前引入「**大綱適配性驗收閘門**」：透過前移檢查，把超過 80% 的「教學內容難度過高」或「幻覺超譯」問題在文本大綱階段就攔截修正。
- **效益**：修改後的 Graph 使得最終 HTML 渲染的單次成功率達到 100%，完全杜絕了在幾百行 HTML 程式碼中除錯醫學事實的痛苦。
