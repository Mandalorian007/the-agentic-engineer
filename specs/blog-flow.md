# Blog Automation: Build and Publish Flow

## Executive Summary

Clean workflow for building and publishing blog posts to Google Blogger:
- `uv build.py <post-dir>` - Validates and previews (no external changes)
- `uv publish.py <post-dir>` - Publishes with intelligent image handling and update detection

Design emphasizes **idempotency**, **path-based duplicate prevention**, and **convention over configuration**.

---

## Design Principles

### 1. Idempotency
- Running publish multiple times is safe
- No duplicate posts or image uploads
- Uses content hashing for change detection

### 2. Separation of Concerns
- **Build**: Validates, previews - NO external mutations
- **Publish**: Uploads images, creates/updates posts, modifies frontmatter

### 3. Path-Based Update Detection
- Directory name (e.g., `2025-10-12-my-post`) is source of uniqueness
- Maps to Blogger URL path `/2025/10/my-post.html`
- `blogger_id` in frontmatter is performance cache only
- Prevents accidental duplicates

### 4. Image Efficiency
- SHA-256 hash-based change detection
- Never upload unchanged images
- Persistent URL mappings in frontmatter

### 5. Convention Over Configuration
- Single required parameter: post directory path
- No flags or options needed
- Standard file locations (`blog-config.yaml`, `.env`)
- Directory naming convention: `YYYY-MM-DD-slug`

---

## Command Interface

### Build

```bash
uv build.py posts/2025-10-12-my-post/
```

Validates markdown, checks images, generates preview HTML. No external API calls or file modifications.

### Publish

```bash
uv publish.py posts/2025-10-12-my-post/
```

Uploads images to Cloudinary, creates/updates Blogger post, saves metadata to frontmatter.

---

## User Flow Example

```bash
# 1. Create post
mkdir -p posts/2025-10-12-my-first-post
cat > posts/2025-10-12-my-first-post/post.md <<EOF
---
title: "My First Post"
date: 2025-10-12T10:00:00Z
tags: [tutorial, python]
status: draft
---

# My First Post
Content with ![diagram](./diagram.png)
EOF

# 2. Validate
uv build.py posts/2025-10-12-my-first-post/
# Output: ✓ Valid, ready to publish as NEW post

# 3. Publish
uv publish.py posts/2025-10-12-my-first-post/
# Output: ✓ Published successfully as DRAFT
#         Post URL: https://my-blog.blogspot.com/2025/10/my-first-post.html
```

Post frontmatter is automatically updated:
```yaml
---
title: "My First Post"
blogger_id: "1234567890123456789"  # Added by publish
date: 2025-10-12T10:00:00Z
updated: 2025-10-12T10:15:23Z      # Added by publish
tags: [tutorial, python]
status: draft
images:                             # Added by publish
  ./diagram.png:
    url: "https://res.cloudinary.com/.../my-first-post/diagram.png"
    hash: "sha256:a1b2c3d4..."
    uploaded_at: "2025-10-12T10:15:20Z"
---
```

---

## Build Process

**Purpose**: Validation before publishing. Catches errors without making external calls.

**Actions**:
1. Validate post structure and frontmatter
2. Parse markdown, extract image references
3. Compute image hashes, compare with cached mappings
4. Generate HTML preview with local image paths
5. Report: NEW or UPDATE, images to upload, validation status

**Exit Codes**:
- `0`: Valid, ready to publish
- `1`: Validation failed

---

## Publish Process

```
1. VALIDATE        → Run build checks, fail fast
2. LOAD CONFIG     → blog-config.yaml + .env credentials
3. DETECT STATUS   → Path-based lookup (CREATE or UPDATE)
4. PROCESS IMAGES  → Hash check → Upload if new/changed
5. CONVERT TO HTML → Replace image paths with Cloudinary URLs
6. CALL BLOGGER    → POST (create) or PATCH (update)
7. UPDATE FRONTMATTER → Save blogger_id, images, timestamps
8. REPORT SUCCESS
```

### Critical Implementation Details

#### Step 3: Post Detection Algorithm

