"""Setup verification script for ClinicDocs AI.

Verifies:
1. All core library imports succeed.
2. The chosen LLM provider API key is present and configured.
3. FastEmbed embedding model downloads/loads and embeds a test string.
4. A minimal LLM call succeeds with the configured provider.
"""

from pathlib import Path
import sys
import time

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def print_step(title: str):
    print(f"\n[+] Checking: {title}...")


def main():
    print("=" * 60)
    print("  ClinicDocs AI - Environment & Setup Verification")
    print("=" * 60)

    # 1. Check Library Imports
    print_step("Core Library Imports")
    try:
        import langchain_core
        import langchain_community
        import langchain_chroma
        import chromadb
        from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
        import pypdf
        import streamlit
        print("    [OK] LangChain core, ChromaDB, FastEmbed, PyPDF, and Streamlit imported successfully.")
    except ImportError as e:
        print(f"    [FAIL] Missing dependency: {e}")
        print("    Run: pip install -r requirements.txt")
        sys.exit(1)

    # 2. Check Configuration & API Keys
    print_step("Configuration & API Keys")
    from src.config import config
    is_valid, err_msg = config.validate_api_keys()
    if not is_valid:
        print(f"    [FAIL] Configuration Error: {err_msg}")
        sys.exit(1)
    print(f"    [OK] Provider configured: {config.llm_provider.upper()}")
    if config.llm_provider == "groq":
        print(f"    [OK] Model: {config.groq_model}")
    else:
        print(f"    [OK] Model: {config.gemini_model}")

    # 3. Check Embedding Model (FastEmbed)
    print_step(f"FastEmbed Embedding Model ({config.embedding_model_name})")
    try:
        t0 = time.perf_counter()
        embeddings = FastEmbedEmbeddings(model_name=config.embedding_model_name)
        vec = embeddings.embed_query("Oakwood Clinic medical policy test.")
        elapsed = time.perf_counter() - t0
        print(f"    [OK] Embedding model loaded in {elapsed:.2f}s! Vector dimensions: {len(vec)}")
    except Exception as e:
        print(f"    [FAIL] Failed to load FastEmbed model: {e}")
        sys.exit(1)

    # 4. Check Minimal LLM Invocation
    print_step(f"Live LLM Connection ({config.llm_provider.upper()})")
    try:
        t0 = time.perf_counter()
        if config.llm_provider == "groq":
            from langchain_groq import ChatGroq
            llm = ChatGroq(
                groq_api_key=config.groq_api_key,
                model_name=config.groq_model,
                temperature=0.0,
                max_tokens=20,
            )
        elif config.llm_provider == "gemini":
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(
                google_api_key=config.gemini_api_key,
                model=config.gemini_model,
                temperature=0.0,
                max_output_tokens=20,
            )
        else:
            raise ValueError(f"Unknown provider: {config.llm_provider}")

        response = llm.invoke("Respond with exactly: 'Setup verified'")
        elapsed = time.perf_counter() - t0
        print(f"    [OK] LLM replied in {elapsed:.2f}s: \"{response.content.strip()}\"")
    except Exception as e:
        print(f"    [FAIL] LLM connection failed: {e}")
        print("    Check your API key in .env or your internet connection.")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("  ALL CHECKS PASSED! Ready for Step 2.")
    print("=" * 60)


if __name__ == "__main__":
    main()
