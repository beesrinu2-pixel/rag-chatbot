import streamlit as st
import os
from utils import extract_text_from_pdf, chunk_pdf_pages, RAGVectorDB, generate_answer_with_gemini

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
        font-size: 2.3rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #64748B;
        margin-bottom: 2rem;
    }
    .stAlert {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📄 Chat with your PDF (RAG Assistant)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Upload a PDF, build a vector index, and ask questions with exact page citations.</div>', unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
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
    
    st.divider()
    st.info("💡 **How it works:**\n1. Upload PDF\n2. Text is split into chunks & embedded into ChromaDB\n3. Your question retrieves top matching passages\n4. Gemini answers with page citations!")

# Initialize session state for vector DB and chat history
if "vector_db" not in st.session_state:
    st.session_state.vector_db = None
if "processed_file" not in st.session_state:
    st.session_state.processed_file = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# File Uploader Section
uploaded_file = st.file_uploader("Upload a PDF document to begin", type=["pdf"])

if uploaded_file is not None:
    # Re-index if a new file is uploaded
    if st.session_state.processed_file != uploaded_file.name:
        with st.spinner("⏳ Extracting text, chunking, and creating vector index..."):
            # 1. Extract text
            pages = extract_text_from_pdf(uploaded_file)
            
            if not pages:
                st.error("❌ Could not extract any readable text from this PDF. Please try another PDF.")
            else:
                # 2. Chunk text
                chunks = chunk_pdf_pages(pages, chunk_size=chunk_size, chunk_overlap=100)
                
                # 3. Embed & Index into ChromaDB
                vector_db = RAGVectorDB()
                vector_db.add_chunks(chunks)
                
                # Save to session state
                st.session_state.vector_db = vector_db
                st.session_state.processed_file = uploaded_file.name
                st.session_state.messages = [] # Reset chat for new file
                
                st.success(f"✅ Successfully indexed **{len(pages)} pages** into **{len(chunks)} searchable vector chunks**!")

# Main Chat Interface
if st.session_state.vector_db is not None:
    st.divider()
    st.subheader("💬 Ask Questions")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
                with st.expander("📌 View Retrieved Source Excerpts"):
                    for src in message["sources"]:
                        st.markdown(f"**Page {src['page']}** (Similarity distance: {src['distance']}):\n> {src['text']}")

    # Accept user prompt
    if prompt := st.chat_input("Ask something about your PDF..."):
        if not api_key_input:
            st.warning("⚠️ Please enter your Google Gemini API Key in the sidebar to get answers.")
        else:
            # Add user message to UI
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate RAG response
            with st.chat_message("assistant"):
                with st.spinner("Searching document & generating answer..."):
                    # 1. Retrieve top chunks
                    retrieved_chunks = st.session_state.vector_db.search(prompt, top_k=top_k)
                    
                    # 2. Generate answer
                    answer = generate_answer_with_gemini(prompt, retrieved_chunks, api_key_input)
                    
                    # Display Answer
                    st.markdown(answer)
                    
                    # Display Source Citations
                    if retrieved_chunks:
                        with st.expander("📌 View Retrieved Source Excerpts"):
                            for src in retrieved_chunks:
                                st.markdown(f"**Page {src['page']}** (Similarity distance: {src['distance']}):\n> {src['text']}")
                    
                    # Save assistant message to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": retrieved_chunks
                    })
else:
    st.info("👆 Please upload a PDF above to start asking questions.")
