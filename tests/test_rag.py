"""Automated evaluation and benchmarking suite for ClinicDocs AI.

Evaluates RAG performance against data/eval_questions.json across:
1. In-Domain Factual QA (accuracy + 1-indexed citation correctness)
2. Conversational Follow-Up Resolution (memory handling + standalone query reformulation)
3. Out-of-Domain Refusal Precision (evaluating Gate Refusals vs LLM Refusals)

Runnable with a single command:
    python tests/test_rag.py
"""

import json
from pathlib import Path
import sys
import time

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import config, logger
from src.ingest import process_local_pdf
from src.retriever import delete_session_collection, index_documents
from src.chain import REFUSAL_MESSAGE, ask_clinicdocs

SAMPLE_PDF = Path("data/sample_docs/clinic_faq.pdf")
EVAL_FILE = Path("data/eval_questions.json")
EVAL_SESSION = "session_benchmark_eval"


def evaluate_response(
    q_data: dict,
    result: dict,
) -> tuple[bool, bool, bool]:
    """Evaluate answer accuracy, citation match, and keyword presence.
    
    Returns:
        tuple[bool, bool, bool]: (is_correct, citation_correct, keywords_matched)
    """
    q_type = q_data["type"]
    expected_page = q_data["expected_page"]
    expected_keywords = q_data["expected_keywords"]
    answer_lower = result["answer"].lower()

    # 1. Keyword matching (case-insensitive)
    if q_type == "out_of_domain":
        # Must refuse
        keywords_matched = REFUSAL_MESSAGE.lower() in answer_lower or "couldn't find" in answer_lower
    else:
        # Check if at least half of the expected keywords appear in the answer
        matches = [kw.lower() in answer_lower for kw in expected_keywords]
        keywords_matched = any(matches) if len(expected_keywords) <= 2 else sum(matches) >= (len(expected_keywords) // 2)

    # 2. Citation correctness (1-indexed page matching)
    if q_type == "out_of_domain":
        # Out-of-domain should have zero sources cited
        citation_correct = len(result["sources"]) == 0
    else:
        cited_pages = [s["page_number"] for s in result["sources"]]
        citation_correct = expected_page in cited_pages if expected_page else False

    # 3. Overall correctness
    if q_type == "out_of_domain":
        is_correct = keywords_matched and citation_correct
    else:
        is_correct = keywords_matched and citation_correct

    return is_correct, citation_correct, keywords_matched


def run_evaluation():
    print("=" * 78)
    print("  ClinicDocs AI — 10-Question RAG Benchmark Evaluation")
    print("=" * 78)

    # Validate configuration
    is_valid, err_msg = config.validate_api_keys()
    if not is_valid:
        print(f"\n[!] Configuration Error: {err_msg}")
        print("Please configure your GROQ_API_KEY or GEMINI_API_KEY in .env before running evaluation.")
        sys.exit(1)

    if not SAMPLE_PDF.exists() or not EVAL_FILE.exists():
        print(f"\n[!] Required files not found: {SAMPLE_PDF} or {EVAL_FILE}")
        sys.exit(1)

    # Ingest test document into evaluation session
    print(f"\n[+] Ingesting '{SAMPLE_PDF}' into session '{EVAL_SESSION}'...")
    chunks = process_local_pdf(SAMPLE_PDF)
    index_documents(EVAL_SESSION, chunks)
    print(f"    Indexed {len(chunks)} chunks.")

    # Load 10 ground-truth questions
    with open(EVAL_FILE, "r", encoding="utf-8") as f:
        questions = json.load(f)

    print(f"\n[+] Running evaluation across {len(questions)} test cases...\n")

    results_table = []
    total_passed = 0
    total_citations_correct = 0
    gate_refusals = 0
    llm_refusals = 0
    latencies = []

    header = f"{'ID':<4} | {'Type':<14} | {'Exp Page':<8} | {'Cited':<8} | {'Latency':<8} | {'Refusal':<8} | {'Result'}"
    print(header)
    print("-" * len(header))

    for q in questions:
        q_id = q["id"]
        q_type = q["type"]
        q_text = q["question"]
        expected_page = q["expected_page"]
        history = q.get("history", [])

        # Execute RAG query
        res = ask_clinicdocs(
            query=q_text,
            session_id=EVAL_SESSION,
            chat_history=history,
        )

        latencies.append(res["latency_seconds"])
        is_correct, cit_correct, kw_matched = evaluate_response(q, res)

        if is_correct:
            total_passed += 1
        if cit_correct:
            total_citations_correct += 1

        if res["refusal_type"] == "gate":
            gate_refusals += 1
        elif res["refusal_type"] == "llm":
            llm_refusals += 1

        exp_pg_str = str(expected_page) if expected_page else "None"
        cited_pages = [str(s["page_number"]) for s in res["sources"]]
        cited_str = ",".join(cited_pages) if cited_pages else "None"
        status_str = "PASS" if is_correct else "FAIL"

        row = f"{q_id:<4} | {q_type:<14} | {exp_pg_str:<8} | {cited_str:<8} | {res['latency_seconds']:.2f}s    | {res['refusal_type']:<8} | {status_str}"
        print(row)

        results_table.append({
            "id": q_id,
            "type": q_type,
            "question": q_text,
            "is_correct": is_correct,
            "citation_correct": cit_correct,
            "refusal_type": res["refusal_type"],
            "latency": res["latency_seconds"],
            "answer": res["answer"],
        })

    # Summary Statistics
    total_q = len(questions)
    accuracy_pct = (total_passed / total_q) * 100
    citation_pct = (total_citations_correct / total_q) * 100
    avg_latency = sum(latencies) / len(latencies)

    print("\n" + "=" * 78)
    print("  EVALUATION BENCHMARK SUMMARY")
    print("=" * 78)
    print(f"  Total Questions Tested      : {total_q}")
    print(f"  Overall Grounded Accuracy   : {total_passed}/{total_q} ({accuracy_pct:.1f}%)")
    print(f"  Citation Correctness        : {total_citations_correct}/{total_q} ({citation_pct:.1f}%)")
    print(f"  Layer 1 Gate Refusals       : {gate_refusals}  (0 LLM tokens used)")
    print(f"  Layer 2 LLM Prompt Refusals : {llm_refusals}  (Strict context grounding)")
    print(f"  Average End-to-End Latency  : {avg_latency:.2f}s")
    print("=" * 78)

    # Clean up session
    delete_session_collection(EVAL_SESSION)

    # Return exit code based on benchmark performance
    if total_passed >= 9:
        print("\n  [PASS] Benchmark passed production standards (>= 90% accuracy).")
        sys.exit(0)
    else:
        print(f"\n  [WARN] Benchmark accuracy fell below target: {total_passed}/{total_q}")
        sys.exit(1)


if __name__ == "__main__":
    run_evaluation()
