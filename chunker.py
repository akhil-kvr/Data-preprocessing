"""
chunker.py - Split text into overlapping chunks for embedding.
"""


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100):
    """
    Split text into chunks of roughly `chunk_size` characters,
    with `overlap` characters of overlap between consecutive chunks.

    Splits on paragraph/sentence boundaries where possible.
    """
    text = text.strip()
    if not text:
        return []

    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)

        # Try to break at a paragraph or sentence boundary near `end`
        if end < text_len:
            break_point = -1
            for sep in ["\n\n", "\n", ". ", " "]:
                idx = text.rfind(sep, start + int(chunk_size * 0.5), end)
                if idx != -1:
                    break_point = idx + len(sep)
                    break
            if break_point != -1:
                end = break_point

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= text_len:
            break

        start = max(end - overlap, start + 1)

    return chunks