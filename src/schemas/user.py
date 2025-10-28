"""User-related schemas."""
from typing import List
from pydantic import BaseModel, EmailStr, Field

from app.db.models import UserPermissions, UserProfile


class UserCreate(BaseModel):
    """Schema for user creation request."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    name: str
    role: str
    department: str
    accessScopes: List[str] = Field(default_factory=list)
    permissions: UserPermissions = Field(default_factory=UserPermissions)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@company.com",
                "password": "SecurePassword123",
                "name": "John Doe",
                "role": "senior_analyst",
                "department": "operations",
                "accessScopes": ["operational_data", "internal_metrics"],
                "permissions": {
                    "viewFinancialData": False,
                    "viewOperationalData": True,
                    "viewHRData": False,
                    "viewSalesData": False,
                    "viewConfidentialData": False
                }
            }
        }


class UserLogin(BaseModel):
    """Schema for user login request."""
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@company.com",
                "password": "SecurePassword123"
            }
        }


class UserResponse(BaseModel):
    """Schema for user response."""
    userId: str
    email: EmailStr
    profile: UserProfile
    isActive: bool

    class Config:
        json_schema_extra = {
            "example": {
                "userId": "usr_123456",
                "email": "john.doe@company.com",
                "profile": {
                    "name": "John Doe",
                    "role": "senior_analyst",
                    "department": "operations",
                    "accessScopes": ["operational_data"],
                    "permissions": {
                        "viewFinancialData": False,
                        "viewOperationalData": True,
                        "viewHRData": False,
                        "viewSalesData": False,
                        "viewConfidentialData": False
                    }
                },
                "isActive": True
            }
        }


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile."""
    name: str | None = None
    role: str | None = None
    department: str | None = None
    accessScopes: List[str] | None = None
    permissions: UserPermissions | None = None


class Token(BaseModel):
    """Schema for authentication token response."""
    accessToken: str
    tokenType: str = "bearer"
    user: UserResponse

    class Config:
        json_schema_extra = {
            "example": {
                "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "tokenType": "bearer",
                "user": {
                    "userId": "usr_123456",
                    "email": "john.doe@company.com",
                    "profile": {
                        "name": "John Doe",
                        "role": "senior_analyst",
                        "department": "operations",
                        "accessScopes": ["operational_data"],
                        "permissions": {}
                    },
                    "isActive": True
                }
            }
        }
