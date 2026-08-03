import streamlit as st
import os
import io
from utils import (
    extract_text_from_pdf,
    fetch_pdf_from_url,
    list_github_repo_pdfs,
    chunk_pdf_pages,
    RAGVectorDB,
    generate_answer_with_gemini
)

# Page configuration
st.set_page_config(
    page_title="PDF Q&A Assistant (RAG)",
    page_icon="📄",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .stButton>button {
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📄 Chat with your PDF (GitHub Integrated RAG)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Connect directly to your GitHub repository files or upload a PDF to build a vector search index.</div>', unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Settings")
    
    api_key_input = st.text_input(
        "Google Gemini API Key",
        type="password",
        help="Get a free key from https://aistudio.google.com/",
        value=os.environ.get("GEMINI_API_KEY", "")
    )
    
    st.divider()
    st.subheader("🔍 RAG Retrieval Settings")
    top_k = st.slider("Top Relevant Excerpts (Top-K)", min_value=1, max_value=8, value=3)
    chunk_size = st.slider("Chunk Size (characters)", min_value=200, max_value=1000, value=500, step=50)

# Initialize Session State
if "vector_db" not in st.session_state:
    st.session_state.vector_db = None
if "active_doc_name" not in st.session_state:
    st.session_state.active_doc_name = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# Data Source Selection Tabs
st.subheader("📂 Choose PDF Source")
source_option = st.radio(
    "Select Document Source:",
    ["🐙 Select from GitHub Repository", "🔗 Direct GitHub / Web PDF URL", "📁 Upload Local File"],
    horizontal=True
)

pdf_file_stream = None
file_identifier = None

if "GitHub Repository" in source_option:
    col1, col2 = st.columns([3, 1])
    with col1:
        repo_input = st.text_input("GitHub Repository (owner/repo):", value="beesrinu2-pixel/rag-chatbot")
    with col2:
        st.write("") # spacing
        st.write("")
        fetch_btn = st.button("🔍 Fetch Repo PDFs", use_container_width=True)

    # Fetch PDFs list from GitHub API
    github_pdfs = list_github_repo_pdfs(repo_input)
    
    if github_pdfs:
        pdf_names = [item["name"] for item in github_pdfs]
        selected_pdf_name = st.selectbox("Select PDF file from GitHub repo:", pdf_names)
        selected_item = next((item for item in github_pdfs if item["name"] == selected_pdf_name), None)
        
        if st.button("🚀 Load & Index Selected GitHub PDF", type="primary"):
            if selected_item and selected_item.get("download_url"):
                with st.spinner(f"Downloading '{selected_pdf_name}' from GitHub and building vector index..."):
                    try:
                        pdf_file_stream = fetch_pdf_from_url(selected_item["download_url"])
                        file_identifier = f"github:{repo_input}:{selected_pdf_name}"
                    except Exception as e:
                        st.error(f"Failed to fetch PDF from GitHub: {str(e)}")
    else:
        st.info("No PDF files found or repo is private/unavailable. Click 'Fetch Repo PDFs' or check the repository path.")

elif "Direct GitHub" in source_option:
    url_input = st.text_input("Enter Direct PDF URL (e.g. raw.githubusercontent.com/...):")
    if st.button("🚀 Fetch & Index PDF from URL", type="primary"):
        if url_input:
            with st.spinner("Downloading PDF from URL and building index..."):
                try:
                    pdf_file_stream = fetch_pdf_from_url(url_input)
                    file_identifier = f"url:{url_input}"
                except Exception as e:
                    st.error(f"Failed to download PDF: {str(e)}")
        else:
            st.warning("Please enter a valid URL.")

else: # Upload Local File
    uploaded_file = st.file_uploader("Upload a PDF file from your computer", type=["pdf"])
    if uploaded_file is not None:
        pdf_file_stream = uploaded_file
        file_identifier = f"upload:{uploaded_file.name}"

# Process & Build Vector Index
if pdf_file_stream is not None and file_identifier is not None:
    if st.session_state.active_doc_name != file_identifier:
        with st.spinner("⏳ Extracting text, chunking, and creating vector index..."):
            pages = extract_text_from_pdf(pdf_file_stream)
            
            if not pages:
                st.error("❌ Could not extract text from this PDF.")
            else:
                chunks = chunk_pdf_pages(pages, chunk_size=chunk_size, chunk_overlap=100)
                vector_db = RAGVectorDB()
                vector_db.add_chunks(chunks)
                
                st.session_state.vector_db = vector_db
                st.session_state.active_doc_name = file_identifier
                st.session_state.messages = []
                
                st.success(f"✅ Successfully indexed **{len(pages)} pages** into **{len(chunks)} vector chunks** from **{file_identifier}**!")

# Main Chat Interface
if st.session_state.vector_db is not None:
    st.divider()
    st.markdown(f"### 💬 Ask Questions about `{st.session_state.active_doc_name.split(':')[-1]}`")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
                with st.expander("📌 View Retrieved Source Excerpts"):
                    for src in message["sources"]:
                        st.markdown(f"**Page {src['page']}** (Distance: {src['distance']}):\n> {src['text']}")

    # Accept user prompt
    if prompt := st.chat_input("Ask something about your PDF..."):
        if not api_key_input:
            st.warning("⚠️ Please enter your Google Gemini API Key in the sidebar.")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Searching document & generating answer..."):
                    retrieved_chunks = st.session_state.vector_db.search(prompt, top_k=top_k)
                    answer = generate_answer_with_gemini(prompt, retrieved_chunks, api_key_input)
                    
                    st.markdown(answer)
                    
                    if retrieved_chunks:
                        with st.expander("📌 View Retrieved Source Excerpts"):
                            for src in retrieved_chunks:
                                st.markdown(f"**Page {src['page']}** (Distance: {src['distance']}):\n> {src['text']}")
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": retrieved_chunks
                    })
