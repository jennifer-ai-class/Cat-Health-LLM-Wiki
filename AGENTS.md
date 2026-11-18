# AGENTS.md — Cat Health LLM-Wiki Schema & Operational Guide

This document defines the schema, architecture, operational workflows, and conventions for the **Cat Health LLM-Wiki (貓咪健康知識庫)**, following the LLM-Wiki pattern proposed by Andrej Karpathy.

---

## 1. Architecture Overview

```
LLM_Wiki/
├── AGENTS.md            # Schema and operational guidelines (this document)
├── raw/                 # Layer 1: Immutable authoritative sources (Source of Truth)
├── wiki/                # Layer 2: LLM-compiled persistent markdown wiki pages
├── index.md             # Content-oriented catalog & hub of all wiki entities/concepts
├── log.md               # Chronological append-only operational event log
├── presentation/        # Layer 3 output: Interactive HTML educational slide decks
├── pdf_reports/         # Input: Dedicated folder for cat health reports (PDF / txt)
├── html_reports/        # Output: Dedicated folder for corresponding generated analysis HTMLs
├── tools/               # Helper scripts (lint, search, report generator, triage)
└── docs/                # Workflow graph, check records, and assignment reflection
```

### The Three Layers
1. **Raw Sources (`raw/`)**: Read-only source texts from veterinary authorities (ISFM, AAFP, IRIS, WSAVA). Never modified by the LLM once curated.
2. **The Wiki (`wiki/`)**: Interlinked, structured knowledge compiled by the LLM. Maintained with `[[PageName]]` bidirectional links, YAML frontmatter, and clinical definitions.
3. **The Schema (`AGENTS.md`)**: The constitution governing how agents interact with, update, query, and verify the knowledge base.

---

## 2. Core Operations & Workflows

### 2.1 Ingest Workflow ("先討論、後生成")
Every source ingested must go through an explicit discussion turn with the user before files are created or modified:
1. **Analyze Source**: Extract key concepts, entities, clinical indicators, and contradictions.
2. **Discuss (先討論)**:
   - Present: Extracted key points, proposed new wiki pages, and proposed updates to existing pages.
   - Clarify: Inquire about user focus (e.g., beginner owner view, emergency recognition, or clinical thresholds).
3. **Compile (後生成)**:
   - Create or update pages in `wiki/`.
   - Ensure all related entities are cross-linked using `[[PageName]]`.
   - Update `index.md` with new entries and summaries.
   - Append an entry to `log.md` with the standard timestamp format `## [YYYY-MM-DD HH:MM] ingest | Title`.

### 2.2 Query & Synthesis Workflow
When answering queries:
1. Read `index.md` first to locate relevant entity/concept pages.
2. Drill down into specific pages in `wiki/`.
3. Synthesize an evidence-based response with citations pointing to wiki pages and raw sources.
4. If the query yields a high-value synthesis or comparison, optionally offer to file it as a new wiki concept page.

### 2.3 Health Check & Linting Workflow
Periodically run lint checks:
- Verify that every `[[Link]]` has a corresponding file in `wiki/`.
- Ensure no orphan pages (pages without inbound links).
- Check for clinical contradictions (e.g. inconsistent normal reference ranges for hydration or kidney values).
- Log the check outcome in `log.md`.

---

## 3. Extended Capabilities

### 3.1 Feature A: Interactive Triage Dialogue (對話式健康狀況整理)
- **Objective**: Guide an owner through systematic questioning to characterize a cat's symptoms without giving unauthorized veterinary diagnosis.
- **Workflow**:
  1. Intake: Ask about vital signs, hydration test results, urination habits, appetite, and behavior.
  2. Map to Wiki: Cross-reference with `[[脫水評估與補水原則]]`, `[[貓下泌尿道疾病_FLUTD]]`, `[[貓咪疼痛與異常行為評估]]`.
  3. Red Flag Check: Immediately screen for emergencies (e.g., male cat urinary obstruction, open-mouth breathing, sudden hindlimb paralysis, acute toxicity).
  4. Output: Formatted summary of observations and targeted questions to take to the vet.

### 3.2 Feature B: Medical Report / PDF Analysis to HTML (健檢報告分析轉 HTML)
- **Objective**: Ingest laboratory bloodwork/urinalysis values (from PDF, image OCR, or text) and compile an interactive, beautiful HTML diagnostic analysis report.
- **Workflow**:
  1. Extract biomarkers: e.g., Creatinine (CREA), BUN, SDMA, Phosphorus (P), Urine Specific Gravity (USG), ALT, etc.
  2. Benchmark against Wiki: Compare against IRIS staging guidelines and reference ranges documented in `[[慢性腎臟病_CKD]]` and other pages.
  3. Generate HTML: Produce a standalone, visual HTML report with visual status meters, risk stage interpretation, and plain-language dietary/lifestyle suggestions for the owner.

---

## 4. Wiki Page Conventions & Frontmatter

All pages in `wiki/` must begin with YAML frontmatter:
```markdown
---
title: Page Title
category: entity | concept | guide | comparison
sources: [source_01, source_02]
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [cat-health, clinical, prevention]
---
```

Use Obsidian-compatible `[[Target Page]]` syntax for all cross-references.
