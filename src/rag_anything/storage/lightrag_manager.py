# ============================================================================
# File: rag_anything/storage/lightrag_manager.py
# ============================================================================
"""LightRAG storage management."""

from pathlib import Path
from typing import Optional, Dict, Any
import structlog

logger = structlog.get_logger(__name__)


class LightRAGManager:
    """Manages LightRAG storage and operations."""
    
    def __init__(self, working_dir: Path):
        """Initialize LightRAG manager.
        
        Args:
            working_dir: Working directory for storage
        """
        self.working_dir = Path(working_dir)
        self.logger = logger.bind(component="lightrag_manager")
    
    def check_storage_exists(self) -> bool:
        """Check if LightRAG storage exists.
        
        Returns:
            True if storage exists
        """
        return (
            self.working_dir.exists() and
            (self.working_dir / "kv_store_text_chunks.json").exists()
        )
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics.
        
        Returns:
            Storage statistics
        """
        if not self.check_storage_exists():
            return {"exists": False}
        
        stats = {
            "exists": True,
            "directory": str(self.working_dir),
            "files": []
        }
        
        # List all storage files
        for file_path in self.working_dir.glob("*"):
            if file_path.is_file():
                stats["files"].append({
                    "name": file_path.name,
                    "size": file_path.stat().st_size
                })
        
        return stats
    
    async def clear_storage(self) -> bool:
        """Clear all LightRAG storage.
        
        Returns:
            True if successful
        """
        try:
            import shutil
            
            if self.working_dir.exists():
                shutil.rmtree(self.working_dir)
            
            self.working_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info("storage_cleared")
            return True
            
        except Exception as e:
            self.logger.error("storage_clear_failed", error=str(e))
            return False