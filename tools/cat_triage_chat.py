#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Cat Health Triage Dialogue Assistant (對話式貓咪狀況整理助手)
Interactively collects a cat's current physical condition, behavior, and vital signs,
screens for emergency red flags against the LLM-Wiki, and compiles a structured clinical briefing.
"""

import os
import sys
from datetime import datetime

def print_banner():
    print("=" * 65)
    print(" 🐾 貓咪健康狀況整理與紅旗警訊快篩助手 (LLM-Wiki Triage)")
    print("   依據《貓咪健康知識庫》臨床標準，協助整理狀況並快篩就醫急迫性")
    print("=" * 65)

def ask(question, default=""):
    prompt = f"\n👉 {question} "
    if default:
        prompt += f"[預設: {default}]: "
    else:
        prompt += ": "
    try:
        ans = input(prompt).strip()
        return ans if ans else default
    except (EOFError, KeyboardInterrupt):
        print("\n使用者中斷輸入。")
        sys.exit(0)

def ask_choice(question, options):
    print(f"\n👉 {question}")
    for idx, opt in enumerate(options, 1):
        print(f"   {idx}. {opt}")
    while True:
        try:
            choice = input("請選擇項目編號: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(options):
                return options[int(choice) - 1]
            print("輸入無效，請輸入正確的選項數字。")
        except (EOFError, KeyboardInterrupt):
            print("\n使用者中斷輸入。")
            sys.exit(0)

def run_interactive_triage():
    print_banner()

    # Step 1: Basic Profile
    name = ask("貓咪的名字是？", "小貓")
    age = ask("貓咪的年齡（如：3歲、10歲熟齡）？", "5歲")
    sex = ask_choice("性別與絕育狀態？", ["已結紮公貓 (Neutered Male)", "未結紮公貓 (Intact Male)", "已結紮母貓 (Spayed Female)", "未結紮母貓 (Intact Female)"])
    weight = ask("體重約幾公斤 (kg)？", "4.0")

    # Step 2: Main Complaint & Urination
    print("\n--- 【排尿與飲水習慣檢查】 ---")
    urination_status = ask_choice("近期排尿狀況如何？", [
        "正常（每天排尿 2~3 次，尿塊完整）",
        "頻尿 / 頻繁進出貓砂盆但尿量少",
        "🚨 蹲盆用力哀叫、完全無尿或僅滴出血尿",
        "排尿位置異常（在砂盆外亂尿、床上或磁磚上）",
        "尿量突然倍增（一大片或極大尿塊）"
    ])

    water_status = ask_choice("近期飲水量變化？", [
        "正常穩定",
        "顯著增加（頻繁在水碗前猛喝水）",
        "顯著減少或幾乎不喝水"
    ])

    # Step 3: Energy, Appetite & Vomiting
    print("\n--- 【食慾、精神與消化道症狀】 ---")
    appetite = ask_choice("食慾與精神狀態？", [
        "精神食慾俱佳",
        "食慾稍減，精神略顯疲憊",
        "拒食厭食超過 24 小時、躲藏於暗處不出來",
        "極度萎靡、甚至無法站立"
    ])

    vomiting = ask_choice("是否有嘔吐或腹瀉？", [
        "無嘔吐",
        "偶發性吐毛球或白色泡沫（小於1天1次）",
        "頻繁劇烈嘔吐（一天超過3次，伴隨水樣吐或黃綠膽汁）"
    ])

    # Step 4: Physical & Pain Signs
    print("\n--- 【理學觸診與面部表情評估】 ---")
    skin_tent = ask_choice("後頸捏皮回彈試驗（捏起後頸皮膚再放開）：", [
        "瞬間平復（< 1秒，水合良好）",
        "回彈稍微遲緩（約 1~2 秒，輕度缺水）",
        "明顯延遲或皮膚滯留呈帳篷狀（> 2 秒，嚴重脫水）"
    ])

    face_pain = ask_choice("面部表情與肢體姿態（參照 FGS 表情量表）：", [
        "表情放鬆、雙耳朝前、眼睛圓睜、自然走動",
        "雙耳稍微外開、偶爾瞇眼、稍微縮著身子",
        "🚨 緊閉雙眼、飛機耳壓平、鬍鬚向前刺出、弓背緊繃「母雞蹲」姿態"
    ])

    toxic_hazard = ask_choice("是否有接觸居家危險物質之疑慮？", [
        "無任何危險接觸",
        "可能啃咬過家中觀葉植物（如黃金葛、龜背竹）",
        "🚨 誤碰/啃咬百合花（含花瓶水、花粉）或誤點狗用除蟲滴劑",
        "可能誤食人類藥物（普拿疼、感冒藥等）"
    ])

    # Step 5: Triage & Synthesis
    print("\n" + "=" * 65)
    print(" 🩺 正在比對《貓咪健康知識庫》臨床標準進行分流快篩...")
    print("=" * 65)

    red_flags = []
    warnings = []

    # Screening rules
    if "公貓" in sex and "完全無尿" in urination_status:
        red_flags.append("🚨 【極危急症】公貓疑似急性尿道阻塞！24-48小時內有高血鉀心臟驟停致命風險，請立即送往急診！")

    if "百合花" in toxic_hazard:
        red_flags.append("🚨 【極危急症】疑似百合花中毒！整株具強烈腎毒性，黃金搶救期為 18 小時內，請立即送醫靜脈輸液！")

    if "狗用除蟲" in toxic_hazard:
        red_flags.append("🚨 【極危急症】疑似百滅寧神經毒性！請立即送醫施打肌肉鬆弛劑抗抽搐！")

    if "人藥" in toxic_hazard:
        red_flags.append("🚨 【極危急症】疑似人類藥物（普拿疼/NSAID）中毒！致命溶血與急性肝腎壞死風險！")

    if "無法站立" in appetite:
        red_flags.append("🚨 【極危急症】嚴重虛脫休克前期徵象，需急診輸液搶救！")

    if "皮膚滯留呈帳篷狀" in skin_tent:
        warnings.append("⚠️ 【中重度脫水】脫水程度估計達 7%~10% 以上，建議就醫評估輸液補水。")

    if "母雞蹲" in face_pain:
        warnings.append("⚠️ 【中重度疼痛】FGS 面部與姿態顯示高度內臟或腹部疼痛，需由獸醫進行理學檢查與止痛處方。")

    if "頻繁進出貓砂盆" in urination_status or "排尿位置異常" in urination_status:
        warnings.append("⚠️ 【下泌尿道症候群】疑似貓自發性膀胱炎 (FIC) 或尿道結晶結石，建議攜帶新鮮尿液檢體就醫檢查。")

    if "尿量突然倍增" in urination_status or "顯著增加" in water_status:
        warnings.append("ℹ️ 【多渴多尿 PU/PD 警訊】常為熟齡貓慢性腎臟病 (CKD)、糖尿病或甲狀腺機能亢進之早期臨床徵象。")

    # Generate Clinical Briefing
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    summary_md = f"""# 貓咪健康狀況分流整理紀錄 (Clinical Triage Summary)

