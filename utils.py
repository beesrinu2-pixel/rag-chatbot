import io
import requests
from typing import List, Dict, Any
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

class EmbeddingFunctionWrapper(EmbeddingFunction):
    """
    SentenceTransformer wrapper fully compatible with ChromaDB 0.4.x and 0.5.x+
    Implements __call__, embed_query, and embed_documents.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = self.model.encode(list(input))
        return embeddings.tolist()

    def embed_query(self, input: Any) -> Embeddings:
        if isinstance(input, str):
            input_texts = [input]
        else:
            input_texts = list(input)
        embeddings = self.model.encode(input_texts)
        return embeddings.tolist()

    def embed_documents(self, input: Documents) -> Embeddings:
        embeddings = self.model.encode(list(input))
        return embeddings.tolist()

def extract_text_from_pdf(pdf_file) -> List[Dict[str, Any]]:
    """
    Extracts text page by page from an uploaded or downloaded PDF stream.
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

def fetch_pdf_from_url(url: str) -> io.BytesIO:
    """
    Fetches raw bytes of a PDF file from a public URL or GitHub raw content URL.
    """
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return io.BytesIO(response.content)

def list_github_repo_pdfs(repo_name: str, branch: str = "main") -> List[Dict[str, str]]:
    """
    Lists all PDF files in a public GitHub repository using the GitHub API.
    Example repo_name: 'beesrinu2-pixel/rag-chatbot'
    Returns: [{'name': 'doc.pdf', 'download_url': 'https://raw.githubusercontent.com/...'}, ...]
    """
    repo_name = repo_name.strip().strip("/")
    if "github.com/" in repo_name:
        repo_name = repo_name.split("github.com/")[-1].replace(".git", "")
        
    api_url = f"https://api.github.com/repos/{repo_name}/contents?ref={branch}"
    try:
        res = requests.get(api_url, timeout=10)
        res.raise_for_status()
        contents = res.json()
        
        pdf_files = []
        if isinstance(contents, list):
            for item in contents:
                if item.get("type") == "file" and item.get("name", "").endswith(".pdf"):
                    pdf_files.append({
                        "name": item["name"],
                        "download_url": item.get("download_url")
                    })
        return pdf_files
    except Exception as e:
        return []

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
    Sends retrieved context and query to Gemini API to generate an answer with citations.
    Uses dynamic model discovery and fallback.
    """
    genai.configure(api_key=api_key)
    
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

    # Try standard supported Gemini models
    candidate_models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash", "gemini-2.0-flash-exp"]
    
    last_exception = None
    for model_name in candidate_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            if response and hasattr(response, "text") and response.text:
                return response.text
        except Exception as e:
            last_exception = e
            continue

    # Fallback: dynamically list available models for the user's API key
    try:
        available_models = genai.list_models()
        for m in available_models:
            if "generateContent" in getattr(m, "supported_generation_methods", []):
                clean_name = m.name.replace("models/", "")
                try:
                    model = genai.GenerativeModel(clean_name)
                    response = model.generate_content(prompt)
                    if response and hasattr(response, "text") and response.text:
                        return response.text
                except Exception as inner_e:
                    last_exception = inner_e
                    continue
    except Exception as list_err:
        return f"Error contacting Gemini API: {str(list_err)}"
        
    return f"Error contacting Gemini API: {str(last_exception) if last_exception else 'No supported model found.'}"
