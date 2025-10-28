# ============================================================================
# File: api/routes/documents.py
# ============================================================================
"""Document upload and management endpoints."""

from typing import List, Optional, Dict, Any
from pathlib import Path
import shutil
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends, BackgroundTasks
from pydantic import BaseModel, Field
import structlog

from src.api.dependencies import get_rag_client
from src.rag_anything.client import RAGAnythingClient
from src.rag_anything.pipeline import DocumentProcessor
from src.rag_anything.storage import DocumentStore, LightRAGManager

logger = structlog.get_logger(__name__)

router = APIRouter()

# Configure upload settings
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".csv", ".xlsx", ".docx", ".md"}


class DocumentUploadResponse(BaseModel):
    """Response for document upload."""
    document_id: str
    filename: str
    size: int
    format: str
    status: str
    message: str


class DocumentIngestionRequest(BaseModel):
    """Request to ingest uploaded documents."""
    document_ids: List[str] = Field(..., description="List of document IDs to ingest")
    model_provider: Optional[str] = Field(
        default=None,
        description="LLM provider for entity extraction: 'ollama', 'cohere', or 'claude'. If not specified, uses server default (from USE_OLLAMA setting)"
    )


class DocumentIngestionResponse(BaseModel):
    """Response for document ingestion."""
    total: int
    successful: int
    failed: int
    skipped: int
    total_time: float
    model_provider: str
    results: List[Dict[str, Any]]


class DocumentListResponse(BaseModel):
    """Response for listing documents."""
    total: int
    documents: List[Dict[str, Any]]


class DocumentDeleteResponse(BaseModel):
    """Response for document deletion."""
    deleted: bool
    document_id: str
    message: str


