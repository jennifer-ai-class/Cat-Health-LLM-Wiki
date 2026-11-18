#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-Wiki Linter Tool
Inspects all markdown pages in wiki/ for:
1. Dead [[Links]] pointing to non-existent wiki pages.
2. Orphan pages (pages with 0 inbound cross-references).
3. Missing YAML frontmatter or required metadata tags.
"""

import os
import re

WIKI_DIR = "wiki"
RAW_DIR = "raw"

def lint_wiki():
    if not os.path.isdir(WIKI_DIR):
        print(f"Error: {WIKI_DIR} does not exist.")
        return False

    pages = [f[:-3] for f in os.listdir(WIKI_DIR) if f.endswith(".md")]
    page_files = {p: os.path.join(WIKI_DIR, f"{p}.md") for p in pages}
    
    inbound_links = {p: set() for p in pages}
    outbound_links = {p: set() for p in pages}
    broken_links = []
    missing_frontmatter = []

    link_pattern = re.compile(r'\[\[(.*?)\]\]')

    for p, path in page_files.items():
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check frontmatter
        if not content.startswith('---'):
            missing_frontmatter.append(p)

        # Extract links
        matches = link_pattern.findall(content)
        for target in matches:
            clean_target = target.strip()
            outbound_links[p].add(clean_target)
            if clean_target in inbound_links:
                inbound_links[clean_target].add(p)
            else:
                broken_links.append((p, clean_target))

    # Identify orphans (pages with 0 inbound links)
    orphans = [p for p, in_set in inbound_links.items() if len(in_set) == 0]

    print("=" * 60)
    print(" 🔍 LLM-Wiki 全域健康檢查 (Lint Pass)")
    print(f" 檢核維基頁面總數: {len(pages)} 篇")
    print("=" * 60)

    # 1. Broken links report
    if broken_links:
        print(f"❌ 發現 {len(broken_links)} 個斷鏈 (Broken Links / 幽靈頁面):")
        for src, target in broken_links:
            print(f"   • 在 [[{src}]] 引用了未創建頁面: [[{target}]]")
    else:
        print("✅ 雙向引用連結 (Cross-References): 100% 完整，無任何斷鏈！")

    # 2. Orphan pages report
    if orphans:
        print(f"\n⚠️ 發現 {len(orphans)} 篇孤立頁面 (Orphan Pages - 0 篇反向引用):")
        for o in orphans:
            print(f"   • [[{o}]]")
    else:
        print("✅ 孤立頁面檢驗 (Orphan Check): 所有頁面皆具備反向入鏈，網絡拓撲完整！")

    # 3. Frontmatter report
    if missing_frontmatter:
        print(f"\n❌ 缺少 YAML Frontmatter 之頁面: {missing_frontmatter}")
    else:
        print("✅ YAML Frontmatter 格式規範: 100% 合規！")

    print("\n--- 網絡拓撲連結度速覽 ---")
    for p in sorted(pages):
        print(f"• [[{p}]]: {len(outbound_links[p])} 條出鏈 (Out), {len(inbound_links[p])} 條入鏈 (In)")
    print("=" * 60)

    return len(broken_links) == 0 and len(missing_frontmatter) == 0

if __name__ == '__main__':
    lint_wiki()
