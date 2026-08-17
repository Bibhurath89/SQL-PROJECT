from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings


BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "chroma_db"

EMBEDDING_MODEL = "nomic-embed-text"


def get_vector_store():
    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL
    )

    vector_store = Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
        collection_name="sql_project_docs",
    )

    return vector_store


def retrieve_context(question: str, k: int = 3):
    vector_store = get_vector_store()

    documents = vector_store.similarity_search(
        question,
        k=k,
    )

    return documents


def format_retrieved_context(documents):
    if not documents:
        return "No relevant business documentation was found."

    context_parts = []

    for i, document in enumerate(documents, start=1):
        source = document.metadata.get("source", "unknown")

        context_parts.append(
            f"""--- Retrieved Document {i} ---
Source: {source}

{document.page_content}
"""
        )

    return "\n\n".join(context_parts)