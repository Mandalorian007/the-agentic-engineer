# Build Task

Implement a task directly without creating a plan first.

## Variables
spec-file-name: $1

## Instructions

1. **Prime with Context**: First, read and execute SlashCommand(`/prime`) to understand the codebase
2. **Analyze Task**: Carefully read and understand the spec plan in the `specs` directory named <spec-file-name>
3. **Implement Solution**: Think hard and then directly implement the solution for the task
4. **Validate Work**: Ensure the implementation is complete and working
5. **Report Results**: Summarize what was done

## Setup Phase

Before implementing the task:
- Execute the prime command to understand the codebase structure
- Read relevant documentation files (README.md, etc.)
- Understand the existing patterns and conventions

## Implementation Guidelines

- Follow existing code patterns and conventions
- Use the libraries and frameworks already in the codebase
- Write clean, maintainable code
- Add appropriate error handling
- Follow security best practices

## Task Description

<Summarize Task Description from the spec>

## Expected Actions

1. **Research**: Understand the codebase and task requirements
2. **Implement**: Make the necessary changes to complete the task
3. **Test**: Verify the implementation works as expected

## Report

After completing the implementation:
- Summarize the work done in clear bullet points
- List all files created or modified
- Report the total lines changed with `git diff --stat`
- Note any important decisions or trade-offs made
- Highlight any follow-up tasks that may be needed