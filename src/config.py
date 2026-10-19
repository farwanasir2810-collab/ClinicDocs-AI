"""Configuration management and structured logging for ClinicDocs AI.

Handles secrets resolution with precedence:
1. Streamlit Cloud Secrets (st.secrets) if running in a Streamlit context
2. Environment variables from .env / os.environ
"""

from dataclasses import dataclass
import logging
import os
import sys
from typing import Tuple
from dotenv import load_dotenv

# Load local .env file if present
load_dotenv()

# Silence ChromaDB telemetry warnings
os.environ["ANONYMIZED_TELEMETRY"] = "False"


def _get_setting(key: str, default: str = "") -> str:
    """Retrieve setting from st.secrets (if available in Streamlit) or os.environ."""
    try:
        import streamlit as st  # type: ignore
        if hasattr(st, "runtime") and st.runtime.exists():
            if hasattr(st, "secrets") and key in st.secrets:
                return str(st.secrets[key])
    except Exception:
        pass

    return os.environ.get(key, default)


def setup_logger(name: str = "clinicdocs") -> logging.Logger:
    """Configure structured logger.
    
    CRITICAL PRIVACY RULE:
    Never log document text, extracted chunks, or raw user health queries.
    Only log operational metrics: latency, chunk counts, similarity scores, and refusal events.
    """
    log_level = _get_setting("LOG_LEVEL", "INFO").upper()
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    return logger


logger = setup_logger("clinicdocs.config")


@dataclass(frozen=True)
class AppConfig:
    """Application configuration and hyperparameter settings."""

    # LLM Settings
    llm_provider: str = _get_setting("LLM_PROVIDER", "groq").lower().strip()
    groq_api_key: str = _get_setting("GROQ_API_KEY", "").strip()
    groq_model: str = _get_setting("GROQ_MODEL", "llama-3.1-8b-instant").strip()
    gemini_api_key: str = _get_setting("GEMINI_API_KEY", "").strip()
    gemini_model: str = _get_setting("GEMINI_MODEL", "gemini-2.0-flash").strip()

    # Embedding Settings
    embedding_model_name: str = _get_setting(
        "EMBEDDING_MODEL_NAME", "BAAI/bge-small-en-v1.5"
    ).strip()

    # RAG Hyperparameters & Guardrails (0.48 calibrated empirically against eval questions)
    similarity_threshold: float = float(_get_setting("SIMILARITY_THRESHOLD", "0.48"))
    retriever_k: int = int(_get_setting("RETRIEVER_K", "4"))
    chunk_size: int = int(_get_setting("CHUNK_SIZE", "800"))
    chunk_overlap: int = int(_get_setting("CHUNK_OVERLAP", "150"))

    # Session Management
    max_active_collections: int = int(_get_setting("MAX_ACTIVE_COLLECTIONS", "10"))

    def validate_api_keys(self) -> Tuple[bool, str]:
        """Validate whether the required API key for the active provider is set.
        
        Returns:
            Tuple[bool, str]: (is_valid, human_readable_message)
        """
        if self.llm_provider == "groq":
            if not self.groq_api_key or "your_groq_api_key" in self.groq_api_key:
                return (
                    False,
                    "GROQ_API_KEY is missing! Obtain a free key from https://console.groq.com "
                    "and set it in your .env file (or Streamlit Secrets for cloud deployment).",
                )
        elif self.llm_provider == "gemini":
            if not self.gemini_api_key or "your_gemini_api_key" in self.gemini_api_key:
                return (
                    False,
                    "GEMINI_API_KEY is missing! Obtain a free key from https://aistudio.google.com "
                    "and set it in your .env file (or Streamlit Secrets for cloud deployment).",
                )
        else:
            return (
                False,
                f"Unsupported LLM_PROVIDER '{self.llm_provider}'. Supported options: 'groq' or 'gemini'.",
            )
        return True, ""


# Singleton instance
config = AppConfig()
