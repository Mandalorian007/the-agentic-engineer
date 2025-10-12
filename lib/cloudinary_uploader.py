"""Cloudinary image upload integration"""

import cloudinary
import cloudinary.uploader
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class CloudinaryError(Exception):
    """Cloudinary upload errors"""
    pass


class CloudinaryUploader:
    """Handles image uploads to Cloudinary"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Cloudinary uploader

        Args:
            config: Cloudinary configuration (cloud_name, api_key, api_secret)
        """
        self.config = config

        # Configure Cloudinary
        cloudinary.config(
            cloud_name=config['cloud_name'],
            api_key=config['api_key'],
            api_secret=config['api_secret'],
            secure=True
        )

    def upload_image(
        self,
        image_path: Path,
        public_id: str,
        folder: str = "blog-posts",
        format: str = "webp",
        quality: str = "auto:good"
    ) -> Dict[str, Any]:
        """
        Upload image to Cloudinary

        Args:
            image_path: Local path to image
            public_id: Public ID for the image (without extension)
            folder: Cloudinary folder (will be auto-created if it doesn't exist)
            format: Output format (webp, jpg, png, auto)
            quality: Quality setting (auto, auto:low, auto:good, auto:best, or 1-100)

        Returns:
            Dict with url, secure_url, public_id, format, width, height

        Raises:
            CloudinaryError: On upload failure
        """
        try:
            # Upload with transformations
            # The 'folder' parameter both creates the folder AND sets the public_id prefix
            result = cloudinary.uploader.upload(
                str(image_path),
                folder=folder,
                public_id=public_id,
                format=format,
                quality=quality,
                overwrite=True,
                resource_type="image",
                invalidate=True  # Invalidate CDN cache
            )

            return {
                'url': result['secure_url'],
                'public_id': result['public_id'],
                'format': result['format'],
                'width': result['width'],
                'height': result['height'],
                'bytes': result['bytes'],
                'uploaded_at': datetime.utcnow().isoformat() + 'Z'
            }

        except cloudinary.exceptions.Error as e:
            raise CloudinaryError(f"Failed to upload {image_path}: {e}")
        except Exception as e:
            raise CloudinaryError(f"Unexpected error uploading {image_path}: {e}")

    def upload_post_images(
        self,
        post_dir: Path,
        image_refs: list,
        post_slug: str,
        cached_images: Dict[str, Any],
        image_hashes: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Upload all images for a post (with deduplication)

        Args:
            post_dir: Post directory path
            image_refs: List of image references from markdown
            post_slug: Post slug for folder organization
            cached_images: Existing image mappings from frontmatter
            image_hashes: Current image hashes

        Returns:
            Updated image mappings dict

        Raises:
            CloudinaryError: On upload failure
        """
        image_mappings = {}

        for img_ref in image_refs:
            # Normalize path
            if img_ref.startswith('./'):
                img_ref = img_ref[2:]

            current_hash = image_hashes.get(img_ref)

            # Check if unchanged
            if img_ref in cached_images:
                cached = cached_images[img_ref]
                if cached.get('hash') == current_hash:
                    # Reuse existing mapping
                    image_mappings[img_ref] = cached
                    print(f"   ✓ {img_ref} (cached)")
                    continue

            # Upload new/changed image
            img_path = post_dir / img_ref
            img_name = Path(img_ref).stem  # Filename without extension

            print(f"   → Uploading {img_ref}...")

            # Build folder path: base_folder/post_slug (e.g., "agentic-engineer-blog/hello-world")
            base_folder = self.config.get('folder', 'blog-posts')
            folder_path = f"{base_folder}/{post_slug}"

            result = self.upload_image(
                image_path=img_path,
                public_id=img_name,
                folder=folder_path,
                format=self.config.get('format', 'webp'),
                quality=self.config.get('quality', 'auto:good')
            )

            image_mappings[img_ref] = {
                'url': result['url'],
                'hash': current_hash,
                'uploaded_at': result['uploaded_at'],
                'width': result['width'],
                'height': result['height'],
                'format': result['format']
            }

            print(f"   ✅ {img_ref} → {result['url']}")

        return image_mappings

    def replace_image_urls(
        self,
        markdown_body: str,
        image_mappings: Dict[str, Any]
    ) -> str:
        """
        Replace local image paths with Cloudinary URLs in markdown

        Args:
            markdown_body: Markdown content with local image paths
            image_mappings: Dict mapping local paths to Cloudinary URLs

        Returns:
            Markdown with Cloudinary URLs
        """
        result = markdown_body

        for local_path, mapping in image_mappings.items():
            cloudinary_url = mapping['url']

            # Replace in markdown syntax: ![alt](./path.png)
            normalized_path = local_path if local_path.startswith('./') else f"./{local_path}"
            result = result.replace(f"]({normalized_path})", f"]({cloudinary_url})")
            result = result.replace(f"]({local_path})", f"]({cloudinary_url})")

            # Replace in HTML syntax: <img src="./path.png">
            result = result.replace(f'src="{normalized_path}"', f'src="{cloudinary_url}"')
            result = result.replace(f'src="{local_path}"', f'src="{cloudinary_url}"')
            result = result.replace(f"src='{normalized_path}'", f"src='{cloudinary_url}'")
            result = result.replace(f"src='{local_path}'", f"src='{cloudinary_url}'")

        return result
