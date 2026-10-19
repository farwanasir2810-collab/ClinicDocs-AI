"""Document ingestion, validation, and chunking pipeline for ClinicDocs AI.

Features:
- PDF loading from both file path and in-memory bytes (Streamlit UploadedFile)
- Input validation: max 10MB file size, max 50 pages, corrupted PDF detection
- Scanned/image-only PDF detection (flags documents with insufficient extracted text)
- 1-indexed page normalization (PyPDF 0-indexed page -> page_number 1, 2, ...)
- SHA-256 content deduplication (avoids re-processing identical documents)
- Duplicate filename disambiguation (e.g., 'clinic_policy (1).pdf')
- Chunking via RecursiveCharacterTextSplitter preserving metadata
"""

import hashlib
import io
from pathlib import Path
import re
from typing import List, Optional, Set, Tuple

import pypdf
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import config, logger


# -----------------------------------------------------------------------------
# Custom Domain Exceptions
# -----------------------------------------------------------------------------
class ScannedPDFError(ValueError):
    """Raised when an uploaded PDF contains little or no extractable text (e.g. scanned image)."""
    pass


class DocumentValidationError(ValueError):
    """Raised when a document violates size, page count, or format constraints."""
    pass


# -----------------------------------------------------------------------------
# Validation & Utility Functions
# -----------------------------------------------------------------------------
def compute_sha256(file_bytes: bytes) -> str:
    """Compute the SHA-256 hexadecimal hash of raw file bytes for deduplication."""
    return hashlib.sha256(file_bytes).hexdigest()


def validate_file_size(file_bytes: bytes, max_mb: int = 10) -> None:
    """Validate that file size does not exceed the allowed threshold."""
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > max_mb:
        raise DocumentValidationError(
            f"File size ({size_mb:.1f} MB) exceeds maximum allowed limit of {max_mb} MB."
        )


def disambiguate_filename(filename: str, existing_filenames: List[str]) -> str:
    """Disambiguate filename when uploading a different file with an existing name.
    
    Example:
        If 'policy.pdf' is in existing_filenames, returns 'policy (1).pdf'.
    """
    if filename not in existing_filenames:
        return filename

    p = Path(filename)
    stem = p.stem
    suffix = p.suffix
    
    # Strip any existing ' (N)' suffix from stem
    clean_stem = re.sub(r"\s\(\d+\)$", "", stem)
    
    counter = 1
    new_name = f"{clean_stem} ({counter}){suffix}"
    while new_name in existing_filenames:
        counter += 1
        new_name = f"{clean_stem} ({counter}){suffix}"

    return new_name


# -----------------------------------------------------------------------------
# PDF Loading & Page Normalization
# -----------------------------------------------------------------------------
def extract_pages_from_pdf(
    file_bytes: bytes,
    source_name: str,
    file_hash: str,
    max_pages: int = 50,
    min_avg_chars_per_page: int = 50,
) -> List[Document]:
    """Parse raw PDF bytes into a list of Document objects with 1-indexed page metadata.
    
    Args:
        file_bytes: Raw binary content of the PDF.
        source_name: Clean display filename for citation metadata.
        file_hash: SHA-256 hash of the file content.
        max_pages: Maximum permitted pages.
        min_avg_chars_per_page: Threshold for detecting scanned/empty PDFs.

    Returns:
        List[Document]: One Document per page with page_number, source, and file_hash.
    
    Raises:
        DocumentValidationError: If corrupted or exceeds page limit.
        ScannedPDFError: If text length indicates a scanned/image-only PDF.
    """
    try:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    except Exception as e:
        raise DocumentValidationError(f"Could not parse '{source_name}'. File may be corrupted or encrypted: {e}")

    num_pages = len(reader.pages)
    if num_pages == 0:
        raise DocumentValidationError(f"'{source_name}' contains zero pages.")

    if num_pages > max_pages:
        raise DocumentValidationError(
            f"'{source_name}' has {num_pages} pages, which exceeds the limit of {max_pages} pages."
        )

    documents: List[Document] = []
    total_extracted_chars = 0

    for idx, page in enumerate(reader.pages):
        try:
            text = page.extract_text() or ""
        except Exception as e:
            logger.warning(f"Error extracting text from page {idx + 1} of '{source_name}': {e}")
            text = ""

        # Normalize whitespace
        clean_text = text.strip()
        total_extracted_chars += len(clean_text)

        # 1-indexed page number: PyPDF index 0 -> page_number 1
        page_number = idx + 1

        documents.append(
            Document(
                page_content=clean_text,
                metadata={
                    "source": source_name,
                    "page_number": page_number,
                    "file_hash": file_hash,
                },
            )
        )

    # Scanned PDF Detection Guardrail
    avg_chars = total_extracted_chars / num_pages if num_pages > 0 else 0
    if total_extracted_chars < 50 or avg_chars < min_avg_chars_per_page:
        raise ScannedPDFError(
            f"Scanned or image-only PDF detected in '{source_name}' (extracted only {total_extracted_chars} characters "
            f"across {num_pages} pages). Please upload digital/searchable text PDFs."
        )

    logger.info(
        f"Parsed '{source_name}': {num_pages} pages, {total_extracted_chars} chars extracted (hash={file_hash[:8]}...)"
    )
    return documents


