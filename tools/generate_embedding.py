#!/usr/bin/env python3
"""
Generate vector embeddings for blog posts using OpenAI API.

Usage:
    # Process single post
    uv run tools/generate_embedding.py website/content/posts/2025-10-12-my-post.mdx

    # Process all posts
    uv run tools/generate_embedding.py

This script:
1. Reads MDX file(s) content
2. Generates embedding using OpenAI text-embedding-3-small (768 dimensions)
3. Stores embeddings in a single JSON file: website/content/embeddings.json
"""

import sys
import os
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import yaml

# Load environment variables from .env.local
env_path = Path('.env.local')
if env_path.exists():
    load_dotenv(env_path)

# Constants
POSTS_DIR = Path("website/content/posts")
EMBEDDINGS_FILE = Path("website/content/embeddings.json")
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536  # Full dimensions (can reduce to 768 later if needed)


def generate_embedding(text: str) -> list[float]:
    """Generate embedding vector for given text."""
    # Get API key from environment
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set", file=sys.stderr)
        print("   Add OPENAI_API_KEY=xxx to .env.local", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
        dimensions=EMBEDDING_DIMENSIONS
    )

    return response.data[0].embedding


def load_embeddings() -> dict:
    """Load existing embeddings from JSON file."""
    if EMBEDDINGS_FILE.exists():
        with open(EMBEDDINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_embeddings(embeddings: dict) -> None:
    """Save embeddings to JSON file."""
    # Ensure directory exists
    EMBEDDINGS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(EMBEDDINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(embeddings, f, indent=2)


def process_mdx_file(mdx_path: Path, embeddings: dict) -> bool:
    """
    Process a single MDX file: generate embedding and store in JSON.
    Returns True if successful, False otherwise.
    """
    try:
        slug = mdx_path.stem  # e.g., "2025-10-12-my-post"
        print(f"\n📄 Processing: {slug}")

        # Read file
        with open(mdx_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split frontmatter and content
        if not content.startswith('---'):
            print(f"⚠️  Skipping {slug}: No frontmatter found")
            return False

        parts = content.split('---', 2)
        if len(parts) < 3:
            print(f"⚠️  Skipping {slug}: Invalid frontmatter format")
            return False

        frontmatter_text = parts[1]
        body_content = parts[2]

        # Parse frontmatter
        frontmatter = yaml.safe_load(frontmatter_text)

        # Check if embedding already exists in JSON
        if slug in embeddings and embeddings[slug]:
            print(f"✓ Embedding already exists, skipping")
            return True

        # Combine title + description + content for embedding
        text_for_embedding = f"{frontmatter.get('title', '')}\n{frontmatter.get('description', '')}\n{body_content}"

        print(f"🔄 Generating embedding for '{frontmatter.get('title', slug)}'...")

        # Generate embedding
        embedding = generate_embedding(text_for_embedding)

        print(f"✅ Generated {len(embedding)}-dimensional embedding")

        # Add embedding to dictionary
        embeddings[slug] = embedding

        return True

    except Exception as e:
        print(f"❌ Error processing {mdx_path.name}: {e}")
        return False


def main():
    # Load existing embeddings
    print(f"📂 Loading embeddings from {EMBEDDINGS_FILE}")
    embeddings = load_embeddings()
    print(f"✓ Found {len(embeddings)} existing embeddings")

    # Check if specific file provided
    if len(sys.argv) == 2:
        # Process single file
        mdx_path = Path(sys.argv[1])

        if not mdx_path.exists():
            print(f"❌ Error: File not found: {mdx_path}")
            sys.exit(1)

        success = process_mdx_file(mdx_path, embeddings)

        if success:
            # Save embeddings
            save_embeddings(embeddings)
            print(f"\n💾 Saved embeddings to {EMBEDDINGS_FILE}")

        sys.exit(0 if success else 1)

    elif len(sys.argv) == 1:
        # Process all files
        mdx_files = sorted(POSTS_DIR.glob("*.mdx"))

        if not mdx_files:
            print(f"❌ No MDX files found in {POSTS_DIR}")
            sys.exit(1)

        print(f"🔍 Found {len(mdx_files)} blog posts")
        print("=" * 60)

        success_count = 0
        error_count = 0

        for mdx_file in mdx_files:
            result = process_mdx_file(mdx_file, embeddings)
            if result:
                success_count += 1
            else:
                error_count += 1

        # Save embeddings
        save_embeddings(embeddings)

        print("\n" + "=" * 60)
        print(f"✅ Successfully processed: {success_count}")
        if error_count > 0:
            print(f"❌ Errors: {error_count}")
        print(f"💾 Embeddings stored in {EMBEDDINGS_FILE}")

    else:
        print("Usage:")
        print("  # Process single post")
        print("  uv run tools/generate_embedding.py website/content/posts/2025-10-12-my-post.mdx")
        print("")
        print("  # Process all posts")
        print("  uv run tools/generate_embedding.py")
        sys.exit(1)


if __name__ == '__main__':
    main()
