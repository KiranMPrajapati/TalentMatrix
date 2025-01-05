import math
import json
import chromadb
from FlagEmbedding import FlagModel
from chromadb.api.types import EmbeddingFunction
from logger_config import get_logger

logger = get_logger("MainModule")


def setup_chromadb(chroma_db_storage_path, collection_name):
    chroma_client = ChromaDB(db_path=chroma_db_storage_path)
    collection = chroma_client.get_or_create_collection(collection_name)

    return chroma_client, collection


class CustomEmbedding(EmbeddingFunction):
    def __init__(self):
        self.embedding_model = FlagModel('BAAI/bge-base-en-v1.5', use_fp16=True)

    def __call__(self, docs):
        if isinstance(docs[0], str):
            return self.embedding_model.encode(docs).tolist()
        else:
            raise TypeError("Input to embedding model must be a list of strings.")


class ChromaDB:
    def __init__(self, db_path, distance_method = "cosine"):
        self.db_path = db_path
        self.client = self.create_connection()
        self.embedding_model = CustomEmbedding()
        self.distance_method = distance_method

    def create_connection(self):
        client = chromadb.PersistentClient(path=self.db_path)
        return client

    def create_collection(self, project_id):
        collection = self.client.create_collection(
            name=project_id,
            embedding_function=CustomEmbedding()
        )
        
        logger.info(f"\nCreate Collection:\n {collection.get().get('ids')}")
        return collection

    def get_collection(self, project_id):
        collection = self.client.get_collection(
            name=project_id,
            embedding_function=CustomEmbedding()
        )
        
        logger.info(f"\nGet Collection:\n {collection.get().get('ids')}")
        return collection

    def get_or_create_collection(self, project_id):
        collection = self.client.get_or_create_collection(
            name=project_id,
            embedding_function=CustomEmbedding()
        )
        
        logger.info(f"\nGet or Create Collection:\n {collection.get().get('ids')}")
        return collection

    def add_to_collection(self, collection, docs):
        documents = [doc["page_content"] for doc in docs]

        embeddings = self.embedding_model(documents)
        num_docs = collection.count()
        ids = [f"id_{i + num_docs}" for i in range(len(docs))]

        collection.add(
            documents=documents,
            embeddings=embeddings,
            ids=ids
        )

    def _calculate_relevance_score(self, distance):
        if self.distance_method == "l2":
            sim_score = 1.0 - distance / math.sqrt(2)
        elif self.distance_method == "cosine":
            sim_score = 1.0 - distance
        else:
            sim_score = None
        return round(sim_score, 2)

    def query_collection(self, collection, query, top_k=2):
        query_result = collection.query(
            query_texts=[query],
            n_results=top_k,
            # where={"action": filter_by}
        )
        results = []
        for result in zip(
            query_result["documents"][0],
            query_result["metadatas"][0],
            query_result["distances"][0],
            query_result["ids"][0]
        ):
            metadata = result[1] or {}
            # Deserialize metadata values if needed
            if "keys" in metadata:
                try:
                    metadata["keys"] = json.loads(metadata["keys"])
                except (json.JSONDecodeError, TypeError):
                    logger.error(f"Failed to deserialize metadata keys: {metadata['keys']}")
                    metadata["keys"] = []  # Default to empty list

            results.append({
                "page_content": result[0],
                "metadata": metadata,
                "similarity_score": self._calculate_relevance_score(result[2]),
                "chunk_id": result[3],
            })

        logger.info(f"\nQuery Results:\n {results}")
        return results

    def delete_collection(self, collection_name):
        self.client.delete_collection(name=collection_name)


if __name__ == "__main__":
    chroma_db_storage_path = "data/chroma-data"
    project_id = "initial_test"

    chroma_client = ChromaDB(db_path=chroma_db_storage_path)
    collection = chroma_client.get_or_create_collection(project_id)

    doc1 = {"page_content": "The city never sleeps, but I miss the quiet countryside.", "metadata": {"action": "content", "keys": ["a"]}}
    doc2 = {"page_content": "Education is the foundation for a brighter future.", "metadata": {"action": "header", "keys": ["b"]}}
    doc3 = {"page_content": "Nature's beauty is a constant source of inspiration.", "metadata": {"action": "header", "keys": ["c", "d"]}}
    doc4 = {"page_content": "Technology connects us, but it also isolates us.", "metadata": {"action": "header", "keys": ["e"]}}

    my_final_doc = [doc1, doc2, doc3, doc4]

    print(f"\nCollection Count Before Adding: {collection.count()}\n")
    chroma_client.add_to_collection(collection=collection, docs=my_final_doc)
    print(f"\nCollection Count After Adding: {collection.count()}\n")

    query = "When does the city sleeps?"
    received_docs = chroma_client.query_collection(collection, query, k=2)                  

    for doc in received_docs:
        print(f"Query Result: {doc}")