"""
ChromaDB Vector Store

Manages the ChromaDB vector store for storing and retrieving
MISRA C:2012 rule embeddings.
"""

import os
import chromadb
from chromadb.config import Settings
from typing import Dict, List, Optional

from backend.utils.config import config


class VectorStore:
    """
    Wrapper around ChromaDB for MISRA rule storage and retrieval.
    
    Provides methods to:
    - Initialize/persist the vector store
    - Add rule embeddings
    - Query for similar rules
    """

    def __init__(
        self,
        persist_dir: Optional[str] = None,
        collection_name: Optional[str] = None
    ):
        """
        Initialize the vector store.
        
        Args:
            persist_dir: Directory to persist ChromaDB data.
            collection_name: Name of the ChromaDB collection.
        """
        self.persist_dir = persist_dir or config.CHROMA_PERSIST_DIR
        self.collection_name = collection_name or config.CHROMA_COLLECTION_NAME
        
        # Ensure persist directory exists
        os.makedirs(self.persist_dir, exist_ok=True)
        
        # Initialize ChromaDB client with persistent storage
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        """Get existing collection or create a new one."""
        try:
            # Try to get existing collection
            collection = self.client.get_collection(name=self.collection_name)
        except Exception:
            # Create new collection if it doesn't exist
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        return collection

    def add_rules(
        self,
        embeddings: List[List[float]],
        rule_ids: List[str],
        documents: List[str],
        metadata: Optional[List[Dict]] = None
    ) -> None:
        """
        Add rule embeddings to the vector store.
        
        Args:
            embeddings: List of embedding vectors.
            rule_ids: List of unique IDs for each rule.
            documents: List of document strings (rule descriptions + examples).
            metadata: Optional list of metadata dicts for each rule.
        """
        if not metadata:
            metadata = [{"rule_id": rid} for rid in rule_ids]
        
        self.collection.upsert(
            ids=rule_ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadata
        )

    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5
    ) -> Dict:
        """
        Query the vector store for similar rules.
        
        Args:
            query_embedding: Embedding vector of the query.
            n_results: Number of similar rules to return.
            
        Returns:
            Dictionary with ids, documents, distances, and metadatas.
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results

    def query_by_text(
        self,
        query_embedding: List[float],
        rule_id: str = "",
        n_results: int = 5
    ) -> Dict:
        """
        Query with optional filter by rule ID.
        
        Args:
            query_embedding: Embedding vector of the query.
            rule_id: Optional rule ID to filter results.
            n_results: Number of similar rules to return.
            
        Returns:
            Dictionary with query results.
        """
        where_filter = None
        if rule_id:
            where_filter = {"rule_id": rule_id}
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter
        )
        return results

    def get_collection_count(self) -> int:
        """Get the number of documents in the collection."""
        return self.collection.count()

    def delete_collection(self) -> None:
        """Delete the entire collection."""
        self.client.delete_collection(name=self.collection_name)