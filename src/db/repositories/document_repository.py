"""Repository for document operations."""
from typing import List, Optional
from datetime import datetime

from app.db.mongodb import get_collection
from app.db.models import AccessibleDocument
from app.utils.logger import get_logger
from app.utils.exceptions import NotFoundException

logger = get_logger(__name__)


class DocumentRepository:
    """Repository for document CRUD operations."""

    def __init__(self):
        self.collection = get_collection("documents")

    async def create_document(
        self,
        document_data: AccessibleDocument
    ) -> AccessibleDocument:
        """Create a new document.

        Args:
            document_data: Document to create

        Returns:
            Created document
        """
        doc_dict = document_data.model_dump()
        doc_dict["createdAt"] = datetime.utcnow()
        doc_dict["updatedAt"] = datetime.utcnow()

        await self.collection.insert_one(doc_dict)

        logger.info(
            "document_created",
            document_id=document_data.documentId,
            document_name=document_data.documentName,
        )

        return document_data

    async def get_document(self, document_id: str) -> Optional[AccessibleDocument]:
        """Get document by ID.

        Args:
            document_id: Document ID

        Returns:
            Document if found, None otherwise
        """
        doc_dict = await self.collection.find_one({"documentId": document_id})
        if doc_dict:
            doc_dict.pop("_id", None)
            return AccessibleDocument(**doc_dict)
        return None

    async def get_accessible_documents(
        self,
        department: Optional[str] = None,
        access_level: Optional[str] = None,
        doc_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[AccessibleDocument]:
        """Get documents with filtering for RBAC.

        Args:
            department: Filter by department
            access_level: Filter by access level
            doc_type: Filter by document type
            tags: Filter by tags

        Returns:
            List of accessible documents
        """
        query = {}
        if department:
            query["department"] = department
        if access_level:
            query["accessLevel"] = access_level
        if doc_type:
            query["docType"] = doc_type
        if tags:
            query["tags"] = {"$in": tags}

        cursor = self.collection.find(query)
        documents = []

        async for doc_dict in cursor:
            doc_dict.pop("_id", None)
            documents.append(AccessibleDocument(**doc_dict))

        return documents

    async def update_document(
        self,
        document_id: str,
        update_data: dict
    ) -> AccessibleDocument:
        """Update document.

        Args:
            document_id: Document ID to update
            update_data: Fields to update

        Returns:
            Updated document

        Raises:
            NotFoundException: If document not found
        """
        update_data["updatedAt"] = datetime.utcnow()

        result = await self.collection.find_one_and_update(
            {"documentId": document_id},
            {"$set": update_data},
            return_document=True,
        )

        if not result:
            raise NotFoundException("Document", document_id)

        result.pop("_id", None)
        logger.info("document_updated", document_id=document_id)
        return AccessibleDocument(**result)

    async def delete_document(self, document_id: str) -> bool:
        """Delete a document.

        Args:
            document_id: Document ID to delete

        Returns:
            True if deleted, False if not found
        """
        result = await self.collection.delete_one({"documentId": document_id})
        deleted = result.deleted_count > 0

        if deleted:
            logger.info("document_deleted", document_id=document_id)

        return deleted

    async def search_documents(
        self,
        search_term: str,
        department: Optional[str] = None,
    ) -> List[AccessibleDocument]:
        """Search documents by name, summary, or tags.

        Args:
            search_term: Term to search for
            department: Optional department filter

        Returns:
            List of matching documents
        """
        query = {
            "$or": [
                {"documentName": {"$regex": search_term, "$options": "i"}},
                {"summary": {"$regex": search_term, "$options": "i"}},
                {"tags": {"$regex": search_term, "$options": "i"}},
                {"topics": {"$regex": search_term, "$options": "i"}},
            ]
        }

        if department:
            query["department"] = department

        cursor = self.collection.find(query).limit(50)
        documents = []

        async for doc_dict in cursor:
            doc_dict.pop("_id", None)
            documents.append(AccessibleDocument(**doc_dict))

        return documents
