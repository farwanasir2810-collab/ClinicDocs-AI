"""ClinicDocs AI: Chat with Your Documents

A production-quality RAG conversational web application for clinical documentation.
Designed for Streamlit Community Cloud with session-isolated ephemeral vector store.
"""

# -----------------------------------------------------------------------------
# 1. Streamlit Cloud SQLite Shim (CRITICAL for Debian / Linux environments)
# -----------------------------------------------------------------------------
import sys

try:
    __import__("pysqlite3")
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

import os
from pathlib import Path
import time
import uuid

import streamlit as st

# Configure page layout and aesthetics
st.set_page_config(
    page_title="ClinicDocs AI | Chat with Your Documents",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.config import config, logger
from src.ingest import (
    DocumentValidationError,
    ScannedPDFError,
    process_local_pdf,
    process_uploaded_pdf,
)
from src.retriever import (
    delete_session_collection,
    index_documents,
)
from src.chain import ask_clinicdocs

SAMPLE_DOC_PATH = Path("data/sample_docs/clinic_faq.pdf")


# -----------------------------------------------------------------------------
# 2. Session State Initialization
# -----------------------------------------------------------------------------
def init_session_state():
    """Initialize session state variables for multi-user isolation."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = uuid.uuid4().hex[:12]
        logger.info(f"Initialized new browser session: {st.session_state.session_id}")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "ingested_hashes" not in st.session_state:
        st.session_state.ingested_hashes = set()

    if "ingested_filenames" not in st.session_state:
        st.session_state.ingested_filenames = []

    if "total_chunks" not in st.session_state:
        st.session_state.total_chunks = 0


init_session_state()


# -----------------------------------------------------------------------------
# 3. Sidebar: Document Management & Safety Notice
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("🩺 ClinicDocs AI")
    st.caption("Grounded Conversational RAG for Clinical Documents")

    st.markdown("---")

    # Healthcare Safety Disclaimer
    st.info(
        "**⚠️ Safety & Privacy Notice**\n\n"
        "• **Informational only**: Does not constitute medical diagnosis or advice.\n"
        "• **Zero Retention**: Documents are processed in-memory for this session only and deleted on reset.\n"
        "• **Do NOT upload**: Real patient Protected Health Information (PHI)."
    )

    st.markdown("### 📁 Document Ingestion")

    # Load Sample PDF Button
    if SAMPLE_DOC_PATH.exists():
        if st.button("📋 Load Sample Document (Noor Care Clinic)", use_container_width=True):
            with st.spinner("Indexing sample clinic policy document..."):
                try:
                    with open(SAMPLE_DOC_PATH, "rb") as f:
                        file_bytes = f.read()

                    chunks, final_name, file_hash, is_dup = process_uploaded_pdf(
                        file_bytes=file_bytes,
                        original_filename="Noor_Care_Clinic_FAQ.pdf",
                        ingested_hashes=st.session_state.ingested_hashes,
                        existing_filenames=st.session_state.ingested_filenames,
                    )

                    if is_dup:
                        st.warning("Sample document is already loaded in your session.")
                    else:
                        num_added = index_documents(st.session_state.session_id, chunks)
                        st.session_state.ingested_hashes.add(file_hash)
                        st.session_state.ingested_filenames.append(final_name)
                        st.session_state.total_chunks += num_added
                        st.success(f"Loaded '{final_name}' ({num_added} chunks)")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error loading sample PDF: {e}")

    # File Uploader
    uploaded_files = st.file_uploader(
        "Upload PDF documents (Max 10 MB per file, max 50 pages)",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload clinic guidelines, schedules, FAQs, or SOP documents.",
    )

    if uploaded_files:
        if st.button("⚡ Process Uploaded Documents", type="primary", use_container_width=True):
            new_files_processed = 0
            with st.spinner("Processing & indexing documents..."):
                for uploaded_file in uploaded_files:
                    file_bytes = uploaded_file.read()
                    filename = uploaded_file.name

                    try:
                        chunks, final_name, file_hash, is_dup = process_uploaded_pdf(
                            file_bytes=file_bytes,
                            original_filename=filename,
                            ingested_hashes=st.session_state.ingested_hashes,
                            existing_filenames=st.session_state.ingested_filenames,
                        )

                        if is_dup:
                            st.info(f"Skipped '{filename}' (already uploaded).")
                            continue

                        num_added = index_documents(st.session_state.session_id, chunks)
                        st.session_state.ingested_hashes.add(file_hash)
                        st.session_state.ingested_filenames.append(final_name)
                        st.session_state.total_chunks += num_added
                        new_files_processed += 1

                    except ScannedPDFError as spe:
                        st.error(f"**Scanned PDF Warning**: {spe}")
                    except DocumentValidationError as dve:
                        st.error(f"**Validation Error**: {dve}")
                    except Exception as e:
                        st.error(f"Failed to process '{filename}': {e}")

            if new_files_processed > 0:
                st.success(f"Successfully indexed {new_files_processed} document(s)!")
                st.rerun()

    # Active Documents Display
    if st.session_state.ingested_filenames:
        st.markdown("#### 📚 Active Documents")
        for idx, doc_name in enumerate(st.session_state.ingested_filenames):
            st.markdown(f"• `{doc_name}`")
        st.caption(f"Total Chunks in Memory: **{st.session_state.total_chunks}**")

    st.markdown("---")

    # Clear Chat & Reset Session
    if st.button("🗑️ Clear Chat & Reset Session", use_container_width=True):
        delete_session_collection(st.session_state.session_id)
        st.session_state.messages = []
        st.session_state.ingested_hashes = set()
        st.session_state.ingested_filenames = []
        st.session_state.total_chunks = 0
        st.success("Session reset and memory cleared.")
        st.rerun()

    # System Status Footer
    st.markdown("---")
    st.caption(f"**Provider**: `{config.llm_provider.upper()}`")
    st.caption(f"**Embeddings**: `FastEmbed (BGE-small)`")
    st.caption(f"**Session**: `{st.session_state.session_id}`")


# -----------------------------------------------------------------------------
# 4. Main Chat Interface
# -----------------------------------------------------------------------------
st.title("ClinicDocs AI: Chat with Your Documents")
st.markdown(
    "Ask factual questions about your uploaded clinic policies, diagnostic turnaround times, "
    "operating hours, and fee schedules. Answers are **strictly grounded** with 1-indexed page citations."
)

# API Key Pre-flight Validation
valid_key, key_err = config.validate_api_keys()
if not valid_key:
    st.error(
        f"**Configuration Required**: {key_err}\n\n"
        "If you are developing locally, set this in your `.env` file. "
        "If running on Streamlit Cloud, add it to your App Settings Secrets."
    )

# Render Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # Display Latency Badge & Sources for Assistant responses
        if msg["role"] == "assistant":
            col1, col2 = st.columns([1, 4])
            with col1:
                if "latency" in msg and msg["latency"] > 0:
                    st.caption(f"⏱️ Response time: `{msg['latency']:.2f}s`")
            with col2:
                if "refusal_type" in msg and msg["refusal_type"] == "gate":
                    st.caption("🛡️ *Refusal source: Similarity Gate (0 API tokens used)*")

            # Expandable Citations
            if msg.get("sources"):
                with st.expander(f"📄 View Source Citations ({len(msg['sources'])})"):
                    for idx, src in enumerate(msg["sources"], 1):
                        st.markdown(
                            f"**Citation {idx}: {src['source']} — Page {src['page_number']}** "
                            f"(Match Similarity: `{src['similarity_score'] * 100:.1f}%`)"
                        )
                        st.markdown(f"> *\"{src['snippet']}\"*")
                        st.markdown("---")

# User Input Handling
user_query = st.chat_input("Ask a question about your uploaded documents...")

if user_query:
    if not st.session_state.ingested_filenames:
        st.warning("⚠️ Please upload a PDF or click **'📋 Load Sample Document'** in the sidebar before asking questions.")
    elif not valid_key:
        st.error("Cannot process query because API key is missing. Please configure your key in `.env` or Streamlit Secrets.")
    else:
        # 1. Render and record user message
        st.chat_message("user").markdown(user_query)
        st.session_state.messages.append({"role": "user", "content": user_query})

        # 2. Build conversational history for query rewriter
        history_tuples = []
        for m in st.session_state.messages[:-1]:
            role = "human" if m["role"] == "user" else "ai"
            history_tuples.append((role, m["content"]))

        # 3. Execute RAG Pipeline with Spinner
        with st.chat_message("assistant"):
            with st.spinner("Searching documents & generating grounded response..."):
                result = ask_clinicdocs(
                    query=user_query,
                    session_id=st.session_state.session_id,
                    chat_history=history_tuples,
                )

            # Display Answer
            st.markdown(result["answer"])

            # Display Metadata & Latency
            col1, col2 = st.columns([1, 4])
            with col1:
                st.caption(f"⏱️ Response time: `{result['latency_seconds']:.2f}s`")
            with col2:
                if result["refusal_type"] == "gate":
                    st.caption("🛡️ *Refusal source: Similarity Gate (0 API tokens used)*")
                elif result["refusal_type"] == "llm":
                    st.caption("🛡️ *Refusal source: LLM Context Grounding*")

            # Display Citations
            if result["sources"]:
                with st.expander(f"📄 View Source Citations ({len(result['sources'])})"):
                    for idx, src in enumerate(result["sources"], 1):
                        st.markdown(
                            f"**Citation {idx}: {src['source']} — Page {src['page_number']}** "
                            f"(Match Similarity: `{src['similarity_score'] * 100:.1f}%`)"
                        )
                        st.markdown(f"> *\"{src['snippet']}\"*")
                        st.markdown("---")

        # 4. Record Assistant Message in Session History
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"],
            "latency": result["latency_seconds"],
            "refusal_type": result["refusal_type"],
            "standalone_query": result["standalone_query"],
        })
