import logging
import shutil
from typing import List

from apps.library.services.embeddings import DeterministicFakeEmbedding
from django.conf import settings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

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
            cls._instance.embedding_function = DeterministicFakeEmbedding(
                size=1536
            )
            cls._instance.vector_store = Chroma(
                persist_directory=str(cls._instance.persist_directory),
                embedding_function=cls._instance.embedding_function,
                collection_name='media_items',
            )
            cls._instance.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
        return cls._instance

    def add_document(self, text: str, metadata: dict):
        """
        Adds a single document to the vector store (raw).
        """
        doc = Document(page_content=text, metadata=metadata)
        self.vector_store.add_documents([doc])
        logger.info(
            f'Added document to RAG: {metadata.get("title", "Unknown")}'
        )

    def index_media_item(self, media_item):
        """
        Indexes a MediaItem: combines summary + transcription, splits into chunks, and indexes.
        """
        try:
            content_parts = []
            if media_item.summary:
                content_parts.append(f'Summary: {media_item.summary}')
            if media_item.transcription:
                content_parts.append(
                    f'Transcription: {media_item.transcription}'
                )

            full_text = '\n\n'.join(content_parts)

            if not full_text.strip():
                logger.warning(
                    f'No content to index for MediaItem ID {media_item.id}'
                )
                return

            metadatas = {
                'source': 'media_item',
                'media_item_id': media_item.id,
                'title': media_item.title,
                'media_type': media_item.media_type,
            }

            chunks = self.text_splitter.create_documents(
                [full_text], metadatas=[metadatas]
            )

            self.vector_store.add_documents(chunks)
            logger.info(
                f'Indexed MediaItem {media_item.id}: {len(chunks)} chunks.'
            )

        except Exception as e:
            logger.error(f'Error indexing MediaItem {media_item.id}: {e}')
            raise e

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
