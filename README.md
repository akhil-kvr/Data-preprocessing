# Data-preprocessing

This repo contains scripts for extraction, chunking, and organizing for building a chatbot for my local disk drive.

When you’re dealing with terabytes of data, you can’t just "upload" it all into a model—it's way too much for a computer to memorize at once. Instead, we need to turn your raw storage into an AI-ready knowledge base using a method called RAG (Retrieval-Augmented Generation). It's basically giving the AI an "open-book" exam. 
Here is how we’re going to handle your data, step-by-step:

1. Cleaning and Standardizing
First, we have to get everything into the same language. Whether it's a PDF, a Word doc, or an Excel sheet, we’ll use tools like LangChain to convert it all into plain text or Markdown.
•	The Goal: Strip out the "junk" like HTML tags, legal footers, and page numbers.
•	The Big Win: We’ll run a deduplication script. Since we have terabytes, removing exact copies will save us in processing costs.

3. Breaking it Down (Chunking)
An AI can only "read" a few pages at a time. We’re going to slice our long documents into small, manageable pieces called chunks (usually about 500 words each).
•	The Trick: We’ll overlap the edges of these chunks so we don't lose the context between them.
•	Organization: We’ll tag every chunk with metadata (like the file name or department) so the chatbot can tell us exactly where it found its information.

5. Creating a Searchable Brain (Embeddings)
To make this searchable, we convert those text chunks into lists of numbers called Embeddings. 
•	How it works: These numbers represent the meaning of the text.
•	The Storage: We’ll put these numbers into a Vector Database (like ChromaDB). This is what allows the chatbot to find the right answer in milliseconds, even across terabytes of info.

7. Fine-Tuning for Your "Vibe"
If your data is full of super-specific industry (like legal or medical terms), we might pick a small, high-quality sample of your data to Fine-Tune the model. This doesn't teach it new facts, but it teaches it how to speak your specific language and follow your preferred tone. 
