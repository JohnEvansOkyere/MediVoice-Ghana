import chromadb
from chromadb.config import Settings
from typing import List, Dict
from loguru import logger
from sentence_transformers import SentenceTransformer


class RAGService:
    """RAG service for medical knowledge retrieval using ChromaDB"""

    def __init__(self, persist_directory: str = "./data/chromadb"):
        # Initialize ChromaDB client
        self.client = chromadb.Client(
            Settings(
                persist_directory=persist_directory,
                anonymized_telemetry=False
            )
        )

        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="medical_knowledge",
            metadata={"description": "Medical knowledge base for Ghana"}
        )

        logger.info("RAG service initialized")

    def add_documents(self, documents: List[Dict[str, str]]):
        """
        Add documents to the knowledge base

        Args:
            documents: List of dicts with 'text', 'metadata'
        """
        try:
            texts = [doc["text"] for doc in documents]
            metadatas = [doc.get("metadata", {}) for doc in documents]
            ids = [f"doc_{i}" for i in range(len(documents))]

            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )

            logger.info(f"Added {len(documents)} documents to knowledge base")

        except Exception as e:
            logger.error(f"Failed to add documents: {str(e)}")

    def search(self, query: str, n_results: int = 3) -> str:
        """
        Search for relevant medical information

        Args:
            query: User's query or symptoms
            n_results: Number of results to return

        Returns:
            Formatted context string
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )

            if not results["documents"] or not results["documents"][0]:
                return ""

            # Format results into context
            context_parts = []
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                source = metadata.get("source", "Medical Database")

                context_parts.append(f"[{source}]\n{doc}")

            context = "\n\n".join(context_parts)
            logger.info(f"Found {len(results['documents'][0])} relevant documents")

            return context

        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return ""

    def extract_symptoms(self, text: str) -> List[str]:
        """
        Extract symptoms from user text using keyword matching

        Args:
            text: User's message

        Returns:
            List of detected symptoms
        """
        # Common symptoms keywords (expand this list)
        symptom_keywords = [
            "fever", "headache", "pain", "cough", "vomiting", "diarrhea",
            "nausea", "fatigue", "weakness", "dizzy", "chills", "sweating",
            "bleeding", "rash", "swelling", "aching", "sore throat",
            "runny nose", "congestion", "shortness of breath", "chest pain",
            "abdominal pain", "stomach pain", "back pain", "joint pain",
            "muscle pain", "body aches", "loss of appetite", "weight loss"
        ]

        text_lower = text.lower()
        detected = []

        for symptom in symptom_keywords:
            if symptom in text_lower:
                detected.append(symptom)

        logger.info(f"Detected symptoms: {detected}")
        return detected

    def is_emergency(self, text: str) -> bool:
        """
        Detect if message contains emergency keywords

        Args:
            text: User's message

        Returns:
            True if emergency detected
        """
        emergency_keywords = [
            "severe bleeding", "heavy bleeding", "blood",
            "chest pain", "heart attack", "stroke",
            "can't breathe", "cannot breathe", "difficulty breathing",
            "unconscious", "passed out", "seizure",
            "severe pain", "extreme pain", "unbearable pain",
            "poisoning", "overdose", "suicide",
            "severe injury", "broken bone", "accident"
        ]

        text_lower = text.lower()

        for keyword in emergency_keywords:
            if keyword in text_lower:
                logger.warning(f"EMERGENCY detected: {keyword}")
                return True

        return False


# Singleton instance
rag_service = RAGService()
