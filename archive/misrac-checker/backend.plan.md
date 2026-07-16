# MISRA-C:2012 AI Fixing Assistant — Implementation Plan

## Objective

Design and develop a MISRA-C:2012 fixing intelligent AI assistant leveraging Retrieval-Augmented Generation (RAG) techniques.

## Tech Stack

| Category | Technology |
|---|---|
| LLM APIs | OpenAI API (GPT-4/4o) |
| Orchestration | LangChain, LangGraph (for multi-step/agentic workflows) |
| Embeddings | OpenAI API for custom models/embeddings |
| Vector Database | ChromaDB (local) |

## Workspace Layout

| Folder | Purpose |
|--------|---------|
| `backend/` | Python modules for the AI assistant |
| `src/` | C source code (referenced by CSV reports) |
| `report/` | CSV violation reports |
| `Example-Suite-master/` | MISRA C:2012 example files (`.c`, `.h`) |
| `tests/` | Unit and integration tests |

---

## Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Reports folder | `./report` (existing) | Matches current `main.py` output |
| Vector Database | ChromaDB (local) | No external service needed, good for development |
| Processing scope | All Example Suite files | Batch process all `R_*.c` and `D_*.c` files |
| Fix validation | LLM self-review only | Faster iteration, no re-run of MISRA checker |
| Orchestration | LangGraph | Agentic multi-step workflows |
| LLM Provider | OpenAI (GPT-4/4o) | High-quality code generation |

---

## Implementation Steps

### Phase 1: Infrastructure Setup

| # | Step | Status |
|---|------|--------|
| 1.1 | Create `backend/` modules: `ingestion`, `analysis`, `rag`, `fix_generation`, `utils` | ✅ Done |
| 1.2 | Create `requirements.txt` (LangChain, LangGraph, OpenAI, ChromaDB) | ✅ Done |
| 1.3 | Create `.env.example` for OpenAI API key | ✅ Done |

### Phase 2: Data Ingestion

| # | Step | Dependencies | Status |
|---|------|--------------|--------|
| 2.1 | CSV report loader for `./report/*.csv` | Phase 1 | ✅ Done |
| 2.2 | Example Suite parser for `./Example-Suite-master/` — discovers all related files per rule (`.c`, `.h`, system/support files, common headers) | Phase 1 | ✅ Done |
| 2.3 | Data models: `Violation`, `Rule`, `CodeContext`, `Fix`, `RuleGroupFix` | 2.1, 2.2 | ✅ Done |

**Example Suite Parser Details:**
- Primary rule files: `R_xx_yy.c`, `D_xx_yy.c`
- Associated headers: `R_xx_yy.h`, `D_xx_yy.h`, shared headers (e.g., `R_08_08.h`)
- System/support files: `R_xx_system.c`, `R_xx_support.c` (for "System" scope rules)
- Common headers: `mc3_header.h`, `mc3_types.h`

### Phase 3: RAG Pipeline

| # | Step | Dependencies | Status |
|---|------|--------------|--------|
| 3.1 | Initialize ChromaDB vector store | Phase 1 | ✅ Done |
| 3.2 | Embed MISRA rules + examples into vector store | 2.3, 3.1 | ✅ Done |
| 3.3 | Retrieval: query relevant context per violation | 3.2 | ✅ Done |

### Phase 4: Analysis Engine

| # | Step | Dependencies | Status |
|---|------|--------------|--------|
| 4.1 | Code context extractor — reads source files from `src/` | 2.3 | ✅ Done |
| 4.2 | LangGraph workflow for multi-step analysis | Phase 1 | ✅ Done |
| 4.3 | Violation categorization & priority scoring | 4.1, 4.2 | ✅ Done |

### Phase 5: Fix Generation

