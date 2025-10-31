#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Setup script for RAG-Anything integration."""
import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, description: str):
    """Run shell command with progress reporting."""
    print(f"\n{'='*60}")
    print(f"[SETUP] {description}")
    print(f"{'='*60}\n")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=False,
            text=True
        )
        print(f"[OK] {description} - SUCCESS\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[FAIL] {description} - FAILED")
        print(f"Error: {e}\n")
        return False


def main():
    """Main setup process."""
    print("\n" + "="*60)
    print("ConvoSynth RAG-Anything Setup")
    print("="*60)

    # Step 1: Install RAG-Anything
    print("\n[Step 1] Installing RAG-Anything with all dependencies...")
    print("   This may take 5-10 minutes...")

    if not run_command(
        'pip install "raganything[all]" openai --upgrade',
        "Install RAG-Anything + OpenAI"
    ):
        print("   [WARN] Installation had issues, but continuing...")

    # Step 2: Verify installation
    print("\n[Step 2] Verifying installation...")

    try:
        import raganything
        print(f"[OK] raganything version: {raganything.__version__ if hasattr(raganything, '__version__') else 'installed'}")
    except ImportError:
        print("[FAIL] raganything not found - installation may have failed")
        print("   Try manually: pip install 'raganything[all]'")
        return False

    try:
        import openai
        print(f"[OK] openai version: {openai.__version__}")
    except ImportError:
        print("[FAIL] openai not found")
        return False

    # Step 3: Create required directories
    print("\n[Step 3] Creating required directories...")

    dirs_to_create = [
        "data/rag_storage",
        "data/rag_storage/processed",
        "data/embeddings",
        "data/exports",
        "logs",
    ]

    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"   [OK] Created: {dir_path}")

    # Step 4: Check environment variables
    print("\n[Step 4] Checking environment configuration...")

    from dotenv import load_dotenv
    import os

    load_dotenv()

    required_keys = {
        "ANTHROPIC_API_KEY": "Claude-4 Sonnet",
        "OPENAI_API_KEY": "OpenAI (for embeddings)",
    }

    missing_keys = []
    for key, description in required_keys.items():
        value = os.getenv(key, "")
        if value and value != "your-openai-key-here" and value != "your-nano-banana-key":
            print(f"   [OK] {key} ({description}): configured")
        else:
            print(f"   [WARN] {key} ({description}): NOT SET")
            missing_keys.append(key)

    if missing_keys:
        print(f"\n[WARN] Missing API keys: {', '.join(missing_keys)}")
        print("   Update .env file with your API keys")

    # Step 5: Test RAG-Anything import
    print("\n[Step 5] Testing RAG-Anything initialization...")

    try:
        from raganything import RAGAnything, RAGAnythingConfig
        from raganything.providers.openai import get_openai_embedding_function
        print("   [OK] RAG-Anything core modules imported successfully")

        # Try to create config (without initializing full system)
        config = RAGAnythingConfig(
            working_dir="./data/rag_storage",
            parser="mineru",
            parse_method="auto",
            enable_image_processing=True,
            enable_table_processing=True,
        )
        print("   [OK] RAG-Anything configuration created successfully")

    except Exception as e:
        print(f"   [WARN] Warning: {e}")
        print("   RAG-Anything may need additional configuration")

    # Final summary
    print("\n" + "="*60)
    print("Setup Complete!")
    print("="*60)

    print("\n[Next Steps]")
    print("   1. Update .env with OPENAI_API_KEY")
    print("   2. Run: python run.py")
    print("   3. Test: python test_api.py")
    print("   4. Access API: http://localhost:8000/docs")

    print("\n[Documents to process]")
    financial_samples = Path("data/financial_samples")
    if financial_samples.exists():
        files = list(financial_samples.glob("**/*.pdf"))
        print(f"   Found {len(files)} PDF files in data/financial_samples/")
        print(f"   These will be processed on first API call")
    else:
        print("   No documents found - add PDFs to data/financial_samples/")

    print("\n[OK] RAG-Anything is ready to use!\n")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
