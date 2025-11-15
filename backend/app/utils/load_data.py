import json
from pathlib import Path
from loguru import logger
from app.services.rag_service import rag_service


def load_medical_knowledge():
    """Load medical knowledge into ChromaDB"""

    data_file = Path("data/medical_knowledge.json")

    if not data_file.exists():
        logger.warning(f"Medical knowledge file not found: {data_file}")
        return

    try:
        with open(data_file, "r") as f:
            documents = json.load(f)

        # Check if collection already has data
        try:
            count = rag_service.collection.count()
            if count > 0:
                logger.info(f"Medical knowledge already loaded ({count} documents)")
                return
        except:
            pass

        # Add documents to ChromaDB
        rag_service.add_documents(documents)
        logger.info(f"Successfully loaded {len(documents)} medical documents")

    except Exception as e:
        logger.error(f"Failed to load medical knowledge: {str(e)}")


if __name__ == "__main__":
    load_medical_knowledge()
