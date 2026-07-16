"""
RAG Retrieval System

Retrieves relevant MISRA C:2012 rule context for violations using
the vector store and embedding pipeline.
"""

from typing import Dict, List

from backend.utils.models import Violation, Rule
from backend.utils.config import config
from backend.rag.vector_store import VectorStore
from backend.rag.embedding_pipeline import EmbeddingPipeline


class RAGRetriever:
    """
    Retrieval-Augmented Generation retriever for MISRA rules.
    
    Uses semantic similarity to find relevant rule examples and
    guidance for each violation.
    """

    def __init__(
        self,
        vector_store: VectorStore = None,
        embedding_pipeline: EmbeddingPipeline = None
    ):
        """
        Initialize the RAG retriever.
        
        Args:
            vector_store: VectorStore instance.
            embedding_pipeline: EmbeddingPipeline instance.
        """
        self.vector_store = vector_store or VectorStore()
        self.embedding_pipeline = embedding_pipeline or EmbeddingPipeline(
            vector_store=self.vector_store
        )

    def retrieve_context(
        self,
        violation: Violation,
        top_k: int = None
    ) -> Dict:
        """
        Retrieve relevant context for a single violation.
        
        Args:
            violation: The violation to find context for.
            top_k: Number of similar rules to retrieve.
            
        Returns:
            Dictionary with retrieved context including:
            - rule_ids: List of matching rule IDs
            - documents: List of matching documents
            - distances: Similarity distances
        """
        if top_k is None:
            top_k = config.RAG_TOP_K

        # Create query from violation description
        query_text = f"{violation.rule_id}: {violation.description}"
        
        # Generate embedding for the query
        query_embedding = self.embedding_pipeline.get_embedding(query_text)
        
        # Query vector store
        results = self.vector_store.query(
            query_embedding=query_embedding,
            n_results=top_k
        )
        
        return results

    def retrieve_context_for_violations(
        self,
        violations: List[Violation],
        top_k: int = None
    ) -> Dict[str, Dict]:
        """
        Retrieve context for multiple violations.
        
        Args:
            violations: List of violations.
            top_k: Number of similar rules per violation.
            
        Returns:
            Dictionary mapping violation key to retrieved context.
        """
        results = {}
        
        for violation in violations:
            # Create unique key for this violation
            key = f"{violation.file}:{violation.line}:{violation.rule_id}"
            results[key] = self.retrieve_context(violation, top_k)
        
        return results

    def format_context_for_llm(self, results: Dict) -> str:
        """
        Format retrieved context into a string suitable for LLM prompts.
        
        Args:
            results: Raw results from vector store query.
            
        Returns:
            Formatted context string.
        """
        if not results or not results.get('documents'):
            return "No relevant context found."

        formatted_parts = []
        
        # Unpack results (ChromaDB returns lists of lists)
        rule_ids = results.get('ids', [[]])[0]
        documents = results.get('documents', [[]])[0]
        distances = results.get('distances', [[]])[0]

        for i, (rule_id, doc, distance) in enumerate(
            zip(rule_ids, documents, distances)
        ):
            similarity = 1 - distance  # Convert distance to similarity
            formatted_parts.append(
                f"--- Relevant Rule {rule_id} (similarity: {similarity:.2f}) ---\n"
                f"{doc}\n"
            )

        return "\n".join(formatted_parts)