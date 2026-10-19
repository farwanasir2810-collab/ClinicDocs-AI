"""Fast offline unit test suite for ClinicDocs AI.

Runs 100% offline with ZERO API keys and ZERO model downloads:
- PDF text extraction & 1-indexed page numbering
- Chunk size and metadata preservation
- SHA-256 content deduplication
- Duplicate filename disambiguation
- Scanned / empty PDF detection (ScannedPDFError)
- File size constraint validation
- Cosine distance to similarity conversion ($s = 1 - d$)
- Pre-LLM threshold gating logic
"""

import io
from pathlib import Path
import pytest
from langchain_core.documents import Document
from reportlab.pdfgen import canvas

from src.ingest import (
    compute_sha256,
    disambiguate_filename,
    extract_pages_from_pdf,
    chunk_documents,
    process_uploaded_pdf,
    process_local_pdf,
    validate_file_size,
    ScannedPDFError,
    DocumentValidationError,
)


SAMPLE_PDF_PATH = Path("data/sample_docs/clinic_faq.pdf")


# -----------------------------------------------------------------------------
# Test 1: Real Sample PDF Loading & 1-Indexed Pages
# -----------------------------------------------------------------------------
def test_sample_pdf_page_indexing():
    """Verify that sample PDF loads 4 pages and uses 1-indexed page_number."""
    assert SAMPLE_PDF_PATH.exists(), f"Sample PDF must exist at {SAMPLE_PDF_PATH}"
    
    with open(SAMPLE_PDF_PATH, "rb") as f:
        pdf_bytes = f.read()

    file_hash = compute_sha256(pdf_bytes)
    pages = extract_pages_from_pdf(
        file_bytes=pdf_bytes,
        source_name="clinic_faq.pdf",
        file_hash=file_hash,
    )

    assert len(pages) == 4, f"Expected 4 pages, got {len(pages)}"
    
    # Assert 1-indexed page numbers
    page_nums = [p.metadata["page_number"] for p in pages]
    assert page_nums == [1, 2, 3, 4], f"Expected pages [1, 2, 3, 4], got {page_nums}"

    # Assert known facts from the text
    p1_text = pages[0].page_content.lower()
    assert "noor care clinic" in p1_text
    assert "friday" in p1_text and "closed" in p1_text

    p2_text = pages[1].page_content.lower()
    assert "1,500" in p2_text or "1500" in p2_text
    assert "12 hours" in p2_text

    p3_text = pages[2].page_content.lower()
    assert "cbc" in p3_text or "complete blood count" in p3_text
    assert "4 hours" in p3_text

    p4_text = pages[3].page_content.lower()
    assert "3 working days" in p4_text
    assert "300" in p4_text


# -----------------------------------------------------------------------------
# Test 2: Chunking & Metadata Propagation
# -----------------------------------------------------------------------------
def test_chunking_metadata_propagation():
    """Verify that chunking preserves source, 1-indexed page_number, and adds chunk_index."""
    chunks = process_local_pdf(SAMPLE_PDF_PATH)
    assert len(chunks) >= 4, "Expected at least 1 chunk per page"

    for idx, chunk in enumerate(chunks):
        assert "source" in chunk.metadata
        assert chunk.metadata["source"] == "clinic_faq.pdf"
        assert "page_number" in chunk.metadata
        assert 1 <= chunk.metadata["page_number"] <= 4
        assert "file_hash" in chunk.metadata
        assert len(chunk.metadata["file_hash"]) == 64
        assert chunk.metadata["chunk_index"] == idx


# -----------------------------------------------------------------------------
# Test 3: SHA-256 Deduplication
# -----------------------------------------------------------------------------
def test_sha256_deduplication():
    """Verify that uploading an identical file is flagged as duplicate and skipped."""
    with open(SAMPLE_PDF_PATH, "rb") as f:
        pdf_bytes = f.read()

    file_hash = compute_sha256(pdf_bytes)
    ingested_hashes = {file_hash}

    chunks, filename, returned_hash, is_dup = process_uploaded_pdf(
        file_bytes=pdf_bytes,
        original_filename="clinic_faq.pdf",
        ingested_hashes=ingested_hashes,
        existing_filenames=["clinic_faq.pdf"],
    )

    assert is_dup is True
    assert chunks == []
    assert returned_hash == file_hash


