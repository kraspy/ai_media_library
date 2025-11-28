import logging
import shutil
from typing import List

from django.conf import settings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

logger = logging.getLogger(__name__)


class RAGService:
    """
    Service for interacting with the Vector Store (ChromaDB).
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RAGService, cls).__new__(cls)
            cls._instance.persist_directory = settings.BASE_DIR / 'chroma_db'
            cls._instance.embedding_function = OpenAIEmbeddings(
                api_key=settings.OPENAI_API_KEY
            )
            cls._instance.vector_store = Chroma(
                persist_directory=str(cls._instance.persist_directory),
                embedding_function=cls._instance.embedding_function,
                collection_name='media_items',
            )
        return cls._instance

    def add_document(self, text: str, metadata: dict):
        """
        Adds a document to the vector store.
        """
        doc = Document(page_content=text, metadata=metadata)
        self.vector_store.add_documents([doc])
        logger.info(
            f'Added document to RAG: {metadata.get("title", "Unknown")}'
        )

    def search(self, query: str, k: int = 3) -> List[Document]:
        """
        Searches for relevant documents.
        """
        return self.vector_store.similarity_search(query, k=k)

    def clear_index(self):
        """
        Clears the vector store.
        """
        if self.persist_directory.exists():
            shutil.rmtree(self.persist_directory)
            self.vector_store = Chroma(
                persist_directory=str(self.persist_directory),
                embedding_function=self.embedding_function,
                collection_name='media_items',
            )
