# Agentic Engineer Blog
Powered by Google's Blogger platform


## Using clade code with this project
```bash
env $(grep -v "^#" .env | grep -v "^$" | xargs) claude --dangerously-skip-permissions
```