import os
from typing import List, Dict

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

from app.utils.rule_loader import load_markdown


class RuleRAGEngine:
    """
    RAG engine for rule grounding.
    Loads weather_minima.md and dispatch_rules.md,
    splits into stable chunks, stores in vector DB,
    retrieves relevant rule chunks with citations.
    """

    def __init__(self, persist_dir: str = "chroma_rules_db"):

        self.persist_dir = persist_dir

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        self.vectorstore = None

        self._initialize_vectorstore()

    def _initialize_vectorstore(self):
        """
        Loads rule documents, splits into chunks,
        and builds (or reloads) vector DB.
        """

        weather_text = load_markdown("data/weather_minima.md")
        dispatch_text = load_markdown("data/dispatch_rules.md")

        documents = []

        documents.extend(
            self._create_documents(
                weather_text,
                source="doc_weather"
            )
        )

        documents.extend(
            self._create_documents(
                dispatch_text,
                source="doc_dispatch"
            )
        )

        self.vectorstore = Chroma.from_documents(
            documents,
            embedding=self.embeddings,
            persist_directory=self.persist_dir
        )

        self.vectorstore.persist()

    def _create_documents(self, text: str, source: str) -> List[Document]:
        """
        Splits markdown into structured chunks.
        Each chunk gets a stable chunk_id for citation.
        """

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=50
        )

        raw_docs = splitter.split_text(text)

        documents = []

        for idx, chunk in enumerate(raw_docs):
            chunk_id = f"{source}#chunk{idx}"

            doc = Document(
                page_content=chunk,
                metadata={
                    "source": source,
                    "chunk_id": chunk_id
                }
            )

            documents.append(doc)

        return documents

    def retrieve_rules(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieves relevant rule chunks.
        Returns list of:
        {
            "chunk_id": str,
            "source": str,
            "content": str
        }
        """

        results = self.vectorstore.similarity_search(
            query,
            k=top_k
        )

        retrieved = []

        for doc in results:
            retrieved.append({
                "chunk_id": doc.metadata["chunk_id"],
                "source": doc.metadata["source"],
                "content": doc.page_content
            })

        return retrieved