# -----------------------------------------------------------------------------
# Document Chunking
# -----------------------------------------------------------------------------
def chunk_documents(
    documents: List[Document],
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
) -> List[Document]:
    """Split documents into semantic chunks using RecursiveCharacterTextSplitter.
    
    Maintains and propagates source, page_number, and file_hash across each chunk.
    """
    c_size = chunk_size or config.chunk_size
    c_overlap = chunk_overlap or config.chunk_overlap

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=c_size,
        chunk_overlap=c_overlap,
        separators=["\n\n", "\n", " ", ""],
        length_function=len,
    )

    chunks: List[Document] = []
    chunk_counter = 0

    for doc in documents:
        if not doc.page_content.strip():
            continue
        page_chunks = splitter.split_documents([doc])
        for chunk in page_chunks:
            chunk.metadata["chunk_index"] = chunk_counter
            chunk_counter += 1
            chunks.append(chunk)

    logger.info(f"Chunked {len(documents)} pages into {len(chunks)} chunks (size={c_size}, overlap={c_overlap})")
    return chunks


# -----------------------------------------------------------------------------
# High-level Ingestion Pipeline
# -----------------------------------------------------------------------------
def process_uploaded_pdf(
    file_bytes: bytes,
    original_filename: str,
    ingested_hashes: Set[str],
    existing_filenames: List[str],
) -> Tuple[List[Document], str, str, bool]:
    """Full ingestion pipeline for an uploaded file.
    
    Args:
        file_bytes: Raw bytes of the uploaded PDF.
        original_filename: Name of the uploaded file.
        ingested_hashes: Set of SHA-256 hashes already ingested in the current session.
        existing_filenames: List of display filenames currently active in the session.

    Returns:
        Tuple[List[Document], str, str, bool]:
            - chunks: list of chunked Document objects (empty if skipped)
            - final_filename: unique display name for citations
            - file_hash: SHA-256 hash string
            - is_duplicate: True if file was skipped due to identical content hash
    """
    # 1. Validate file size
    validate_file_size(file_bytes)

    # 2. Compute SHA-256 hash
    file_hash = compute_sha256(file_bytes)

    # 3. Check for content duplication
    if file_hash in ingested_hashes:
        logger.info(f"Skipping duplicate file '{original_filename}' (SHA-256: {file_hash[:8]}... already ingested)")
        return [], original_filename, file_hash, True

    # 4. Handle filename collisions with different content
    final_filename = disambiguate_filename(original_filename, existing_filenames)

    # 5. Extract pages and validate searchable text
    pages = extract_pages_from_pdf(
        file_bytes=file_bytes,
        source_name=final_filename,
        file_hash=file_hash,
    )

    # 6. Chunk into retriever-ready passages
    chunks = chunk_documents(pages)

    return chunks, final_filename, file_hash, False


def process_local_pdf(file_path: Path | str) -> List[Document]:
    """Helper for local scripts and tests to ingest a PDF directly from path."""
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"PDF file not found at: {p}")

    with open(p, "rb") as f:
        file_bytes = f.read()

    chunks, _, _, _ = process_uploaded_pdf(
        file_bytes=file_bytes,
        original_filename=p.name,
        ingested_hashes=set(),
        existing_filenames=[],
    )
    return chunks
