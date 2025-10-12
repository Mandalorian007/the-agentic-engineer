# Google OAuth Setup for Blogger API

Quick guide to set up Google OAuth 2.0 authentication for the Blogger API.

**Time Required**: 15 minutes

---

## 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **New Project** → Name: `blogger-automation` → **Create**
3. Navigate to **APIs & Services** → **Library**
4. Search "Blogger API v3" → Click **Enable**

## 2. Configure OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Select **External** → **Create**
3. Fill in required fields:
   - **App name**: `Blogger Automation`
   - **User support email**: Your email
   - **Developer contact**: Your email
4. Click **Save and Continue**
5. **Scopes page**: Click **Save and Continue** (skip, leave empty)
6. **Test users page**: Click **+ Add Users** → Enter your email → **Add**
7. Click **Save and Continue** → **Back to Dashboard**

## 3. Create OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Application type: **Desktop app**
4. Name: `blogger-cli-client` → **Create**
5. Download the credentials (click ⬇️ icon)
6. Save as `client_secret.json` in project root

## 4. Generate Refresh Token

Run:
```bash
uv run tools/generate_refresh_token.py
```

When the browser opens:
1. Select your Google account
2. Click **Advanced** → **Go to Blogger Automation (unsafe)**
3. Click **Continue** to grant permissions

Copy the output to `.env.local`:
```bash
BLOGGER_CLIENT_ID=xxx.apps.googleusercontent.com
BLOGGER_CLIENT_SECRET=xxx
BLOGGER_REFRESH_TOKEN=xxx
```

## 5. Verify Setup

Run:
```bash
uv run tools/test_auth.py
```

You should see: `✅ All tests passed! Authentication is working.`

---

## Troubleshooting

**"Access blocked: This app's request is invalid"**
- Go to OAuth consent screen → Add your email to Test users → Regenerate token

**"invalid_grant"**
- Run `uv run tools/generate_refresh_token.py` again → Update `.env.local`

**"insufficient_permissions" or "The caller does not have permission"**
- Ensure you're using the Google account that owns/manages the blog
- Check permissions at blogger.com → Settings → Permissions