```python
def detect_post_status(frontmatter, post_directory, blogger_client, blog_id):
    # Derive expected URL from directory name
    # "2025-10-12-my-post" → "/2025/10/my-post.html"
    expected_path = derive_blogger_path(post_directory)

    # Fast path: Try cached blogger_id
    cached_id = frontmatter.get('blogger_id')
    if cached_id:
        try:
            blogger_client.get_post(blog_id, cached_id)
            return UPDATE, cached_id
        except NotFoundError:
            pass  # Fall through to path lookup

    # Authoritative: Check by path
    try:
        post = blogger_client.get_post_by_path(blog_id, expected_path)
        return UPDATE, post['id']
    except NotFoundError:
        return CREATE, None

def derive_blogger_path(post_directory):
    """2025-10-12-my-post → /2025/10/my-post.html"""
    dir_name = Path(post_directory).name
    match = re.match(r'(\d{4})-(\d{2})-(\d{2})-(.+)', dir_name)
    if not match:
        raise ValidationError(f"Directory must match: YYYY-MM-DD-slug")
    year, month, _, slug = match.groups()
    return f"/{year}/{month}/{slug}.html"
```

**Why Path-Based?**
- Directory names are naturally unique in git
- Prevents duplicates when markdown files are copied
- Robust if frontmatter is lost or corrupted
- `blogger_id` becomes optional performance cache

#### Step 4: Image Processing Algorithm

```python
def process_images(markdown_content, frontmatter, post_slug):
    image_refs = extract_image_references(markdown_content)
    existing = frontmatter.get('images', {})
    image_mapping = {}

    for image_path in image_refs:
        current_hash = compute_sha256(image_path)

        # Check if unchanged
        if image_path in existing:
            if existing[image_path]['hash'] == current_hash:
                image_mapping[image_path] = existing[image_path]
                continue  # Skip upload

        # Upload new/changed image
        optimized = optimize_image(image_path)
        url = cloudinary.upload(
            optimized,
            public_id=f"{post_slug}/{Path(image_path).name}",
            format="webp",
            quality="auto:good"
        )

        image_mapping[image_path] = {
            'url': url,
            'hash': current_hash,
            'uploaded_at': datetime.utcnow().isoformat() + 'Z'
        }

    return image_mapping

def compute_sha256(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return f"sha256:{sha256.hexdigest()}"
```

**Why SHA-256?**
- Detects any byte-level change in image
- Collision probability negligible
- Fast computation on modern hardware

#### Step 6: Blogger API Calls

```python
# CREATE
POST /blogs/{blogId}/posts/
{
  "kind": "blogger#post",
  "title": "Post Title",
  "content": "<html>",
  "labels": ["tag1", "tag2"]
}

# UPDATE
PATCH /blogs/{blogId}/posts/{postId}
{
  "title": "Updated Title",
  "content": "<html>",
  "labels": ["tag1", "tag2"]
}
```

Use exponential backoff for rate limiting (429) and server errors (500).

#### Step 7: Frontmatter Update

Update atomically using temp file + rename:
```python
def atomic_write(file_path, content):
    temp_fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(file_path))
    try:
        with os.fdopen(temp_fd, 'w') as f:
            f.write(content)
        shutil.move(temp_path, file_path)  # Atomic on Unix
    except:
        os.remove(temp_path)
        raise
```

---

## Configuration

### blog-config.yaml
```yaml
blog_name: "Agentic Engineer Blog"
blogger_blog_id: "1234567890"
image_optimization:
  max_width: 1200
  quality: 85
  convert_to_webp: true
```

### .env (never commit!)
```bash
BLOGGER_CLIENT_ID=your-client-id.apps.googleusercontent.com
BLOGGER_CLIENT_SECRET=your-client-secret
BLOGGER_REFRESH_TOKEN=your-refresh-token

CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

### Loading Logic
```python
def load_config():
    load_dotenv()

    with open('blog-config.yaml') as f:
        config = yaml.safe_load(f)

    config['blogger_credentials'] = {
        'client_id': os.getenv('BLOGGER_CLIENT_ID'),
        'client_secret': os.getenv('BLOGGER_CLIENT_SECRET'),
        'refresh_token': os.getenv('BLOGGER_REFRESH_TOKEN')
    }

    config['cloudinary'] = {
        'cloud_name': os.getenv('CLOUDINARY_CLOUD_NAME'),
        'api_key': os.getenv('CLOUDINARY_API_KEY'),
        'api_secret': os.getenv('CLOUDINARY_API_SECRET')
    }

    validate_config(config)  # Fail fast if missing
    return config
