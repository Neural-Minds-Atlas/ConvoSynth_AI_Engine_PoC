"""Example Python client for ConvoSynth Backend API."""
import requests
from typing import Optional, Dict, Any
import json


class ConvoSynthClient:
    """Client for interacting with ConvoSynth Backend API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize client.

        Args:
            base_url: Base URL of the API
        """
        self.base_url = base_url
        self.token: Optional[str] = None
        self.session_id: Optional[str] = None

    def register(
        self,
        email: str,
        password: str,
        name: str,
        role: str,
        department: str,
        access_scopes: list = None,
        permissions: dict = None,
    ) -> Dict[str, Any]:
        """Register a new user.

        Args:
            email: User email
            password: User password
            name: User full name
            role: User role
            department: User department
            access_scopes: List of access scopes
            permissions: Permission dictionary

        Returns:
            Registration response with token
        """
        if access_scopes is None:
            access_scopes = ["operational_data", "internal_metrics"]

        if permissions is None:
            permissions = {
                "viewFinancialData": False,
                "viewOperationalData": True,
                "viewHRData": False,
                "viewSalesData": False,
                "viewConfidentialData": False,
            }

        response = requests.post(
            f"{self.base_url}/api/v1/auth/register",
            json={
                "email": email,
                "password": password,
                "name": name,
                "role": role,
                "department": department,
                "accessScopes": access_scopes,
                "permissions": permissions,
            },
        )
        response.raise_for_status()

        data = response.json()
        self.token = data["accessToken"]

        print(f"✓ Registered user: {data['user']['profile']['name']}")
        print(f"  User ID: {data['user']['userId']}")
        print(f"  Role: {data['user']['profile']['role']}")
        print(f"  Department: {data['user']['profile']['department']}")

        return data

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login user.

        Args:
            email: User email
            password: User password

        Returns:
            Login response with token
        """
        response = requests.post(
            f"{self.base_url}/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        response.raise_for_status()

        data = response.json()
        self.token = data["accessToken"]

        print(f"✓ Logged in: {data['user']['profile']['name']}")

        return data

    def send_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        cycle_type: str = "generation",
    ) -> Dict[str, Any]:
        """Send a message to the conversation agent.

        Args:
            message: User message
            session_id: Optional session ID (creates new if None)
            cycle_type: "generation" or "editing"

        Returns:
            Agent response
        """
        if not self.token:
            raise ValueError("Not authenticated. Call login() or register() first.")

        headers = {"Authorization": f"Bearer {self.token}"}

        payload = {"userMessage": message, "cycleType": cycle_type}

        if session_id:
            payload["sessionId"] = session_id

        endpoint = (
            "/api/v1/conversation/generate"
            if cycle_type == "generation"
            else "/api/v1/conversation/edit"
        )

        response = requests.post(
            f"{self.base_url}{endpoint}", json=payload, headers=headers
        )
        response.raise_for_status()

        data = response.json()

        # Store session ID for subsequent messages
        if not session_id:
            self.session_id = data["sessionId"]

        return data

    def get_session_info(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get session information.

        Args:
            session_id: Session ID (uses stored session_id if None)

        Returns:
            Session information
        """
        if not self.token:
            raise ValueError("Not authenticated")

        sid = session_id or self.session_id
        if not sid:
            raise ValueError("No session ID provided or stored")

        headers = {"Authorization": f"Bearer {self.token}"}

        response = requests.get(
            f"{self.base_url}/api/v1/conversation/session/{sid}", headers=headers
        )
        response.raise_for_status()

        return response.json()

    def get_history(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """Get conversation history.

        Args:
            page: Page number
            page_size: Items per page

        Returns:
            Conversation history
        """
        if not self.token:
            raise ValueError("Not authenticated")

        headers = {"Authorization": f"Bearer {self.token}"}

        response = requests.get(
            f"{self.base_url}/api/v1/conversation/history",
            params={"page": page, "page_size": page_size},
            headers=headers,
        )
        response.raise_for_status()

        return response.json()

    def print_response(self, response: Dict[str, Any]):
        """Pretty print agent response.

        Args:
            response: Agent response dictionary
        """
        print("\n" + "=" * 80)
        print(f"Agent: {response['response']}")
        print("=" * 80)
        print(f"Session ID: {response['sessionId']}")
        print(f"Complete: {response['isComplete']}")
        print(f"Confidence: {response['confidenceScore']:.2f}")
        print(f"State: {response['conversationState']}")

        if response.get("missingInformation"):
            print(f"\nMissing Information: {', '.join(response['missingInformation'])}")

        if response.get("suggestedDocuments"):
            print(f"\nSuggested Documents:")
            for doc in response["suggestedDocuments"]:
                print(f"  - {doc}")

        if response.get("handoffToAgent"):
            print(f"\n→ Handoff to: {response['handoffToAgent']}")

        print("=" * 80 + "\n")


def main():
    """Example usage of ConvoSynth client."""
    print("ConvoSynth Backend API - Example Client\n")

    client = ConvoSynthClient()

    # 1. Register a new user
    print("Step 1: Registering user...")
    try:
        client.register(
            email="demo@example.com",
            password="SecurePassword123",
            name="Demo User",
            role="senior_analyst",
            department="operations",
            access_scopes=["operational_data", "internal_metrics"],
            permissions={
                "viewFinancialData": False,
                "viewOperationalData": True,
                "viewHRData": False,
                "viewSalesData": False,
                "viewConfidentialData": False,
            },
        )
    except requests.HTTPError:
        # User might already exist, try login
        print("User exists, logging in...")
        client.login("demo@example.com", "SecurePassword123")

    # 2. Start a conversation
    print("\n\nStep 2: Starting conversation...")
    result = client.send_message(
        "I need to create a presentation about Q3 operational performance"
    )
    client.print_response(result)

    # 3. Continue conversation
    print("Step 3: Continuing conversation...")
    user_input = input("You: ").strip() or "The presentation is for department leadership"

    result = client.send_message(user_input, session_id=client.session_id)
    client.print_response(result)

    # 4. Another turn
    print("Step 4: Another turn...")
    user_input = (
        input("You: ").strip()
        or "Focus on efficiency improvements and cost savings"
    )

    result = client.send_message(user_input, session_id=client.session_id)
    client.print_response(result)

    # 5. Get session info
    print("\nStep 5: Getting session info...")
    session_info = client.get_session_info()
    print(f"Message Count: {session_info['messageCount']}")
    print(f"Conversation State: {session_info['conversationState']}")

    # 6. Get history
    print("\nStep 6: Getting conversation history...")
    history = client.get_history()
    print(f"Total Conversations: {history['totalCount']}")

    print("\n✓ Example completed successfully!")


if __name__ == "__main__":
    main()
