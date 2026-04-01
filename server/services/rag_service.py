"""RAG Service — PDF policy upload, ChromaDB vectorization, and policy-aware querying.

Uses ChromaDB (local, free) + PyPDF2 for text extraction.
During consultation, queries policy docs to check if prescriptions are covered.
"""
import os
import chromadb
from chromadb.config import Settings as ChromaSettings
from PyPDF2 import PdfReader
from typing import List, Optional

from config import settings


# Initialize ChromaDB with local persistent storage
chroma_client = chromadb.Client(ChromaSettings(
    persist_directory=settings.CHROMA_PERSIST_DIR,
    anonymized_telemetry=False,
))


def get_policy_collection(policy_id: str):
    """Get or create a ChromaDB collection for a specific insurance policy."""
    return chroma_client.get_or_create_collection(
        name=f"policy_{policy_id}",
        metadata={"description": "Insurance policy document chunks"},
    )


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF file using PyPDF2 (free)."""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks for better retrieval."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks


async def index_policy_pdf(pdf_path: str, policy_id: str, insurer_name: str) -> dict:
    """Extract text from policy PDF, chunk it, and store in ChromaDB.

    Returns metadata about the indexed document.
    """
    # Extract text from PDF
    text = extract_text_from_pdf(pdf_path)
    if not text.strip():
        return {"error": "No text could be extracted from the PDF"}

    # Chunk the text for better retrieval
    chunks = chunk_text(text)

    # Store in ChromaDB
    collection = get_policy_collection(policy_id)

    # Add chunks with metadata
    ids = [f"{policy_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"policy_id": policy_id, "insurer": insurer_name, "chunk_index": i} for i in range(len(chunks))]

    collection.upsert(
        ids=ids,
        documents=chunks,
        metadatas=metadatas,
    )

    return {
        "policy_id": policy_id,
        "insurer_name": insurer_name,
        "total_pages": len(PdfReader(pdf_path).pages),
        "total_chunks": len(chunks),
        "text_length": len(text),
    }


async def query_policy(policy_id: str, query: str, n_results: int = 3) -> str:
    """Query a policy's vector store to find relevant context for a question.

    Used during consultation to check if medications/procedures are covered.
    """
    try:
        collection = get_policy_collection(policy_id)

        results = collection.query(
            query_texts=[query],
            n_results=n_results,
        )

        if results and results["documents"] and results["documents"][0]:
            # Combine the most relevant chunks as context
            context = "\n---\n".join(results["documents"][0])
            return context

    except Exception as e:
        print(f"RAG query error: {e}")

    return "No policy information available. Defaulting to standard coverage assumptions."


async def check_medication_coverage(policy_id: str, medication: str) -> dict:
    """Check if a specific medication is covered under a policy using RAG + LLM."""
    from services.llm_service import check_policy_coverage

    # Query vector store for relevant policy sections
    policy_context = await query_policy(
        policy_id,
        f"coverage for {medication} medication drug formulary excluded medicines"
    )

    # Use LLM to interpret the policy context
    result = await check_policy_coverage(medication, policy_context)
    return result


def list_indexed_policies() -> List[str]:
    """List all policy IDs that have been indexed in ChromaDB."""
    collections = chroma_client.list_collections()
    return [c.name.replace("policy_", "") for c in collections if c.name.startswith("policy_")]


def delete_policy_index(policy_id: str) -> bool:
    """Delete a policy's vector store."""
    try:
        chroma_client.delete_collection(f"policy_{policy_id}")
        return True
    except Exception:
        return False
