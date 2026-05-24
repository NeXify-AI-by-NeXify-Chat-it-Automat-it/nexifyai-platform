"""
LangChain RAG Pipeline — Enterprise Retrieval-Augmented Generation
===================================================================
Ersetzt: brain_api.py (243 Zeilen, Zero-Vector-Placeholder) + oracle_engine.py RAG-Teil (~300 Zeilen)

Architektur:
  Loader → Splitter → Embeddings → Qdrant Vector Store → Retriever → QA Chain
  
Vorteile gegenüber Custom-Lösung:
  - Echte Embeddings (intfloat/e5-small-v2) statt Zero-Vector-Placeholder
  - Native Qdrant-Integration (kein manuelles Scroll/Filter)
  - Contextual Compression (nur relevante Chunks ans LLM)
  - Multi-Query Retriever (bessere Recall-Rate)
  - Source-Citations automatisch
"""
import os
import logging
from typing import List, Optional

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.retrievers import ContextualCompressionRetriever, MultiQueryRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    WebBaseLoader,
    DirectoryLoader,
)
from langchain_chroma import Chroma
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from langchain_config import get_embedding_model, create_llm_with_fallbacks, get_llm_for_task

logger = logging.getLogger("nexifyai.rag")

# ─── Qdrant-Verbindung ────────────────────────────────────────────────────────

def get_qdrant_client() -> QdrantClient:
    """Qdrant-Client (lokal, läuft im Docker-Netzwerk)."""
    host = os.getenv("QDRANT_HOST", "localhost")
    port = int(os.getenv("QDRANT_PORT", "6333"))
    return QdrantClient(host=host, port=port)


def get_vector_store(
    collection_name: str = "nexifyai_brain",
    embedding_model: Optional[str] = None,
) -> QdrantVectorStore:
    """Qdrant Vector Store mit echten Embeddings.
    
    Ersetzt brain_api.py's Zero-Vector-Placeholder (4096 Nullen).
    """
    embeddings = get_embedding_model(model_name=embedding_model) if embedding_model else get_embedding_model()
    client = get_qdrant_client()
    
    return QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings,
    )


# ─── Retriever-Konfiguration ──────────────────────────────────────────────────

def get_retriever(
    collection_name: str = "nexifyai_brain",
    k: int = 5,
    score_threshold: Optional[float] = None,
    use_multi_query: bool = True,
    use_compression: bool = True,
) -> VectorStoreRetriever:
    """Erstelle einen optimierten Retriever mit optionalem Multi-Query + Contextual Compression.
    
    Multi-Query: Generiert 3 verwandte Fragen für bessere Recall-Rate
    Compression: Entfernt irrelevante Teile aus gefundenen Dokumenten
    
    >>> retriever = get_retriever(k=4)
    >>> docs = retriever.get_relevant_documents("Was sind Python Decorators?")
    """
    vector_store = get_vector_store(collection_name)
    
    # Basis-Retriever
    search_kwargs = {"k": k}
    if score_threshold is not None:
        search_kwargs["score_threshold"] = score_threshold
    
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs=search_kwargs,
    )
    
    # Multi-Query: Automatische Query-Expansion für bessere Ergebnisse
    if use_multi_query:
        llm = get_llm_for_task("extract")
        retriever = MultiQueryRetriever.from_llm(
            retriever=retriever,
            llm=llm,
            include_original=True,  # Original-Query behalten
        )
    
    # Contextual Compression: Nur relevante Passagen behalten
    if use_compression:
        compressor_llm = get_llm_for_task("extract")
        compressor = LLMChainExtractor.from_llm(compressor_llm)
        retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=retriever,
        )
    
    return retriever


# ─── QA Chains ────────────────────────────────────────────────────────────────

def create_qa_chain(
    collection_name: str = "nexifyai_brain",
    k: int = 5,
    return_sources: bool = True,
    chain_type: str = "stuff",
) -> RetrievalQA:
    """Erstelle eine QA-Chain für Single-Turn Fragen.
    
    >>> qa = create_qa_chain()
    >>> result = qa.invoke({"query": "Was ist die Architektur-Entscheidung für Supabase?"})
    >>> print(result["result"])
    >>> print(f"Quellen: {len(result['source_documents'])}")
    
    Args:
        collection_name: Qdrant Collection
        k: Anzahl relevanter Dokumente
        return_sources: Quellen in Antwort inkludieren
        chain_type: 'stuff' (schnell), 'map_reduce' (viele Docs), 'refine' (gründlich)
    """
    retriever = get_retriever(collection_name, k=k)
    llm = get_llm_for_task("research")
    
    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=return_sources,
        chain_type=chain_type,
    )


