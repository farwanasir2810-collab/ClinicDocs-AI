"""Threshold calibration script for ClinicDocs AI.

Embeds data/sample_docs/clinic_faq.pdf, runs all 10 questions in data/eval_questions.json,
and prints the top similarity score per question grouped by category.

Key Architecture Insight:
- The similarity score gate catches semantically distant questions (e.g., 'Capital of France').
- Near-topic out-of-domain questions (e.g., 'Which doctor is on duty Monday?') share vocabulary
  with clinic chunks and will have higher similarity. Those MUST be refused by the LLM system prompt.
- Therefore, evaluation tracks two layers: GATE REFUSALS vs LLM REFUSALS.
"""

import json
from pathlib import Path
import sys
import time

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ingest import process_local_pdf
from src.retriever import (
    index_documents,
    retrieve_with_scores,
    delete_session_collection,
)

SAMPLE_PATH = Path("data/sample_docs/clinic_faq.pdf")
EVAL_PATH = Path("data/eval_questions.json")
CALIBRATION_SESSION = "session_calibration_run"


def main():
    print("=" * 72)
    print("  ClinicDocs AI — Empirical Threshold Calibration")
    print("=" * 72)

    if not SAMPLE_PATH.exists() or not EVAL_PATH.exists():
        print(f"[!] Missing required data files. Ensure {SAMPLE_PATH} and {EVAL_PATH} exist.")
        return

    # 1. Ingest Sample Document
    print(f"\n[1] Ingesting '{SAMPLE_PATH}' into ephemeral calibration collection...")
    chunks = process_local_pdf(SAMPLE_PATH)
    index_documents(CALIBRATION_SESSION, chunks)
    print(f"    Indexed {len(chunks)} chunks.")

    # 2. Load Evaluation Questions
    with open(EVAL_PATH, "r", encoding="utf-8") as f:
        questions = json.load(f)
    print(f"\n[2] Loaded {len(questions)} evaluation questions from '{EVAL_PATH}'.")

    # 3. Retrieve Scores for All Questions
    print("\n[3] Computing top cosine similarity scores...")
    results_by_type = {"in_domain": [], "follow_up": [], "out_of_domain": []}

    print(f"\n    {'ID':<4} | {'Type':<14} | {'Top Sim':<8} | {'Question'}")
    print("    " + "-" * 66)

    for q in questions:
        q_id = q["id"]
        q_type = q["type"]
        text = q["question"]

        scored = retrieve_with_scores(CALIBRATION_SESSION, text, k=4)
        top_score = scored[0][1] if scored else 0.0

        results_by_type[q_type].append((q_id, text, top_score))
        print(f"    {q_id:<4} | {q_type:<14} | {top_score:.4f}   | {text[:40]}...")

    # 4. Summary Statistics by Category
    print("\n" + "=" * 72)
    print("  SIMILARITY SCORE DISTRIBUTION BY CATEGORY")
    print("=" * 72)

    all_in = [s for _, _, s in results_by_type["in_domain"]]
    all_follow = [s for _, _, s in results_by_type["follow_up"]]
    all_out = [s for _, _, s in results_by_type["out_of_domain"]]

    def stats(scores):
        if not scores:
            return 0.0, 0.0, 0.0
        return min(scores), sum(scores) / len(scores), max(scores)

    in_min, in_avg, in_max = stats(all_in)
    fl_min, fl_avg, fl_max = stats(all_follow)
    out_min, out_avg, out_max = stats(all_out)

    print(f"  In-Domain (5 Qs)    : Min = {in_min:.4f} | Avg = {in_avg:.4f} | Max = {in_max:.4f}")
    print(f"  Follow-Up (2 Qs)    : Min = {fl_min:.4f} | Avg = {fl_avg:.4f} | Max = {fl_max:.4f}")
    print(f"  Out-of-Domain (3 Qs): Min = {out_min:.4f} | Avg = {out_avg:.4f} | Max = {out_max:.4f}")

    print("\n  Out-of-Domain Breakdown:")
    for q_id, text, score in results_by_type["out_of_domain"]:
        print(f"    - [{q_id}] ({score:.4f}) \"{text}\"")

    # 5. Calibration Analysis & Recommendation
    # Distant OOD (e.g. capital of France) has low score
    # Near-topic OOD (e.g. doctor on duty, pet dog) has moderate score
    print("\n" + "-" * 72)
    print("  CALIBRATION ANALYSIS & RECOMMENDATION:")
    print("-" * 72)
    
    # Lowest in-domain query score
    lowest_in_domain = min(all_in + all_follow)
    # Distant out-of-domain score (e.g. France)
    distant_ood_score = results_by_type["out_of_domain"][0][2]

    # Recommended threshold between distant OOD and lowest in-domain
    recommended_thresh = round((distant_ood_score + lowest_in_domain) / 2.0, 2)
    # Ensure threshold does not exceed lowest in_domain
    if recommended_thresh >= lowest_in_domain:
        recommended_thresh = round(lowest_in_domain - 0.05, 2)

    print(f"  1. Distant out-of-domain query ('Capital of France') score : {distant_ood_score:.4f}")
    print(f"  2. Lowest in-domain query score                           : {lowest_in_domain:.4f}")
    print(f"  3. RECOMMENDED SIMILARITY_THRESHOLD                       : {recommended_thresh:.2f}")
    print("\n  Crucial Note for Architecture:")
    print("  - The gate threshold catches semantically distant queries (0 API tokens used).")
    print("  - Near-topic out-of-domain queries match clinic words and pass the gate;")
    print("    they are grounded and refused by the LLM system prompt.")
    print("=" * 72)

    # Clean up calibration session
    delete_session_collection(CALIBRATION_SESSION)


if __name__ == "__main__":
    main()
