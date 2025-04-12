# backend/create_embeddings.py
import os
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document


def create_document_chunks(chapters_json_path):
    """
    Load chapters and split them into smaller chunks for embedding.
    """
    # Load chapters
    with open(chapters_json_path, "r", encoding="utf-8") as f:
        chapters = json.load(f)

    # Convert to LangChain documents
    documents = []

    for chapter in chapters:
        # Create metadata for better retrieval context
        metadata = {
            "book": chapter["book"],
            "chapter": chapter["chapter"],
            "source": f"Harry Potter Book {chapter['book']}, Chapter {chapter['chapter']}"
        }

        # Create document with text and metadata
        doc = Document(
            page_content=chapter["text"],
            metadata=metadata
        )

        documents.append(doc)

    # Split documents into smaller chunks for better retrieval
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=128,
        separators=["\n\n", "\n", ".", "?", "!"]
    )

    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks from {len(documents)} chapters")

    return chunks


def create_vector_store(chunks, persist_directory):
    """
    Create vector embeddings and store them in ChromaDB.
    """
    # Initialize HuggingFace embeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Create vector store
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )

    # Persist vector store to disk
    vectordb.persist()
    print(f"Created vector store with {len(chunks)} chunks at {persist_directory}")

    return vectordb


def main():
    # Paths
    data_dir = r"C:\Users\sumit jha\Desktop\codes\Storybook\backend\data\processed"
    chapters_path = os.path.join(data_dir, "all_chapters.json")
    vector_store_dir = os.path.join(data_dir, "chroma_db")

    # Create chunks from chapters
    chunks = create_document_chunks(chapters_path)

    # Create and save vector store
    create_vector_store(chunks, vector_store_dir)


if __name__ == "__main__":
    main()
