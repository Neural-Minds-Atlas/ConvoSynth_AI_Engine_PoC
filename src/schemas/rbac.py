"""RBAC-related schemas."""
from typing import List, Dict, Any
from pydantic import BaseModel


class RBACValidationRequest(BaseModel):
    """Schema for RBAC validation request."""
    userId: str
    requestedDataCategories: List[str]
    requestedDocuments: List[str] = []
    requestedMetrics: List[str] = []
    cycleType: str = "generation"

    class Config:
        json_schema_extra = {
            "example": {
                "userId": "usr_123456",
                "requestedDataCategories": ["financial_data", "operational_data"],
                "requestedDocuments": ["Q3_Financial_Report.pdf"],
                "requestedMetrics": ["revenue", "operating_efficiency"],
                "cycleType": "generation"
            }
        }


class RBACValidationResponse(BaseModel):
    """Schema for RBAC validation response."""
    validationResult: str  # allowed | partially_allowed | denied
    allowedItems: List[str]
    deniedItems: List[str]
    explanation: str
    suggestedAlternatives: List[str]
    professionalMessage: str | None

    class Config:
        json_schema_extra = {
            "example": {
                "validationResult": "partially_allowed",
                "allowedItems": ["operational_data", "operating_efficiency"],
                "deniedItems": ["financial_data", "revenue"],
                "explanation": "User has access to operational data but not financial data",
                "suggestedAlternatives": ["operational_metrics", "productivity_metrics"],
                "professionalMessage": "I understand you'd like financial metrics, but as an Operations Analyst..."
            }
        }
