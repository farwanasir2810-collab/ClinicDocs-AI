"""Diagnostic script to inspect FastEmbedEmbeddings query prefix behavior."""

import inspect
import sys


def main():
    print("=" * 60)
    print("  FastEmbed Query Instruction Prefix Diagnostic")
    print("=" * 60)
    try:
        from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
    except ImportError as e:
        print(f"[!] FastEmbed or LangChain not installed yet: {e}")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)

    print("\n[+] Source code of FastEmbedEmbeddings.embed_query:\n")
    try:
        src = inspect.getsource(FastEmbedEmbeddings.embed_query)
        print(src)
    except Exception as e:
        print(f"Could not retrieve source: {e}")

    print("-" * 60)
    print("Analysis:")
    print("If embed_query calls `self._model.query_embed(text)` or passes a query prefix,")
    print("then BGE's asymmetric query instruction is automatically applied.")
    print("If it calls `self._model.embed([text])`, documents and queries use the same prompt.")
    print("=" * 60)


if __name__ == "__main__":
    main()
