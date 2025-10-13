#!/usr/bin/env python3
"""
Generate images using OpenAI's GPT-Image-1 API and save as WebP format.

Usage:
    python tools/generate_image.py "modern minimalist illustration of a robot writing code at a desk, blue and purple gradient background, clean tech aesthetic, isometric view" output.webp
    python tools/generate_image.py "sleek futuristic dashboard interface with glowing charts and graphs, dark theme with neon accents, professional tech aesthetic, wide angle view" website/public/blog/2025-10-12-my-post/hero.webp

Tip: More detailed prompts produce better results. Include style, colors, perspective, and mood.
Note: Output is automatically converted to WebP format for optimal web performance.
"""

import argparse
import base64
import os
import sys
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image


def generate_image(prompt: str, output_path: str) -> None:
    """
    Generate an image using DALL-E and save it as WebP format.

    Args:
        prompt: The text prompt to generate the image from
        output_path: Path where the image should be saved (will use .webp extension)
    """
    # Save the current working directory to restore later
    original_cwd = os.getcwd()

    # Load environment variables from .env.local
    env_path = Path('.env.local')
    if env_path.exists():
        load_dotenv(env_path)

    # Get API key from environment
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set", file=sys.stderr)
        print("   Add OPENAI_API_KEY=xxx to .env.local", file=sys.stderr)
        sys.exit(1)

    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)

    print(f"🎨 Generating image with prompt: '{prompt}'")
    print(f"📐 Size: 1024x1024")
    print(f"🤖 Model: gpt-image-1")

    try:
        # Generate the image using GPT-Image-1
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024",
            n=1,
        )

        # Get the image data (gpt-image-1 returns base64 by default)
        image_data = response.data[0]
        print(f"✅ Image generated successfully")

        # Decode the image
        if hasattr(image_data, 'b64_json') and image_data.b64_json:
            # Base64 encoded response
            image_bytes = base64.b64decode(image_data.b64_json)
        elif hasattr(image_data, 'url') and image_data.url:
            # URL response (fallback)
            import requests
            image_response = requests.get(image_data.url)
            image_response.raise_for_status()
            image_bytes = image_response.content
        else:
            raise ValueError("No image data in response")

        # Load image with PIL
        print(f"🔄 Converting to WebP format...")
        img = Image.open(BytesIO(image_bytes))

        # Ensure output path has .webp extension
        output_file = Path(output_path)
        if output_file.suffix.lower() != '.webp':
            output_file = output_file.with_suffix('.webp')

        # Create output directory if it doesn't exist
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Save as WebP with quality 85 (good balance of quality and file size)
        img.save(output_file, 'WEBP', quality=85, method=6)

        final_size = output_file.stat().st_size
        print(f"✅ Image saved to: {output_file}")
        print(f"📊 File size: {final_size / 1024:.1f} KB (WebP format)")

        # Print revised prompt if available
        if hasattr(response.data[0], 'revised_prompt') and response.data[0].revised_prompt:
            print(f"\n📝 Revised prompt used by DALL-E:")
            print(f"   {response.data[0].revised_prompt}")

    except Exception as e:
        print(f"❌ Error generating image: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Always restore the original working directory
        os.chdir(original_cwd)


def main():
    parser = argparse.ArgumentParser(
        description="Generate images using OpenAI's GPT-Image-1 API and save as WebP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Blog post hero image with detailed prompt
  python tools/generate_image.py "modern minimalist illustration of a robot writing code at a desk, blue and purple gradient background, clean tech aesthetic, isometric view" website/public/blog/2025-10-12-my-post/hero.webp

  # Data visualization image
  python tools/generate_image.py "sleek futuristic dashboard with glowing charts and metrics, dark theme with neon blue accents, professional tech aesthetic, wide angle perspective" website/public/blog/2025-10-12-analytics/dashboard.webp

  # Architecture diagram style
  python tools/generate_image.py "clean technical diagram of microservices architecture with connected nodes and data flows, white background, blue and gray color scheme, minimalist flat design" website/public/blog/2025-10-12-architecture/diagram.webp

Tip: More detailed prompts produce better results. Include:
  - Style (minimalist, modern, flat design, realistic, abstract)
  - Colors (blue gradient, warm tones, monochrome, neon accents)
  - Perspective (isometric, top-down, close-up, wide angle)
  - Mood (professional, playful, serious, energetic, futuristic)
  - Subject details (objects, actions, composition, lighting)

Note: Output is automatically converted to WebP format for optimal web performance.
      If you provide a .png extension, it will be changed to .webp automatically.
        """
    )

    parser.add_argument(
        "prompt",
        help="Text prompt describing the image to generate"
    )

    parser.add_argument(
        "output_path",
        help="Path where the generated image should be saved (e.g., output.webp)"
    )

    args = parser.parse_args()

    generate_image(args.prompt, args.output_path)


if __name__ == "__main__":
    main()
