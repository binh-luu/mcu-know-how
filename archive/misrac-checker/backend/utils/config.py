"""
Configuration module for the MISRA-C:2012 AI Fixing Assistant.

Loads environment variables and provides centralized configuration.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Centralized configuration for the application."""

    # OpenAI LLM Configuration
    OPENAI_LLM_API_KEY: str = os.getenv('OPENAI_LLM_API_KEY', '')
    OPENAI_LLM_API_ENDPOINT: str = os.getenv('OPENAI_LLM_API_ENDPOINT', '')
    OPENAI_LLM_MODEL: str = os.getenv('OPENAI_LLM_MODEL', 'gpt-4o').strip('"')

    # OpenAI Embedding Configuration
    OPENAI_EMBEDDING_API_KEY: str = os.getenv('OPENAI_EMBEDDING_API_KEY', '')
    OPENAI_EMBEDDING_API_ENDPOINT: str = os.getenv('OPENAI_EMBEDDING_API_ENDPOINT', '')
    OPENAI_EMBEDDING_MODEL: str = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small').strip('"')

    # Legacy aliases (for backward compatibility)
    @property
    def OPENAI_API_KEY(self) -> str:
        return self.OPENAI_LLM_API_KEY

    @property
    def OPENAI_MODEL(self) -> str:
        return self.OPENAI_LLM_MODEL

    # ChromaDB Configuration
    CHROMA_PERSIST_DIR: str = os.getenv('CHROMA_PERSIST_DIR', './chroma_db')
    CHROMA_COLLECTION_NAME: str = 'misra_c_2012_rules'

    # Project Paths
    SRC_DIR: str = os.getenv('SRC_DIR', './src')
    REPORT_DIR: str = os.getenv('REPORT_DIR', './report')
    EXAMPLE_SUITE_DIR: str = os.getenv('EXAMPLE_SUITE_DIR', './Example-Suite-master')

    # Context extraction settings
    CONTEXT_LINES_ABOVE: int = 10
    CONTEXT_LINES_BELOW: int = 10

    # RAG settings
    RAG_TOP_K: int = 5  # Number of similar rules to retrieve

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        if not cls.OPENAI_LLM_API_KEY:
            raise ValueError(
                "OPENAI_LLM_API_KEY not set. "
                "Copy .env.example to .env and add your API key."
            )
        if not cls.OPENAI_EMBEDDING_API_KEY:
            raise ValueError(
                "OPENAI_EMBEDDING_API_KEY not set. "
                "Copy .env.example to .env and add your API key."
            )


# Singleton config instance
config = Config()