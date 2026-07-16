"""
Embedding Pipeline

Creates embeddings for MISRA C:2012 rules and examples using OpenAI's
embedding API, then stores them in the ChromaDB vector store.
"""

import openai
from typing import Dict, List

from backend.utils.models import Rule
from backend.utils.config import config
from backend.rag.vector_store import VectorStore


class EmbeddingPipeline:
    """
    Pipeline for creating and storing MISRA rule embeddings.
    
    Uses OpenAI's embedding API to generate vector representations
    of rule descriptions and example code.
    """

    def __init__(
        self,
        openai_client: openai.OpenAI = None,
        vector_store: VectorStore = None
    ):
        """
        Initialize the embedding pipeline.
        
        Args:
            openai_client: OpenAI client instance.
            vector_store: VectorStore instance for storage.
        """
        self.client = openai_client or openai.OpenAI(
            api_key=config.OPENAI_EMBEDDING_API_KEY,
            base_url=config.OPENAI_EMBEDDING_API_ENDPOINT or None
        )
        self.vector_store = vector_store or VectorStore()

    def create_embeddings(self, rules: Dict[str, Rule]) -> None:
        """
        Create embeddings for all rules and store in vector store.
        
        Args:
            rules: Dictionary of rule_id to Rule objects.
        """
        if not rules:
            print("No rules to embed.")
            return

        # Prepare data for embedding
        rule_ids = []
        documents = []
        metadata_list = []

        for rule_id, rule in rules.items():
            rule_ids.append(rule_id)
            
            # Create document from rule description and examples
            doc = self._create_document(rule)
            documents.append(doc)
            
            # Create metadata
            metadata = {
                "rule_id": rule_id,
                "rule_type": rule.rule_type.value,
                "category": rule.category,
                "example_files": rule.example_files
            }
            metadata_list.append(metadata)

        # Generate embeddings in batches (OpenAI limit: 16384 max)
        embeddings = self._generate_embeddings(documents)

        # Store in vector database
        self.vector_store.add_rules(
            embeddings=embeddings,
            rule_ids=rule_ids,
            documents=documents,
            metadata=metadata_list
        )

        print(f"Embedded {len(rules)} rules into vector store.")

    def _create_document(self, rule: Rule) -> str:
        """
        Create a document string from a Rule for embedding.
        
        Args:
            rule: Rule object to convert.
            
        Returns:
            Document string combining description and examples.
        """
        parts = [
            f"Rule {rule.rule_id}: {rule.description}",
            f"Category: {rule.category}",
        ]
        
        # Add example content (truncated if too long)
        if rule.example_content:
            # Limit example content to avoid token limits
            max_example_length = 4000
            example = rule.example_content[:max_example_length]
            parts.append(f"Example code:\n{example}")
        
        return "\n\n".join(parts)

    def _generate_embeddings(self, documents: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of documents.
        
        Args:
            documents: List of document strings.
            
        Returns:
            List of embedding vectors.
        """
        embeddings = []
        
        # Process in batches to handle rate limits
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            
            response = self.client.embeddings.create(
                model=config.OPENAI_EMBEDDING_MODEL,
                input=batch
            )
            
            batch_embeddings = [
                embedding.embedding for embedding in response.data
            ]
            embeddings.extend(batch_embeddings)

        return embeddings

    def get_embedding(self, text: str) -> List[float]:
        """
        Generate a single embedding for a text string.
        
        Args:
            text: Text to embed.
            
        Returns:
            Embedding vector.
        """
        response = self.client.embeddings.create(
            model=config.OPENAI_EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding