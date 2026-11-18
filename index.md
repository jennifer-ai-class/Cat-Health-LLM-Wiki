# 貓咪健康知識庫 (Cat Health LLM-Wiki) 索引目錄

> 本知識庫基於 Andrej Karpathy LLM-Wiki 模式構建，採用「先討論、後生成」原則，由 LLM 從不可變之權威醫學指引編譯維護。

最後更新時間：2026-11-18  
頁面總數：7 篇維基核心頁面，5 篇原始資料文獻  

---

## 📚 知識庫核心架構與頁面導覽

### 1. 核心臨床實體 (Entities & Conditions)
- [[貓下泌尿道疾病_FLUTD]] — 深入解析 FLUTD、自發性膀胱炎（FIC）、潘朵拉症候群與公貓致命性尿道阻塞時間線。
- [[慢性腎臟病_CKD]] — 熟齡貓頭號殺手，國際 IRIS 2023 血液（CREA / SDMA）四期分期標準、併發症與四大照護支柱。
- [[貓咪糖尿病與內分泌代謝]] — 胰島素阻抗機轉、三多一少徵狀、果糖胺（Fructosamine）診斷標準與早期低碳飲食逆轉臨床緩解。
- [[貓咪口腔疾病與齒吸收_FORL]] — 貓咪隱形劇痛齒吸收（FORL）、口炎（FCGS）成因與甩頭拔牙處置。
- [[貓心肌肥大_HCM與主動脈血栓]] — 貓最常見心臟病 HCM、致命後肢動脈血栓（ATE 5P徵象）與張口呼吸急救。

### 2. 生理機制與臨床評估 (Concepts & Assessments)
- [[貓咪水分生理與脫水評估]] — 沙漠祖先生理遺傳、每日需水量精算法（40-60 mL/kg）、乾濕糧補水效益與 5 級脫水理學檢查表。
- [[貓咪疼痛評估與面部表情量表_FGS]] — 蒙特婁大學 FGS 五大面部動作單元（FAUs）評分系統（$\ge 4/10$ 行動閾值）、母雞蹲姿態與關節炎警訊。

### 3. 安全指引與急救守則 (Guides & Protocols)
- [[居家中毒危險與致命物質]] — 貓肝臟缺乏 UGT 代謝酶機制，百合花、百滅寧、普拿疼等極毒物質與「三要三不」黃金急救守則。
- [[貓咪急症紅旗信號總覽]] — 跨領域三級急症分流總表（公貓無尿、張口呼吸、中度以上脫水、休克）與致命盲點破除。
- [[健檢指標與臨床判讀基準]] — 健檢生化、電解質、尿液指標常模與 IRIS 臨床判讀邏輯（支援自動化報告分析）。

---

## 🗃️ 原始文獻庫 (Raw Sources)

| 文獻標題 | 權威來源 | 涉及核心領域 | 對應維基頁面 |
| :--- | :--- | :--- | :--- |
| `raw/source_01_hydration_and_water_balance.md` | WSAVA / AAFP / ISFM 水分共識 | 水分生理、脫水評級 | [[貓咪水分生理與脫水評估]] |
| `raw/source_02_flutd_and_fic.md` | ISFM FIC 共識 / ACVIM 下泌尿道指引 | FLUTD、自發性膀胱炎、尿道阻塞 | [[貓下泌尿道疾病_FLUTD]] |
| `raw/source_03_ckd_staging_and_care.md` | IRIS 2023 CKD 指引 / AAFP 老年貓指南 | 腎衰竭分期、SDMA、尿比重 | [[慢性腎臟病_CKD]], [[健檢指標與臨床判讀基準]] |
| `raw/source_04_toxicities_and_household_hazards.md` | ASPCA APCC / Pet Poison Helpline | 百合花、藥物中毒、急救洗胃 | [[居家中毒危險與致命物質]] |
| `raw/source_05_feline_grimace_scale_and_pain_signs.md` | 蒙特婁大學 FGS 研究 / WSAVA 疼痛指引 | 疼痛表情量表、行為異常、母雞蹲 | [[貓咪疼痛評估與面部表情量表_FGS]] |
| `raw/source_06_diabetes_and_endocrinology.md` | AAFP 糖尿病指引 / ISFM 內分泌共識 | 糖尿病、胰島素、果糖胺、低碳飲食 | [[貓咪糖尿病與內分泌代謝]] |
| `raw/source_07_dental_and_oral_diseases.md` | WSAVA 牙科指引 / AVDC 齒科共識 | 齒吸收 FORL、口炎、下顎顫抖 | [[貓咪口腔疾病與齒吸收_FORL]] |
| `raw/source_08_cardiovascular_hcm_and_thrombosis.md` | ACVIM 心肌病共識 / ISFM 急症標準 | HCM 心肌肥厚、後肢血栓 5P、張口呼吸 | [[貓心肌肥大_HCM與主動脈血栓]] |

---

## 🛠️ 衍生工具與應用模組 (Extensions)
- **教學簡報模組**：`presentation/cat_health_guide.html`（專為零基礎飼主打造的現代互動式 HTML 簡報）
- **PDF 與報告資料夾**：
  - 輸入資料夾：`pdf_reports/`（存放貓咪健檢 PDF 檔案或報告）
  - 輸出資料夾：`html_reports/`（自動產出對應的視覺化 HTML 分析報告）
- **狀況整理對話引擎**：`tools/cat_triage_chat.py`（對話式引導飼主釐清貓咪狀況並篩查紅旗警訊）
- **健檢 PDF / 報告分析模組**：`tools/health_report_analyzer.py`（自動解析 `pdf_reports/`，生化指標比對 IRIS 標準，產出至 `html_reports/`）
