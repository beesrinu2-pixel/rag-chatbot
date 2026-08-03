import io
from typing import List, Dict, Any
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

class EmbeddingFunctionWrapper:
    """Wrapper to integrate SentenceTransformer with ChromaDB."""
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def __call__(self, input: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(input)
        return embeddings.tolist()

def extract_text_from_pdf(pdf_file) -> List[Dict[str, Any]]:
    """
    Extracts text page by page from an uploaded PDF file stream.
    Returns a list of dicts: [{'page': 1, 'text': '...'}, ...]
    """
    reader = PdfReader(pdf_file)
    extracted_pages = []
    
    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = text.strip()
        if text:
            extracted_pages.append({
                "page": idx + 1,
                "text": text
            })
    return extracted_pages

def chunk_pdf_pages(pages: List[Dict[str, Any]], chunk_size: int = 500, chunk_overlap: int = 100) -> List[Dict[str, Any]]:
    """
    Splits page text into smaller overlapping chunks while preserving page metadata.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = []
    chunk_id = 0
    for page_info in pages:
        page_num = page_info["page"]
        page_text = page_info["text"]
        
        split_texts = text_splitter.split_text(page_text)
        for text_chunk in split_texts:
            chunks.append({
                "id": f"chunk_{chunk_id}",
                "text": text_chunk,
                "metadata": {"page": page_num}
            })
            chunk_id += 1
            
    return chunks

class RAGVectorDB:
    """In-memory ChromaDB vector store for RAG indexing and similarity retrieval."""
    def __init__(self):
        self.client = chromadb.Client()
        self.embedding_fn = EmbeddingFunctionWrapper("all-MiniLM-L6-v2")
        # Create or reset collection
        try:
            self.client.delete_collection("pdf_rag")
        except Exception:
            pass
        self.collection = self.client.create_collection(
            name="pdf_rag",
            embedding_function=self.embedding_fn
        )

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """Indexes text chunks into ChromaDB."""
        if not chunks:
            return
            
        ids = [c["id"] for c in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]
        
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieves top_k relevant chunks for a query."""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        retrieved = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results["distances"][0] if "distances" in results and results["distances"] else [0]*len(docs)
            
            for doc, meta, dist in zip(docs, metas, distances):
                retrieved.append({
                    "text": doc,
                    "page": meta.get("page", 1),
                    "distance": round(dist, 4)
                })
        return retrieved

def generate_answer_with_gemini(query: str, retrieved_chunks: List[Dict[str, Any]], api_key: str) -> str:
    """
    Sends the retrieved context and user query to Google Gemini API to generate an answer with citations.
    """
    genai.configure(api_key=api_key)
    
    # Format context passages
    context_str = ""
    for idx, chunk in enumerate(retrieved_chunks, 1):
        context_str += f"\n--- Excerpt {idx} (Page {chunk['page']}) ---\n{chunk['text']}\n"
        
    prompt = f"""You are an intelligent PDF Q&A assistant powered by RAG (Retrieval-Augmented Generation).

Answer the user's question strictly using the provided context excerpts below. 
If the answer cannot be determined from the excerpts, respond clearly: "I could not find the answer in the provided document."

Always cite the page number(s) in your answer when referencing specific information.

Context Excerpts:
{context_str}

User Question: {query}

Answer:"""

    # Try gemini-1.5-flash or gemini-pro
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        try:
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(prompt)
            return response.text
        except Exception as err:
            return f"Error contacting Gemini API: {str(err)}"
