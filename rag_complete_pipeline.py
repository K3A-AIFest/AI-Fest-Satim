#!/usr/bin/env python3
"""
Complete RAG System Pipeline - Fixed Version
Regulatory Document Processing with FAISS, LangChain, and Chunking
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Core imports
try:
    import numpy as np
    import faiss
    from sentence_transformers import SentenceTransformer
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.document_loaders import PyPDFLoader, TextLoader
    from langchain.schema import Document
    import pdfplumber
    from tqdm import tqdm
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please run: pip install faiss-cpu sentence-transformers langchain langchain-community pdfplumber PyPDF2 numpy tqdm")
    exit(1)

class CompleteRAGSystem:
    """
    Complete RAG System for Regulatory Documents
    
    Features:
    - Document loading (PDF, TXT)
    - Intelligent chunking with LangChain
    - Sentence Transformers embeddings
    - FAISS vector storage
    - Semantic search
    - Persistence (save/load)
    """
    
    def __init__(self, 
                 embedding_model: str = "all-MiniLM-L6-v2",
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200):
        """
        Initialize the RAG system.
        
        Args:
            embedding_model: HuggingFace model name for embeddings
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.embedding_model_name = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize components
        print(f"🤖 Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        
        print(f"📝 Setting up text splitter (chunk_size={chunk_size}, overlap={chunk_overlap})")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # FAISS components
        self.index: Optional[faiss.Index] = None
        self.documents: List[Dict] = []
        self.is_trained = False
        
        print(f"✅ RAG System initialized (embedding_dim={self.embedding_dim})")
    
    def load_documents(self, directory_path: str) -> List[Document]:
        """
        Load all PDF and TXT files from a directory.
        
        Args:
            directory_path: Path to directory containing documents
            
        Returns:
            List of LangChain Document objects
        """
        documents = []
        directory = Path(directory_path)
        
        if not directory.exists():
            print(f"⚠️  Directory {directory_path} does not exist. Creating it...")
            directory.mkdir(parents=True, exist_ok=True)
            return documents
        
        # Load PDF files
        pdf_files = list(directory.glob("*.pdf"))
        txt_files = list(directory.glob("*.txt"))
        
        print(f"📁 Found {len(pdf_files)} PDF files and {len(txt_files)} TXT files in {directory_path}")
        
        # Process PDF files
        for pdf_file in tqdm(pdf_files, desc="Loading PDFs"):
            try:
                # Try pdfplumber first (better for complex layouts)
                with pdfplumber.open(pdf_file) as pdf:
                    text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n\n"
                
                if text.strip():
                    doc = Document(
                        page_content=text,
                        metadata={
                            "source": str(pdf_file),
                            "filename": pdf_file.name,
                            "file_type": "pdf",
                            "total_pages": len(pdf.pages) if hasattr(pdf, 'pages') else 0
                        }
                    )
                    documents.append(doc)
                    print(f"  ✅ Loaded {pdf_file.name} ({len(text)} characters)")
                else:
                    print(f"  ⚠️  {pdf_file.name} - No text extracted")
                    
            except Exception as e:
                print(f"  ❌ Error loading {pdf_file.name}: {e}")
                # Fallback to PyPDF2
                try:
                    loader = PyPDFLoader(str(pdf_file))
                    docs = loader.load()
                    documents.extend(docs)
                    print(f"  ✅ Loaded {pdf_file.name} with PyPDF2 fallback")
                except Exception as e2:
                    print(f"  ❌ Fallback also failed for {pdf_file.name}: {e2}")
        
        # Process TXT files
        for txt_file in tqdm(txt_files, desc="Loading TXT files"):
            try:
                loader = TextLoader(str(txt_file))
                docs = loader.load()
                documents.extend(docs)
                print(f"  ✅ Loaded {txt_file.name}")
            except Exception as e:
                print(f"  ❌ Error loading {txt_file.name}: {e}")
        
        print(f"📄 Total documents loaded: {len(documents)}")
        return documents
    
    def chunk_documents(self, documents: List[Document]) -> List[Dict]:
        """
        Chunk documents using LangChain's text splitter.
        
        Args:
            documents: List of LangChain Document objects
            
        Returns:
            List of chunk dictionaries with metadata
        """
        chunks = []
        
        print(f"✂️  Chunking {len(documents)} documents...")
        
        for doc_idx, document in enumerate(tqdm(documents, desc="Chunking documents")):
            # Split the document
            text_chunks = self.text_splitter.split_text(document.page_content)
            
            # Create chunk metadata
            for chunk_idx, chunk_text in enumerate(text_chunks):
                chunk_metadata = {
                    "chunk_id": f"doc_{doc_idx}_chunk_{chunk_idx}",
                    "text": chunk_text,
                    "chunk_index": chunk_idx,
                    "document_index": doc_idx,
                    "chunk_length": len(chunk_text),
                    "source": document.metadata.get("source", "unknown"),
                    "filename": document.metadata.get("filename", "unknown"),
                    "file_type": document.metadata.get("file_type", "unknown"),
                }
                
                # Add document-specific metadata
                chunk_metadata.update(document.metadata)
                chunks.append(chunk_metadata)
        
        print(f"📋 Created {len(chunks)} chunks from {len(documents)} documents")
        
        # Show chunking statistics
        if chunks:
            chunk_lengths = [chunk["chunk_length"] for chunk in chunks]
            avg_length = np.mean(chunk_lengths)
            print(f"   Average chunk length: {avg_length:.0f} characters")
            print(f"   Min chunk length: {min(chunk_lengths)}")
            print(f"   Max chunk length: {max(chunk_lengths)}")
        
        return chunks
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings
            
        Returns:
            Numpy array of embeddings
        """
        print(f"🧠 Generating embeddings for {len(texts)} texts...")
        
        # Generate embeddings in batches for memory efficiency
        batch_size = 32
        all_embeddings = []
        
        for i in tqdm(range(0, len(texts), batch_size), desc="Generating embeddings"):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.embedding_model.encode(
                batch,
                convert_to_numpy=True,
                show_progress_bar=False,
                normalize_embeddings=True  # For cosine similarity
            )
            all_embeddings.append(batch_embeddings)
        
        embeddings = np.vstack(all_embeddings).astype('float32')
        print(f"✅ Generated embeddings shape: {embeddings.shape}")
        
        return embeddings
    
    def create_faiss_index(self, embeddings: np.ndarray, chunks: List[Dict]) -> None:
        """
        Create and populate FAISS index.
        
        Args:
            embeddings: Numpy array of embeddings
            chunks: List of chunk metadata dictionaries
        """
        print("🔍 Creating FAISS index...")
        
        # Create index (using cosine similarity via inner product on normalized vectors)
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        
        # Add embeddings to index
        self.index.add(embeddings)
        
        # Store document metadata
        self.documents = chunks
        self.is_trained = True
        
        print(f"✅ FAISS index created with {self.index.ntotal} vectors")
    
    def save_index(self, index_path: str, metadata_path: str) -> None:
        """
        Save FAISS index and metadata to disk.
        
        Args:
            index_path: Path to save FAISS index
            metadata_path: Path to save metadata
        """
        if self.index is None:
            print("❌ No index to save!")
            return
        
        # Create directories
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, index_path)
        
        # Save metadata
        save_data = {
            "documents": self.documents,
            "embedding_model": self.embedding_model_name,
            "embedding_dim": self.embedding_dim,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "total_vectors": self.index.ntotal if self.index else 0
        }
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved FAISS index to: {index_path}")
        print(f"💾 Saved metadata to: {metadata_path}")
    
    def load_index(self, index_path: str, metadata_path: str) -> bool:
        """
        Load FAISS index and metadata from disk.
        
        Args:
            index_path: Path to FAISS index
            metadata_path: Path to metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load FAISS index
            self.index = faiss.read_index(index_path)
            
            # Load metadata
            with open(metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.documents = data["documents"]
            self.embedding_dim = data["embedding_dim"]
            self.is_trained = True
            
            print(f"📂 Loaded FAISS index from: {index_path}")
            print(f"📂 Loaded {len(self.documents)} documents from: {metadata_path}")
            if self.index:
                print(f"📊 Index contains {self.index.ntotal} vectors")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading index: {e}")
            return False
    
    def search(self, query: str, k: int = 5, score_threshold: float = 0.0) -> List[Dict]:
        """
        Search for relevant chunks using semantic similarity.
        
        Args:
            query: Search query string
            k: Number of results to return
            score_threshold: Minimum similarity score
            
        Returns:
            List of search results with metadata and scores
        """
        if self.index is None:
            print("❌ No index loaded! Please create or load an index first.")
            return []
        
        print(f"🔎 Searching for: '{query}'")
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        ).astype('float32')
        
        # Search with proper parameters
        scores, indices = self.index.search(query_embedding, k)
        
        # Prepare results
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx != -1 and score >= score_threshold:
                result = self.documents[idx].copy()
                result['score'] = float(score)
                result['rank'] = i + 1
                results.append(result)
        
        print(f"✅ Found {len(results)} results")
        return results
    
    def build_index_from_directory(self, directory_path: str) -> bool:
        """
        Complete pipeline: load documents, chunk, embed, and index.
        
        Args:
            directory_path: Path to directory containing documents
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load documents
            documents = self.load_documents(directory_path)
            if not documents:
                print("⚠️  No documents found!")
                return False
            
            # Chunk documents
            chunks = self.chunk_documents(documents)
            if not chunks:
                print("❌ No chunks created!")
                return False
            
            # Generate embeddings
            texts = [chunk["text"] for chunk in chunks]
            embeddings = self.generate_embeddings(texts)
            
            # Create FAISS index
            self.create_faiss_index(embeddings, chunks)
            
            print("✅ Index building completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error building index: {e}")
            return False
    
    def add_documents_to_existing_index(self, directory_path: str) -> bool:
        """
        Add new documents to an existing index.
        
        Args:
            directory_path: Path to directory containing new documents
            
        Returns:
            True if successful, False otherwise
        """
        if self.index is None:
            print("❌ No existing index! Use build_index_from_directory instead.")
            return False
        
        try:
            # Load new documents
            new_documents = self.load_documents(directory_path)
            if not new_documents:
                print("⚠️  No new documents found!")
                return False
            
            # Chunk new documents
            new_chunks = self.chunk_documents(new_documents)
            if not new_chunks:
                print("❌ No new chunks created!")
                return False
            
            # Generate embeddings for new chunks
            new_texts = [chunk["text"] for chunk in new_chunks]
            new_embeddings = self.generate_embeddings(new_texts)
            
            # Add to existing index
            if self.index is not None:
                self.index.add(new_embeddings)
                self.documents.extend(new_chunks)
                
                print(f"✅ Added {len(new_chunks)} new chunks to existing index")
                print(f"📊 Total vectors in index: {self.index.ntotal}")
                return True
            else:
                print("❌ Index is None, cannot add documents")
                return False
                
        except Exception as e:
            print(f"❌ Error adding documents to index: {e}")
            return False

def create_sample_documents():
    """Create sample documents for testing."""
    # Create directories
    os.makedirs("policies", exist_ok=True)
    os.makedirs("standards", exist_ok=True)
    
    # Sample policy document
    policy_content = """
    # Information Security Policy
    
    ## 1. Purpose and Scope
    This Information Security Policy establishes the framework for protecting organizational information assets and ensuring compliance with regulatory requirements including ISO 27001 and NIST guidelines.
    
    ## 2. Access Control Requirements
    All users must authenticate using multi-factor authentication (MFA) before accessing sensitive systems. Access rights must be reviewed quarterly and immediately revoked upon termination of employment.
    
    ## 3. Data Classification
    Information must be classified as Public, Internal, Confidential, or Restricted based on sensitivity and impact of unauthorized disclosure.
    
    ## 4. Incident Response
    Security incidents must be reported within 1 hour of discovery to the Security Operations Center (SOC). A formal incident response plan must be activated for all Category 2 and above incidents.
    
    ## 5. Risk Management
    Risk assessments must be conducted annually and whenever significant changes occur to systems or processes. All identified risks must be documented in the corporate risk register.
    """
    
    # Sample standard document
    standard_content = """
    # NIST Cybersecurity Framework Implementation Guide
    
    ## Identify Function
    
    ### Asset Management (ID.AM)
    Organizations must maintain an accurate inventory of all physical devices, systems, software platforms, and applications within the organization.
    
    ### Business Environment (ID.BE)
    The organization's mission, objectives, stakeholders, and activities must be understood and prioritized to enable risk management decisions.
    
    ## Protect Function
    
    ### Access Control (PR.AC)
    Access to physical and logical assets and associated facilities is limited to authorized users, processes, and devices.
    
    Specific requirements:
    - Identity and credentials are issued, managed, verified, revoked, and audited
    - Physical access to assets is managed and protected
    - Remote access is managed with appropriate controls
    
    ### Data Security (PR.DS)
    Information and records (data) are managed consistent with the organization's risk strategy to protect confidentiality, integrity, and availability.
    
    ## Detect Function
    
    ### Anomalies and Events (DE.AE)
    Anomalous activity is detected and the potential impact of events is understood through continuous monitoring.
    """
    
    # Write sample documents
    with open("policies/information_security_policy.txt", "w") as f:
        f.write(policy_content)
    
    with open("standards/nist_cybersecurity_framework.txt", "w") as f:
        f.write(standard_content)
    
    print("📝 Created sample documents:")
    print("  - policies/information_security_policy.txt")
    print("  - standards/nist_cybersecurity_framework.txt")

def main():
    """Main test function demonstrating the complete RAG pipeline."""
    print("🎯 Complete RAG System Test")
    print("=" * 60)
    
    # Create sample documents if none exist
    print("\n1️⃣  Checking for documents...")
    policies_exist = os.path.exists("policies") and any(Path("policies").glob("*"))
    standards_exist = os.path.exists("standards") and any(Path("standards").glob("*"))
    
    if not policies_exist and not standards_exist:
        print("📝 No documents found. Creating sample documents...")
        create_sample_documents()
    
    # Initialize RAG system
    print("\n2️⃣  Initializing RAG system...")
    rag = CompleteRAGSystem(
        embedding_model="all-MiniLM-L6-v2",  # Fast, lightweight model
        chunk_size=500,  # Smaller chunks for testing
        chunk_overlap=100
    )
    
    # Try to load existing index
    index_path = "faiss_store/test_index.faiss"
    metadata_path = "faiss_store/test_metadata.json"
    
    print("\n3️⃣  Checking for existing index...")
    if rag.load_index(index_path, metadata_path):
        print("✅ Loaded existing index!")
    else:
        print("🔨 Building new index...")
        
        # Build index from policies
        if os.path.exists("policies"):
            print("\n📁 Processing policies folder...")
            if not rag.build_index_from_directory("policies"):
                print("❌ Failed to build index from policies")
                return
        
        # Add standards to the same index
        if os.path.exists("standards"):
            print("\n📁 Processing standards folder...")
            if not rag.add_documents_to_existing_index("standards"):
                print("❌ Failed to add standards to index")
                return
        
        # Save the index
        print("\n💾 Saving index...")
        rag.save_index(index_path, metadata_path)
    
    # Test search functionality
    print("\n4️⃣  Testing search functionality...")
    test_queries = [
        "access control requirements",
        "multi-factor authentication",
        "incident response",
        "risk management",
        "data classification",
        "NIST cybersecurity framework"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        results = rag.search(query, k=3, score_threshold=0.1)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"  Result {i} (Score: {result['score']:.3f}):")
                print(f"    📄 Source: {result['filename']}")
                print(f"    🆔 Chunk: {result['chunk_id']}")
                print(f"    📝 Text: {result['text'][:150]}...")
                print()
        else:
            print("  ❌ No results found")
    
    # Display system statistics
    print("\n5️⃣  System Statistics:")
    unique_files = set(doc['filename'] for doc in rag.documents)
    print(f"  📊 Total documents in index: {len(unique_files)}")
    print(f"  📋 Total chunks: {len(rag.documents)}")
    print(f"  🧠 Embedding model: {rag.embedding_model_name}")
    print(f"  📐 Embedding dimension: {rag.embedding_dim}")
    if rag.index:
        print(f"  🔍 FAISS index size: {rag.index.ntotal} vectors")
    
    print("\n✅ RAG System test completed successfully!")
    print("\n🎯 Next steps:")
    print("  - Add your own PDF files to policies/ and standards/ folders")
    print("  - Rerun this script to rebuild the index with your documents")
    print("  - Try different search queries to test retrieval quality")

if __name__ == "__main__":
    main()