- **紀錄時間**：{timestamp}
- **病患資訊**：{name}｜{age}｜{sex}｜約 {weight} kg

---

## 一、 快速篩檢警戒結果

"""
    if red_flags:
        summary_md += "### 🚨 【一級極危紅旗警訊 — 立即就診】\n"
        for rf in red_flags:
            summary_md += f"- **{rf}**\n"
        summary_md += "\n"

    if warnings:
        summary_md += "### ⚠️ 【重點異常症狀與追蹤建議】\n"
        for w in warnings:
            summary_md += f"- {w}\n"
        summary_md += "\n"

    if not red_flags and not warnings:
        summary_md += "### 🟢 【目前狀態尚稱平穩】\n- 未觸發急性紅旗指標，請持續觀察並維持日常良好飲水習慣。\n\n"

    summary_md += f"""---

## 二、 飼主觀察記錄條列 (供看診獸醫參考)

1. **排尿狀況**：{urination_status}
2. **飲水變化**：{water_status}
3. **精神食慾**：{appetite}
4. **嘔吐下痢**：{vomiting}
5. **水合狀態**：後頸捏皮回彈 —— {skin_tent}
6. **表情姿態**：{face_pain}
7. **環境毒素**：{toxic_hazard}

---

## 三、 建議向主治獸醫諮詢之重點問題
- 若有頻尿或排尿困難，是否需進行超音波掃描排查結石、膀胱壁增厚或膀胱炎？
- 是否需安排全套血液生化（檢測 BUN、Creatinine、SDMA 與鉀離子 K+）？
- 是否需檢驗尿比重（USG）與尿渣沉澱鏡檢？
"""

    print(summary_md)

    # Save to file
    out_dir = "reports"
    os.makedirs(out_dir, exist_ok=True)
    out_filename = os.path.join(out_dir, f"triage_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    with open(out_filename, 'w', encoding='utf-8') as f:
        f.write(summary_md)
    print(f"\n✅ 整理報告已成功匯出至：{out_filename}")

if __name__ == '__main__':
    run_interactive_triage()