```

---

## Edge Cases

### 1. Post Deleted on Blogger
- Cached `blogger_id` returns 404
- Path lookup also returns 404
- **Action**: Create new post at same path, update frontmatter with new ID

### 2. Directory Name Invalid Format
- Regex match fails in `derive_blogger_path()`
- **Action**: Fail with clear error:
  ```
  ❌ Directory must match: YYYY-MM-DD-slug
  Found: my-post
  Example: 2025-10-12-my-post
  ```

### 3. User Copies Markdown File
- Different directories → Different paths → Different posts (correct!)
- Same directory → Git prevents (impossible)
- **No special handling needed**

### 4. Image File Renamed Locally
- Old path in frontmatter becomes orphaned
- New path treated as new image (uploaded)
- **Action**: Cleanup orphaned mappings:
  ```python
  current_refs = set(extract_image_references(markdown))
  for path in frontmatter['images'].keys():
      if path not in current_refs:
          del frontmatter['images'][path]
  ```

### 5. Cloudinary Upload Fails Mid-Process
- Don't update frontmatter (rollback)
- User retries → Successfully uploaded images skipped (hash matches)
- **Transaction safety**: Only update frontmatter after ALL images uploaded

---

## Error Handling

### Validation Errors (Build Phase)
Fail fast with actionable message:
```
❌ Error: Missing required field 'title'
File: posts/2025-10-12-my-post/post.md

Action Required:
  - Add title field to frontmatter
  - Example: title: "My Post Title"
```

### API Errors
- **401 Unauthorized**: Fail - check credentials
- **404 Not Found**: Handle gracefully (treat as CREATE)
- **429 Rate Limit**: Retry with exponential backoff (1s, 2s, 4s)
- **500 Server Error**: Retry with exponential backoff (max 3 attempts)

### Network Errors
Retry with exponential backoff:
```python
def retry_with_backoff(func, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            return func()
        except (Timeout, ConnectionError) as e:
            if attempt == max_attempts - 1:
                raise
            delay = 2 ** attempt
            time.sleep(delay)
```

---

## Implementation Roadmap

### Phase 1: Core Infrastructure
- Configuration loading (YAML + env)
- Frontmatter parser
- Markdown to HTML converter (mistune + Pygments)
- CLI argument parsing

### Phase 2: Build Command
- Validation logic
- Image reference extractor
- SHA-256 hash computation
- HTML preview generation

### Phase 3: Blogger API Integration
- OAuth authentication
- GET/POST/PATCH endpoints
- Retry logic and error handling

### Phase 4: Image Processing
- PIL-based optimization (resize, compress, WebP)
- Cloudinary upload
- Hash-based deduplication

### Phase 5: Publish Command
- Path-based post detection
- End-to-end workflow
- Atomic frontmatter updates

### Phase 6: Polish
- Comprehensive error messages
- Transaction safety
- Documentation and setup guide

---

## Architecture Summary

**Two Commands, Zero Flags**
- `build.py <post-dir>` - Validate and preview
- `publish.py <post-dir>` - Publish to Blogger

**Path-Based Uniqueness**
- Directory name → URL path → Post identity
- Prevents accidental duplicates
- `blogger_id` is optional cache

**Hash-Based Image Deduplication**
- SHA-256 content hashing
- Upload only new/changed images
- Persistent mappings in frontmatter

**Convention Over Configuration**
- Standard file locations
- Directory naming convention
- Single blog per repository
- Minimal required configuration

**Idempotent & Safe**
- Retry-safe operations
- Atomic file writes
- Fail-fast validation
- Clear error messages

The workflow is simple to use, hard to break, and handles edge cases gracefully.