| # | Step | Dependencies | Status |
|---|------|--------------|--------|
| 5.1 | LLM prompt templates with RAG context | 3.3, 4.3 | ✅ Done |
| 5.2 | Fix generation via OpenAI API | 5.1 | ✅ Done |
| 5.3 | Git patch generation per rule group | 5.2 | ✅ Done |
| 5.4 | LLM self-review of generated fixes | 5.3 | ✅ Done |

### Phase 6: Integration

| # | Step | Dependencies | Status |
|---|------|--------------|--------|
| 6.1 | CLI interface for the AI assistant | Phase 5 | ✅ Done |
| 6.2 | End-to-end tests with Example Suite | All phases | ✅ Done |

---

## CLI Usage

```bash
# Activate virtual environment
source venv/bin/activate

# Set up .env with your OpenAI API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Initialize vector store with Example Suite
python -m backend.cli init

# Analyze violations and generate fixes
python -m backend.cli analyze --output results.json --patch-dir ./patches

# List violations from reports
python -m backend.cli list
```

---

## Project Structure

```
misrac-checker/
├── backend/
│   ├── __init__.py
│   ├── cli.py                          # CLI interface (init, analyze, list)
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── csv_loader.py               # CSV report loader
│   │   └── example_suite_parser.py     # Example Suite parser
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── context_extractor.py        # Code context extractor
│   │   ├── dump_parser.py              # Cppcheck .dump + .ctu-info parser
│   │   ├── categorizer.py              # Violation categorization
│   │   └── workflow.py                 # Multi-step workflow
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── vector_store.py             # ChromaDB vector store
│   │   ├── embedding_pipeline.py       # OpenAI embeddings
│   │   └── retriever.py                # RAG retrieval
│   ├── fix_generation/
│   │   ├── __init__.py
│   │   ├── prompts.py                  # LLM prompt templates
│   │   └── fix_generator.py            # Fix generation + self-review
│   └── utils/
│       ├── __init__.py
│       ├── models.py                   # Data models
│       └── config.py                   # Configuration
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_csv_loader.py
│   ├── test_example_suite_parser.py
│   ├── test_categorizer.py
│   ├── test_context_extractor.py
│   └── test_fix_generator.py
├── requirements.txt
├── .env.example
├── pytest.ini
└── venv/                               # Virtual environment
```

---

## Data Models

### Violation
```python
@dataclass
class Violation:
    file: str                  # Source file name (maps to src/<file>)
    line: int                  # Line number of violation
    column: Optional[int]      # Column number (may be empty)
    rule_id: str               # MISRA rule ID (e.g., "8.4")
    category: str              # Category (Required, Advisory, Mandatory)
    description: str           # Violation description
    code_context: Optional[str]  # Surrounding code (populated during analysis)
```

### Rule
```python
@dataclass
class Rule:
    rule_id: str               # Rule identifier (e.g., "8.4")
    rule_type: RuleType        # Rule or Directive
    category: str              # Category (Required, Advisory, Mandatory)
    description: str           # Rule description
    example_files: list[str]   # Related Example Suite files
    example_content: str       # Full text of example files
```

### Fix
```python
@dataclass
class Fix:
    violation: Violation       # The violation this fix addresses
    description: str           # Explanation of the fix
    original_code: str         # Original code snippet
    fixed_code: str            # Corrected code snippet
    git_patch: str             # Git unified diff patch
    self_review: str           # LLM self-review assessment
```

---

## Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MISRA Workflow                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Load CSV Reports ──► Violations                                 │
│         │                                                          │
│         ▼                                                          │
│  2. Parse Example Suite ──► Rules + Examples                       │
│         │                                                          │
│         ▼                                                          │
│  3. Categorize Violations ──► Priority-ordered groups              │
│         │                                                          │
│         ▼                                                          │
│  4. Extract Code Context ──► Source lines + function scope + static analysis   │
│         │  (from .dump: types, symbols, macros | from .ctu-info: cross-file info) │
│         ▼                                                                      │
│  5. RAG Retrieval ──► Similar rule examples from vector store                  │
│         │                                                                      │
│         ▼                                                                      │
│  6. Generate Fixes ──► LLM uses code + static analysis + RAG context          │
│         │                                                                      │
│         ▼                                                          │
│  7. Self-Review ──► LLM validates fix quality                      │
│         │                                                          │
│         ▼                                                          │
│  8. Generate Patches ──► Git diffs grouped by rule                 │
│         │                                                          │
│         ▼                                                          │
│  Output: patches/rule_X.Y.patch + results.json                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Verification