def create_conversational_qa(
    collection_name: str = "nexifyai_brain",
    k: int = 5,
) -> ConversationalRetrievalChain:
    """Erstelle eine Conversational QA Chain mit Memory.
    
    >>> qa = create_conversational_qa()
    >>> qa.invoke({"question": "Was ist Python?"})
    >>> qa.invoke({"question": "Gib mir Beispiele"})  # Merkt Kontext!
    """
    retriever = get_retriever(collection_name, k=k)
    llm = get_llm_for_task("research")
    
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer",
    )
    
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
    )


# ─── Dokumenten-Ingestion ─────────────────────────────────────────────────────

def ingest_document(
    file_path: str,
    collection_name: str = "nexifyai_brain",
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    metadata: Optional[dict] = None,
) -> int:
    """Lade ein Dokument in den Vector Store.
    
    >>> ingest_document("docs/ADR-001-dos-v2-adoption.md")
    
    Args:
        file_path: Pfad zur Datei
        collection_name: Qdrant Collection
        chunk_size: Zeichen pro Chunk (Default: 1000)
        chunk_overlap: Überlappung zwischen Chunks (Default: 200)
        metadata: Zusätzliche Metadaten (z.B. {"category": "adr"})
    
    Returns: Anzahl der gespeicherten Chunks
    """
    # Loader je nach Dateityp
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    else:
        loader = TextLoader(file_path, encoding="utf-8")
    
    documents = loader.load()
    
    # Metadaten hinzufügen
    if metadata:
        for doc in documents:
            doc.metadata.update(metadata)
    
    # Chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""],
    )
    
    chunks = text_splitter.split_documents(documents)
    
    # In Qdrant speichern
    vector_store = get_vector_store(collection_name)
    vector_store.add_documents(chunks)
    
    logger.info(f"Ingested {len(chunks)} Chunks aus {file_path}")
    return len(chunks)


def ingest_directory(
    directory_path: str,
    glob_pattern: str = "**/*.md",
    collection_name: str = "nexifyai_brain",
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> int:
    """Lade alle Dokumente eines Verzeichnisses in den Vector Store.
    
    >>> ingest_directory("docs/adrs/", "**/*.md")
    
    Args:
        directory_path: Verzeichnispfad
        glob_pattern: Dateimuster (Default: **/*.md)
        collection_name: Qdrant Collection
    
    Returns: Anzahl der gespeicherten Chunks
    """
    loader = DirectoryLoader(
        directory_path,
        glob=glob_pattern,
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    
    documents = loader.load()
    
    # Metadaten: Kategorie aus Verzeichnisname ableiten
    for doc in documents:
        rel_path = os.path.relpath(doc.metadata.get("source", ""), directory_path)
        category = os.path.dirname(rel_path).split("/")[0] or "docs"
        doc.metadata["category"] = category
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    
    chunks = text_splitter.split_documents(documents)
    
    vector_store = get_vector_store(collection_name)
    vector_store.add_documents(chunks)
    
    logger.info(f"Ingested {len(chunks)} Chunks aus {directory_path} ({glob_pattern})")
    return len(chunks)


# ─── Knowledge Base Initialisierung ───────────────────────────────────────────

def init_knowledge_base():
    """Initiale Befüllung der Wissensdatenbank mit allen ADRs, Policies und Docs.
    
    Aufruf in server.py lifespan():
        from rag_pipeline import init_knowledge_base
        init_knowledge_base()
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    docs_dir = os.path.join(base_dir, "docs")
    
    total = 0
    
    # ADRs
    adr_dir = os.path.join(docs_dir, "adrs")
    if os.path.exists(adr_dir):
        total += ingest_directory(adr_dir, "ADR-*.md", metadata_defaults={"category": "adr"})
    
    # Policies
    policy_dir = os.path.join(docs_dir, "policies")
    if os.path.exists(policy_dir):
        total += ingest_directory(policy_dir, "*.md", metadata_defaults={"category": "policy"})
    
    # Architecture
    arch_dir = os.path.join(docs_dir, "architecture")
    if os.path.exists(arch_dir):
        total += ingest_directory(arch_dir, "*.md", metadata_defaults={"category": "architecture"})
    
    logger.info(f"Wissensdatenbank initialisiert: {total} Chunks gespeichert")
    return total
