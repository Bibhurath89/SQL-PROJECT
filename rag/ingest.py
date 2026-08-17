from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
CHROMA_DIR = BASE_DIR / "chroma_db"

EMBEDDING_MODEL = "nomic-embed-text"


def build_vector_store():
    print("Loading documentation...")

    loader = DirectoryLoader(
        str(DOCS_DIR),
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )

    documents = loader.load()

    if not documents:
        raise ValueError("No documents found in the docs directory.")

    print(f"Loaded {len(documents)} documents.")

    # Split documents into smaller pieces.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100,
        separators=[
            "\n## ",
            "\n### ",
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
    )

    chunks = text_splitter.split_documents(documents)

    print(f"Created {len(chunks)} chunks.")

    # Add useful metadata.
    for chunk in chunks:
        source = chunk.metadata.get("source", "unknown")
        chunk.metadata["source"] = Path(source).name

    print("Creating embeddings...")

    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL
    )

    print("Building Chroma vector database...")

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
        collection_name="sql_project_docs",
    )

    print("RAG ingestion complete.")
    print(f"Vector database: {CHROMA_DIR}")
    print(f"Stored chunks: {len(chunks)}")

    return vector_store


if __name__ == "__main__":
    build_vector_store()