| # | Test | Command |
|---|------|---------|
| 1 | All unit tests pass | `python -m pytest tests/` |
| 2 | CLI runs on Example Suite file | `python -m backend.cli analyze` |
| 3 | ChromaDB embeddings created | Query vector store |
| 4 | Git patches are valid | `patch -p0` on generated patches |
| 5 | LLM self-review catches issues | Review test output |

### Verified execution notes

The following workflow was verified in the current workspace:

- Activated the project environment with `source venv/bin/activate`
- Ran the full analysis workflow successfully with:
  `python -m backend.cli analyze --output results.json --patch-dir ./patches`
- Verified generated patch files with:
  `patch --dry-run -p0 < ./patches/rule_10.4.patch`
- Apply the patch with:
  `patch -p0 < ./patches/rule_10.4.patch`
- The `patch` utility was used for application verification because the local workspace layout and file handling made `git apply` unreliable for these generated patches

---

## Known Considerations

1. **Reports folder naming**: Prompt references `./reports` but workspace uses `./report` — standardized on `./report`
2. **Rule categories**: `misrac-2012.txt` hardcodes "Mandatory" for all rules; actual category (Required/Advisory/Mandatory) is extracted from Example Suite comments
3. **Column numbers**: Currently empty in CSV reports because `misra.py` doesn't provide them — documented behavior
4. **CSV column mapping**: CSV columns (`File`, `Line`, `Column`, `Rule ID`, `Rule Category`, `Description`) map to `Violation` data model fields
5. **File path resolution**: CSV `file` column references files in `src/` folder (e.g., `example.c` → `src/example.c`)

---

## Implementation Details

### Class diagram
Note: Use this to generate to image https://www.plantuml.com/plantuml/uml

@startuml
left to right direction

' --- Classes -------------------------------------------------------
class Violation {
    + file : string
    + line : int
    + column : int
    + rule_id : string
    + category : str
    + description : str
    + code_context : str
}

class Rule {
    + rule_id : str
    + rule_type : RuleType
    + category : str
    + description : str
    + example_files : list
    + example_content : str
}

class CodeContext {
    + file_path : str
    + line_number : int
    + surrounding_lines : str
    + function_scope : str
    + full_file_content : str
    + dump_context : str
    + ctu_context : str
}

class Fix {
    + violation : Violation
    + description : str
    + original_code : str
    + fixed_code : str
    + git_patch : str
    + self_review : str
}

class RuleGroupFix {
    + rule_id : str
    + fixes : Fix
    + combined_patch : str
}

class Config {
    + OPENAI_API_KEY : str
    + OPENAI_MODEL : str
    + CHROMA_PERSIST_DIR : str
    + SRC_DIR : str
    + REPORT_DIR : str
    + EXAMPLE_SUITE_DIR : str
}

class Workflow {
    + categorize() : void
    + extract_context() : void
    + rag_retrieval() : void
    + generate_fixes() : void
    + self_review() : void
    + generate_patches() : void
}

class FixGenerator {
    + generate_fix() : Fix
    + self_review() : str
    + generate_git_patch() : str
}

class RAGRetriever {
    + retrieve_context() : str
}

class Categorizer {
    + group_by_rule() : dict
    + get_processing_order() : list
}

class Embedder {
    + create_embeddings() : list
}

class ConfigSettings {
    + validate() : void
}

class VectorStore {
    + manage_embeddings() : void
}

