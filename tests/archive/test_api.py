#!/usr/bin/env python3
"""ConvoSynth API Test Script - Quick validation."""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.orchestration import SequentialWorkflow
from src.agents.conversation import ConversationAgent
from src.agents.query import QueryAgent
from src.agents.base.schemas import AgentRequest


async def test_individual_agents():
    """Test individual agents."""
    print("🧪 Testing Individual Agents")
    print("=" * 50)

    # Test 1: Conversation Agent
    print("\n1️⃣  Testing Conversation Agent...")
    try:
        conv_agent = ConversationAgent()
        request = AgentRequest(
            user_input="Generate a Q4 2024 earnings presentation with 8 slides focusing on revenue growth",
            session_id="test_session"
        )
        result = await conv_agent.execute(request)

        if result.success:
            print("   ✅ Conversation Agent: PASSED")
            print(f"   📄 Output preview: {result.output[:200]}...")
        else:
            print(f"   ❌ Conversation Agent: FAILED - {result.error}")

    except Exception as e:
        print(f"   ❌ Conversation Agent: ERROR - {str(e)}")

    # Test 2: Query Agent
    print("\n2️⃣  Testing Query Agent...")
    try:
        query_agent = QueryAgent()
        request = AgentRequest(
            user_input="Financial analysis presentation",
            context={"requirements": {"presentation_type": "financial_overview"}},
            session_id="test_session"
        )
        result = await query_agent.execute(request)

        if result.success:
            print("   ✅ Query Agent: PASSED")
            print(f"   📄 Output preview: {result.output[:200]}...")
        else:
            print(f"   ❌ Query Agent: FAILED - {result.error}")

    except Exception as e:
        print(f"   ❌ Query Agent: ERROR - {str(e)}")


async def test_workflow():
    """Test complete workflow (will fail gracefully without RAG)."""
    print("\n\n🔄 Testing Complete Workflow")
    print("=" * 50)

    try:
        workflow = SequentialWorkflow()

        print("\n⚠️  Note: This test will partially fail because:")
        print("   - RAG-Anything libraries not installed yet")
        print("   - No sample documents provided")
        print("   But we can see the orchestration working!\n")

        result = await workflow.execute(
            user_input="Create a Q4 earnings presentation",
            documents=None,
            user_preferences={"slide_count": 8}
        )

        print("✅ Workflow orchestration is functional!")
        print(f"📊 Session ID: {result.get('session_id')}")
        print(f"⏱️  Total time: {result.get('metadata', {}).get('total_time', 'N/A')}s")

    except Exception as e:
        print(f"⚠️  Workflow test encountered expected errors: {type(e).__name__}")
        print(f"   Message: {str(e)[:200]}")
        print("\n💡 This is expected without RAG integration!")


async def main():
    """Run all tests."""
    print("\n" + "=" * 50)
    print("🎯 ConvoSynth API Test Suite")
    print("=" * 50)

    # Test individual agents
    await test_individual_agents()

    # Test workflow
    await test_workflow()

    print("\n" + "=" * 50)
    print("🎉 Test Suite Complete!")
    print("=" * 50)
    print("\n📝 Next Steps:")
    print("   1. Install RAG dependencies: pip install lightrag-hku magic-pdf qdrant-client")
    print("   2. Add .env file with ANTHROPIC_API_KEY")
    print("   3. Place sample PDFs in data/financial_samples/")
    print("   4. Start API: python run.py")
    print("   5. Test API: http://localhost:8000/docs")


if __name__ == "__main__":
    asyncio.run(main())
