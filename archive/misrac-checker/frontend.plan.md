# MISRA-C:2012 AI Fixing Assistant UI/GUI — Implementation Plan

## Objective

Design and develop a UI/GUI screens MISRA-C:2012 fixing intelligent AI assistant leveraging Retrieval-Augmented Generation (RAG) techniques.

## Tech Stack

| Category | Technology |
|---|---|
| Frontend | Streamlit, Gradio (Python), React.js (JS), Flask/FastAPI |

## Workspace Layout

| Folder | Purpose |
|--------|---------|
| `frontend/` | Python modules / Implementation for UI/GUI of the AI assistant |
| `src/` | C source code (referenced by CSV reports) |
| `report/` | CSV violation reports |
| `patches/` | Fixing patches for violation items |
| `chroma_db/` | Vector Database (ChromaDB local) | 
| `backend/` | Python modules for the AI assistant |

Write allows on `frontend/` only, others will be read-only

---

## Instructions / Requirements for the UI/GUI implementation

### General requirement for UI/GUI: looking professional, easy to use and good UI/UX

### The screens for RAG/Vector Database
A-1. One screen for showing the ER diagram of the Vector Database (ChromaDB local) in `chroma_db`
A-2. One screen for showing the graph relationship of data in ChromaDB
A-3. One screen for searching the infor of a MISRA-C rule

### The screens for MISRA-C processing
B-1. One screen for showing the list of C source files (*.c, *h) from `src` folder
In this screen, we will have a nagivation button for each source file, which is allow to open below screen:
B-2. The main screen for MISRA-C follow, in which shows 3 flow blocks: MISRA-C scanner for analysis (`S1`), Generate fix patches (`S2`), View generated patches (`S3`)
B-2.1. `S1` will request execute this command from backend/background: `python3 main.py source_file_path`, in which `source_file_path` will get from the list showing on the screen described at B-1
B-2.2. `S2` will request execute this command from backend/background: `python -m backend.cli analyze --output results.json --patch-dir ./patches`
B-2.3. `S3` will display all patches for `source_file_path`, in which `source_file_path` will get from the list showing on the screen described at B-1

All these screens need to display the output from backend/background calling.

---

## Implemented Frontend Summary

### What has been implemented
- Built a Streamlit-based MISRA-C assistant UI with a sidebar navigation for Workflow, RAG / Vector DB, and Source files.
- Added a workflow screen that lets the user:
  - select a source file from the workspace,
  - run the MISRA scan,
  - generate fix patches,
  - load and preview generated patch files.
- Connected the UI to the backend through a dedicated runner layer that executes backend commands and captures stdout/stderr.
- Added a live backend output panel for fix generation so users can see streaming progress while the analysis is running.

### Frontend improvements completed
- Fixed the live log display so backend output appears progressively during patch generation rather than only after completion.
- Improved state handling so the workflow UI does not keep stale results from previous actions.
- Cleared old scan, analysis, patch, and log output whenever the user starts a new workflow action.
- Removed the "Streaming backend output..." caption once the backend process finishes, leaving a cleaner completed view.
- Ensured page changes reset workflow-related displays so content from one screen does not bleed into another.

### Current frontend behavior
- The Workflow screen shows the selected source file and provides the main MISRA workflow actions.
- The RAG / Vector DB screen provides a simple searchable view over local example-suite content.
- The Source files screen displays C/C++ source content from the selected file.
- The UI is now more stable and easier to use for iterative scanning and patch-generation flows.

### How to use the frontend
1. Open a terminal in the project root.
2. Activate the virtual environment:
   - `source venv/bin/activate`
3. Start the Streamlit frontend:
   - `python -m streamlit run frontend/app.py --server.headless true --server.port 8501`
4. Open the local URL shown in the terminal, typically `http://localhost:8501`.
5. Use the sidebar to switch between:
   - Workflow: run MISRA scan, generate fix patches, and view patch previews.
   - RAG / Vector DB: search example content and inspect local vector-database-related information.
   - Source files: browse and inspect source files from the workspace.

### How to stop the frontend
- Press `Ctrl+C` in the terminal running Streamlit.
- If needed, stop any lingering process with:
  - `pkill -f "streamlit run frontend/app.py"`
