"""RBAC (Role-Based Access Control) service."""
from typing import List, Dict, Any

from src.db.models import UserProfile, UserPermissions, AccessibleDocument
from src.db.repositories import DocumentRepository
from src.utils.logger import get_logger

logger = get_logger(__name__)


class RBACService:
    """Service for RBAC validation and enforcement."""

    def __init__(self):
        self.document_repo = DocumentRepository()

    async def validate_data_access(
        self,
        user_profile: UserProfile,
        requested_data_categories: List[str],
        requested_documents: List[str] = None,
        requested_metrics: List[str] = None,
        cycle_type: str = "generation",
    ) -> Dict[str, Any]:
        """Validate if user can access requested data.

        Args:
            user_profile: User's profile with permissions
            requested_data_categories: Data categories requested
            requested_documents: Document names requested
            requested_metrics: Metrics/KPIs requested
            cycle_type: generation or editing

        Returns:
            Validation result dictionary
        """
        permissions = user_profile.permissions
        access_scopes = user_profile.accessScopes
        role = user_profile.role
        department = user_profile.department

        allowed_items = []
        denied_items = []
        suggested_alternatives = []

        # Validate data categories
        for category in requested_data_categories:
            category_lower = category.lower()

            if self._can_access_category(
                category_lower, permissions, access_scopes, role, department
            ):
                allowed_items.append(category)
            else:
                denied_items.append(category)
                # Suggest alternatives
                alternatives = self._get_alternatives(category_lower, permissions, access_scopes)
                suggested_alternatives.extend(alternatives)

        # Validate metrics
        if requested_metrics:
            for metric in requested_metrics:
                metric_category = self._categorize_metric(metric)
                if self._can_access_category(
                    metric_category, permissions, access_scopes, role, department
                ):
                    allowed_items.append(metric)
                else:
                    denied_items.append(metric)

        # Determine validation result
        if not denied_items:
            validation_result = "allowed"
            explanation = "All requested data is within user's access scope"
            professional_message = None
        elif not allowed_items:
            validation_result = "denied"
            explanation = f"User does not have access to requested data. Role: {role}, Department: {department}"
            professional_message = self._create_professional_denial_message(
                user_profile, denied_items, suggested_alternatives
            )
        else:
            validation_result = "partially_allowed"
            explanation = f"Some requested data is outside user's scope. Allowed: {len(allowed_items)}, Denied: {len(denied_items)}"
            professional_message = self._create_professional_partial_message(
                user_profile, allowed_items, denied_items, suggested_alternatives
            )

        # Be more lenient in editing mode
        if cycle_type == "editing" and denied_items:
            logger.info(
                "rbac_editing_mode_lenient",
                user_id=user_profile.name,
                denied_items=denied_items,
                message="Editing mode - being lenient with access"
            )

        logger.info(
            "rbac_validation_complete",
            user_role=role,
            department=department,
            validation_result=validation_result,
            allowed_count=len(allowed_items),
            denied_count=len(denied_items)
        )

        return {
            "validationResult": validation_result,
            "allowedItems": list(set(allowed_items)),
            "deniedItems": list(set(denied_items)),
            "explanation": explanation,
            "suggestedAlternatives": list(set(suggested_alternatives)),
            "professionalMessage": professional_message,
        }

    def _can_access_category(
        self,
        category: str,
        permissions: UserPermissions,
        access_scopes: List[str],
        role: str,
        department: str,
    ) -> bool:
        """Check if user can access a data category."""
        category = category.lower()

        # Financial data
        if any(term in category for term in ["financial", "revenue", "profit", "cost", "budget"]):
            return (
                permissions.viewFinancialData
                or department.lower() == "finance"
                or "executive" in role.lower()
                or "financial" in " ".join(access_scopes).lower()
            )

        # Operational data
        if any(term in category for term in ["operational", "operations", "efficiency", "productivity"]):
            return (
                permissions.viewOperationalData
                or department.lower() == "operations"
                or "operational" in " ".join(access_scopes).lower()
            )

        # HR data
        if any(term in category for term in ["hr", "salary", "employee", "headcount", "compensation"]):
            return (
                permissions.viewHRData
                or department.lower() == "hr"
                or department.lower() == "human resources"
                or "hr" in " ".join(access_scopes).lower()
            )

        # Sales data
        if any(term in category for term in ["sales", "customer", "pipeline", "conversion"]):
            return (
                permissions.viewSalesData
                or department.lower() in ["sales", "marketing"]
                or "sales" in " ".join(access_scopes).lower()
            )

        # Confidential data
        if any(term in category for term in ["confidential", "strategic", "executive"]):
            return (
                permissions.viewConfidentialData
                or "executive" in role.lower()
                or "director" in role.lower()
            )

        # Internal metrics - generally accessible
        if any(term in category for term in ["internal", "metrics", "kpi"]):
            return "analyst" in role.lower() or "lead" in role.lower() or "manager" in role.lower()

        # Default: allow if user has broad access
        return len(access_scopes) > 0

    def _categorize_metric(self, metric: str) -> str:
        """Categorize a metric into a data category."""
        metric_lower = metric.lower()

        if any(term in metric_lower for term in ["revenue", "profit", "cost", "financial"]):
            return "financial_data"
        if any(term in metric_lower for term in ["efficiency", "productivity", "operational"]):
            return "operational_data"
        if any(term in metric_lower for term in ["sales", "customer", "conversion"]):
            return "sales_data"
        if any(term in metric_lower for term in ["headcount", "employee", "salary"]):
            return "hr_data"

        return "internal_metrics"

    def _get_alternatives(
        self,
        denied_category: str,
        permissions: UserPermissions,
        access_scopes: List[str],
    ) -> List[str]:
        """Get accessible alternatives for denied category."""
        alternatives = []

        if "financial" in denied_category and permissions.viewOperationalData:
            alternatives.extend(["operational_efficiency", "productivity_metrics"])

        if "sales" in denied_category and permissions.viewOperationalData:
            alternatives.extend(["operational_performance", "process_metrics"])

        if "hr" in denied_category and permissions.viewOperationalData:
            alternatives.extend(["team_performance", "operational_headcount"])

        # General accessible alternatives
        if permissions.viewOperationalData:
            alternatives.append("operational_data")
        if "internal_metrics" in access_scopes:
            alternatives.append("internal_kpis")

        return alternatives[:3]  # Return top 3

    def _create_professional_denial_message(
        self,
        user_profile: UserProfile,
        denied_items: List[str],
        alternatives: List[str],
    ) -> str:
        """Create professional message for full denial."""
        name = user_profile.name.split()[0] if user_profile.name else "there"
        role = user_profile.role.replace("_", " ").title()
        department = user_profile.department.title()

        denied_str = ", ".join(denied_items[:2])
        if len(denied_items) > 2:
            denied_str += f" and {len(denied_items) - 2} more"

        message = f"I understand you'd like access to {denied_str}, but as a {role} in {department}, "
        message += "your current access scope doesn't include this data. "

        if alternatives:
            alt_str = ", ".join(alternatives[:2])
            message += f"However, I can help you with {alt_str}, which might provide similar insights. "
            message += "Would that work for you?"
        else:
            message += "Please contact your administrator if you need additional access permissions."

        return message

    def _create_professional_partial_message(
        self,
        user_profile: UserProfile,
        allowed_items: List[str],
        denied_items: List[str],
        alternatives: List[str],
    ) -> str:
        """Create professional message for partial access."""
        name = user_profile.name.split()[0] if user_profile.name else "there"

        allowed_str = ", ".join(allowed_items[:2])
        denied_str = ", ".join(denied_items[:2])

        message = f"Good news, {name}! I can include {allowed_str} in your presentation. "
        message += f"However, {denied_str} is outside your current access scope. "

        if alternatives:
            alt_str = ", ".join(alternatives[:2])
            message += f"I can include {alt_str} as an alternative. "

        message += "Shall we proceed with the accessible data?"

        return message

    async def get_accessible_documents(
        self,
        user_profile: UserProfile,
    ) -> List[AccessibleDocument]:
        """Get documents accessible to user based on their profile.

        Args:
            user_profile: User's profile

        Returns:
            List of accessible documents
        """
        department = user_profile.department
        access_scopes = user_profile.accessScopes

        # Get documents from user's department
        dept_docs = await self.document_repo.get_accessible_documents(
            department=department
        )

        # Get documents matching access scopes
        scope_docs = []
        for scope in access_scopes:
            docs = await self.document_repo.get_accessible_documents(
                tags=[scope]
            )
            scope_docs.extend(docs)

        # Combine and deduplicate
        all_docs = {doc.documentId: doc for doc in dept_docs + scope_docs}

        logger.info(
            "accessible_documents_retrieved",
            user_department=department,
            access_scopes=access_scopes,
            document_count=len(all_docs)
        )

        return list(all_docs.values())
