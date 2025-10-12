#!/usr/bin/env python3
"""
One-time script to generate a Blogger API refresh token.
Run this once, then store the refresh token in .env.local
"""

from google_auth_oauthlib.flow import InstalledAppFlow
import json

SCOPES = ['https://www.googleapis.com/auth/blogger']

def main():
    print("=== Blogger API Token Generator ===\n")

    # Check for client_secret.json
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.json',
            scopes=SCOPES
        )
    except FileNotFoundError:
        print("❌ Error: client_secret.json not found")
        print("Download it from Google Cloud Console → Credentials")
        return

    # Run local server for OAuth flow
    print("🌐 Opening browser for authorization...")
    print("   If browser doesn't open, copy the URL from the terminal\n")

    creds = flow.run_local_server(
        port=8080,
        prompt='consent',
        access_type='offline'
    )

    print("\n✅ Authorization successful!\n")

    # Extract credentials
    client_id = creds.client_id
    client_secret = creds.client_secret
    refresh_token = creds.refresh_token

    # Display for .env.local
    print("=== Add these to your .env.local file ===\n")
    print(f"BLOGGER_CLIENT_ID={client_id}")
    print(f"BLOGGER_CLIENT_SECRET={client_secret}")
    print(f"BLOGGER_REFRESH_TOKEN={refresh_token}")
    print("\n" + "="*50)

    # Optional: Save to file for reference
    with open('.credentials.json', 'w') as f:
        json.dump({
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token
        }, f, indent=2)

    print("\n💾 Credentials also saved to .credentials.json")
    print("⚠️  Remember to add both files to .gitignore!\n")

if __name__ == '__main__':
    main()
