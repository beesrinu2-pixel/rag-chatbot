# 📄 Chat with Your PDF — RAG Assistant (Streamlit Web App)

An interactive, production-ready Retrieval-Augmented Generation (RAG) web application that allows you to upload any PDF document, automatically chunks and indexes it into a vector database (ChromaDB), and answers questions with precise page citations using Google Gemini.

---

## 🌟 Key Features
- **100% Zero-Install Online Deployment**: Can be hosted on Streamlit Cloud directly from GitHub.
- **Automatic Text Extraction & Chunking**: Parses PDFs page by page with `pypdf` and splits text using `langchain-text-splitters`.
- **In-Memory Vector Search**: Uses `ChromaDB` and HuggingFace `all-MiniLM-L6-v2` embeddings for fast similarity retrieval.
- **Accurate LLM Generation**: Augments prompts to Google Gemini API to return factual answers with page citations.
- **Transparent Sources**: Inspect exact retrieved document excerpts & similarity scores right inside the UI.

---

## 🚀 Option 1: Deploy Online (No VS Code Needed!)

You can host this app online for free in **3 simple steps**:

1. **Push to GitHub**:
   - Create a new repository on GitHub (e.g., `rag-pdf-chatbot`).
   - Upload all files in this project (`app.py`, `utils.py`, `requirements.txt`, `README.md`).

2. **Deploy to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io/).
   - Click **"New App"** and connect your GitHub repository.
   - Set Main file path to `app.py` and click **Deploy**!

3. **Use the Web App**:
   - Open your app's public URL in any browser.
   - Enter your free Gemini API Key in the sidebar.
   - Upload your PDF and start chatting!

---

## 💻 Option 2: Run Locally (Optional)

If you wish to run it locally on your computer:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch Streamlit dev server
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## ⚙️ Tech Stack & Architecture
- **UI**: Streamlit
- **PDF Parser**: PyPDF
- **Embeddings**: `sentence-transformers` (`all-MiniLM-L6-v2`)
- **Vector DB**: ChromaDB (In-Memory)
- **LLM**: Google Gemini API (`gemini-1.5-flash` / `gemini-pro`)
