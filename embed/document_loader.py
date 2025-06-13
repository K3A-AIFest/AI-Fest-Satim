"""
Document loader module for RAG pipeline.
"""
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from llama_index.core import SimpleDirectoryReader
from llama_index.core.schema import Document

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentLoader:
    """
    Document loader class to load documents from directories and files.
    
    Supports:
    - Loading PDF, TXT, and DOCX files from directories
    - Extracting metadata from documents
    - Adding custom metadata to documents
    """
    
    def __init__(self):
        """Initialize the document loader."""
        pass
    
    def load_from_directory(self, directory_path: str) -> List[Document]:
        """
        Load all supported files from a directory.
        
        Args:
            directory_path: Path to directory containing documents
            
        Returns:
            List of LlamaIndex Document objects
        """
        directory = Path(directory_path)
        
        if not directory.exists():
            logger.warning(f"⚠️  Directory {directory_path} does not exist. Creating it...")
            directory.mkdir(parents=True, exist_ok=True)
            return []
        
        # Count files for logging
        pdf_files = list(directory.glob("*.pdf"))
        txt_files = list(directory.glob("*.txt"))
        docx_files = list(directory.glob("*.docx"))
        
        logger.info(f"📁 Found {len(pdf_files)} PDF files, {len(txt_files)} TXT files, "
                   f"and {len(docx_files)} DOCX files in {directory_path}")
        
        # Use SimpleDirectoryReader to load all supported files
        try:
            loader = SimpleDirectoryReader(
                input_dir=directory_path,
                recursive=True,
                filename_as_id=True,
            )
            documents = loader.load_data()
            
            # Add custom metadata
            for i, doc in enumerate(documents):
                if not hasattr(doc, 'metadata') or not doc.metadata:
                    doc.metadata = {}
                
                doc.metadata.update({
                    "document_index": i,
                    "filename": Path(doc.metadata.get("file_path", "unknown")).name,
                    "file_type": Path(doc.metadata.get("file_path", "unknown")).suffix[1:],
                })
            
            logger.info(f"📄 Total documents loaded: {len(documents)}")
            return documents
            
        except Exception as e:
            logger.error(f"❌ Error loading documents: {e}")
            return []
    
    def load_from_file(self, file_path: str) -> Optional[Document]:
        """
        Load a single file.
        
        Args:
            file_path: Path to the file to load
            
        Returns:
            Document object or None if loading failed
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"❌ File {file_path} does not exist")
                return None
                
            # Use SimpleDirectoryReader to load the file (it handles detecting file type)
            loader = SimpleDirectoryReader(
                input_files=[file_path],
                filename_as_id=True,
            )
            documents = loader.load_data()
            
            if documents:
                doc = documents[0]
                # Add custom metadata
                if not hasattr(doc, 'metadata') or not doc.metadata:
                    doc.metadata = {}
                
                doc.metadata.update({
                    "filename": Path(file_path).name,
                    "file_type": Path(file_path).suffix[1:],
                })
                
                logger.info(f"📄 Loaded file: {file_path}")
                return doc
            else:
                logger.warning(f"⚠️  No content loaded from file: {file_path}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error loading file {file_path}: {e}")
            return None
