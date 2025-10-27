"""Example usage of the ConvoSynth Multi-Agent System."""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents import AgentOrchestrator
from src.rag_anything.client import RAGAnythingClient


async def example_simple_generation():
    """Example 1: Simple presentation generation without documents."""
    print("=" * 60)
    print("Example 1: Simple Presentation Generation")
    print("=" * 60)

    # Initialize orchestrator
    orchestrator = AgentOrchestrator()
    await orchestrator.initialize()

    # Generate presentation
    result = await orchestrator.run_full_workflow(
        user_request="Create a presentation about Q3 2024 financial performance",
        preferences={
            "theme": "professional",
            "num_slides": 8,
            "audience": "executives"
        }
    )

    # Display results
    if result["success"]:
        print("\n✓ Presentation generated successfully!")
        print(f"  Outline slides: {result['presentation']['outline'].get('total_slides', 0)}")
        print(f"  Content slides: {result['presentation']['content'].get('total_slides', 0)}")
        print(f"  Visualizations: {len(result['presentation'].get('visualizations', []))}")

        # Save HTML
        output_file = "output/simple_presentation.html"
        Path("output").mkdir(exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result["presentation"]["html"])
        print(f"  Saved to: {output_file}")
    else:
        print(f"\n✗ Generation failed: {result.get('error')}")


async def example_with_documents():
    """Example 2: Presentation generation with document upload."""
    print("\n" + "=" * 60)
    print("Example 2: Presentation with Document Context")
    print("=" * 60)

    # Initialize RAG client
    print("\nInitializing RAG client...")
    rag_client = RAGAnythingClient()
    await rag_client.initialize()

    # Process documents (simulated - replace with actual documents)
    print("Processing documents...")
    # Uncomment and add your documents:
    # documents = [
    #     Path("data/q3_report.pdf"),
    #     Path("data/financial_data.xlsx")
    # ]
    # for doc in documents:
    #     await rag_client.process_document(doc)

    # Initialize orchestrator with RAG
    orchestrator = AgentOrchestrator(rag_client=rag_client)
    await orchestrator.initialize()

    # Generate presentation
    result = await orchestrator.run_full_workflow(
        user_request="Create an executive summary of Q3 2024 results highlighting revenue growth and profitability",
        documents=[],  # Add document paths here
        preferences={
            "theme": "corporate",
            "num_slides": 10,
            "audience": "board_of_directors",
            "color_scheme": "blue"
        }
    )

    # Display results
    if result["success"]:
        print("\n✓ Presentation generated successfully!")
        metadata = result["metadata"]

        print(f"\nMetadata:")
        print(f"  Query Intent: {metadata['query_analysis'].get('query_context', {}).get('intent')}")
        print(f"  RAG Sources: {len(metadata.get('rag_sources', []))}")
        print(f"  QA Passed: {metadata['qa_results'].get('validation_passed', False)}")
        print(f"  Accuracy Score: {metadata['qa_results'].get('accuracy_score', 0):.2%}")
        print(f"  Validation Passed: {metadata['validation_results'].get('validation_passed', False)}")
        print(f"  Completeness: {metadata['validation_results'].get('completeness_score', 0):.2%}")

        # Save HTML
        output_file = "output/document_based_presentation.html"
        Path("output").mkdir(exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result["presentation"]["html"])
        print(f"\n  Saved to: {output_file}")
    else:
        print(f"\n✗ Generation failed: {result.get('error')}")


async def example_conversation_workflow():
    """Example 3: Conversational information gathering."""
    print("\n" + "=" * 60)
    print("Example 3: Conversational Workflow")
    print("=" * 60)

    orchestrator = AgentOrchestrator()
    await orchestrator.initialize()

    session_id = "example_user_123"

    # Conversation flow
    messages = [
        "I need to create a presentation",
        "It's about our Q3 financial results",
        "The audience is our executive team",
        "I want 10 slides with a professional theme"
    ]

    print("\nConversation:")
    for user_msg in messages:
        print(f"\nUser: {user_msg}")

        response = await orchestrator.run_conversation_workflow(
            user_message=user_msg,
            session_id=session_id
        )

        print(f"Agent: {response['response']}")

        if response['is_complete']:
            print("\n✓ All information gathered!")

            # Extract gathered information
            info = response['extracted_information']
            print(f"\nExtracted Information:")
            print(f"  Topic: {info.get('presentation_requirements', {}).get('topic')}")
            print(f"  Audience: {info.get('presentation_requirements', {}).get('target_audience')}")
            print(f"  Slides: {info.get('presentation_requirements', {}).get('num_slides')}")

            # Would now proceed to full workflow
            print("\n(Would now proceed to generate presentation...)")
            break


async def example_individual_agent():
    """Example 4: Using individual agents."""
    print("\n" + "=" * 60)
    print("Example 4: Individual Agent Usage")
    print("=" * 60)

    from src.agents import QueryAgent, OutlineAgent, AgentRequest

    # Test Query Agent
    print("\nTesting Query Agent:")
    query_agent = QueryAgent()

    request = AgentRequest(
        user_input="Create a 10-slide presentation about Q3 revenue growth and market expansion"
    )

    response = await query_agent.execute(request)

    if response.success:
        print("✓ Query Analysis Complete")
        print(f"  Intent: {response.output['query_context']['intent']}")
        print(f"  Primary Focus: {response.output['query_context']['primary_focus']}")
        print(f"  Entities: {response.output['entities']}")
        print(f"  Execution Time: {response.metadata['execution_time']:.2f}s")

    # Test Outline Agent
    print("\nTesting Outline Agent:")
    outline_agent = OutlineAgent()

    request = AgentRequest(
        user_input="Q3 Revenue Growth Presentation",
        context={"query_output": response.output}
    )

    outline_response = await outline_agent.execute(request)

    if outline_response.success:
        print("✓ Outline Generation Complete")
        outline = outline_response.output.get("outline", [])
        print(f"  Total Slides: {len(outline)}")
        if outline:
            print(f"  First Slide: {outline[0].get('title')}")
            print(f"  Last Slide: {outline[-1].get('title')}")
        print(f"  Execution Time: {outline_response.metadata['execution_time']:.2f}s")


async def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("ConvoSynth Multi-Agent System - Examples")
    print("=" * 60)

    try:
        # Run examples
        await example_simple_generation()
        # await example_with_documents()  # Uncomment when you have documents
        await example_conversation_workflow()
        await example_individual_agent()

        print("\n" + "=" * 60)
        print("All examples completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run examples
    asyncio.run(main())
