"""
Print Edit Payload for Swagger UI Testing
==========================================
This script prints the complete edit payload in JSON format for easy copy-paste into Swagger UI.
"""

import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api.routes.test_outline_edit_payload import (
    EDIT_EXAMPLE_GLOBAL_CONCISE,
    EDIT_EXAMPLE_SINGLE_SLIDE,
    EDIT_EXAMPLE_ADD_DATA,
    EDIT_EXAMPLE_RESTRUCTURE,
    EDIT_EXAMPLE_CHANGE_VISUALS,
    EDIT_EXAMPLE_MINIMAL
)


def print_payload(payload_name: str, payload: dict):
    """Print payload in formatted JSON."""
    print(f"\n{'='*80}")
    print(f"{payload_name}")
    print(f"{'='*80}")
    print("\nCOPY THE JSON BELOW (everything between the --- lines):")
    print("-" * 80)
    print(json.dumps(payload, indent=2))
    print("-" * 80)
    print(f"\nPayload size: {len(json.dumps(payload))} characters\n")


def main():
    """Main function."""
    print("\n🎯 OUTLINE EDIT API - SWAGGER UI TEST PAYLOADS")
    print("=" * 80)
    print("\nAvailable payloads:")
    print("1. EDIT_EXAMPLE_MINIMAL - Quick test with small outline")
    print("2. EDIT_EXAMPLE_GLOBAL_CONCISE - Make entire outline concise (FULL)")
    print("3. EDIT_EXAMPLE_SINGLE_SLIDE - Edit slide 5 specifically (FULL)")
    print("4. EDIT_EXAMPLE_ADD_DATA - Add more data to slides (FULL)")
    print("5. EDIT_EXAMPLE_RESTRUCTURE - Reorder slides (FULL)")
    print("6. EDIT_EXAMPLE_CHANGE_VISUALS - Change visualization types (FULL)")
    
    # Check if user provided argument
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        print("\n" + "=" * 80)
        choice = input("\nEnter your choice (1-6) or 'all' for all payloads: ").strip()
    
    payloads = {
        '1': ('EDIT_EXAMPLE_MINIMAL', EDIT_EXAMPLE_MINIMAL),
        '2': ('EDIT_EXAMPLE_GLOBAL_CONCISE', EDIT_EXAMPLE_GLOBAL_CONCISE),
        '3': ('EDIT_EXAMPLE_SINGLE_SLIDE', EDIT_EXAMPLE_SINGLE_SLIDE),
        '4': ('EDIT_EXAMPLE_ADD_DATA', EDIT_EXAMPLE_ADD_DATA),
        '5': ('EDIT_EXAMPLE_RESTRUCTURE', EDIT_EXAMPLE_RESTRUCTURE),
        '6': ('EDIT_EXAMPLE_CHANGE_VISUALS', EDIT_EXAMPLE_CHANGE_VISUALS)
    }
    
    if choice.lower() == 'all':
        for name, payload in payloads.values():
            print_payload(name, payload)
    elif choice in payloads:
        name, payload = payloads[choice]
        print_payload(name, payload)
    else:
        print(f"\n❌ Invalid choice: {choice}")
        print("Please choose 1-6 or 'all'\n")
        sys.exit(1)
    
    print("\n✅ DONE! Copy the JSON above and paste it into Swagger UI's request body.\n")
    print("📍 Endpoint: POST /api/v1/outline/edit")
    print("📍 Swagger UI: http://localhost:8000/docs#/agents/edit_outline_edit_post\n")


if __name__ == "__main__":
    main()
