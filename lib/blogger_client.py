"""Blogger API client wrapper"""

import time
from typing import Dict, Any, Optional, Tuple
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class BloggerError(Exception):
    """Blogger API errors"""
    pass


class BloggerClient:
    """Wrapper for Blogger API v3"""

    def __init__(self, credentials: Dict[str, str]):
        """
        Initialize Blogger client

        Args:
            credentials: Dict with client_id, client_secret, refresh_token
        """
        self.credentials = credentials
        self.service = self._build_service()

    def _build_service(self):
        """Build authenticated Blogger API service"""
        try:
            creds = Credentials(
                token=None,
                refresh_token=self.credentials['refresh_token'],
                client_id=self.credentials['client_id'],
                client_secret=self.credentials['client_secret'],
                token_uri='https://oauth2.googleapis.com/token'
            )

            # Refresh to get valid access token
            creds.refresh(Request())

            # Build service
            return build('blogger', 'v3', credentials=creds)

        except Exception as e:
            raise BloggerError(f"Failed to authenticate with Blogger API: {e}")

    def get_post_by_path(self, blog_id: str, path: str) -> Optional[Dict[str, Any]]:
        """
        Get post by URL path

        Args:
            blog_id: Blogger blog ID
            path: URL path (e.g., /2025/10/my-post.html)

        Returns:
            Post dict if found, None otherwise

        Raises:
            BloggerError: On API errors
        """
        try:
            result = self.service.posts().getByPath(
                blogId=blog_id,
                path=path
            ).execute()

            return result

        except HttpError as e:
            if e.resp.status == 404:
                return None
            raise BloggerError(f"Error fetching post by path: {e}")

    def get_post_by_id(self, blog_id: str, post_id: str, view: str = 'READER') -> Optional[Dict[str, Any]]:
        """
        Get post by ID

        Args:
            blog_id: Blogger blog ID
            post_id: Post ID
            view: View type ('READER' for published, 'AUTHOR' for drafts)

        Returns:
            Post dict if found, None otherwise

        Raises:
            BloggerError: On API errors
        """
        try:
            result = self.service.posts().get(
                blogId=blog_id,
                postId=post_id,
                view=view
            ).execute()

            return result

        except HttpError as e:
            if e.resp.status == 404:
                return None
            raise BloggerError(f"Error fetching post by ID: {e}")

    def create_post(
        self,
        blog_id: str,
        title: str,
        content: str,
        labels: list = None,
        is_draft: bool = True,
        published: str = None
    ) -> Dict[str, Any]:
        """
        Create a new blog post

        Args:
            blog_id: Blogger blog ID
            title: Post title
            content: Post HTML content
            labels: List of tags/labels
            is_draft: Whether post is a draft
            published: ISO 8601 datetime string for scheduled publishing

        Returns:
            Created post dict

        Raises:
            BloggerError: On API errors
        """
        post_body = {
            'kind': 'blogger#post',
            'title': title,
            'content': content
        }

        if labels:
            post_body['labels'] = labels

        if published:
            post_body['published'] = published

        try:
            result = self._retry_api_call(
                lambda: self.service.posts().insert(
                    blogId=blog_id,
                    body=post_body,
                    isDraft=is_draft
                ).execute()
            )

            return result

        except HttpError as e:
            raise BloggerError(f"Failed to create post: {e}")

    def update_post(
        self,
        blog_id: str,
        post_id: str,
        title: str = None,
        content: str = None,
        labels: list = None,
        is_draft: bool = None,
        published: str = None
    ) -> Dict[str, Any]:
        """
        Update an existing blog post

        Args:
            blog_id: Blogger blog ID
            post_id: Post ID to update
            title: New title (optional)
            content: New HTML content (optional)
            labels: New list of tags/labels (optional)
            is_draft: Whether post is a draft (optional)
            published: ISO 8601 datetime string for scheduled publishing (optional)

        Returns:
            Updated post dict

        Raises:
            BloggerError: On API errors
        """
        # Fetch current post to get full data (use AUTHOR view to include drafts)
        try:
            current = self.get_post_by_id(blog_id, post_id, view='AUTHOR')
            if not current:
                raise BloggerError(f"Post not found: {post_id}")

            # Update fields
            if title is not None:
                current['title'] = title
            if content is not None:
                current['content'] = content
            if labels is not None:
                current['labels'] = labels
            if published is not None:
                current['published'] = published

            # Use PUT (update) for more reliable updates
            result = self._retry_api_call(
                lambda: self.service.posts().update(
                    blogId=blog_id,
                    postId=post_id,
                    body=current
                ).execute()
            )

            return result

        except HttpError as e:
            raise BloggerError(f"Failed to update post: {e}")

    def detect_post_status(
        self,
        blog_id: str,
        blogger_path: str,
        cached_blogger_id: str = None
    ) -> Tuple[str, Optional[str]]:
        """
        Detect if post exists (CREATE or UPDATE)

        Args:
            blog_id: Blogger blog ID
            blogger_path: Expected URL path for post
            cached_blogger_id: Cached post ID from frontmatter

        Returns:
            Tuple of (status, post_id) where status is 'CREATE' or 'UPDATE'

        Raises:
            BloggerError: On API errors
        """
        # Fast path: Try cached ID with AUTHOR view (includes drafts)
        if cached_blogger_id:
            try:
                post = self.get_post_by_id(blog_id, cached_blogger_id, view='AUTHOR')
                if post:
                    return ('UPDATE', cached_blogger_id)
            except BloggerError:
                pass  # Fall through to path lookup

        # Authoritative: Check by path (only works for published posts)
        post = self.get_post_by_path(blog_id, blogger_path)
        if post:
            return ('UPDATE', post['id'])

        return ('CREATE', None)

    def _retry_api_call(self, api_call, max_attempts=3):
        """
        Retry API call with exponential backoff

        Args:
            api_call: Callable that makes the API call
            max_attempts: Maximum retry attempts

        Returns:
            API call result

        Raises:
            BloggerError: If all retries fail
        """
        for attempt in range(max_attempts):
            try:
                return api_call()

            except HttpError as e:
                # Retry on rate limit or server error
                if e.resp.status in (429, 500, 502, 503, 504):
                    if attempt < max_attempts - 1:
                        delay = 2 ** attempt  # Exponential backoff
                        time.sleep(delay)
                        continue

                raise BloggerError(f"API call failed: {e}")

        raise BloggerError("Max retry attempts exceeded")
