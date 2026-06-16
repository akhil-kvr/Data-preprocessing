"""
index_docs.py - Crawl a directory tree, extract text from documents,
chunk it, embed it with Ollama, and store it in a local ChromaDB.

Usage:
    python index_docs.py "C:\\Users\\YourName\\Documents"
    python index_docs.py "C:\\Users\\YourName\\Documents" "C:\\Work"
"""

import os
import sys
import hashlib
import time

import chromadb
import ollama
from tqdm import tqdm

from extract import extract_text, SUPPORTED_EXTENSIONS
from chunker import chunk_text

# ---- Config ----
DB_PATH = "./chroma_db"
COLLECTION_NAME = "local_docs"
EMBED_MODEL = "nomic-embed-text"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

# Folders to always skip (common junk / system folders on Windows)
SKIP_DIR_NAMES = {
    "windows", "program files", "program files (x86)", "programdata",
    "$recycle.bin", "appdata", "node_modules", ".git", "__pycache__",
    "venv", ".venv", "site-packages", "temp", "tmp", "cache",
}

MAX_FILE_SIZE_MB = 50  # skip huge files


def should_skip_dir(dirname: str) -> bool:
    return dirname.lower() in SKIP_DIR_NAMES or dirname.startswith(".")


def file_id(filepath: str, chunk_idx: int) -> str:
    h = hashlib.md5(filepath.encode("utf-8")).hexdigest()
    return f"{h}_{chunk_idx}"


def gather_files(root_dirs):
    """Walk directories and yield file paths with supported extensions."""
    for root_dir in root_dirs:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            dirnames[:] = [d for d in dirnames if not should_skip_dir(d)]
            for fname in filenames:
                ext = os.path.splitext(fname)[1].lower()
                if ext in SUPPORTED_EXTENSIONS:
                    full = os.path.join(dirpath, fname)
                    try:
                        size_mb = os.path.getsize(full) / (1024 * 1024)
                        if size_mb <= MAX_FILE_SIZE_MB:
                            yield full
                    except OSError:
                        continue


def embed_batch(texts):
    """Get embeddings for a list of texts from Ollama, one at a time."""
    embeddings = []
    for t in texts:
        resp = ollama.embeddings(model=EMBED_MODEL, prompt=t)
        embeddings.append(resp["embedding"])
    return embeddings


def main():
    if len(sys.argv) < 2:
        print("Usage: python index_docs.py <folder1> [folder2] ...")
        print('Example: python index_docs.py "C:\\Users\\You\\Documents"')
        sys.exit(1)

    root_dirs = sys.argv[1:]
    for d in root_dirs:
        if not os.path.isdir(d):
            print(f"Warning: '{d}' is not a directory, skipping.")

    print("Connecting to local ChromaDB...")
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_or_create_collection(COLLECTION_NAME)

    print("Scanning for files (this may take a while for large drives)...")
    files = list(gather_files(root_dirs))
    print(f"Found {len(files)} candidate files.")

    # Track already-indexed files (by path) to allow resuming
    existing = set()
    try:
        all_meta = collection.get(include=["metadatas"])
        for m in all_meta["metadatas"]:
            existing.add(m["source"])
    except Exception:
        pass

    indexed_count = 0
    skipped_count = 0
    error_count = 0

    for filepath in tqdm(files, desc="Indexing"):
        if filepath in existing:
            skipped_count += 1
            continue

        text = extract_text(filepath)
        if not text or not text.strip():
            continue

        chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
        if not chunks:
            continue

        try:
            embeddings = embed_batch(chunks)
        except Exception as e:
            print(f"\n  [embed error] {filepath}: {e}")
            error_count += 1
            continue

        ids = [file_id(filepath, i) for i in range(len(chunks))]
        metadatas = [{"source": filepath, "chunk": i} for i in range(len(chunks))]

        try:
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas,
            )
            indexed_count += 1
        except Exception as e:
            print(f"\n  [db error] {filepath}: {e}")
            error_count += 1

    print("\n--- Indexing complete ---")
    print(f"Newly indexed files: {indexed_count}")
    print(f"Already indexed (skipped): {skipped_count}")
    print(f"Errors: {error_count}")
    print(f"Total chunks in DB: {collection.count()}")


if __name__ == "__main__":
    main()