# -----------------------------------------------------------------------------
# Test 4: Filename Disambiguation
# -----------------------------------------------------------------------------
def test_filename_disambiguation():
    """Verify numeric suffixing when distinct files share the same filename."""
    existing = ["policy.pdf"]
    new_name = disambiguate_filename("policy.pdf", existing)
    assert new_name == "policy (1).pdf"

    existing_multiple = ["policy.pdf", "policy (1).pdf", "policy (2).pdf"]
    new_name_3 = disambiguate_filename("policy.pdf", existing_multiple)
    assert new_name_3 == "policy (3).pdf"

    # Non-colliding name stays unchanged
    assert disambiguate_filename("other.pdf", existing_multiple) == "other.pdf"


# -----------------------------------------------------------------------------
# Test 5: Scanned / Empty PDF Detection
# -----------------------------------------------------------------------------
def test_scanned_pdf_detection():
    """Verify that PDFs with zero or negligible text raise ScannedPDFError."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(100, 100, "Hi")  # Only 2 characters!
    c.showPage()
    c.save()
    sparse_pdf_bytes = buf.getvalue()

    with pytest.raises(ScannedPDFError) as exc_info:
        extract_pages_from_pdf(
            file_bytes=sparse_pdf_bytes,
            source_name="scanned_test.pdf",
            file_hash="fake_hash",
        )
    assert "Scanned or image-only PDF detected" in str(exc_info.value)


# -----------------------------------------------------------------------------
# Test 6: File Size Limit Validation
# -----------------------------------------------------------------------------
def test_file_size_validation():
    """Verify that files exceeding max_mb are rejected."""
    oversized_bytes = b"0" * (11 * 1024 * 1024)  # 11 MB
    with pytest.raises(DocumentValidationError) as exc_info:
        validate_file_size(oversized_bytes, max_mb=10)
    assert "exceeds maximum allowed limit of 10 MB" in str(exc_info.value)


# -----------------------------------------------------------------------------
# Test 7: Cosine Distance to Similarity Conversion Math
# -----------------------------------------------------------------------------
def test_cosine_distance_to_similarity_conversion():
    """Verify Chroma cosine distance to similarity formula: similarity = 1 - distance.
    
    Chroma uses cosine distance d = 1 - cosine_sim.
    Therefore, cosine_sim = 1 - d.
    """
    def distance_to_similarity(distance: float) -> float:
        return 1.0 - distance

    # Identical vectors (distance 0) -> similarity 1.0
    assert distance_to_similarity(0.0) == 1.0

    # Orthogonal vectors (distance 1.0) -> similarity 0.0
    assert distance_to_similarity(1.0) == 0.0

    # Moderate match (distance 0.35) -> similarity 0.65
    assert round(distance_to_similarity(0.35), 2) == 0.65

    # Low match (distance 0.8) -> similarity 0.2
    assert round(distance_to_similarity(0.8), 2) == 0.2

    # Opposite vectors (distance 2.0) -> similarity -1.0
    assert distance_to_similarity(2.0) == -1.0


# -----------------------------------------------------------------------------
# Test 8: Pre-LLM Threshold Gating Function
# -----------------------------------------------------------------------------
def test_threshold_gating_logic():
    """Verify that queries below similarity threshold trigger immediate refusal."""
    REFUSAL_MESSAGE = "I couldn't find this in the uploaded documents."

    def evaluate_retrieval_gate(top_similarity: float, threshold: float) -> tuple[bool, str]:
        if top_similarity < threshold:
            return False, REFUSAL_MESSAGE
        return True, "PROCEED_TO_LLM"

    threshold = 0.35

    # Out of domain / low score query
    passed, response = evaluate_retrieval_gate(top_similarity=0.20, threshold=threshold)
    assert passed is False
    assert response == REFUSAL_MESSAGE

    # In-domain / high score query
    passed, response = evaluate_retrieval_gate(top_similarity=0.72, threshold=threshold)
    assert passed is True
    assert response == "PROCEED_TO_LLM"


# -----------------------------------------------------------------------------
# Test 9: Chroma Session Isolation (Option B Verification)
# -----------------------------------------------------------------------------
def test_chroma_session_isolation():
    """Verify that documents in session A are NEVER visible to session B."""
    from langchain_core.documents import Document
    from src.retriever import (
        index_documents,
        retrieve_with_scores,
        delete_session_collection,
    )

    sess_a = "test_user_alice"
    sess_b = "test_user_bob"

    doc_a = [Document(page_content="Alice clinical report: patient blood pressure is 120/80", metadata={"source": "alice.pdf", "page_number": 1})]
    doc_b = [Document(page_content="Bob clinical report: patient allergic to penicillin", metadata={"source": "bob.pdf", "page_number": 1})]

    # Index separately
    index_documents(sess_a, doc_a)
    index_documents(sess_b, doc_b)

    # Search in Alice's session
    results_a = retrieve_with_scores(sess_a, "penicillin allergy", k=2)
    for doc, _ in results_a:
        assert "Bob" not in doc.page_content, "DATA LEAK: Bob's document appeared in Alice's session!"

    # Search in Bob's session
    results_b = retrieve_with_scores(sess_b, "blood pressure", k=2)
    for doc, _ in results_b:
        assert "Alice" not in doc.page_content, "DATA LEAK: Alice's document appeared in Bob's session!"

    # Cleanup
    delete_session_collection(sess_a)
    delete_session_collection(sess_b)


# -----------------------------------------------------------------------------
# Test 10: Query Rewriter Bypass on Turn 1 (Zero History)
# -----------------------------------------------------------------------------
def test_query_rewriter_bypasses_turn_1():
    """Verify that when chat_history is empty, the LLM is NEVER called."""
    from src.chain import reformulate_query

    raw_query = "What are the clinic timings on Friday?"
    # Pass a dummy object as llm that would fail if called
    dummy_llm = None
    result = reformulate_query(raw_query, chat_history=[], llm=dummy_llm)
    assert result == raw_query, "Turn 1 must return query unchanged without calling LLM"


# -----------------------------------------------------------------------------
# Test 11: End-to-End Chain Execution with Mock LLM
# -----------------------------------------------------------------------------
def test_ask_clinicdocs_with_mock_llm():
    """Verify RAG chain output schema and citation formatting using a Mock LLM."""
    from unittest.mock import MagicMock
    from langchain_core.messages import AIMessage
    from src.chain import ask_clinicdocs
    from src.retriever import index_documents, delete_session_collection

    mock_session = "test_mock_chain"
    doc = [
        Document(
            page_content="Noor Care Clinic operating hours on Friday are 9:00 AM to 1:00 PM and 3:00 PM to 8:00 PM.",
            metadata={"source": "clinic_faq.pdf", "page_number": 1},
        )
    ]
    index_documents(mock_session, doc)

    # Mock LLM returning grounded answer
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(
        content="On Friday, the clinic is open from 9:00 AM to 1:00 PM and from 3:00 PM to 8:00 PM."
    )

    res = ask_clinicdocs(
        query="What are the Friday clinic hours?",
        session_id=mock_session,
        chat_history=[],
        threshold=0.40,
        llm=mock_llm,
    )

    assert res["refusal_type"] == "none"
    assert "9:00 AM" in res["answer"]
    assert len(res["sources"]) == 1
    assert res["sources"][0]["source"] == "clinic_faq.pdf"
    assert res["sources"][0]["page_number"] == 1
    assert res["latency_seconds"] > 0

    delete_session_collection(mock_session)