@router.post("/upload", response_model=List[DocumentUploadResponse])
async def upload_documents(
    files: List[UploadFile] = File(..., description="Documents to upload")
):
    """Upload documents for ingestion.
    
    Supports: PDF, TXT, CSV, XLSX, DOCX, MD
    Max size: 50MB per file
    
    Args:
        files: List of files to upload
        
    Returns:
        List of upload results with document IDs
        
    Raises:
        HTTPException: If file validation fails
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided"
        )
    
    if len(files) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 20 files allowed per upload"
        )
    
    logger.info("documents_upload_started", file_count=len(files))
    
    results = []
    
    for file in files:
        try:
            # Validate file extension
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                results.append(DocumentUploadResponse(
                    document_id="",
                    filename=file.filename,
                    size=0,
                    format=file_ext,
                    status="rejected",
                    message=f"Unsupported format: {file_ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
                ))
                continue
            
            # Read file content
            content = await file.read()
            file_size = len(content)
            
            # Validate file size
            if file_size > MAX_FILE_SIZE:
                results.append(DocumentUploadResponse(
                    document_id="",
                    filename=file.filename,
                    size=file_size,
                    format=file_ext,
                    status="rejected",
                    message=f"File too large: {file_size / (1024*1024):.2f}MB (max: 50MB)"
                ))
                continue
            
            # Generate unique document ID
            doc_id = str(uuid.uuid4())
            
            # Save file
            file_path = UPLOAD_DIR / f"{doc_id}_{file.filename}"
            with open(file_path, "wb") as f:
                f.write(content)
            
            logger.info(
                "document_uploaded",
                document_id=doc_id,
                filename=file.filename,
                size=file_size,
                format=file_ext
            )
            
            results.append(DocumentUploadResponse(
                document_id=doc_id,
                filename=file.filename,
                size=file_size,
                format=file_ext,
                status="uploaded",
                message="File uploaded successfully. Use /ingest to process."
            ))
            
        except Exception as e:
            logger.error("document_upload_failed", filename=file.filename, error=str(e))
            results.append(DocumentUploadResponse(
                document_id="",
                filename=file.filename,
                size=0,
                format="",
                status="error",
                message=f"Upload failed: {str(e)}"
            ))
    
    return results


@router.post("/ingest", response_model=DocumentIngestionResponse)
async def ingest_documents(
    req: DocumentIngestionRequest,
    background_tasks: BackgroundTasks
):
    """Ingest uploaded documents into RAG system with model provider choice.

    This processes documents and makes them searchable using either Cohere or Claude
    for entity extraction and knowledge graph building.

    Args:
        req: Document ingestion request with model_provider
        background_tasks: FastAPI background tasks

    Returns:
        Ingestion results

    Raises:
        HTTPException: If RAG not initialized or ingestion fails
    """
    # Determine model provider
    # If not specified in request, use server's USE_OLLAMA setting
    from src.config.settings import get_settings
    settings = get_settings()

    if req.model_provider:
        model_provider = req.model_provider.lower()
    else:
        # Use server default based on USE_OLLAMA setting
        model_provider = "ollama" if settings.use_ollama else "cohere"

    # Validate model provider
    if model_provider not in ["ollama", "cohere", "claude"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid model_provider: {model_provider}. Must be 'ollama', 'cohere', or 'claude'"
        )

    logger.info(
        "ingestion_model_provider_selected",
        provider=model_provider,
        from_request=req.model_provider is not None,
        server_default="ollama" if settings.use_ollama else "cohere"
    )

    # Create a new RAG client with the specified model provider
    try:
        from src.rag_anything.config import RAGConfig
        rag_config = RAGConfig()
        rag_client = RAGAnythingClient(config=rag_config, model_provider=model_provider)
        await rag_client.initialize()

        logger.info(
            "rag_client_initialized_for_ingestion",
            model_provider=model_provider,
            initialized=rag_client._initialized
        )

    except Exception as e:
        logger.error("rag_client_initialization_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to initialize RAG system with {model_provider}: {str(e)}"
        )

    if not rag_client._initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG system not initialized"
        )
    
    if not req.document_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No document IDs provided"
        )
    
    logger.info("document_ingestion_started", document_count=len(req.document_ids))
    
    # Find uploaded files
    document_paths = []
    for doc_id in req.document_ids:
        found = False
        for file_path in UPLOAD_DIR.glob(f"{doc_id}_*"):
            document_paths.append(file_path)
            found = True
            break
        
        if not found:
            logger.warning("document_not_found", document_id=doc_id)
    
    if not document_paths:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No uploaded documents found for provided IDs"
        )
    
    # Initialize processor
    processor = DocumentProcessor()
    
    # Process documents
    import time
    results = []
    successful = 0
    failed = 0
    skipped = 0
    total_time = 0
    
    for doc_path in document_paths:
        start_time = time.time()
        doc_name = doc_path.name
        
        try:
            # Process based on format
            result = await processor.process(doc_path)
            
            if result.get("use_mineru"):
                # PDF - use MinerU through RAG client
                process_result = await rag_client.process_document(doc_path)
                
                if process_result.get("status") == "success":
                    elapsed = time.time() - start_time
                    total_time += elapsed
                    successful += 1
                    results.append({
                        "document": doc_name,
                        "status": "success",
                        "elapsed": round(elapsed, 2)
                    })
                else:
                    elapsed = time.time() - start_time
                    total_time += elapsed
                    failed += 1
                    results.append({
                        "document": doc_name,
                        "status": "failed",
                        "error": process_result.get("error", "Unknown error"),
                        "elapsed": round(elapsed, 2)
                    })
            else:
                # Other formats - insert text directly
                content = result.get("content")
                
                if content and hasattr(rag_client._rag, 'lightrag') and rag_client._rag.lightrag:
                    await rag_client._rag.lightrag.ainsert(content)
                    elapsed = time.time() - start_time
                    total_time += elapsed
                    successful += 1
                    results.append({
                        "document": doc_name,
                        "status": "success",
                        "elapsed": round(elapsed, 2)
                    })
                else:
                    elapsed = time.time() - start_time
                    total_time += elapsed
                    failed += 1
                    results.append({
                        "document": doc_name,
                        "status": "failed",
                        "error": "Failed to extract content or LightRAG not initialized",
                        "elapsed": round(elapsed, 2)
                    })
        
        except Exception as e:
            elapsed = time.time() - start_time
            total_time += elapsed
            failed += 1
            logger.error("document_ingestion_failed", document=doc_name, error=str(e))
            results.append({
                "document": doc_name,
                "status": "failed",
                "error": str(e),
                "elapsed": round(elapsed, 2)
            })
    
    logger.info(
        "document_ingestion_completed",
        total=len(document_paths),
        successful=successful,
        failed=failed,
        model_provider=model_provider,
        total_time=round(total_time, 2)
    )

    return DocumentIngestionResponse(
        total=len(document_paths),
        successful=successful,
        failed=failed,
        skipped=skipped,
        total_time=round(total_time, 2),
        model_provider=model_provider,
        results=results
    )


@router.get("/list", response_model=DocumentListResponse)
async def list_documents():
    """List all uploaded documents.
    
    Returns:
        List of uploaded documents with metadata
    """
    try:
        documents = []
        
        for file_path in UPLOAD_DIR.glob("*"):
            if file_path.is_file():
                # Extract document ID and original filename
                filename = file_path.name
                parts = filename.split("_", 1)
                
                doc_id = parts[0] if len(parts) > 0 else ""
                original_name = parts[1] if len(parts) > 1 else filename
                
                stat = file_path.stat()
                
                documents.append({
                    "document_id": doc_id,
                    "filename": original_name,
                    "size": stat.st_size,
                    "format": file_path.suffix.lower(),
                    "uploaded_at": stat.st_ctime
                })
        
        # Sort by upload time (newest first)
        documents.sort(key=lambda x: x["uploaded_at"], reverse=True)
        
        return DocumentListResponse(
            total=len(documents),
            documents=documents
        )
    
    except Exception as e:
        logger.error("list_documents_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.delete("/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(document_id: str):
    """Delete an uploaded document.
    
    Note: This only deletes the uploaded file, not from RAG storage.
    Use /admin/storage/clear to clear RAG storage.
    
    Args:
        document_id: Document ID to delete
        
    Returns:
        Deletion result
        
    Raises:
        HTTPException: If document not found
    """
    try:
        # Find and delete the file
        deleted = False
        for file_path in UPLOAD_DIR.glob(f"{document_id}_*"):
            file_path.unlink()
            deleted = True
            logger.info("document_deleted", document_id=document_id, filename=file_path.name)
            break
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found: {document_id}"
            )
        
        return DocumentDeleteResponse(
            deleted=True,
            document_id=document_id,
            message="Document deleted successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("document_deletion_failed", document_id=document_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )