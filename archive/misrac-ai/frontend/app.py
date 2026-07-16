from __future__ import annotations

import sys
import time
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from frontend.services.backend_runner import BackendRunner
from frontend.utils.source_discovery import discover_source_files

# ──────────────────────────────────────────────────────────────
# Page Configuration & Zephyr-style Documentation Theme
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MISRA-C:2012 AI Fixing Assistant",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Zephyr-style documentation design (light theme, blue accents, clean layout)
ZEPHYR_CSS = """
<style>
/* Import Zephyr-like font stack */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Roboto+Mono:wght@400;500&display=swap');

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}

/* Main background */
.stApp {
    background-color: #ffffff;
    color: #333;
}

/* Documentation-style header */
.main-header {
    text-align: center;
    padding: 1.5rem 0 1rem 0;
    margin-bottom: 1rem;
    border-bottom: 1px solid #e5e7eb;
}

/* Sidebar styling (light theme) */
section[data-testid="stSidebar"] {
    background: #fafafa;
    border-right: 1px solid #e5e7eb;
}

section[data-testid="stSidebar"] * {
    color: #333 !important;
}

/* Sidebar header */
.sidebar-header {
    padding: 1rem 0.5rem 1rem 0.5rem;
    border-bottom: 1px solid #e5e7eb;
    margin-bottom: 1rem;
    text-align: center;
}

/* Sidebar section headers */
.sidebar-section {
    font-size: 0.85rem;
    font-weight: 600;
    color: #4b5563;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: 0.75rem 0 0.5rem 0;
    padding: 0 0.5rem;
}

/* Cards with subtle shadows */
.doc-card {
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.doc-card h4 {
    margin: 0 0 0.5rem 0;
    color: #1e40af;
    font-size: 1rem;
    font-weight: 600;
}

.doc-card h3 {
    margin: 0 0 0.75rem 0;
    color: #1e3a8a;
    font-size: 1.15rem;
    font-weight: 600;
}

/* Step cards */
.step-card {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 0.75rem;
    transition: all 0.2s ease;
}

.step-card.completed {
    background: #f0fdf4;
    border-color: #86efac;
}

.step-card.in-progress {
    background: #eff6ff;
    border-color: #60a5fa;
    border-left: 3px solid #2563eb;
}

.step-card.pending {
    background: #fafafa;
    border-color: #e5e7eb;
}

/* Step number badge */
.step-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    font-weight: 600;
    font-size: 0.85rem;
    margin-right: 0.75rem;
}
.step-badge.completed { background: #22c55e; color: white; }
.step-badge.in-progress { background: #2563eb; color: white; }
.step-badge.pending { background: #9ca3af; color: white; }

/* Buttons - Zephyr style */
.stButton > button {
    border-radius: 6px;
    font-weight: 500;
    padding: 0.5rem 1rem;
    transition: all 0.15s ease;
    border: 1px solid #d1d5db;
    background: #f9fafb;
    color: #374151;
}

.stButton > button[data-baseweb="button"][id^="primary"] {
    background: #2563eb;
    color: white;
    border-color: #2563eb;
}

.stButton > button[data-baseweb="button"][id^="primary"]:hover {
    background: #1d4ed8;
    border-color: #1d4ed8;
}

/* Status badges */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.25rem 0.75rem;
    border-radius: 16px;
    font-size: 0.8rem;
    font-weight: 500;
}
.status-badge.success { background: #dcfce7; color: #166534; }
.status-badge.error { background: #fee2e2; color: #991b1b; }
.status-badge.running { background: #dbeafe; color: #1e40af; }
.status-badge.pending { background: #f3f4f6; color: #6b7280; }

/* Code blocks */
.code-block {
    background: #1e293b;
    color: #e2e8f0;
    border-radius: 6px;
    padding: 1rem;
    font-family: 'Roboto Mono', monospace;
    font-size: 0.85rem;
    overflow-x: auto;
}

/* Log container */
.log-panel {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 6px;
    padding: 1rem;
    max-height: 350px;
    overflow-y: auto;
    font-family: 'Roboto Mono', monospace;
    font-size: 0.8rem;
    line-height: 1.5;
    color: #cbd5e1;
}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    gap: 4px;
    padding: 0.25rem;
    margin-bottom: 1rem;
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 6px;
    padding: 0.5rem 1rem;
    font-weight: 500;
    color: #6b7280;
}

.stTabs [aria-selected="true"] {
    background: #eff6ff !important;
    color: #1d4ed8 !important;
}

/* Section headers */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
    border-bottom: 1px solid #e5e7eb;
}

.section-header h2 {
    margin: 0;
    font-size: 1.35rem;
    font-weight: 600;
    color: #1e3a8a;
}

.icon-badge {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
}

/* Empty state */
.empty-state {
    text-align: center;
    padding: 2.5rem 1.5rem;
    color: #6b7280;
    background: #fafafa;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
}

/* Metrics in sidebar */
[data-testid="stMetric"] {
    background: transparent;
    padding: 0.25rem 0;
}

[data-testid="stMetricValue"] {
    color: #1e3a8a !important;
    font-size: 1rem !important;
}

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
}
th {
    background: #f9fafb;
    color: #374151;
    font-weight: 600;
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #e5e7eb;
}
td {
    padding: 0.75rem;
    border-bottom: 1px solid #e5e7eb;
}

/* Download button fix */
stDownloadButton > button {
    background: #2563eb;
    color: white;
}
</style>
"""

