# Vector Embeddings for Blog Content

**Status:** Build-time generation implemented
**Last Updated:** October 2025

---

## Concept

Vector embeddings transform text into numerical representations (arrays of floats) that capture semantic meaning. Similar content produces similar vectors, enabling semantic search and content recommendations beyond keyword matching.

**Example:**
```
"AI automation workflow" → [0.018, -0.023, 0.012, ..., 0.045]  (1536 numbers)
"Claude Code automation"  → [0.015, 0.031, 0.008, ..., 0.041]  (1536 numbers)
```

**Similarity Measurement:**
Cosine similarity calculates how "close" two vectors are (range: -1 to 1, higher = more similar).

Typical related posts score: 0.70-0.90

---

## Use Cases

### 1. Related Posts
Show semantically similar posts at the bottom of each article (e.g., "Readers who enjoyed this also read...").

### 2. Semantic Search
Enable natural language search that understands meaning, not just keywords.

### 3. Content Clustering
Group related posts by semantic similarity for navigation or recommendations.

### 4. Future Vector Store Integration
Pre-computed embeddings can be imported into a vector database for advanced use cases.

---

## Build-Time Generation

### Why Build Time?
- One-time cost (~$0.00003 per post)
- No runtime latency
- Embeddings don't change unless content changes
- Deterministic and version-controlled

### Process

**Tool:** `tools/generate_embedding.py`

**Usage:**
```bash
# Single post
uv run tools/generate_embedding.py website/content/posts/2025-10-12-my-post.mdx

# All posts (skips existing)
uv run tools/generate_embedding.py
```

**Algorithm:**
1. Load existing `website/content/embeddings.json` (if exists)
2. For each MDX file:
   - Extract slug from filename (e.g., `2025-10-12-my-post`)
   - Skip if embedding already exists in JSON
   - Parse frontmatter (title, description)
   - Combine for embedding: `f"{title}\n{description}\n{content}"`
   - Call OpenAI API: `text-embedding-3-small` (1536 dimensions)
   - Store in embeddings dictionary: `embeddings[slug] = [0.018, ...]`
3. Save updated `embeddings.json`

**Why this text combination?**
- Title: Most important keywords
- Description: SEO summary with key concepts
- Content: Full semantic context

---

## Storage Format

**File:** `website/content/embeddings.json`

**Structure:**
```json
{
  "2025-10-12-voice-to-blog-automation": [
    0.018904367461800575,
    0.0028905710205435753,
    -0.02303137816488743,
    ...1533 more floats...
  ],
  "2025-10-13-taming-claude-yolo-mode": [
    0.015,
    0.031,
    ...
  ]
}
```

**Size:**
- Per post: ~39KB (1536 dimensions)
- 3 posts: 118KB
- 50 posts: ~2MB
- 500 posts: ~20MB

---

## OpenAI API Details

**Model:** `text-embedding-3-small`
**Dimensions:** 1536 (full precision)
**Cost:** $0.02 per 1M tokens (~$0.00003 per blog post)
**Matryoshka Representation Learning:** Supports dimension reduction via API parameter (e.g., 768 dimensions for 50% smaller files)

---

## Integration Points

The generated `embeddings.json` file can be consumed by:

1. **Next.js API routes** - Load and query at runtime
2. **Build-time scripts** - Precompute related posts or search indices
3. **Vector stores** - Import into Pinecone, Supabase, or similar
4. **Client-side search** - Bundle with static site (if size permits)

This spec documents the **generation process only**. Consumption patterns are implementation-specific and may evolve based on vector store integration.

---

## Regeneration

**When to regenerate:**
- New post created
- Existing post content updated
- Changed embedding model or dimensions

**Command:** `uv run tools/generate_embedding.py` (skips unchanged posts automatically)

---

## References

- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [Matryoshka Representation Learning](https://arxiv.org/abs/2205.13147)
