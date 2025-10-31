"""Test script for the Conversation Agent API endpoint."""
import requests
import json
import time
from typing import Optional


class ConversationAPIClient:
    """Simple client for testing the Conversation Agent API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize API client.

        Args:
            base_url: Base URL of the API
        """
        self.base_url = base_url
        self.session_id: Optional[str] = None

    def send_message(self, message: str, documents: Optional[list] = None) -> dict:
        """Send a message to the conversation agent.

        Args:
            message: User's message
            documents: Optional list of document paths

        Returns:
            API response dictionary
        """
        url = f"{self.base_url}/api/v1/agents/conversation"

        payload = {
            "message": message,
            "session_id": self.session_id,
            "documents": documents
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()

            data = response.json()

            # Store session ID for continuity
            if not self.session_id:
                self.session_id = data.get("session_id")

            return data

        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise

    def get_session_info(self) -> dict:
        """Get information about current session.

        Returns:
            Session information dictionary
        """
        if not self.session_id:
            return {"error": "No active session"}

        url = f"{self.base_url}/api/v1/agents/conversation/session/{self.session_id}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            raise

    def reset_session(self):
        """Reset the current session."""
        if not self.session_id:
            return {"error": "No active session"}

        url = f"{self.base_url}/api/v1/agents/conversation/reset"

        payload = {"session_id": self.session_id}

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            raise

    def list_sessions(self) -> dict:
        """List all active sessions.

        Returns:
            Dictionary with all sessions
        """
        url = f"{self.base_url}/api/v1/agents/conversation/sessions"

        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            raise


def print_response(response: dict):
    """Pretty print the agent's response.

    Args:
        response: Response dictionary from API
    """
    print("\n" + "="*60)
    print(f"🤖 Agent: {response.get('response')}")
    print("="*60)
    print(f"Session ID: {response.get('session_id')}")
    print(f"Complete: {response.get('is_complete')}")
    print(f"Confidence: {response.get('confidence_score', 0):.1%}")
    print(f"State: {response.get('conversation_state')}")
    print(f"Next Action: {response.get('next_action')}")

    # Show extracted information if available
    extracted = response.get('extracted_information', {})
    if extracted.get('presentation_requirements'):
        print("\n📋 Extracted Information:")
        reqs = extracted['presentation_requirements']
        for key, value in reqs.items():
            if value:
                print(f"  • {key}: {value}")


def interactive_conversation():
    """Run an interactive conversation with the agent."""
    print("\n" + "="*60)
    print("ConvoSynth Conversation Agent - Interactive Test")
    print("="*60)
    print("\nType your messages to chat with the agent.")
    print("Commands:")
    print("  /info    - Show session information")
    print("  /reset   - Reset current session")
    print("  /list    - List all sessions")
    print("  /quit    - Exit")
    print("="*60)

    client = ConversationAPIClient()

    while True:
        # Get user input
        user_input = input("\n👤 You: ").strip()

        if not user_input:
            continue

        # Handle commands
        if user_input == "/quit":
            print("\n👋 Goodbye!")
            break

        elif user_input == "/info":
            info = client.get_session_info()
            print(f"\n📊 Session Info:")
            print(json.dumps(info, indent=2))
            continue

        elif user_input == "/reset":
            result = client.reset_session()
            print(f"\n✓ {result.get('message', 'Session reset')}")
            continue

        elif user_input == "/list":
            sessions = client.list_sessions()
            print(f"\n📋 Active Sessions: {sessions.get('total_sessions', 0)}")
            for session in sessions.get('sessions', []):
                print(f"  • {session['session_id']}: {session['message_count']} messages, "
                      f"Complete: {session['is_complete']}")
            continue

        # Send message to agent
        try:
            response = client.send_message(user_input)
            print_response(response)

            # Check if conversation is complete
            if response.get('is_complete'):
                print("\n✅ Information gathering complete!")
                print("You can now use this information to generate a presentation.")

                choice = input("\nContinue chatting or quit? (c/q): ").strip().lower()
                if choice == 'q':
                    break

        except Exception as e:
            print(f"\n❌ Error: {e}")


def automated_test():
    """Run an automated test conversation."""
    print("\n" + "="*60)
    print("ConvoSynth Conversation Agent - Automated Test")
    print("="*60)

    client = ConversationAPIClient()

    # Simulated conversation
    messages = [
        "I need to create a presentation",
        "It's about Q3 2024 financial results",
        "The audience is our executive team",
        "I want 10 slides with a professional theme",
        "Focus on revenue growth and profitability",
        "I have quarterly reports and financial data available",
        "Yes, that looks perfect!"
    ]

    print("\nStarting automated conversation...\n")

    for i, message in enumerate(messages, 1):
        print(f"\n--- Turn {i} ---")
        print(f"👤 User: {message}")

        try:
            response = client.send_message(message)
            print_response(response)

            # Add delay to be nice to the API
            time.sleep(1)

            # Stop if complete
            if response.get('is_complete'):
                print("\n✅ Conversation complete!")
                break

        except Exception as e:
            print(f"\n❌ Error: {e}")
            break

    # Show final session info
    print("\n" + "="*60)
    print("Final Session Information:")
    print("="*60)

    info = client.get_session_info()
    print(json.dumps(info, indent=2))


def test_api_health():
    """Test if the API is running."""
    print("\n" + "="*60)
    print("Testing API Health")
    print("="*60)

    base_url = "http://localhost:8000"

    try:
        # Test root endpoint
        response = requests.get(base_url)
        response.raise_for_status()
        print("✓ API is running")

        # Test health endpoint
        response = requests.get(f"{base_url}/api/v1/health")
        response.raise_for_status()
        print("✓ Health check passed")

        # Test agents info endpoint
        response = requests.get(f"{base_url}/api/v1/agents/info")
        response.raise_for_status()
        data = response.json()
        print(f"✓ Agents endpoint accessible")
        print(f"  Available agents: {len(data.get('available_agents', []))}")

        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ API not accessible: {e}")
        print("\nMake sure the API is running:")
        print("  python -m uvicorn src.main:app --reload")
        return False


if __name__ == "__main__":
    import sys

    # Test API health first
    if not test_api_health():
        sys.exit(1)

    # Choose mode
    print("\n" + "="*60)
    print("Select Test Mode:")
    print("="*60)
    print("1. Interactive conversation")
    print("2. Automated test")
    print("3. Exit")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        interactive_conversation()
    elif choice == "2":
        automated_test()
    elif choice == "3":
        print("\n👋 Goodbye!")
    else:
        print("\n❌ Invalid choice")
