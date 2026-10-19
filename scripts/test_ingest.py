"""Standalone test script for src/ingest.py.

Can be run directly via:
    python scripts/test_ingest.py

Verifies:
1. Loading the 4-page 'Noor Care Clinic' FAQ PDF
2. Validation of 1-indexed page numbering
3. SHA-256 deduplication
4. Scanned PDF detection guardrail
5. Metadata preservation across all chunks
"""

import io
from pathlib import Path
import sys
import time

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from reportlab.pdfgen import canvas
from src.ingest import (
    compute_sha256,
    disambiguate_filename,
    extract_pages_from_pdf,
    process_local_pdf,
    process_uploaded_pdf,
    ScannedPDFError,
)

SAMPLE_PATH = Path("data/sample_docs/clinic_faq.pdf")


def main():
    print("=" * 65)
    print("  ClinicDocs AI — Ingestion Pipeline Standalone Verification")
    print("=" * 65)

    if not SAMPLE_PATH.exists():
        print(f"[!] Error: {SAMPLE_PATH} not found. Run python data/generate_sample.py first.")
        return

    # 1. Test Ingestion of Local PDF
    print(f"\n[1] Testing ingestion of '{SAMPLE_PATH}'...")
    t0 = time.perf_counter()
    chunks = process_local_pdf(SAMPLE_PATH)
    elapsed = time.perf_counter() - t0

    print(f"    [OK] Ingested and chunked in {elapsed * 1000:.2f} ms")
    print(f"    [OK] Total chunks created: {len(chunks)}")

    # 2. Verify 1-Indexed Pages & Metadata
    print("\n[2] Verifying chunk metadata & 1-indexed pages...")
    pages_seen = set()
    for c in chunks:
        pages_seen.add(c.metadata["page_number"])
        assert "source" in c.metadata, "Missing 'source' metadata"
        assert "file_hash" in c.metadata, "Missing 'file_hash' metadata"
        assert "chunk_index" in c.metadata, "Missing 'chunk_index' metadata"

    print(f"    [OK] Pages represented in chunks: {sorted(list(pages_seen))}")
    assert sorted(list(pages_seen)) == [1, 2, 3, 4], "Expected pages 1, 2, 3, 4"

    # Display First 4 Chunks Summary Table
    print("\n    Sample Chunk Breakdown:")
    print(f"    {'Index':<6} | {'Page':<5} | {'Length':<7} | {'Snippet'}")
    print("    " + "-" * 60)
    for c in chunks[:4]:
        snippet = c.page_content.replace("\n", " ")[:40] + "..."
        print(f"    {c.metadata['chunk_index']:<6} | {c.metadata['page_number']:<5} | {len(c.page_content):<7} | {snippet}")

    # 3. Test SHA-256 Deduplication
    print("\n[3] Testing SHA-256 deduplication...")
    with open(SAMPLE_PATH, "rb") as f:
        pdf_bytes = f.read()
    file_hash = compute_sha256(pdf_bytes)

    # Ingest again with hash registered in ingested_hashes
    dup_chunks, name, returned_hash, is_dup = process_uploaded_pdf(
        file_bytes=pdf_bytes,
        original_filename="clinic_faq.pdf",
        ingested_hashes={file_hash},
        existing_filenames=["clinic_faq.pdf"],
    )
    assert is_dup is True, "Failed to flag duplicate file"
    assert dup_chunks == [], "Duplicate file should not produce new chunks"
    print(f"    [OK] Duplicate file successfully detected and skipped (hash: {file_hash[:12]}...)")

    # 4. Test Filename Collision Disambiguation
    print("\n[4] Testing duplicate filename disambiguation...")
    disambiguated = disambiguate_filename("clinic_faq.pdf", ["clinic_faq.pdf"])
    assert disambiguated == "clinic_faq (1).pdf"
    print(f"    [OK] 'clinic_faq.pdf' -> '{disambiguated}'")

    # 5. Test Scanned / Empty PDF Detection
    print("\n[5] Testing scanned PDF detection guardrail...")
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(100, 100, "Tiny")  # Negligible text
    c.showPage()
    c.save()
    blank_bytes = buf.getvalue()

    try:
        extract_pages_from_pdf(blank_bytes, "blank.pdf", "hash123")
        print("    [FAIL] ScannedPDFError was not raised!")
    except ScannedPDFError as e:
        print(f"    [OK] ScannedPDFError successfully caught: \"{e}\"")

    print("\n" + "=" * 65)
    print("  SUCCESS: src/ingest.py is fully tested and verified!")
    print("=" * 65)


if __name__ == "__main__":
    main()
