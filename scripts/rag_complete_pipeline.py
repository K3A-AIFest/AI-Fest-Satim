import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Union
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Core imports
try:
    import numpy as np
    from tqdm import tqdm
    
    # LlamaIndex imports
    from llama_index.core import Settings, VectorStoreIndex, StorageContext
    from llama_index.core.schema import Document, TextNode
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from llama_index.core.retrievers import VectorIndexRetriever
    from llama_index.core.query_engine import RetrieverQueryEngine
    from llama_index.core.storage.docstore import SimpleDocumentStore
    from llama_index.core.storage.index_store import SimpleIndexStore
    from llama_index.core.storage.storage_context import StorageContext
    

    from llama_index.core import SimpleDirectoryReader
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please run: pip install llama-index numpy tqdm")
    exit(1)
    
    
class LlamaIndexRAGSystem:
    """
    Complete RAG System for Regulatory Documents using LlamaIndex
    
    Features:
    - Document loading (PDF, TXT)
    - Intelligent chunking with LlamaIndex
    - Hugging Face embeddings integration
    - VectorStoreIndex for storage and retrieval
    - Semantic search
    - Persistence (save/load)
    """
    
    def __init__(self, 
                 embedding_model: str = "BAAI/bge-m3",
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
        self.embed_model = HuggingFaceEmbedding(model_name=embedding_model)
        
        # Set global settings for LlamaIndex
        Settings.embed_model = self.embed_model
        Settings.chunk_size = chunk_size
        Settings.chunk_overlap = chunk_overlap
        
        print(f"📝 Setting up text splitter (chunk_size={chunk_size}, overlap={chunk_overlap})")
        self.text_splitter = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        # LlamaIndex components
        self.index = None
        self.documents = []
        self.is_trained = False
        
        print(f"✅ RAG System initialized (using model: {embedding_model})")
    
    def load_documents(self, directory_path: str) -> List[Document]:
        """
        Load all PDF and TXT files from a directory using LlamaIndex.
        
        Args:
            directory_path: Path to directory containing documents
            
        Returns:
            List of LlamaIndex Document objects
        """
        directory = Path(directory_path)
        
        if not directory.exists():
            print(f"⚠️  Directory {directory_path} does not exist. Creating it...")
            directory.mkdir(parents=True, exist_ok=True)
            return []
        
        # Count PDF and TXT files for logging
        pdf_files = list(directory.glob("*.pdf"))
        txt_files = list(directory.glob("*.txt"))
        docx_files = list(directory.glob("*.docx"))
        
        print(f"📁 Found {len(pdf_files)} PDF files, {len(txt_files)} TXT files, and {len(docx_files)} DOCX files in {directory_path}")
        
        # Use SimpleDirectoryReader to load all supported files
        try:
            loader = SimpleDirectoryReader(
                input_dir=directory_path,
                recursive=True,
                filename_as_id=True,
             
            )
            documents = loader.load_data()
            
            # Add some custom metadata
            for i, doc in enumerate(documents):
                if not hasattr(doc, 'metadata') or not doc.metadata:
                    doc.metadata = {}
                
                doc.metadata.update({
                    "document_index": i,
                    "filename": Path(doc.metadata.get("file_path", "unknown")).name,
                    "file_type": Path(doc.metadata.get("file_path", "unknown")).suffix[1:],
                })
            
            print(f"📄 Total documents loaded: {len(documents)}")
            self.documents = documents
            return documents
            
        except Exception as e:
            print(f"❌ Error loading documents: {e}")
            return []
    
    def build_index(self, documents: List[Document] = None) -> bool:
        """
        Process documents and build the vector index.
        
        Args:
            documents: List of LlamaIndex Document objects (optional)
            
        Returns:
            True if successful, False otherwise
        """
        if documents is None:
            documents = self.documents
            
        if not documents:
            print("⚠️  No documents to index!")
            return False
        
        try:
            print(f"✂️  Processing {len(documents)} documents...")
            
            # Parse documents into nodes
            nodes = self.text_splitter.get_nodes_from_documents(documents)
            
            print(f"📋 Created {len(nodes)} nodes/chunks")
            
            # Show chunking statistics
            if nodes:
                chunk_lengths = [len(node.text) for node in nodes]
                avg_length = sum(chunk_lengths) / len(chunk_lengths)
                print(f"   Average chunk length: {avg_length:.0f} characters")
                print(f"   Min chunk length: {min(chunk_lengths)}")
                print(f"   Max chunk length: {max(chunk_lengths)}")
            
            # Build index
            print("🔍 Creating Vector Index...")
            self.index = VectorStoreIndex(nodes)
            self.is_trained = True
            
            print("✅ Index building completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error building index: {e}")
            return False
    
    def save_index(self, persist_dir: str) -> None:
        """
        Save index to disk.
        
        Args:
            persist_dir: Directory to save the index
        """
        if self.index is None:
            print("❌ No index to save!")
            return
        
        try:
            # Create directory
            os.makedirs(persist_dir, exist_ok=True)
            
            # Save index
            self.index.storage_context.persist(persist_dir=persist_dir)
            
            # Save additional metadata
            metadata = {
                "embedding_model": self.embedding_model_name,
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
                "document_count": len(self.documents),
            }
            
            with open(os.path.join(persist_dir, "metadata.json"), 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved index to: {persist_dir}")
            
        except Exception as e:
            print(f"❌ Error saving index: {e}")
    
    def load_index(self, persist_dir: str) -> bool:
        """
        Load index from disk.
        
        Args:
            persist_dir: Directory containing the saved index
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(persist_dir):
                print(f"❌ Directory {persist_dir} does not exist!")
                return False
                
            # Load additional metadata if exists
            metadata_path = os.path.join(persist_dir, "metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    
                self.embedding_model_name = metadata.get("embedding_model", self.embedding_model_name)
                self.chunk_size = metadata.get("chunk_size", self.chunk_size)
                self.chunk_overlap = metadata.get("chunk_overlap", self.chunk_overlap)
                
                # Update embed model if needed
                if self.embedding_model_name != Settings.embed_model.model_name:
                    self.embed_model = HuggingFaceEmbedding(model_name=self.embedding_model_name)
                    Settings.embed_model = self.embed_model

            # Create storage context
            storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
            
            # Use load_index_from_storage instead of VectorStoreIndex.from_storage
            from llama_index.core import load_index_from_storage
            self.index = load_index_from_storage(storage_context, embed_model=self.embed_model)
            self.is_trained = True
            
            print(f"📂 Loaded index from: {persist_dir}")
            print(f"📊 Using embedding model: {self.embedding_model_name}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading index: {e}")
            return False
    
    def search(self, query: str, k: int = 5, similarity_threshold: float = 0.0) -> List[Dict]:
        """
        Search for relevant chunks using semantic similarity.
        
        Args:
            query: Search query string
            k: Number of results to return
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of search results with metadata and scores
        """
        if self.index is None:
            print("❌ No index loaded! Please create or load an index first.")
            return []
        
        print(f"🔎 Searching for: '{query}'")
        
        try:
            # Create retriever
            retriever = VectorIndexRetriever(
                index=self.index,
                similarity_top_k=k,
            )
            
            # Execute query
            query_engine = RetrieverQueryEngine.from_args(retriever)
            results = retriever.retrieve(query)
            
            # Prepare results
            formatted_results = []
            for i, node in enumerate(results):
                score = node.score if hasattr(node, 'score') else 0.0
                
                if score >= similarity_threshold:
                    result = {
                        'text': node.text,
                        'score': float(score) if score is not None else 0.0,
                        'rank': i + 1,
                        'node_id': node.node_id,
                    }
                    
                    # Add metadata
                    if hasattr(node, 'metadata') and node.metadata:
                        result.update(node.metadata)
                    
                    if 'filename' not in result and hasattr(node, 'metadata'):
                        result['filename'] = Path(node.metadata.get('file_path', 'unknown')).name
                        
                    formatted_results.append(result)
            
            print(f"✅ Found {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            print(f"❌ Error during search: {e}")
            return []
    
    def build_index_from_directory(self, directory_path: str) -> bool:
        """
        Complete pipeline: load documents and build index.
        
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
            
            # Build index
            return self.build_index(documents)
            
        except Exception as e:
            print(f"❌ Error building index from directory: {e}")
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
            
            print(f"🔄 Adding {len(new_documents)} documents to existing index...")
            
            # Parse documents into nodes
            new_nodes = self.text_splitter.get_nodes_from_documents(new_documents)
            
            # Add to existing index
            self.index.insert_nodes(new_nodes)
            
            print(f"✅ Added {len(new_nodes)} nodes to existing index")
            return True
                
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
    """Main test function demonstrating the complete RAG pipeline with LlamaIndex."""
    print("🎯 Complete LlamaIndex RAG System Test (Separate DBs)")
    print("=" * 60)

    # Create sample documents if none exist
    print("\n1️⃣  Checking for documents...")
    policies_exist = os.path.exists("./policies") and any(Path("policies").glob("*"))
    standards_exist = os.path.exists("./standards") and any(Path("standards").glob("*"))

    if not policies_exist and not standards_exist:
        print("📝 No documents found. Creating sample documents...")
        create_sample_documents()

    # --- POLICIES ---
    print("\n2️⃣  Initializing LlamaIndex RAG system for POLICIES...")
    rag_policies = LlamaIndexRAGSystem(
        embedding_model="BAAI/bge-m3",
        chunk_size=500,
        chunk_overlap=100
    )
    policies_persist_dir = "llamaindex_store_policies"
    print("\n3️⃣  Checking for existing POLICIES index...")
    if rag_policies.load_index(policies_persist_dir):
        print("✅ Loaded existing POLICIES index!")
    else:
        print("🔨 Building new POLICIES index...")
        if os.path.exists("policies"):
            print("\n📁 Processing policies folder...")
            if not rag_policies.build_index_from_directory("policies"):
                print("❌ Failed to build index from policies")
                return
            print("\n💾 Saving POLICIES index...")
            rag_policies.save_index(policies_persist_dir)
        else:
            print("❌ No policies folder found!")
            return

    # --- STANDARDS ---
    print("\n2️⃣  Initializing LlamaIndex RAG system for STANDARDS...")
    rag_standards = LlamaIndexRAGSystem(
        embedding_model="BAAI/bge-m3",
        chunk_size=500,
        chunk_overlap=100
    )
    standards_persist_dir = "llamaindex_store_standards"
    print("\n3️⃣  Checking for existing STANDARDS index...")
    if rag_standards.load_index(standards_persist_dir):
        print("✅ Loaded existing STANDARDS index!")
    else:
        print("🔨 Building new STANDARDS index...")
        if os.path.exists("standards"):
            print("\n📁 Processing standards folder...")
            if not rag_standards.build_index_from_directory("standards"):
                print("❌ Failed to build index from standards")
                return
            print("\n💾 Saving STANDARDS index...")
            rag_standards.save_index(standards_persist_dir)
        else:
            print("❌ No standards folder found!")
            return

    # Test search functionality for each DB
    print("\n4️⃣  Testing search functionality (POLICIES DB)...")
    test_queries = [
        "access control requirements",
        "multi-factor authentication",
        "incident response",
        "risk management",
        "data classification"
    ]
    for query in test_queries:
        print(f"\n🔍 Query (POLICIES): '{query}'")
        results = rag_policies.search(query, k=3, similarity_threshold=0.1)
        if results:
            for i, result in enumerate(results, 1):
                print(f"  Result {i} (Score: {result.get('score', 0):.3f}):")
                print(f"    📄 Source: {result.get('filename', 'Unknown')}")
                print(f"    🆔 ID: {result.get('node_id', 'Unknown')}")
                print(f"    📝 Text: {result.get('text', '')[:150]}...")
                print()
        else:
            print("  ❌ No results found")

    print("\n4️⃣  Testing search functionality (STANDARDS DB)...")
    test_queries_standards = [
        "NIST cybersecurity framework",
        "asset management",
        "data security",
        "anomalies and events"
    ]
    for query in test_queries_standards:
        print(f"\n🔍 Query (STANDARDS): '{query}'")
        results = rag_standards.search(query, k=3, similarity_threshold=0.1)
        if results:
            for i, result in enumerate(results, 1):
                print(f"  Result {i} (Score: {result.get('score', 0):.3f}):")
                print(f"    📄 Source: {result.get('filename', 'Unknown')}")
                print(f"    🆔 ID: {result.get('node_id', 'Unknown')}")
                print(f"    📝 Text: {result.get('text', '')[:150]}...")
                print()
        else:
            print("  ❌ No results found")

    # Display system statistics
    print("\n5️⃣  System Statistics:")
    print(f"  🧠 Embedding model: {rag_policies.embedding_model_name}")
    print(f"  📐 Chunk size: {rag_policies.chunk_size}")
    print(f"  📏 Chunk overlap: {rag_policies.chunk_overlap}")
    print(f"  📂 Policies index location: {policies_persist_dir}")
    print(f"  📂 Standards index location: {standards_persist_dir}")

    print("\n✅ LlamaIndex RAG System test completed successfully!")
    print("\n🎯 Next steps:")
    print("  - Add your own PDF or text files to policies/ and standards/ folders")
    print("  - Rerun this script to rebuild the index with your documents")
    print("  - Try different search queries to test retrieval quality")

if __name__ == "__main__":
    main()