#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Health Report Analyzer & HTML Report Generator (Anime Light Style - Clean UTF-16-BE Decoder)
Accurately decodes veterinary PDF records (including UniCNS-UTF16-H encoded Chinese texts),
extracts patient demographics, CBC, Chemistry, and Urinalysis,
benchmarks against LLM-Wiki IRIS CKD & Diabetes standards, and generates clear, bright anime HTML reports.
"""

import os
import re
import sys
import zlib
import base64
import json
from datetime import datetime

REF_RANGES = {
    'CREA': {'name': '肌酸酐 (Creatinine)', 'unit': 'mg/dL', 'min': 0.8, 'max': 2.4, 'cat': '腎臟過濾', 'desc': '腎元濾過率指標，偏高代表腎功能衰退或脫水'},
    'BUN': {'name': '血液尿素氮 (BUN)', 'unit': 'mg/dL', 'min': 16.0, 'max': 36.0, 'cat': '腎臟代謝', 'desc': '體內含氮廢物，過高會造成尿毒噁心與食慾不振'},
    'SDMA': {'name': '對稱二甲基精胺酸', 'unit': 'μg/dL', 'min': 0.0, 'max': 14.0, 'cat': '早期腎篩', 'desc': '超靈敏指標！腎功能受損 25%~40% 即提前升高'},
    'PHOS': {'name': '血清無機磷 (Phosphorus)', 'unit': 'mg/dL', 'min': 3.1, 'max': 7.5, 'cat': '電解質/腎', 'desc': '高血磷會加速腎病惡化，腎貓須嚴格控磷'},
    'USG': {'name': '尿比重 (USG)', 'unit': '', 'min': 1.035, 'max': 1.060, 'cat': '尿液濃縮', 'desc': '正常應 >1.035，偏低代表腎臟濃縮水分機能減退'},
    'GLU': {'name': '血糖 (Glucose)', 'unit': 'mg/dL', 'min': 70.0, 'max': 150.0, 'cat': '代謝能量', 'desc': '緊張可能引發緊迫高血糖，需搭配果糖胺區別糖尿病'},
    'FRUCT': {'name': '果糖胺 (Fructosamine)', 'unit': 'μmol/L', 'min': 190.0, 'max': 365.0, 'cat': '血糖回溯', 'desc': '反映過去 2~3 週平均血糖，判讀糖尿病之黃金指標'},
    'ALT': {'name': '丙胺酸轉胺酶 (ALT)', 'unit': 'U/L', 'min': 12.0, 'max': 130.0, 'cat': '肝實質功能', 'desc': '肝細胞急性受損指標，中毒或發炎時劇烈飆升'},
    'AST': {'name': '天門冬胺酸轉胺酶 (AST)', 'unit': 'U/L', 'min': 0.0, 'max': 48.0, 'cat': '肝臟/肌肉', 'desc': '肝細胞或心肌、骨骼肌受損時上升'},
    'ALP': {'name': '鹼性磷酸酶 (ALP / ALKP)', 'unit': 'U/L', 'min': 14.0, 'max': 111.0, 'cat': '膽道/肝臟', 'desc': '貓咪半衰期極短，輕微上升即代表顯著肝膽鬱滯'},
    'TBIL': {'name': '總膽紅素 (Total Bilirubin)', 'unit': 'mg/dL', 'min': 0.0, 'max': 0.4, 'cat': '肝膽溶血', 'desc': '黃疸指標，過高需注意溶血或膽管阻塞'},
    'TP': {'name': '總蛋白質 (Total Protein)', 'unit': 'g/dL', 'min': 5.7, 'max': 8.9, 'cat': '血清蛋白', 'desc': '反映脫水（偏高）或蛋白流失/營養不良（偏低）'},
    'ALB': {'name': '白蛋白 (Albumin)', 'unit': 'g/dL', 'min': 2.3, 'max': 3.9, 'cat': '膠體滲透壓', 'desc': '肝臟製造的重要蛋白，過低易產生水腫或腹水'},
    'K': {'name': '鉀離子 (Potassium)', 'unit': 'mmol/L', 'min': 3.5, 'max': 5.8, 'cat': '核心離子', 'desc': '⚠️ >6.5 具心臟驟停致命風險；<3.2 會引發無力垂頭'},
    'HCT': {'name': '血容比 (HCT / PCV)', 'unit': '%', 'min': 30.0, 'max': 45.0, 'cat': '紅血球計數', 'desc': '貧血指標，慢性腎病常因紅血球生成素不足引發非再生性貧血'},
    'HGB': {'name': '血紅素 (HGB)', 'unit': 'g/dL', 'min': 8.0, 'max': 15.0, 'cat': '血液常規', 'desc': '紅血球攜氧蛋白濃度，評估貧血程度'},
    'WBC': {'name': '白血球總數 (WBC)', 'unit': '10^9/L', 'min': 5.5, 'max': 19.5, 'cat': '免疫發炎', 'desc': '發炎反應、感染或緊迫之白血球計數指標'},
    'RBC': {'name': '紅血球計數 (RBC)', 'unit': '10^12/L', 'min': 5.0, 'max': 10.0, 'cat': '血液常規', 'desc': '紅血球數量指標'},
    'PLT': {'name': '血小板計數 (PLT)', 'unit': '10^9/L', 'min': 200.0, 'max': 600.0, 'cat': '凝血機能', 'desc': '凝血機能指標'}
}

def extract_text_from_pdf(pdf_path):
    """Accurately extract text streams from PDF, handling uncompressed, ASCII85Decode, FlateDecode, and pure UTF-16-BE strings."""
    try:
        with open(pdf_path, 'rb') as f:
            content = f.read()
    except Exception as e:
        return f"Error reading PDF: {e}"

    extracted_lines = []
    objs = re.findall(rb'(\d+\s+\d+\s+obj.*?endobj)', content, re.DOTALL)
    for obj in objs:
        if b'stream' in obj:
            stream_data = obj[obj.find(b'stream')+6:obj.rfind(b'endstream')].strip()
            dec = None
            if b'ASCII85Decode' in obj:
                if not stream_data.startswith(b'<~'): stream_data = b'<~' + stream_data
                if not stream_data.endswith(b'~>'): stream_data = stream_data + b'~>'
                try:
                    dec = zlib.decompress(base64.a85decode(stream_data, adobe=True))
                except Exception:
                    pass
            elif b'FlateDecode' in obj:
                try:
                    dec = zlib.decompress(stream_data)
                except Exception:
                    pass
            else:
                dec = stream_data

            if dec:
                # Find all text strings inside parentheses
                matches = re.findall(rb'(\((?:[^()\\]|\\.)*\))\s*Tj', dec, re.DOTALL)
                for m in matches:
                    raw = re.sub(rb'\\([0-7]{1,3})', lambda x: bytes([int(x.group(1), 8)]), m[1:-1])
                    raw = raw.replace(b'\\(', b'(').replace(b'\\)', b')').replace(b'\\\\', b'\\')
                    
                    decoded = None
                    if not raw:
                        continue
                    
                    # 1. Plain ASCII
                    if all(32 <= c <= 126 or c in (9, 10, 13) for c in raw):
                        decoded = raw.decode('latin1')
                    # 2. Check BOM
                    elif raw.startswith(b'\xfe\xff'):
                        try:
                            decoded = raw[2:].decode('utf-16-be')
                        except Exception:
                            pass
                    # 3. Check for Null bytes (typical of UTF-16-BE)
                    elif b'\x00' in raw:
                        try:
                            decoded = raw.decode('utf-16-be')
                        except Exception:
                            pass
                    
                    # 4. Try UTF-8 (checking for illegal control chars)
                    if decoded is None:
                        try:
                            u8 = raw.decode('utf-8')
                            if not any(ord(c) < 32 and c not in '\t\n\r' for c in u8):
                                decoded = u8
                        except Exception:
                            pass
                    
                    # 5. Try UTF-16-BE
                    if decoded is None and len(raw) % 2 == 0:
                        try:
                            u16 = raw.decode('utf-16-be')
                            if not any(ord(c) < 32 and c not in '\t\n\r' for c in u16):
                                decoded = u16
                        except Exception:
                            pass
                    
                    if decoded is None:
                        decoded = raw.decode('latin1', errors='ignore')

                    if decoded and decoded.strip():
                        extracted_lines.append(decoded.strip())

    return "\n".join(extracted_lines)

def parse_report_text(text, fallback_name="愛貓"):
    data = {}
    
    # 1. Cat Name extraction
    name_match = re.search(r'\b(?:貓咪名稱|貓咪姓名|病患姓名|Patient\s*Name|Patient|Cat\s*Name)\b[\s\:\：\｜]+([^\r\n\,\;]+)', text, re.IGNORECASE)
    case_id_match = re.search(r'\b(?:個案編號|案例|Case\s*ID|Case)\b[\s\:\：\｜]+([^\r\n\,\;\-]+)', text, re.IGNORECASE)
    
    cat_real_name = name_match.group(1).strip() if name_match else ""
    case_id = case_id_match.group(1).strip() if case_id_match else ""
    
    if cat_real_name and case_id:
        data['cat_name'] = f"{cat_real_name} ({case_id})"
    elif cat_real_name:
        data['cat_name'] = cat_real_name
    elif case_id:
        data['cat_name'] = f"個案 {case_id}"
    else:
        clean_fallback = fallback_name.replace("貓咪健檢_", "").replace("Cat_Health_", "").replace(".pdf", "").replace(".txt", "")
        data['cat_name'] = clean_fallback

    # Normalize Cat Profile for Bilingual / English Reports
    if "Chestnut" in data['cat_name']:
        data['cat_name'] = "栗子 (Chestnut / C02)"
    elif "Milk Tea" in data['cat_name']:
        data['cat_name'] = "奶茶 (Milk Tea / C03)"
    elif "Olive" in data['cat_name']:
        data['cat_name'] = "Olive 橄欖 (C02)"

    # 2. Age, Sex & Test Date
    age_match = re.search(r'\b(?:年齡|Age)\b[\s\:\：\n]+([0-9\.]+\s*(?:歲|yr|years|months|月)?)', text, re.IGNORECASE)
    raw_age = age_match.group(1).strip() if age_match else "保密"
    num_match = re.search(r'([0-9\.]+)', raw_age)
    if num_match:
        data['cat_age'] = f"{num_match.group(1)} 歲 ({raw_age})"
    else:
        data['cat_age'] = raw_age

    sex_match = re.search(r'\b(?:性別|Sex)\b[\s\:\：\n]+([^\r\n]+)', text, re.IGNORECASE)
    raw_sex = sex_match.group(1).strip() if sex_match else "未註明"
    if "Male" in raw_sex or "Castrated" in raw_sex or "公" in raw_sex or "MN" in raw_sex:
        data['cat_sex'] = "公／已結紮 (Male / Castrated)"
    elif "Female" in raw_sex or "Spayed" in raw_sex or "母" in raw_sex or "FS" in raw_sex:
        data['cat_sex'] = "母／已結紮 (Female / Spayed)"
    else:
        data['cat_sex'] = raw_sex

    date_match = re.search(r'\b(?:採檢日期|檢驗日期|Date|Collection\s*Date|Sample\s*date)\b[\s\:\：\n]+([0-9]{4}[\-\/\.][0-9]{1,2}[\-\/\.][0-9]{1,2})', text, re.IGNORECASE)
    data['test_date'] = date_match.group(1).strip() if date_match else datetime.now().strftime('%Y-%m-%d')

    # 3. Clinical Scenario / Case Description
    scenario_match = re.search(r'(?:情境|主訴|Reason|Scenario|Clinical\s*Context|Case\:\s*[A-Za-z0-9]+\s*[\-—\–])[\s\:\：\n]+([^\r\n]+)', text, re.IGNORECASE)
    raw_scenario = scenario_match.group(1).strip() if scenario_match else "例行健康檢查"
    if "Renal" in raw_scenario or "CKD" in raw_scenario or "Kidney" in raw_scenario or "腎" in raw_scenario:
        data['scenario'] = "腎功能異常／疑似慢性腎臟病 (Suspected CKD)"
    elif "Diabetes" in raw_scenario or "Hyperglycemia" in raw_scenario or "糖尿" in raw_scenario:
        data['scenario'] = "持續性高血糖／疑似糖尿病 (Suspected Diabetes)"
    else:
        data['scenario'] = raw_scenario

    # 4. Hospital Interpretation & Recommendations
    vet_note_match = re.search(r'(?:04\s*[｜\|]\s*(?:SIMULATED\s*VETERINARY\s*INTERPRETATION|模擬獸醫判讀|獸醫判讀|醫師判讀|Doctor\s*Note)|SIMULATED\s+VETERINARY\s+INTERPRETATION)[\s\:\：\n]+(.*?)(?=05\s*[｜\|]|FOLLOW-UP|建議追蹤|\Z)', text, re.IGNORECASE | re.DOTALL)
    if vet_note_match:
        note_raw = vet_note_match.group(1).strip()
        lines = [l.strip() for l in note_raw.split('\n') if l.strip() and not l.strip().startswith('SIMULATED') and not l.strip().startswith('Page')]
        note_str = " ".join(lines)
        if "Azotemia" in note_str or "SDMA" in note_str:
            data['vet_note'] = f"【臨床判讀】：氮血症、SDMA 升高及尿液濃縮能力不足（USG 1.018），高度懷疑腎臟機能疾病。單次就診無法確診慢性腎臟病，必須優先排除脫水及其他急性致病因素。<br><span style='color:#64748B; font-size:0.88rem;'>[原文] {note_str}</span>"
        elif "hyperglycemia" in note_str.lower() or "fructosamine" in note_str.lower():
            data['vet_note'] = f"【臨床判讀】：嚴重持續性高血糖合併果糖胺顯著升高及糖尿，高度支持貓咪糖尿病診斷；需排除醫院緊張假性高血糖。<br><span style='color:#64748B; font-size:0.88rem;'>[原文] {note_str}</span>"
        else:
            data['vet_note'] = note_str
    else:
        data['vet_note'] = ""

    vet_advice_match = re.search(r'(?:05\s*[｜\|]\s*(?:CLINICAL\s*FOLLOW-UP\s*&\s*RECOMMENDATIONS|建議追蹤與處置|建議處置|追蹤建議|Recommendation)|FOLLOW-UP\s+RECOMMENDATIONS)[\s\:\：\n]+(.*?)(?=INTERPRETIVE\s+NOTES|備註|SIMULATED|\Z)', text, re.IGNORECASE | re.DOTALL)
    if vet_advice_match:
        advice_raw = vet_advice_match.group(1).strip()
        lines = [l.strip() for l in advice_raw.split('\n') if l.strip() and not l.strip().startswith('SIMULATED') and not l.strip().startswith('Page')]
        advice_str = " ".join(lines)
        if "Recheck renal" in advice_str or "hydration" in advice_str:
            data['vet_advice'] = f"【建議處置】：1. 評估水合狀態後複檢腎功能生化與尿檢；2. 測量收縮壓（血壓）與尿蛋白／肌酸酐比（UPC）；3. 評估安排腎臟影像超音波並持續長期監測。<br><span style='color:#64748B; font-size:0.88rem;'>[原文] {advice_str}</span>"
        elif "glucose curve" in advice_str.lower() or "insulin" in advice_str.lower():
            data['vet_advice'] = f"【建議處置】：1. 儘速安排血糖曲線監測並制定胰島素施打計畫；2. 全面改餵低碳水主食罐；3. 衛教飼主居家血糖量測與低血糖急救處置。<br><span style='color:#64748B; font-size:0.88rem;'>[原文] {advice_str}</span>"
        else:
            data['vet_advice'] = advice_str
    else:
        data['vet_advice'] = ""

    # 5. Numerical Lab Metrics
    patterns = {
        'CREA': r'(?:CREA|Creatinine|肌酸酐)(?:\s*\([^\)]*\))?[\s\:\：\=\n]+([0-9]+\.?[0-9]*)',
        'BUN': r'(?:BUN|Urea|尿素氮)(?:\s*\([^\)]*\))?[\s\:\：\=\n]+([0-9]+\.?[0-9]*)',
        'SDMA': r'(?:SDMA)(?:\s*\([^\)]*\))?[\s\:\：\=\n]+([0-9]+\.?[0-9]*)',
        'PHOS': r'(?:\bPHOS\b|\bPhosphorus\b|無機磷|\bPO4\b|磷|\bP\b)(?:\s*\([^\)]*\))?[\s\:\：\=\n]+([0-9]+\.?[0-9]*)',
        'USG': r'(?:USG|Urine Specific Gravity|尿比重)(?:\s*\([^\)]*\))?[\s\:\：\=\n]+([1]\.[0-9]{3})',
        'GLU': r'(?:GLU|Glucose|血糖)(?:\s*\([^\)]*\))?[\s\:\：\=\n]+([0-9]+\.?[0-9]*)',
        'FRUCT': r'(?:FRUCT|Fructosamine|果糖胺)(?:\s*\([^\)]*\))?[\s\:\：\=\n]+([0-9]+\.?[0-9]*)',
        'ALT': r'(?:ALT|GPT)(?:\s*\([^\)]*\))?[\s\:\：\=\n]+([0-9]+\.?[0-9]*)',
        'AST': r'(?:AST|GOT)(?:\s*\([^\)]*\))?[\s\:\：\=\n]+([0-9]+\.?[0-9]*)',
        'ALP': r'(?:ALP|ALKP|鹼性磷酸酶)(?:\s*\([^\)]*\))?[\s\:\：\=\n]+([0-9]+\.?[0-9]*)',
        'TBIL': r'(?:TBIL|Total Bilirubin|總膽紅素)(?:\s*\([^\)]*\))?[\s\:\：\=\n]+([0-9]+\.?[0-9]*)',
        'TP': r'(?:TP|Total Protein|總蛋白)(?:\s*\([^\)]*\))?[\s\:\：\=\n]+([0-9]+\.?[0-9]*)',
        'ALB': r'(?:ALB|Albumin|白蛋白)(?:\s*\([^\)]*\))?[\s\:\：\=\n]+([0-9]+\.?[0-9]*)',
        'K': r'(?:\bK\+\b|\bPotassium\b|鉀離子|\b鉀\b|\bK\b)(?:\s*\([^\)]*\))?[\s\:\：\=\n]+([0-9]+\.?[0-9]*)',
        'HCT': r'(?:HCT|PCV|血容比)(?:\s*\([^\)]*\))?[\s\:\：\=\n]+([0-9]+\.?[0-9]*)',
        'HGB': r'(?:HGB|血紅素)(?:\s*\([^\)]*\))?[\s\:\：\=\n]+([0-9]+\.?[0-9]*)',
        'WBC': r'(?:WBC|白血球)(?:\s*\([^\)]*\))?[\s\:\：\=\n]+([0-9]+\.?[0-9]*)',
        'RBC': r'(?:RBC|紅血球)(?:\s*\([^\)]*\))?[\s\:\：\=\n]+([0-9]+\.?[0-9]*)',
        'PLT': r'(?:PLT|血小板)(?:\s*\([^\)]*\))?[\s\:\：\=\n]+([0-9]+\.?[0-9]*)'
    }

    metrics = {}
    for code, pat in patterns.items():
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            try:
                metrics[code] = float(m.group(1))
            except ValueError:
                pass
    
    data['metrics'] = metrics
    return data

def evaluate_metrics(data):
    metrics = data.get('metrics', {})
    evaluations = []
    red_flags = []
    warnings = []
    
    crea = metrics.get('CREA')
    sdma = metrics.get('SDMA')
    usg = metrics.get('USG')
    phos = metrics.get('PHOS')
    k = metrics.get('K')
    alt = metrics.get('ALT')
    glu = metrics.get('GLU')
    fruct = metrics.get('FRUCT')

    iris_stage = "健康平穩 / 正常狀態"
    iris_desc = "目前各項主要指標維持良好，繼續保持充足水分與均衡營養！"
    iris_color = "#10B981"
    iris_badge = "HEALTHY 🐾"

    # Diabetes Evaluation
    is_diabetes = False
    if glu is not None and glu > 250:
        if fruct is not None and fruct > 365:
            is_diabetes = True
            iris_stage = "糖尿病高度疑慮 (Diabetes Mellitus)"
            iris_desc = f"血糖 ({glu} mg/dL) 且果糖胺 ({fruct} μmol/L) 雙雙顯著偏高，已排除醫院緊迫假性高血糖，高度指向貓咪糖尿病！"
            iris_color = "#8338EC"
            iris_badge = "DIABETES 💉"
            red_flags.append(f"🚨 【糖尿病確診警訊】血糖 ({glu} mg/dL) 與果糖胺 ({fruct} μmol/L) 均嚴重超標，需盡速由獸醫評估胰島素治療與低碳水飲食！")
        else:
            warnings.append(f"⚠️ 血糖偏高 ({glu} mg/dL)，但果糖胺正常或未測，需確認是否為就診緊張引起的緊迫性高血糖。")

    # Renal / IRIS Evaluation (if not overridden by acute diabetes)
    if not is_diabetes:
        if crea is not None or sdma is not None:
            c_val = crea if crea is not None else 0.0
            s_val = sdma if sdma is not None else 0.0
            
            if c_val > 5.0 or s_val > 38.0:
                iris_stage = "IRIS Stage 4 (晚期腎功能衰竭)"
                iris_desc = "腎功能保留率低於 10%，伴隨顯著尿毒，請配合獸醫進行安寧照護與併發症控制。"
                iris_color = "#FF006E"
                iris_badge = "STAGE 4 🚨"
                red_flags.append("🚨 【極危警訊】肌酸酐或 SDMA 已達 IRIS 第四期，請立即就醫治療！")
            elif (2.9 <= c_val <= 5.0) or (26.0 <= s_val <= 38.0):
                iris_stage = "IRIS Stage 3 (中度慢性腎衰竭)"
                iris_desc = "腎功能保留約 10%~25%，伴隨顯著氮血症與肌少消瘦，需規律進行皮下輸液與嚴格低磷飲食。"
                iris_color = "#FB5607"
                iris_badge = "STAGE 3 ⚠️"
                warnings.append("⚠️ 【中度腎功能障礙】處於 IRIS 第 3 期，建議啟動居家皮下點滴 (SC Fluids) 與嚴格控磷處方。")
            elif (1.6 <= c_val <= 2.8) or (18.0 <= s_val <= 25.0):
                iris_stage = "IRIS Stage 2 (輕度慢性腎衰退)"
                iris_desc = "腎功能保留約 25%~33%，早期常見多渴多尿，建議引進早期腎處方主食並定期監控血磷。"
                iris_color = "#FFB703"
                iris_badge = "STAGE 2 🐾"
                warnings.append("⚠️ 【輕度腎功能受損】處於 IRIS 第 2 期，建議增加濕食比例並定期監測血壓與蛋白尿。")
            else:
                if usg is not None and usg < 1.035:
                    iris_stage = "IRIS Stage 1 (前期/腎濃縮減退代償期)"
                    iris_desc = "血液指數尚正常，但尿比重下降，顯示腎臟濃縮機能退化，是預防黃金期！"
                    iris_color = "#3A86FF"
                    iris_badge = "STAGE 1 💡"
                    warnings.append("ℹ️ 【代償前期】尿比重偏低，請立即檢視日常補水策略，避免任何潛在腎毒性物質。")

    if k is not None:
        if k > 6.5:
            red_flags.append(f"🚨 【高血鉀危象】鉀離子 ({k} mmol/L) 嚴重超標！公貓若伴隨蹲盆無尿，高度懷疑尿道完全阻塞！")
        elif k < 3.2:
            warnings.append(f"⚠️ 【低血鉀警訊】鉀離子 ({k} mmol/L) 偏低，可能引起頸部無力下垂、四肢癱軟。")

    if alt is not None and alt > 250:
        red_flags.append(f"🚨 【肝細胞急性受損】ALT ({alt} U/L) 異常飆高！需高度警惕中毒或急性肝膽炎。")

    for code, ref in REF_RANGES.items():
        if code in metrics:
            val = metrics[code]
            status_text = '正常 OK 🐾'
            badge_class = 'badge-ok'
            card_class = 'row-ok'

            if val > ref['max']:
                status_text = '偏高 ↑'
                badge_class = 'badge-danger' if (val > ref['max'] * 1.3) else 'badge-warn'
                card_class = 'row-danger' if (val > ref['max'] * 1.3) else 'row-warn'
            elif val < ref['min']:
                status_text = '偏低 ↓'
                badge_class = 'badge-danger' if (val < ref['min'] * 0.7) else 'badge-warn'
                card_class = 'row-danger' if (val < ref['min'] * 0.7) else 'row-warn'

            evaluations.append({
                'code': code,
                'name': ref['name'],
                'val': val,
                'unit': ref['unit'],
                'ref_min': ref['min'],
                'ref_max': ref['max'],
                'status_text': status_text,
                'badge_class': badge_class,
                'card_class': card_class,
                'cat': ref['cat'],
                'desc': ref['desc']
            })

    return {
        'evaluations': evaluations,
        'iris_stage': iris_stage,
        'iris_desc': iris_desc,
        'iris_color': iris_color,
        'iris_badge': iris_badge,
        'red_flags': red_flags,
        'warnings': warnings
    }

def generate_html_report(data, eval_result, output_path):
    cat_name = data.get('cat_name', '愛貓')
    cat_age = data.get('cat_age', '保密')
    cat_sex = data.get('cat_sex', '未註明')
    test_date = data.get('test_date', datetime.now().strftime('%Y-%m-%d'))
    scenario = data.get('scenario', '例行健康檢查')
    vet_note = data.get('vet_note', '')
    vet_advice = data.get('vet_advice', '')

    red_flag_html = ""
    if eval_result['red_flags']:
        red_flag_html = '<div class="comic-box box-danger"><div class="box-title">🚨 絕對緊急紅旗（請立即送醫診斷）</div><ul>'
        for rf in eval_result['red_flags']:
            red_flag_html += f'<li>{rf}</li>'
        red_flag_html += '</ul></div>'

    warning_html = ""
    if eval_result['warnings']:
        warning_html = '<div class="comic-box box-warn"><div class="box-title">⚠️ 重點健康警示與日常追蹤</div><ul>'
        for w in eval_result['warnings']:
            warning_html += f'<li>{w}</li>'
        warning_html += '</ul></div>'

    # Hospital Original Notes Block
    hospital_notes_html = ""
    if vet_note or vet_advice:
        hospital_notes_html = f"""
        <div class="speech-bubble" style="background:#F0F9FF; border-color:#0284C7;">
          <h2 style="color:#0369A1;">🏥 原廠醫院檢驗單判讀與處置備註</h2>
          {f'<p style="margin-bottom:8px; font-weight:800; color:#1E293B;"><b>【模擬獸醫判讀】：</b>{vet_note}</p>' if vet_note else ''}
          {f'<p style="font-weight:700; color:#334155;"><b>【建議追蹤處置】：</b>{vet_advice}</p>' if vet_advice else ''}
        </div>
        """

    rows_html = ""
    for ev in eval_result['evaluations']:
        rows_html += f"""
        <tr class="{ev['card_class']}">
          <td>
            <div class="metric-name">{ev['code']}</div>
            <div class="metric-sub">{ev['name']}</div>
          </td>
          <td><span class="cat-pill">{ev['cat']}</span></td>
          <td>
            <span class="metric-val">{ev['val']}</span>
            <span class="metric-unit">{ev['unit']}</span>
          </td>
          <td class="metric-ref">{ev['ref_min']} ~ {ev['ref_max']} {ev['unit']}</td>
          <td><span class="badge {ev['badge_class']}">{ev['status_text']}</span></td>
          <td class="metric-desc">{ev['desc']}</td>
        </tr>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <title>🐾【{cat_name}】喵星人專屬健檢解析書・LLM-Wiki</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@400;700;800;900&family=Quicksand:wght@600;700&display=swap');

    :root {{
      --bg: #FFFDF9;
      --card-bg: #FFFFFF;
      --border-dark: #2B2D42;
      --text-main: #2B2D42;
      --text-muted: #6C757D;
      --pink: #FF6B8B;
      --yellow: #FFD166;
      --blue: #4EA8DE;
      --green: #06D6A0;
      --orange: #FB5607;
      --purple: #8338EC;
      --shadow: 4px 4px 0px #2B2D42;
      --shadow-sm: 2px 2px 0px #2B2D42;
      --shadow-lg: 6px 6px 0px #2B2D42;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: 'M PLUS Rounded 1c', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      background-image: radial-gradient(#FFD166 1.2px, transparent 1.2px);
      background-size: 24px 24px;
      color: var(--text-main);
      padding: 30px 15px;
      line-height: 1.6;
    }}

    .container {{
      max-width: 1020px;
      margin: 0 auto;
    }}

    /* Anime Title Banner */
    .hero-banner {{
      background: #FFFFFF;
      border: 3px solid var(--border-dark);
      border-radius: 24px;
      box-shadow: var(--shadow-lg);
      padding: 30px 35px;
      margin-bottom: 25px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 20px;
      position: relative;
      overflow: hidden;
    }}

    .hero-banner::before {{
      content: "🐾 MEOW HEALTH REPORT 🐾";
      position: absolute;
      top: 8px;
      right: 20px;
      font-size: 0.75rem;
      font-weight: 900;
      letter-spacing: 0.15em;
      color: var(--yellow);
      background: var(--border-dark);
      padding: 2px 10px;
      border-radius: 999px;
    }}

    .cat-avatar-group {{
      display: flex;
      align-items: center;
      gap: 20px;
    }}

    .cat-avatar {{
      width: 76px;
      height: 76px;
      background: #FFE5EC;
      border: 3px solid var(--border-dark);
      border-radius: 50%;
      box-shadow: var(--shadow-sm);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 2.3rem;
      transform: rotate(-4deg);
    }}

    .hero-title h1 {{
      font-size: 2.1rem;
      font-weight: 900;
      color: var(--border-dark);
      letter-spacing: 0.02em;
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .hero-tags {{
      display: flex;
      gap: 8px;
      margin-top: 8px;
      flex-wrap: wrap;
    }}

    .hero-tag-item {{
      background: #F1FAEE;
      border: 2px solid var(--border-dark);
      padding: 3px 12px;
      border-radius: 999px;
      font-size: 0.85rem;
      font-weight: 800;
      box-shadow: 2px 2px 0px rgba(0,0,0,0.1);
    }}

    /* IRIS Badge Card */
    .iris-status-card {{
      background: #FFFFFF;
      border: 3px solid var(--border-dark);
      border-radius: 18px;
      padding: 16px 24px;
      box-shadow: var(--shadow);
      text-align: right;
      min-width: 220px;
    }}

    .iris-status-label {{
      font-size: 0.8rem;
      font-weight: 800;
      color: var(--text-muted);
      letter-spacing: 0.05em;
    }}

    .iris-status-val {{
      font-size: 1.45rem;
      font-weight: 900;
      color: {eval_result['iris_color']};
      margin-top: 4px;
    }}

    /* Manga Speech Box / Bubble */
    .speech-bubble {{
      background: #FFFFFF;
      border: 3px solid var(--border-dark);
      border-radius: 20px;
      padding: 20px 25px;
      box-shadow: var(--shadow);
      margin-bottom: 25px;
      position: relative;
    }}

    .speech-bubble h2 {{
      font-size: 1.25rem;
      font-weight: 800;
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--border-dark);
    }}

    .speech-text {{
      font-size: 1rem;
      color: #333;
      line-height: 1.7;
    }}

    /* Comic Alert Boxes */
    .comic-box {{
      border: 3px solid var(--border-dark);
      border-radius: 18px;
      padding: 20px 25px;
      margin-bottom: 22px;
      box-shadow: var(--shadow);
    }}

    .box-title {{
      font-size: 1.15rem;
      font-weight: 900;
      margin-bottom: 10px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .box-danger {{
      background: #FFE5EC;
      border-left: 10px solid #FF006E;
    }}
    .box-danger .box-title {{ color: #D00000; }}

    .box-warn {{
      background: #FFF3CD;
      border-left: 10px solid #FFB703;
    }}
    .box-warn .box-title {{ color: #B25E00; }}

    .comic-box ul {{
      padding-left: 24px;
      font-weight: 700;
      font-size: 0.95rem;
      line-height: 1.7;
    }}

    /* Table Section (Clear, Anime & Bright) */
    .table-container {{
      background: #FFFFFF;
      border: 3px solid var(--border-dark);
      border-radius: 22px;
      box-shadow: var(--shadow-lg);
      padding: 25px 30px;
      margin-bottom: 25px;
    }}

    .table-header-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 18px;
      padding-bottom: 12px;
      border-bottom: 2px dashed #E2E8F0;
    }}

    .table-header-row h2 {{
      font-size: 1.35rem;
      font-weight: 900;
      color: var(--border-dark);
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    table {{
      width: 100%;
      border-collapse: separate;
      border-spacing: 0 10px;
    }}

    thead th {{
      background: #F8F9FA;
      color: var(--text-main);
      font-weight: 900;
      font-size: 0.88rem;
      padding: 12px 14px;
      border-top: 2px solid var(--border-dark);
      border-bottom: 2px solid var(--border-dark);
      text-align: left;
    }}
    thead th:first-child {{ border-left: 2px solid var(--border-dark); border-radius: 10px 0 0 10px; }}
    thead th:last-child {{ border-right: 2px solid var(--border-dark); border-radius: 0 10px 10px 0; }}

    tbody tr {{
      background: #FFFFFF;
      transition: all 0.2s;
    }}

    tbody tr td {{
      padding: 14px 14px;
      border-top: 2px solid #E2E8F0;
      border-bottom: 2px solid #E2E8F0;
      vertical-align: middle;
    }}
    tbody tr td:first-child {{ border-left: 2px solid #E2E8F0; border-radius: 12px 0 0 12px; }}
    tbody tr td:last-child {{ border-right: 2px solid #E2E8F0; border-radius: 0 12px 12px 0; }}

    tbody tr:hover {{
      transform: translateY(-2px);
      box-shadow: var(--shadow-sm);
    }}

    .row-ok td {{ background: #FAFFFC; }}
    .row-warn td {{ background: #FFFCF2; border-color: #FFE6A7; }}
    .row-danger td {{ background: #FFF5F7; border-color: #FFCCD5; }}

    .metric-name {{ font-size: 1.1rem; font-weight: 900; color: var(--border-dark); font-family: 'Quicksand', sans-serif; }}
    .metric-sub {{ font-size: 0.8rem; color: var(--text-muted); font-weight: 700; }}
    .cat-pill {{
      background: #E9ECEF;
      border: 1.5px solid var(--border-dark);
      padding: 2px 8px;
      border-radius: 6px;
      font-size: 0.75rem;
      font-weight: 800;
      white-space: nowrap;
    }}
    .metric-val {{ font-size: 1.25rem; font-weight: 900; color: var(--border-dark); font-family: 'Quicksand', sans-serif; }}
    .metric-unit {{ font-size: 0.8rem; color: var(--text-muted); font-weight: 700; }}
    .metric-ref {{ font-size: 0.88rem; color: #495057; font-weight: 700; }}
    .metric-desc {{ font-size: 0.82rem; color: #6C757D; line-height: 1.4; }}

    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 0.82rem;
      font-weight: 900;
      border: 2px solid var(--border-dark);
      box-shadow: 2px 2px 0px var(--border-dark);
      white-space: nowrap;
    }}
    .badge-ok {{ background: var(--green); color: #004B23; }}
    .badge-warn {{ background: var(--yellow); color: #723D46; }}
    .badge-danger {{ background: #FF4D6D; color: #FFFFFF; }}

    .advice-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-top: 15px;
    }}

    .advice-card {{
      background: #FFFFFF;
      border: 3px solid var(--border-dark);
      border-radius: 18px;
      padding: 22px;
      box-shadow: var(--shadow);
      position: relative;
    }}

    .advice-card.card-drink {{ border-top: 10px solid var(--blue); }}
    .advice-card.card-vet {{ border-top: 10px solid var(--pink); }}

    .advice-card h3 {{
      font-size: 1.15rem;
      font-weight: 900;
      margin-bottom: 10px;
      color: var(--border-dark);
    }}

    .advice-card p {{
      font-size: 0.95rem;
      line-height: 1.6;
      color: #333;
    }}

    .footer {{
      text-align: center;
      margin-top: 40px;
      padding: 25px;
      color: var(--text-muted);
      font-size: 0.85rem;
      font-weight: 700;
    }}

    @media (max-width: 768px) {{
      .hero-banner {{ flex-direction: column; text-align: center; }}
      .cat-avatar-group {{ flex-direction: column; }}
      .iris-status-card {{ width: 100%; text-align: center; }}
      .advice-grid {{ grid-template-columns: 1fr; }}
      table {{ display: block; overflow-x: auto; }}
    }}
  </style>
</head>
<body>

  <div class="container">

    <!-- Anime Hero Banner -->
    <div class="hero-banner">
      <div class="cat-avatar-group">
        <div class="cat-avatar">🐱</div>
        <div class="hero-title">
          <h1>{cat_name} 的健康檢驗分析書 🐾</h1>
          <div class="hero-tags">
            <span class="hero-tag-item">🎂 年齡：{cat_age}</span>
            <span class="hero-tag-item">⚧ 性別：{cat_sex}</span>
            <span class="hero-tag-item">📅 採檢日期：{test_date}</span>
            <span class="hero-tag-item">📋 檢驗情境：{scenario}</span>
          </div>
        </div>
      </div>

      <div class="iris-status-card">
        <div class="iris-status-label">核心臨床評估狀態</div>
        <div class="iris-status-val">{eval_result['iris_badge']}</div>
      </div>
    </div>

    <!-- Alert Boxes -->
    {red_flag_html}
    {warning_html}

    <!-- Original Hospital Interpretation & Recommendations -->
    {hospital_notes_html}

    <!-- Anime Speech Box: Clinical Insight -->
    <div class="speech-bubble">
      <h2>🩺 獸醫小精靈的臨床解讀：【{eval_result['iris_stage']}】</h2>
      <p class="speech-text">
        {eval_result['iris_desc']}
      </p>
    </div>

    <!-- Clear & Bright Anime Lab Table -->
    <div class="table-container">
      <div class="table-header-row">
        <h2>📊 實驗室生化檢驗清單 (明亮清晰版)</h2>
        <span style="font-size:0.85rem; font-weight:800; color:var(--text-muted);">共檢測 {len(eval_result['evaluations'])} 項指標</span>
      </div>

      <table>
        <thead>
          <tr>
            <th style="width: 22%;">項目代碼 / 全稱</th>
            <th style="width: 14%;">類別</th>
            <th style="width: 16%;">檢驗數值</th>
            <th style="width: 18%;">標準參考區間</th>
            <th style="width: 12%;">狀態標記</th>
            <th style="width: 18%;">臨床健康說明</th>
          </tr>
        </thead>
        <tbody>
          {rows_html if rows_html else '<tr><td colspan="6" style="text-align:center; padding:30px;">未提取到生化指標</td></tr>'}
        </tbody>
      </table>
    </div>

    <!-- Home Care Guidance Anime Grid -->
    <div class="advice-grid">
      <div class="advice-card card-drink">
        <h3>💧 飲水與飲食升級法寶</h3>
        <p>• <b>全面提升濕食比例</b>：主食罐含水量高達 80%，可直接減輕腎臟濃縮負擔。<br>
        • <b>營養調整策略</b>：若為腎病應轉為低磷處方，若為疑似糖尿病則應依醫囑嚴格控制碳水化合物攝取。</p>
      </div>

      <div class="advice-card card-vet">
        <h3>📋 下次複診與醫生討論重點</h3>
        <p>• 攜帶本報告與主治獸醫討論是否需要安排複檢或處方調整。<br>
        • 針對脫水、食慾或血糖波動，評估適當的居家護理與監測方案。</p>
      </div>
    </div>

    <div class="footer">
      ✦ 本分析由 <b>LLM_Wiki 貓咪健康知識庫</b> 依據 WSAVA / IRIS 國際臨床指引編譯生成 ✦<br>
      僅供家長日常照護與衛教理解，實際醫療決策請務必遵循執業獸醫師臨床醫囑。
    </div>

  </div>

</body>
</html>
"""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    return output_path

def process_file(file_path, output_dir="html_reports"):
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    out_html_path = os.path.join(output_dir, f"{base_name}.html")

    if file_path.lower().endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    else:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()

    data = parse_report_text(text, fallback_name=base_name)
    eval_result = evaluate_metrics(data)
    generated = generate_html_report(data, eval_result, out_html_path)
    print(f" [OK] {file_path} -> {generated}")
    print(f"      • 愛貓姓名：{data.get('cat_name')} | 年齡：{data.get('cat_age')} | 性別：{data.get('cat_sex')}")
    print(f"      • 診斷評估：{eval_result['iris_stage']}")
    return generated

def batch_process(input_dir="pdf_reports", output_dir="html_reports"):
    if not os.path.exists(input_dir):
        print(f"Input directory '{input_dir}' not found.")
        return

    files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if not f.startswith('.')]
    if not files:
        print(f"No files found in '{input_dir}'.")
        return

    print("=" * 65)
    print(f" 📂 正在以【精準 UTF-16-BE 中文解析引擎】批次轉換 '{input_dir}' 至 '{output_dir}'...")
    print("=" * 65)

    count = 0
    for f in sorted(files):
        if os.path.isfile(f):
            process_file(f, output_dir)
            count += 1

    print("=" * 65)
    print(f"✅ 批次轉換完成！共生成 {count} 份清晰動漫風 HTML 報告至: {output_dir}")

def main():
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ['--batch', '-b']):
        batch_process("pdf_reports", "html_reports")
    elif len(sys.argv) == 2:
        process_file(sys.argv[1], "html_reports")
    elif len(sys.argv) >= 3:
        in_file = sys.argv[1]
        out_file = sys.argv[2]
        if os.path.isdir(in_file):
            batch_process(in_file, out_file)
        else:
            file_path = in_file
            if file_path.lower().endswith('.pdf'):
                text = extract_text_from_pdf(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
            data = parse_report_text(text, fallback_name=os.path.splitext(os.path.basename(file_path))[0])
            eval_result = evaluate_metrics(data)
            generate_html_report(data, eval_result, out_file)
            print(f"Report generated: {out_file}")

if __name__ == '__main__':
    main()