' --- Relationships -------------------------------------------------------
Violation --> Config : uses
Fix --> Violation : depends on
Fix --> CodeContext : depends on
Fix --> RAGRetriever : depends on
RuleGroupFix --> Fix : contains
Workflow --> Categorizer : orchestrates
Workflow --> RAGRetriever : orchestrates
Workflow --> FixGenerator : orchestrates
FixGenerator --> Fix : uses
FixGenerator --> RAGRetriever : uses
FixGenerator --> ConfigSettings : uses
RAGRetriever --> VectorStore : uses
VectorStore --> Embedder : uses

@enduml

### `backend/utils/models.py` — Core Data Structures

| Class/Enum | Purpose | Key Fields |
|------------|---------|------------|
| `RuleCategory` (enum) | MISRA rule categories | `REQUIRED`, `ADVISORY`, `MANDATORY` |
| `RuleType` (enum) | Rule vs Directive | `RULE`, `DIRECTIVE` |
| `Violation` (dataclass) | Single MISRA violation | `file`, `line`, `column`, `rule_id`, `category`, `description`, `code_context` |
| `Rule` (dataclass) | MISRA rule with examples | `rule_id`, `rule_type`, `category`, `description`, `example_files`, `example_content` |
| `CodeContext` (dataclass) | Source code context | `file_path`, `line_number`, `surrounding_lines`, `function_scope`, `full_file_content`, `dump_context`, `ctu_context` |
| `Fix` (dataclass) | Generated fix | `violation`, `description`, `original_code`, `fixed_code`, `git_patch`, `self_review` |
| `RuleGroupFix` (dataclass) | Fixes grouped by rule | `rule_id`, `fixes`, `combined_patch` |

### `backend/utils/config.py` — Centralized Configuration

