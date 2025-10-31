# ============================================================================
# File: rag_anything/storage/document_store.py
# ============================================================================
"""Original document storage management."""

from pathlib import Path
from typing import Dict, Any, Optional
import shutil
import structlog

logger = structlog.get_logger(__name__)


class DocumentStore:
    """Manages original document storage."""
    
    def __init__(self, storage_dir: Path):
        """Initialize document store.
        
        Args:
            storage_dir: Directory for document storage
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger.bind(component="document_store")
    
    async def store_document(
        self,
        document_path: Path,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store original document.
        
        Args:
            document_path: Path to document
            metadata: Optional metadata
            
        Returns:
            Document ID
        """
        try:
            # Copy document to storage
            doc_id = document_path.stem
            stored_path = self.storage_dir / document_path.name
            
            shutil.copy2(document_path, stored_path)
            
            self.logger.info("document_stored", 
                           document=document_path.name, 
                           doc_id=doc_id)
            
            return doc_id
            
        except Exception as e:
            self.logger.error("document_store_failed", error=str(e))
            raise
    
    async def get_document(self, doc_id: str) -> Optional[Path]:
        """Retrieve document path.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            Path to document or None
        """
        for file_path in self.storage_dir.glob(f"{doc_id}.*"):
            if file_path.is_file():
                return file_path
        
        return None
    
    def list_documents(self) -> list:
        """List all stored documents.
        
        Returns:
            List of document info
        """
        documents = []
        
        for file_path in self.storage_dir.glob("*"):
            if file_path.is_file():
                documents.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "size": file_path.stat().st_size
                })
        
        return documents