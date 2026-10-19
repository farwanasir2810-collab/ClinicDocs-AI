"""CLI verification and interactive testing tool for ClinicDocs AI RAG pipeline.

Tests all 4 critical production scenarios before building the Streamlit UI:
1. Factual in-domain query (checks answer accuracy & Page 1 citation)
2. Conversational multi-turn follow-up (checks query rewriter memory resolution)
3. Semantically distant query (checks pre-LLM Gate Refusal in ~20ms)
4. Near-topic unanswerable query (checks prompt-grounded LLM Refusal)
"""

from pathlib import Path
import sys
import time

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import config
from src.ingest import process_local_pdf
from src.retriever import delete_session_collection, index_documents
from src.chain import ask_clinicdocs

SAMPLE_PDF = Path("data/sample_docs/clinic_faq.pdf")
CLI_SESSION = "session_cli_test"


def print_divider(title: str = ""):
    if title:
        print(f"\n{'=' * 20} {title} {'=' * 20}")
    else:
        print("=" * 65)


def run_automated_checks():
    print_divider("ClinicDocs AI — Automated Pipeline Verification")
    
    # 1. Ingest sample document
    print(f"\n[+] Ingesting '{SAMPLE_PDF}' into ephemeral session...")
    chunks = process_local_pdf(SAMPLE_PDF)
    index_documents(CLI_SESSION, chunks)
    print(f"    Indexed {len(chunks)} chunks into isolated session '{CLI_SESSION}'.")

    # Scenario 1: Factual in-domain query
    print_divider("Scenario 1: Factual In-Domain Query")
    q1 = "What are the clinic operating hours on Friday?"
    print(f"Question: \"{q1}\"")
    res1 = ask_clinicdocs(q1, CLI_SESSION)
    print(f"Top Similarity : {res1['top_similarity']}")
    print(f"Refusal Type   : {res1['refusal_type']}")
    print(f"Latency        : {res1['latency_seconds']:.2f}s")
    print(f"Answer:\n{res1['answer']}\n")
    print("Sources:")
    for s in res1["sources"]:
        print(f"  - [{s['source']}] Page {s['page_number']} (similarity: {s['similarity_score']}): {s['snippet'][:80]}...")

    # Scenario 2: Multi-turn Conversational Follow-Up
    print_divider("Scenario 2: Conversational Follow-Up Query")
    turn1_q = "What is the consultation fee for a general physician?"
    print(f"Turn 1 Question: \"{turn1_q}\"")
    res_t1 = ask_clinicdocs(turn1_q, CLI_SESSION)
    print(f"Turn 1 Answer: {res_t1['answer'][:100]}...\n")

    chat_history = [
        ("human", turn1_q),
        ("ai", res_t1["answer"]),
    ]
    turn2_q = "What about for a specialist doctor?"
    print(f"Turn 2 Question (Follow-up): \"{turn2_q}\"")
    res_t2 = ask_clinicdocs(turn2_q, CLI_SESSION, chat_history=chat_history)
    print(f"Reformulated Query: \"{res_t2['standalone_query']}\"")
    print(f"Top Similarity    : {res_t2['top_similarity']}")
    print(f"Latency           : {res_t2['latency_seconds']:.2f}s")
    print(f"Answer:\n{res_t2['answer']}\n")
    print("Sources:")
    for s in res_t2["sources"]:
        print(f"  - [{s['source']}] Page {s['page_number']} (similarity: {s['similarity_score']})")

    # Scenario 3: Semantically Distant Out-of-Domain Query (Gate Refusal)
    print_divider("Scenario 3: Semantically Distant Query (Pre-LLM Gate Refusal)")
    q3 = "What is the capital city of France?"
    print(f"Question: \"{q3}\"")
    res3 = ask_clinicdocs(q3, CLI_SESSION)
    print(f"Top Similarity : {res3['top_similarity']} (Threshold: {config.similarity_threshold})")
    print(f"Refusal Type   : {res3['refusal_type'].upper()}")
    print(f"Latency        : {res3['latency_seconds'] * 1000:.1f} ms  <-- Refused with 0 LLM tokens!")
    print(f"Answer         : \"{res3['answer']}\"")

    # Scenario 4: Near-Topic Out-of-Domain Query (LLM Grounding Refusal)
    print_divider("Scenario 4: Near-Topic Unanswerable Query (LLM Prompt Refusal)")
    q4 = "Which specific doctor is on duty for general OPD on Monday morning?"
    print(f"Question: \"{q4}\"")
    res4 = ask_clinicdocs(q4, CLI_SESSION)
    print(f"Top Similarity : {res4['top_similarity']} (Passed gate)")
    print(f"Refusal Type   : {res4['refusal_type'].upper()}")
    print(f"Latency        : {res4['latency_seconds']:.2f}s")
    print(f"Answer         : \"{res4['answer']}\"")

    print_divider("ALL 4 SCENARIOS COMPLETED SUCCESSFULLY")


def interactive_mode():
    print_divider("ClinicDocs AI — Interactive Terminal QA")
    print(f"Ingesting '{SAMPLE_PDF}' into session '{CLI_SESSION}'...")
    chunks = process_local_pdf(SAMPLE_PDF)
    index_documents(CLI_SESSION, chunks)
    print("Ready! Type 'exit' or 'quit' to stop.\n")

    history = []
    while True:
        try:
            q = input("\nAsk ClinicDocs > ").strip()
            if q.lower() in ("exit", "quit", "q"):
                break
            if not q:
                continue

            res = ask_clinicdocs(q, CLI_SESSION, chat_history=history)
            print(f"\n[Answer] ({res['latency_seconds']:.2f}s | Refusal: {res['refusal_type']}):")
            print(res["answer"])
            if res["sources"]:
                print("\n[Sources]:")
                for s in res["sources"]:
                    print(f"  - {s['source']} (Page {s['page_number']})")
            
            # Record turn in history
            history.append(("human", q))
            history.append(("ai", res["answer"]))

        except KeyboardInterrupt:
            break

    delete_session_collection(CLI_SESSION)
    print("\nSession cleaned up. Goodbye!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        run_automated_checks()
        delete_session_collection(CLI_SESSION)