| Setting | Default | Source |
|---------|---------|--------|
| `OPENAI_API_KEY` | `""` | `.env` |
| `OPENAI_MODEL` | `gpt-4o` | `.env` |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-ada-002` | `.env` |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | `.env` |
| `CHROMA_COLLECTION_NAME` | `misra_c_2012_rules` | Hardcoded |
| `SRC_DIR` | `./src` | `.env` |
| `REPORT_DIR` | `./report` | `.env` |
| `EXAMPLE_SUITE_DIR` | `./Example-Suite-master` | `.env` |
| `CONTEXT_LINES_ABOVE` | `10` | Hardcoded |
| `CONTEXT_LINES_BELOW` | `10` | Hardcoded |
| `RAG_TOP_K` | `5` | Hardcoded |

- Uses `python-dotenv` for `.env` file loading
- `Config.validate()` raises `ValueError` if `OPENAI_API_KEY` is missing

### `backend/ingestion/csv_loader.py` — CSV Report Loader

| Function | Purpose |
|----------|---------|
| `load_csv_report(csv_path)` | Load single CSV → `List[Violation]` |
| `load_all_reports(report_dir)` | Load all `*.csv` from directory → `List[Violation]` |

- CSV columns: `File`, `Line`, `Column`, `Rule ID`, `Rule Category`, `Description`
- Handles empty column values (maps to `None`)
- Gracefully handles missing report directory (returns empty list)

### `backend/ingestion/example_suite_parser.py` — Example Suite Parser

| Function | Purpose |
|----------|---------|
| `parse_example_suite(suite_dir)` | Parse entire suite → `Dict[str, Rule]` |
| `_parse_rule_files(suite_dir, all_files, rule_type)` | Parse R/D files by type |
| `_parse_single_file(filepath, rule_type)` | Extract metadata from single file |
| `_extract_description(content)` | Parse rule description from comments |
| `_extract_category(content)` | Extract Mandatory/Required/Advisory |
| `_attach_related_files(suite_dir, all_files, rules)` | Attach headers, system/support files |
| `_append_file_content(suite_dir, filename, rule)` | Append file content to rule |
| `_parse_rule_id(rule_id)` | Parse `"8.4"` → `(8, 4)` |

**File Discovery Pattern:**
- Primary: `R_xx_yy.c`, `D_xx_yy.c` (matched by regex `^[RD]_\d+_\d+\.c$`)
- Headers: `R_xx_yy.h`, `R_xx_yy_1.h`, `R_xx_yy_2.h` (variant headers)
- System/Support: `R_xx_system.c`, `R_xx_support.c`
- Common: `mc3_header.h`, `mc3_types.h`

### `backend/rag/vector_store.py` — ChromaDB Wrapper

| Method | Purpose |
|--------|---------|
| `__init__(persist_dir, collection_name)` | Init ChromaDB with persistent storage |
| `_get_or_create_collection()` | Get or create collection with cosine similarity |
| `add_rules(embeddings, rule_ids, documents, metadata)` | Upsert rule embeddings |
| `query(query_embedding, n_results)` | Query by embedding vector |
| `query_by_text(query_embedding, rule_id, n_results)` | Query with optional rule_id filter |
| `get_collection_count()` | Return document count |
| `delete_collection()` | Delete entire collection |

- Uses `chromadb.PersistentClient` with `anonymized_telemetry=False`
- Collection metadata: `{"hnsw:space": "cosine"}` for cosine similarity

### `backend/rag/embedding_pipeline.py` — OpenAI Embeddings

| Method | Purpose |
|--------|---------|
| `__init__(openai_client, vector_store)` | Init with OpenAI client and vector store |
| `create_embeddings(rules)` | Create embeddings for all rules → store in ChromaDB |
| `_create_document(rule)` | Build document string from rule + examples (max 4000 chars) |
| `_generate_embeddings(documents)` | Batch generate embeddings (batch size 100) |
| `get_embedding(text)` | Generate single embedding for query text |

- Document format: `"Rule {id}: {description}\n\nCategory: {cat}\n\nExample code:\n{examples}"`
- Batch processing (100 per request) to handle rate limits

### `backend/rag/retriever.py` — RAG Retrieval

| Method | Purpose |
|--------|---------|
| `__init__(vector_store, embedding_pipeline)` | Init with vector store and embedding pipeline |
| `retrieve_context(violation, top_k)` | Retrieve context for single violation |
| `retrieve_context_for_violations(violations, top_k)` | Batch retrieval for multiple violations |
| `format_context_for_llm(results)` | Format ChromaDB results for LLM prompts |

- Query text format: `"{rule_id}: {description}"`
- Output format: `"--- Relevant Rule {id} (similarity: {score}) ---\n{doc}"`

### `backend/analysis/context_extractor.py` — Code Context

| Method | Purpose |
|--------|---------|
| `__init__(src_dir)` | Init with source directory + `DumpParser` |
| `extract(violation)` | Extract full context → `CodeContext` |
| `_extract_surrounding_lines(lines, violation_line)` | Extract ±10 lines with line numbers |
| `_extract_function_scope(lines, violation_line)` | Extract enclosing function |
| `_find_function_start(lines, target_line)` | Search backwards for function signature |
| `_find_function_end(lines, start_line)` | Brace-counting to find function end |
| `_is_function_signature(line)` | Regex match for C function signatures |

- Surrounding lines format: `">>> 10: int c = a + b;"` (marker on violation line)
- Function detection: regex `^\s*(?:static|inline|extern|\w+[\s*]+)+\w+\s*\([^)]*\)\s*(?:\{|$)`
- Brace-counting for function boundary detection
- **Also calls `DumpParser` to extract static analysis context from `.dump` and `.ctu-info` files**

### `backend/analysis/dump_parser.py` — Cppcheck Dump & CTU Parser

| Function/Class | Purpose |
|----------------|---------|
| `DumpParser.get_context(source_file, target_line)` | High-level: find and parse `.dump` + `.ctu-info` → formatted strings |
| `_find_dump_file(source_file)` | Locate `.dump` file (same dir, workspace root, `src/`) |
| `_find_ctu_info_file(source_file)` | Locate `.ctu-info` file (same dir, workspace root, `src/`) |
| `parse_dump_file(dump_path, target_line)` | Parse `.dump` XML → `Dict` (platform, typedefs, macros, variables, functions, tokens) |
| `parse_ctu_info_file(ctu_path)` | Parse `.ctu-info` JSON lines → `Dict` (typedefs, tags, macros, external/internal/local IDs, usage) |
| `format_dump_context(dump_data, target_line)` | Format dump data → human-readable string for LLM |
| `format_ctu_context(ctu_data)` | Format CTU data → human-readable string for LLM |

**Dump File (`.dump`) Extraction:**
- Platform type sizes (`char_bit`, `int_bit`, `pointer_bit`, etc.)
- Typedef declarations (from raw tokens)
- `#define` macros (from raw tokens)
- Variables with resolved types (from tokenlist `valueType-*` attributes)
- Functions with resolved return types
- Per-line token type info near violation (signed/unsigned, pointer depth, varId)

**CTU Info File (`.ctu-info`) Extraction:**
- Exported typedefs (with used/unused status)
- Struct/union tag names
- Macros (with used/unused status)
- External identifiers (visible from other translation units)
- Internal (static) identifiers
- Local variable identifiers
- Symbol usage across files

### `backend/analysis/categorizer.py` — Violation Categorization

| Method | Purpose |
|--------|---------|
| `group_by_rule(violations)` | Group by rule_id → `Dict[str, List[Violation]]` |
| `get_priority(category)` | Category → priority number |
| `sort_by_priority(violations)` | Sort violations by priority |
| `get_processing_order(violations)` | Sorted groups: `(rule_id, violations)` tuples |
| `get_summary(violations)` | Summary stats: total, by_category, by_rule, by_file |

**Priority Map:**
| Category | Priority |
|----------|----------|
| Mandatory | 1 (highest) |
| Required | 2 |
| Advisory | 3 (lowest) |
| Unknown | 99 |

### `backend/analysis/workflow.py` — Multi-Step Workflow

| Class | Purpose |
|-------|---------|
| `AnalysisState` | State container: `violations`, `rules`, `contexts`, `rag_contexts`, `fixes`, `errors` |
| `MISRAWorkflow` | 6-step workflow orchestrator |

**Workflow Steps:**
1. **Categorize** — Group violations by rule, sort by priority
2. **Extract context** — Read source files, extract surrounding lines + function scope + static analysis context (from `.dump` and `.ctu-info`)
3. **RAG retrieval** — Query vector store for similar rule examples
4. **Generate fixes** — LLM generates fix per violation (using code context + static analysis context + RAG context)
5. **Self-review** — LLM validates each fix's quality
6. **Generate patches** — Create git unified diffs per fix

### `backend/fix_generation/prompts.py` — LLM Prompt Templates

| Template | Purpose |
|----------|---------|
| `FIX_GENERATION_SYSTEM_PROMPT` | System prompt for fix generation (JSON response format) |
| `FIX_GENERATION_USER_PROMPT_TEMPLATE` | User prompt with rule, code context, static analysis context, and RAG info |
| `SELF_REVIEW_SYSTEM_PROMPT` | System prompt for self-review (approved/issues/summary) |
| `SELF_REVIEW_USER_PROMPT_TEMPLATE` | User prompt with original/fixed code |
| `build_fix_generation_prompt(...)` | Format fix generation prompt |
| `build_self_review_prompt(...)` | Format self-review prompt |

### `backend/fix_generation/fix_generator.py` — Fix Generation

| Method | Purpose |
|--------|---------|
| `__init__(openai_client)` | Init with OpenAI client |
| `generate_fix(violation, code_context, rag_context, rule)` | Generate fix via LLM → `Fix` |
| `self_review(fix)` | LLM self-review → approval string |
| `generate_git_patch(fix)` | Generate unified diff → git patch string |

- LLM temperature: `0.1` (deterministic fixes)
- Response format: `{"type": "json_object"}`
- Git patch: uses `difflib.unified_diff` with `src/<file>` paths

### `backend/cli.py` — CLI Interface

| Command | Arguments | Purpose |
|---------|-----------|---------|
| `init` | None | Parse Example Suite, create embeddings, populate ChromaDB |
| `analyze` | `--output/-o`, `--patch-dir/-p` | Full workflow: load violations → generate fixes → save patches |
| `list` | None | List all violations from CSV reports |

**Output Files:**
- `results.json`: Violations, fixes (with self-review), errors
- `patches/rule_X.Y.patch`: Combined patch per rule with descriptions and diffs

---

## Test Suite (23 tests, all passing)

| File | Tests | Coverage |
|------|-------|----------|
| `tests/test_models.py` | 6 | All data models + enums |
| `tests/test_csv_loader.py` | 4 | Single CSV, multiple CSVs, empty dir, missing dir |
| `tests/test_example_suite_parser.py` | 3 | Rule ID parsing, minimal suite, missing dir |
| `tests/test_categorizer.py` | 5 | Group by rule, priority, sort, processing order, summary |
| `tests/test_context_extractor.py` | 3 | Context extraction, missing file, function scope |
| `tests/test_fix_generator.py` | 2 | Fix generation (mocked LLM), git patch generation |

---

---

## Data Flow

### End-to-End Pipeline

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                        │
│  Phase 1: Static Analysis (main.py)                                                                    │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                                                                                                  │  │
│  │  src/example.c ──► cppcheck --dump ──► src/example.c.dump (XML: AST, types, symbols, CFG)       │  │
│  │                              └──► src/example.c.ctu-info (JSON: cross-file symbols)              │  │
│  │                                                                                                  │  │
│  │  src/example.c.dump + misrac-2012.txt ──► python misra.py ──► report/example.c.csv              │  │
│  │                                                                                                  │  │
│  └──────────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                                        │
│  Phase 2: Violation Ingestion (backend/ingestion/)                                                     │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                                                                                                  │  │
│  │  report/*.csv ──► csv_loader.load_all_reports() ──► List[Violation]                              │  │
│  │                                                                                                  │  │
│  └──────────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                                        │
│  Phase 3: Context Enrichment (backend/analysis/)                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                                                                                                  │  │
│  │  For each Violation:                                                                             │  │
│  │                                                                                                  │  │
│  │  ┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐                 │  │
│  │  │ CodeContextExtractor│    │ DumpParser           │    │ RAGRetriever         │                 │  │
│  │  │                     │    │                      │    │                     │                 │  │
│  │  │ Reads src/example.c │    │ Parses .dump XML:   │    │ Queries ChromaDB:   │                 │  │
│  │  │                     │    │ - typedefs           │    │ - Similar rule      │                 │  │
│  │  │ - surrounding lines │    │ - macros             │    │   examples          │                 │  │
│  │  │ - function scope    │    │ - variables + types  │    │ - Example code      │                 │  │
│  │  │                     │    │ - functions + types  │    │                     │                 │  │
│  │  │                     │    │ - token type info    │    │                     │                 │  │
│  │  │                     │    │                      │    │                     │                 │  │
│  │  │                     │    │ Parses .ctu-info:    │    │                     │                 │  │
│  │  │                     │    │ - exported typedefs  │    │                     │                 │  │
│  │  │                     │    │ - external IDs       │    │                     │                 │  │
│  │  │                     │    │ - internal IDs       │    │                     │                 │  │
│  │  │                     │    │ - symbol usage       │    │                     │                 │  │
│  │  └────────┬────────────┘    └──────────┬───────────┘    └────────┬────────────┘                 │  │
│  │           │                            │                         │                               │  │
│  │           └────────────┬───────────────┴─────────────────────────┘                               │  │
│  │                        ▼                                                                         │  │
│  │              CodeContext object:                                                                 │  │
│  │              - surrounding_lines                                                                 │  │
│  │              - function_scope                                                                    │  │
│  │              - dump_context (formatted string)                                                   │  │
│  │              - ctu_context (formatted string)                                                    │  │
│  │                                                                                                  │  │
│  └──────────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                                        │
│  Phase 4: Fix Generation (backend/fix_generation/)                                                     │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                                                                                                  │  │
│  │  LLM Prompt includes:                                                                           │  │
│  │  ┌──────────────────────────────────────────────────────────────────────────────────────────┐   │  │
│  │  │ Rule: 10.4, Category: Mandatory                                                          │   │  │
│  │  │                                                                                          │   │  │
│  │  │ --- Code Context ---                                                                     │   │  │
│  │  │ >>> 42: result = (uint16)(N - 1) + idx;                                                  │   │  │
│  │  │                                                                                          │   │  │
│  │  │ --- Static Analysis Context ---                                                          │   │  │
│  │  │ Platform: char_bit=8, int_bit=32, pointer_bit=64                                        │   │  │
│  │  │ Variables: uint16 idx (line 23), sint16 currentTemp (line 21)                           │   │  │
│  │  │ Type Info Near Line 42: ...                                                              │   │  │
│  │  │                                                                                          │   │  │
│  │  │ --- Cross-Translation-Unit Info ---                                                      │   │  │
│  │  │ External Identifiers: TableData, main                                                    │   │  │
│  │  │                                                                                          │   │  │
│  │  │ --- Relevant MISRA Rule Context ---                                                      │   │  │
│  │  │ Rule 10.4 examples from Example Suite...                                                 │   │  │
│  │  └──────────────────────────────────────────────────────────────────────────────────────────┘   │  │
│  │                                                                                                  │  │
│  │  LLM ──► Fix(description, original_code, fixed_code) ──► Self-Review ──► Git Patch              │  │
│  │                                                                                                  │  │
│  └──────────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                                        │
│  Output: patches/rule_X.Y.patch + results.json                                                         │
│                                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### File Roles

| File | Generated By | Consumed By | Purpose |
|------|-------------|-------------|---------|
| `src/example.c` | Developer | `cppcheck`, `CodeContextExtractor` | Original source code |
| `src/example.c.dump` | `cppcheck --dump` | `DumpParser` → `FixGenerator` | AST, resolved types, symbols, control flow |
| `src/example.c.ctu-info` | `cppcheck --dump` | `DumpParser` → `FixGenerator` | Cross-file symbol visibility |
| `report/example.c.csv` | `misra.py` (via `main.py`) | `csv_loader` | Violation list (file, line, rule, description) |
| `misrac-2012.txt` | `main.py` (from Example Suite) | `misra.py` | Rule descriptions for violation messages |
| `chroma_db/` | `EmbeddingPipeline` | `RAGRetriever` | Vector-embedded rule examples |
| `patches/rule_X.Y.patch` | `FixGenerator` | Developer (`git apply`) | Unified diffs for each rule |

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `langchain` | >=0.2.0 | LLM orchestration |
| `langchain-openai` | >=0.1.0 | OpenAI integration |
| `langchain-chroma` | >=0.1.0 | ChromaDB integration |
| `langgraph` | >=0.0.20 | Agentic workflows |
| `openai` | >=1.0.0 | OpenAI API client |
| `chromadb` | >=0.4.0 | Local vector database |
| `python-dotenv` | >=1.0.0 | Environment variables |
| `pytest` | >=7.0.0 | Testing framework |
| `pytest-asyncio` | >=0.21.0 | Async test support |
| `pydantic` | >=2.0.0 | Data validation |