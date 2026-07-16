# MISRA-C:2012 AI Fixing Assistant

## Overview

A sophisticated AI-powered assistant that automatically detects and fixes MISRA-C:2012 violations in C code. The system combines Retrieval-Augmented Generation (RAG) with LLM-based code analysis to provide intelligent suggestions for compliance.

## 📖 User Stories & Use Case Documentation

### **Embedded Systems Engineer**
- **Goal**: Automatically detect and fix MISRA-C:2012 violations in embedded C code
- **Scenario**: Developer uploads source files → System analyzes → AI provides fix suggestions
- **Benefits**: Reduced manual effort, consistent compliance, faster development cycle

### **Quality Assurance Team**
- **Goal**: Integrate MISRA compliance checking into CI/CD pipeline
- **Scenario**: Automated analysis reports generated → Fix verification → Compliance validation
- **Benefits**: Consistent standards, early violation detection, improved code quality

### **Technical Documentation Team**
- **Goal**: Document and visualize MISRA rule violations and fixes
- **Scenario**: Generated reports → Categorization → Visualization of violations by type and severity
- **Benefits**: Easier documentation, better tracking of compliance progress

## 🚀 MVP Feature List with Implemented Functionalities

| Feature | Status |
|---------|--------|
| Static Analysis (cppcheck integration) | ✅ |
| MISRA Rule Parser (misrac-2012.txt) | ✅ |
| Vector Database (ChromaDB) | ✅ |
| RAG Retrieval for context | ✅ |
| Code Context Extraction | ✅ |
| LLM Fix Generation (GPT-4/4o) | ✅ |
| Self-Review of generated fixes | ✅ |
| Git patch generation | ✅ |
| Streamlit UI | ✅ |
| Workflow with live progress | ✅ |

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐   ┌─────────────────┐
│   Source Files  │ ──► MISRA Analysis   ──► │   Violations    │
│   (src/)        │    │   (cppcheck)    │   │                 │
└─────────────────┘    └─────────────────┘   └─────────────────┘
      │                                          │    │
      ▼                                    ┌-----┘    │
┌─────────────────┐    ┌─────────────────┐ │          │
│   CSV Reports   │◄───┤   Example Suite │◄┘          │
│   (report/)     │    │   (R_*.c, etc.) │            │
└─────────────────┘    └─────────────────┘            │
                                                      │
┌─────────────────┐   ┌──────────────────┐   ┌─────────────────┐
│   Categorizer   │   │ Context Extractor│   │ Vector Store    │
│                 │   │                  │   │ (ChromaDB)      │
└─────────────────┘   └──────────────────┘   └─────────────────┘
       │                      │                     │
       └──────────────────────┼─────────────────────┘
                              ▼
                    ┌─────────────────┐
                    │    LLM Fix      │
                    │   Generator     │
                    └─────────────────┘
```

### End-to-End Pipeline

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                        │
│  Phase 1: Static Analysis (main.py)                                                                    │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │  src/example.c ──► cppcheck --dump ──► src/example.c.dump (XML: AST, types, symbols, CFG)        │  │
│  │                              └──► src/example.c.ctu-info (JSON: cross-file symbols)              │  │
│  │  src/example.c.dump + misrac-2012.txt ──► python misra.py ──► report/example.c.csv               │  │
│  └──────────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                                        │
│  Phase 2: Violation Ingestion (backend/ingestion/)                                                     │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │  report/*.csv ──► csv_loader.load_all_reports() ──► List[Violation]                              │  │
│  └──────────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                                        │
│  Phase 3: Context Enrichment (backend/analysis/)                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │  For each Violation:                                                                             │  │
│  │  CodeContextExtractor + DumpParser + RAGRetriever → CodeContext object                           │  │
│  │  - surrounding_lines, function_scope, dump_context, ctu_context                                  │  │
│  └──────────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                                        │
│  Phase 4: Fix Generation (backend/fix_generation/)                                                     │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │  LLM Prompt (Rule + Code + Static Analysis Context + RAG Examples)                               │  │
│  │  LLM ──► Fix(description, original_code, fixed_code) ──► Self-Review ──► Git Patch               │  │
│  └──────────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                                        │
│  Output: patches/rule_X.Y.patch + results.json                                                         │
│                                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### File Roles

| File | Generated By | Consumed By | Purpose |
|------|-------------|-----------|---------|
| `src/example.c` | Developer | cppcheck, CodeContextExtractor | Original source code |
| `src/example.c.dump` | cppcheck --dump | DumpParser → FixGenerator | AST, resolved types, symbols, CFG |
| `src/example.c.ctu-info` | cppcheck --dump | DumpParser → FixGenerator | Cross-file symbol visibility |
| `report/example.c.csv` | misra.py (via main.py) | csv_loader | Violation list |
| `misrac-2012.txt` | main.py (from Example Suite) | misra.py | Rule descriptions |
| `chroma_db/` | EmbeddingPipeline | RAGRetriever | Vector-embedded rule examples |
| `patches/rule_X.Y.patch` | FixGenerator | Developer/CLI | Unified diffs for each rule |

## 🎨 Interface Mockups & Screenshots

### Workflow Progress UI
```
┌───────────────────────────────────────────────────┐
│ Workflow Progress                                 │
├───────────────────────────────────────────────────┤
  1️⃣ MISRA Scan   ✓ Completed                       
  2️⃣ Generate Fixes ⏳ Running                                        
  3️⃣ Review Patches ⏸ Pending                      
└───────────────────────────────────────────────────┘
```

### Source File Browser
- Displays selected source file with code preview
- Shows file statistics (lines, comments, size)
- Lists function signatures detected in the file

### RAG / Vector DB Explorer
- Rule search with live results
- Collection statistics display
- Data relationship visualization placeholder

## 🏗️ Source Code Structure

```
misrac-checker/
├── backend/
│   ├── cli.py              # CLI interface
│   ├── ingestion/          # CSV loader, example suite parser
│   ├── analysis/           # Context extractor, workflow
│   ├── rag/                # Vector store, embeddings, retriever
│   ├── fix_generation/     # LLM prompts, fix generator
│   └── utils/              # Models, config
├── frontend/
│   ├── app.py              # Streamlit application
│   └── services/           # Backend runner
├── src/                    # C source files to analyze
├── report/                 # Generated CSV violation reports
├── patches/                # Generated git patches
└── tests/                  # Unit tests
```

## 🧪 Test Plan and Results Summary

### Test Coverage
- **23 tests** total, all passing
- Full coverage of data models, CSV parsing, categorization
- Mocked LLM tests for fix generation

### Test Commands
```bash
python -m pytest tests/
```

### Verified Workflows
1. ✅ Static analysis with cppcheck
2. ✅ MISRA violation detection
3. ✅ CSV report generation
4. ✅ Vector database initialization
5. ✅ Fix generation and patch creation
6. ✅ UI navigation and workflow