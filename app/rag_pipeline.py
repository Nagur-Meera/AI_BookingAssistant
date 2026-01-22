"""
RAG Pipeline - PDF ingestion, embedding, and retrieval
"""
import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from app.config import EMBED_MODEL, OPENAI_API_KEY

def ingest_pdfs(uploaded_files):
    """
    Process uploaded PDF files and create a vector store.
    
    Args:
        uploaded_files: List of Streamlit UploadedFile objects
    
    Returns:
        FAISS vector store or None if error
    """
    if not uploaded_files:
        return None
    
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key not configured")
    
    docs = []
    
    for uploaded_file in uploaded_files:
        try:
            # Save uploaded file to temp location
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            # Load PDF
            loader = PyPDFLoader(tmp_path)
            docs.extend(loader.load())
            
            # Clean up temp file
            os.unlink(tmp_path)
            
        except Exception as e:
            print(f"Error processing {uploaded_file.name}: {str(e)}")
            continue
    
    if not docs:
        return None
    
    # Split documents into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(docs)
    
    if not chunks:
        return None
    
    # Create embeddings and vector store
    embeddings = OpenAIEmbeddings(
        model=EMBED_MODEL,
        openai_api_key=OPENAI_API_KEY
    )
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    return vectorstore

def rag_query(vectorstore, query, k=3):
    """
    Query the vector store and return relevant context.
    
    Args:
        vectorstore: FAISS vector store
        query: User's question
        k: Number of documents to retrieve
    
    Returns:
        str: Combined context from retrieved documents
    """
    if vectorstore is None:
        return None
    
    try:
        docs = vectorstore.similarity_search(query, k=k)
        if not docs:
            return None
        
        context = "\n\n".join([doc.page_content for doc in docs])
        return context
    except Exception as e:
        print(f"RAG query error: {str(e)}")
        return None

def create_rag_prompt(context, query):
    """
    Create a RAG-enhanced prompt.
    
    Args:
        context: Retrieved context from documents
        query: User's question
    
    Returns:
        str: Enhanced prompt with context
    """
    if context:
        return f"""Use the following context from uploaded documents to answer the question. 
If the context doesn't contain relevant information, say so and provide a general response.

Context:
{context}

Question: {query}

Answer:"""
    else:
        return query

def get_rag_answer(vectorstore, query, llm_func):
    """
    Get an answer using RAG pipeline.
    
    Args:
        vectorstore: FAISS vector store
        query: User's question  
        llm_func: Function to call LLM with prompt
    
    Returns:
        str: Answer from LLM
    """
    context = rag_query(vectorstore, query)
    prompt = create_rag_prompt(context, query)
    return llm_func(prompt), context is not None