st.markdown(ZEPHYR_CSS, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────────────────────
def clear_workflow_state() -> None:
    """Clear all workflow-related session state."""
    keys_to_clear = [
        "scan_result",
        "analysis_result",
        "patch_files",
        "analysis_running",
        "analysis_logs",
        "analysis_done",
        "analysis_result_payload",
        "current_step",
        "expander_step1",
        "expander_step2",
        "expander_step3",
    ]
    for key in keys_to_clear:
        st.session_state.pop(key, None)


def render_workflow_steps(current_step: int = 0) -> None:
    """Render visual workflow steps in Zephyr style."""
    steps = [
        {"num": 1, "title": "MISRA Scan", "desc": "Static analysis on source file"},
        {"num": 2, "title": "Generate Fixes", "desc": "AI-powered patch generation via RAG"},
        {"num": 3, "title": "Review Patches", "desc": "Inspect and apply generated patches"},
    ]

    for i, step in enumerate(steps):
        if i < current_step:
            status = "completed"
        elif i == current_step:
            status = "in-progress"
        else:
            status = "pending"

        icon = "✓" if status == "completed" else step["num"]

        st.markdown(
            f"""
            <div class="step-card {status}">
                <div style="display: flex; align-items: center; margin-bottom: 0.25rem;">
                    <span class="step-badge {status}">{icon}</span>
                    <span style="font-weight: 600; color: #1e3a8a;">{step['title']}</span>
                </div>
                <div style="font-size: 0.85rem; color: #6b7280; margin-left: 2.5rem;">{step['desc']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_status_badge(status: str) -> str:
    """Render a status badge HTML snippet."""
    return f'<span class="status-badge {status}">{status.replace("_", " ").title()}</span>'


def render_info_card(title: str, content: str) -> None:
    """Render an info card."""
    st.markdown(
        f"""
        <div class="doc-card">
            <h3>🔧 {title}</h3>
            <div style="color: #6b7280; font-size: 0.9rem; line-height: 1.5;">{content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(icon: str, title: str, description: str) -> None:
    """Render an empty state message."""
    st.markdown(
        f"""
        <div class="empty-state">
            <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">{icon}</div>
            <h3 style="margin: 0 0 0.5rem 0; color: #374151;">{title}</h3>
            <p style="margin: 0; color: #6b7280;">{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────────────────────
# Initialize Session State & Services
# ──────────────────────────────────────────────────────────────
runner = BackendRunner(project_root=PROJECT_ROOT)
source_files = discover_source_files(PROJECT_ROOT / "src")

# Initialize session state keys with proper defaults (never None)
if "selected_file_widget" not in st.session_state:
    st.session_state["selected_file_widget"] = source_files[0] if source_files else None
if "last_page" not in st.session_state:
    st.session_state["last_page"] = "Workflow"
if "current_step" not in st.session_state:
    st.session_state["current_step"] = 0
if "analysis_running" not in st.session_state:
    st.session_state["analysis_running"] = False
if "analysis_done" not in st.session_state:
    st.session_state["analysis_done"] = [False]
if "analysis_logs" not in st.session_state:
    st.session_state["analysis_logs"] = []
if "analysis_result_payload" not in st.session_state:
    st.session_state["analysis_result_payload"] = {}

# Expander state persistence - remembers if each step was expanded
if "expander_step1" not in st.session_state:
    st.session_state["expander_step1"] = False
if "expander_step2" not in st.session_state:
    st.session_state["expander_step2"] = False
if "expander_step3" not in st.session_state:
    st.session_state["expander_step3"] = False


# ──────────────────────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-header">
            <div style="font-size: 1.75rem; font-weight: 700; color: #1e3a8a;">MISRA-C AI</div>
            <div style="font-size: 0.85rem; color: #6b7280;">Fixing Assistant</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-section">Navigation</div>', unsafe_allow_html=True)

    page = st.radio(
        "Go to",
        ["Workflow", "RAG / Vector DB", "Source Files"],
        index=["Workflow", "RAG / Vector DB", "Source Files"].index(st.session_state["last_page"]),
        label_visibility="collapsed",
        key="nav_radio",
    )

    # Clear state when page changes
    if st.session_state["last_page"] != page:
        # Do NOT clear workflow state here – only when the user clicks
        # the explicit Reset button.  Preserve expander states and results.
        st.session_state["last_page"] = page
        st.session_state["current_step"] = 0  # reset step counter for new page
        st.rerun()

    st.divider()

    st.markdown('<div class="sidebar-section">Source File</div>', unsafe_allow_html=True)

    if source_files:
        selected_file = st.selectbox(
            "Choose file",
            source_files,
            index=source_files.index(st.session_state["selected_file_widget"])
            if st.session_state["selected_file_widget"] in source_files
            else 0,
            key="selected_file_widget",
            label_visibility="collapsed",
        )

        file_path = PROJECT_ROOT / "src" / selected_file
        if file_path.exists():
            size_kb = file_path.stat().st_size / 1024
            lines = len(file_path.read_text(encoding="utf-8", errors="ignore").splitlines())
            st.markdown(
                f'<div style="font-size: 0.8rem; color: #6b7280; padding: 0 0.5rem;">{lines} lines · {size_kb:.1f} KB</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown("<div style='color: #6b7280;'>No source files found</div>", unsafe_allow_html=True)

    st.divider()

    st.markdown('<div class="sidebar-section">Workspace</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Project", PROJECT_ROOT.name)
    with col2:
        st.metric("Files", len(source_files))

    chroma_dir = PROJECT_ROOT / "chroma_db"
    if chroma_dir.exists():
        st.markdown('<div style="color: #22c55e; font-size: 0.85rem; padding: 0 0.5rem; margin-top: 0.5rem;">● Vector DB: Ready</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="color: #f59e0b; font-size: 0.85rem; padding: 0 0.5rem; margin-top: 0.5rem;">● Vector DB: Not initialized</div>', unsafe_allow_html=True)

    st.divider()

    st.markdown('<div class="sidebar-section">Quick Actions</div>', unsafe_allow_html=True)
    if st.button("🔄 Reset Workflow", key="reset_btn", use_container_width=True):
        clear_workflow_state()
        st.session_state["current_step"] = 0
        st.rerun()
    if st.button("🗑️ Clear Patches", key="clear_patches_btn", use_container_width=True):
        patch_dir = PROJECT_ROOT / "patches"
        if patch_dir.exists():
            for f in patch_dir.glob("*.patch"):
                f.unlink()
        st.success("Cleared")
        st.rerun()


# ──────────────────────────────────────────────────────────────
# Main Content
# ──────────────────────────────────────────────────────────────
if page == "Source Files":
    st.markdown(
        """
        <div class="section-header">
            <div class="icon-badge" style="background: #10b981; color: white;">📄</div>
            <h2>Source File Browser</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not source_files:
        render_empty_state("📂", "No Source Files", "Add C/C++ source files to `src/` directory to begin.")
    else:
        selected_file_name = st.session_state["selected_file_widget"]
        selected_path = PROJECT_ROOT / "src" / selected_file_name

        if selected_path.exists():
            code = selected_path.read_text(encoding="utf-8", errors="ignore")
            lines = code.splitlines()

            tab1, tab2 = st.tabs(["Source Code", "Statistics"])

            with tab1:
                st.markdown(
                    f'<div style="font-family: monospace; font-size: 0.85rem; color: #6b7280; margin-bottom: 0.5rem;">{selected_file_name}</div>',
                    unsafe_allow_html=True,
                )
                st.code(code, language="c", line_numbers=True)

            with tab2:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Lines", len(lines))
                with col2:
                    st.metric("Non-empty", sum(1 for l in lines if l.strip()))
                with col3:
                    st.metric("Comments", sum(1 for l in lines if l.strip().startswith(("/*", "//"))))
                with col4:
                    st.metric("Size", f"{len(code) / 1024:.1f} KB")

                # Function signatures
                st.markdown("**Functions**")
                import re
                func_pattern = re.compile(r'^\s*(?:static|inline|extern|\w+[\s*]+)+\w+\s*\([^)]*\)\s*(?:\{|$)')
                functions = [(i + 1, l.strip()) for i, l in enumerate(lines) if func_pattern.match(l)]
                if functions:
                    for line_num, func in functions[:15]:
                        st.markdown(
                            f'<div style="font-family: monospace; font-size: 0.8rem; color: #6b7280; padding: 0.25rem 0.5rem; background: #f9fafb; border-radius: 4px; margin: 0.2rem 0;">L{line_num}: {func}</div>',
                            unsafe_allow_html=True,
                        )
                    if len(functions) > 15:
                        st.caption(f"... and {len(functions) - 15} more functions")
                else:
                    st.caption("No function signatures detected")
        else:
            st.error(f"File not found: {selected_path}")

elif page == "RAG / Vector DB":
    st.markdown(
        """
        <div class="section-header">
            <div class="icon-badge" style="background: #8b5cf6; color: white;">🗄️</div>
            <h2>RAG & Vector Database</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    rag_tab1, rag_tab2, rag_tab3 = st.tabs(["Rule Search", "Vector DB Explorer", "Data Relationships"])

    with rag_tab1:
        st.markdown("**Search MISRA Rule Examples**")

        col1, col2 = st.columns([3, 1])
        with col1:
            rule_query = st.text_input("Search", placeholder="Rule ID (e.g., 10.4), keyword...", label_visibility="collapsed")
        with col2:
            if st.button("Search", key="search_btn", type="primary", use_container_width=True):
                pass

        if rule_query:
            examples_dir = PROJECT_ROOT / "Example-Suite-master"
            if examples_dir.exists():
                matches = []
                with st.spinner("Searching..."):
                    for path in examples_dir.rglob("*"):
                        if path.is_file() and path.suffix in {".c", ".h", ".txt"}:
                            try:
                                text = path.read_text(encoding="utf-8", errors="ignore")
                                if rule_query.lower() in text.lower():
                                    matches.append({
                                        "file": path.relative_to(PROJECT_ROOT).as_posix(),
                                        "context": text[:500],
                                    })
                            except Exception:
                                pass

                if matches:
                    st.success(f"Found {len(matches)} matches")
                    for match in matches[:10]:
                        with st.expander(f"📄 {match['file']}"):
                            st.code(match["context"], language="c")
                else:
                    st.warning("No matches found.")
            else:
                st.error("Example-Suite-master directory not found")

    with rag_tab2:
        st.markdown("**Vector Store Explorer**")
        chroma_dir = PROJECT_ROOT / "chroma_db"

        if chroma_dir.exists():
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Status", "Initialized")
            with col2:
                files = [f for f in chroma_dir.rglob("*") if f.is_file()]
                st.metric("Files", len(files))
            with col3:
                st.metric("Size", f"{sum(f.stat().st_size for f in files) / 1024 / 1024:.2f} MB")

            st.divider()

            st.markdown("**Collections:**")
            try:
                import chromadb
                client = chromadb.PersistentClient(str(chroma_dir))
                collections = client.list_collections()
                for col in collections:
                    with st.expander(f"📦 {col.name}"):
                        st.markdown(f"- Documents: {col.count()}")
                        st.markdown(f"- Metadata: {col.metadata}")
            except Exception as e:
                st.caption(f"Could not read collections: {e}")
        else:
            render_empty_state("🗄️", "Not Initialized", "Run `python -m backend.cli init` to create vector store.")

    with rag_tab3:
        st.markdown("**Data Relationships**")
        render_info_card(
            "Relationship View",
            "Shows connections between MISRA rules, detected violations, and generated fixes.",
        )

        if "analysis_result" in st.session_state and st.session_state["analysis_result"]:
            result = st.session_state["analysis_result"]
            if result.get("patch_files"):
                st.divider()
                st.markdown("**Recent Fix Relationships:**")
                for patch in result["patch_files"][:5]:
                    rule_id = patch.name.replace("rule_", "").replace(".patch", "")
                    st.markdown(
                        f'<div style="padding: 0.5rem; background: #f9fafb; border-radius: 4px;">'
                        f'Rule {rule_id} → <code>{patch.name}</code></div>',
                        unsafe_allow_html=True,
                    )

else:
    st.markdown(
        """
        <div class="section-header">
            <div class="icon-badge" style="background: #3b82f6; color: white;">🔄</div>
            <h2>Workflow Progress</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected_file_name = st.session_state["selected_file_widget"]
    if not selected_file_name:
        render_empty_state("📁", "No File Selected", "Select a source file from sidebar to begin.")
        st.stop()

    selected_path = PROJECT_ROOT / "src" / selected_file_name
    if not selected_path.exists():
        st.error(f"File not found: {selected_path}")
        st.stop()

    # ── 3-step collage: each step shows status, action button, and output logs ──
    st.markdown(f"**Selected file:** `{selected_file_name}`")
    st.divider()

    # ===== STEP 1: MISRA Scan =====
    # Persist expansion state: stay open if it has content or was previously expanded
    step1_expanded = st.session_state.get("expander_step1", False) or "scan_result" in st.session_state
    with st.expander("1️⃣ MISRA Scan", expanded=step1_expanded):
        st.caption("Run static analysis to detect MISRA-C:2012 violations in the source file.")
        if st.button("Run MISRA Scan", key="btn_scan", type="primary", use_container_width=True,
                     disabled="scan_result" in st.session_state):
            clear_workflow_state()
            with st.spinner("Running MISRA scan..."):
                result = runner.run_scan(selected_file_name)
            st.session_state["scan_result"] = result
            st.rerun()

        if "scan_result" in st.session_state:
            sr = st.session_state["scan_result"]
            st.markdown(render_status_badge("success" if sr["returncode"] in (0, 1) else "error"),
                        unsafe_allow_html=True)
            with st.expander("Scan Output / Logs", expanded=True):
                st.code(sr["stdout"] or sr["stderr"], language="text")

    st.divider()

    # ===== STEP 2: Generate Fixes =====
    # Persist expansion state: stay open if it has content, is running, or was previously expanded
    step2_expanded = (
        st.session_state.get("expander_step2", False)
        or st.session_state.get("analysis_running", False)
        or "analysis_result" in st.session_state
    )
    with st.expander("2️⃣ Generate Fixes", expanded=step2_expanded):
        st.caption("AI-powered fix generation using RAG context (runs the full analysis workflow).")

        # Track step-specific state (doesn't interfere with other steps)
        is_running = bool(st.session_state.get("analysis_running", False))
        has_results = "analysis_result" in st.session_state

        # Action button - only starts analysis, doesn't clear other step results
        if st.button("Generate Fixes", key="btn_generate", type="primary", use_container_width=True,
                     disabled=is_running or has_results):
            # Only clear step-2 specific state, preserve scan_result and patch_files
            for key in ["analysis_running", "analysis_logs", "analysis_done", "analysis_result_payload", "analysis_result"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state["analysis_running"] = True
            st.session_state["analysis_logs"] = []
            st.session_state["analysis_result_payload"] = {}
            st.session_state["analysis_done"] = [False]
            runner.start_analysis(
                logs=st.session_state["analysis_logs"],
                result_holder=st.session_state["analysis_result_payload"],
                done_flag=st.session_state["analysis_done"],
                patch_dir=str(PROJECT_ROOT / "patches"),
            )
            st.rerun()

        # Status indicator & live logs
        if is_running:
            st.markdown(render_status_badge("running"), unsafe_allow_html=True)
            st.markdown("**Backend Status: Running**")
            log_text = "".join(st.session_state.get("analysis_logs", []))
            st.markdown(f'<div class="log-panel">{log_text.replace(chr(10), "<br>")}</div>',
                        unsafe_allow_html=True)
            if not st.session_state.get("analysis_done", [False])[0]:
                time.sleep(0.2)
                st.rerun()
            # Analysis finished - capture results
            payload = st.session_state.get("analysis_result_payload")
            if payload:
                payload["patch_files"] = runner.list_patch_files(PROJECT_ROOT / "patches")
                st.session_state["analysis_result"] = payload
            st.session_state["analysis_running"] = False
            st.session_state["analysis_done"] = [False]
            st.rerun()

        # Show completed status
        if has_results:
            ar = st.session_state["analysis_result"]
            status = "success" if ar.get("returncode") == 0 else "error"
            st.markdown(render_status_badge(status), unsafe_allow_html=True)
            st.markdown(f"**Backend Status: Completed ({status.title()})**")
            with st.expander("Generation Output / Logs", expanded=False):
                st.code(ar.get("stdout") or ar.get("stderr"), language="text")

    st.divider()

    # ===== STEP 3: Review Patches =====
    # Persist expansion state: stay open if we have patch files
    step3_expanded = "patch_files" in st.session_state
    with st.expander("3️⃣ Review Patches", expanded=step3_expanded):
        st.caption("Inspect generated patches before applying them to your source code.")
        if st.button("Load Patch Previews", key="btn_load_patches", type="secondary",
                     use_container_width=True):
            patch_files = runner.list_patch_files(PROJECT_ROOT / "patches")
            st.session_state["patch_files"] = patch_files
            st.rerun()

        if "patch_files" in st.session_state and st.session_state["patch_files"]:
            st.markdown(f"**{len(st.session_state['patch_files'])} patch file(s) generated:**")
            for pp in st.session_state["patch_files"]:
                try:
                    content = pp.read_text(encoding="utf-8", errors="ignore")
                except FileNotFoundError:
                    content = "Patch file not found."
                with st.expander(f"🔧 {pp.name}", expanded=False):
                    st.code(content[:4000], language="diff")
        elif "patch_files" in st.session_state:
            st.info("No patch files found. Generate fixes first.")