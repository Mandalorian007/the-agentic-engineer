#!/usr/bin/env python3
"""Helper script to list your blogs and their IDs"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

load_dotenv('.env.local')

def main():
    creds = Credentials(
        token=None,
        refresh_token=os.getenv('BLOGGER_REFRESH_TOKEN'),
        client_id=os.getenv('BLOGGER_CLIENT_ID'),
        client_secret=os.getenv('BLOGGER_CLIENT_SECRET'),
        token_uri='https://oauth2.googleapis.com/token'
    )

    service = build('blogger', 'v3', credentials=creds)
    result = service.blogs().listByUser(userId='self').execute()

    print("=== Your Blogger Blogs ===\n")
    for blog in result.get('items', []):
        print(f"Name: {blog['name']}")
        print(f"ID:   {blog['id']}")
        print(f"URL:  {blog['url']}")
        print()

if __name__ == '__main__':
    main()
