# Lifecycle Planning Template v5

**Last Updated**: 2025-10-18

**Purpose**: Streamlined sequential agent execution plan for software development lifecycle.

**Flow**: Requirements & Approach → Implementation → Verification → Documentation

**Principle**: Clear direction, concise expression. What to build, not how to code it.

---

# [Feature Name]

**Date**: YYYY-MM-DD
**Context**: [One-line summary of what this addresses]

---

## Overview

**Problem**: [What specific issue are we solving? 2-3 sentences max]

**Solution**: [What we're building - one sentence]

**Outcome**: [What success looks like - one sentence]

---

## Phase 1: Requirements & Approach

### What We're Building

**Current State**: [What exists now - 1 sentence]

**Pain Point**: [Why this is a problem - 1 sentence]

**Success Criteria**:
- ✅ [Testable outcome 1 with acceptance metric]
- ✅ [Testable outcome 2 with acceptance metric]
- ✅ [Testable outcome 3 with acceptance metric]
- ✅ [Testable outcome 4 with acceptance metric]
- ✅ [Testable outcome 5 with acceptance metric]

*Example: ✅ Python lib/ modules achieve ≥80% test coverage*

### How We're Building It

**Approach**: [Specific implementation strategy - 1-2 sentences]

**Tools/Technologies**: [List key tools/libraries/frameworks]

**Rationale**:
- Fits pattern: [specific file/pattern reference]
- Minimal risk: [why this is safe]
- Reuses: [existing components/utilities]

**Rejected Alternatives**:
- [Alternative 1]: [Why rejected - 1 line]
- [Alternative 2]: [Why rejected - 1 line]

> Implementation agent: Follow ONLY the selected approach above.

### Architecture

**Components**:
```
component/
├── file1.ext     # Purpose
├── file2.ext     # Purpose
└── file3.ext     # Purpose
```

**Data Models** *(if needed)*:
```
Model: EntityName
- field1: [type] - Purpose/constraints
- field2: [type] - Purpose/constraints
```

**API Contracts** *(if applicable)*:
```
[METHOD] /path
Request: [key fields]
Response: [key fields]
Status: 200 (success), 400 (validation), 500 (error)
```

**State Flow** *(if stateful)*:
1. [Initial state] → [Action] → [New state]
2. [State] → [Action] → [Final state]

**Integration Points**:
- Internal: [Existing components this touches]
- External: [Third-party services/APIs]

### Codebase Context

**Relevant Files**:
- `path/to/file1.ext` - [What it does, why relevant - 1 line]
- `path/to/file2.ext` - [What it does, why relevant - 1 line]

**Patterns to Follow**:
- [Pattern name]: See `path/to/example.ext:123-145`
- [Pattern name]: See `path/to/example.ext:67-89`

**Don't Touch** *(looks relevant but isn't)*:
- `path/to/file.ext` - [Why it's not relevant]

---

## Phase 2: Implementation Tasks

### Task 1: [Specific Action]

**Create/Modify**:
- Create `path/to/file.ext` - [Purpose]
- Modify `path/to/file.ext` - [Purpose]

**What to Do**:
- [ ] [Specific change with acceptance criterion]
- [ ] [Specific change with acceptance criterion]
- [ ] [Specific change with acceptance criterion]
- [ ] Edge case: [Specific scenario to handle]
- [ ] Constraint: [Specific requirement to ensure]

**Verify**: [Command or method to confirm completion]

---

### Task 2: [Specific Action]

**Create/Modify**:
- Create/Modify `path/to/file.ext` - [Purpose]

**What to Do**:
- [ ] [Specific change with acceptance criterion]
- [ ] [Specific change with acceptance criterion]
- [ ] Edge case: [Specific scenario to handle]

**Verify**: [Command or method to confirm completion]

---

### Task 3: [Specific Action]

**Create/Modify**:
- Create/Modify `path/to/file.ext` - [Purpose]

**What to Do**:
- [ ] [Specific change with acceptance criterion]
- [ ] [Specific change with acceptance criterion]

**Verify**: [Command or method to confirm completion]

---

*Repeat pattern for tasks 4-8 (aim for 5-8 tasks total)*

### Implementation Notes

**Follow Patterns**: [Reference specific files demonstrating the project style]

**Naming Conventions**: [Project-specific conventions]

**Special Considerations**: [Anything unusual about this implementation]

---

## Phase 3: Verification & Acceptance

### Automated Checks

**Build**:
```bash
[build command]
```
✅ Expected: [Success criteria]

**Tests**:
```bash
[test command]
```
✅ Expected: [Coverage/pass criteria]

**Linting** *(if applicable)*:
```bash
[lint command]
```
✅ Expected: No warnings or errors

**Full Verification** *(if project has comprehensive verification)*:
```bash
[project verify command]
```
✅ Expected: [What should pass]

### Manual Verification

- [ ] **[Scenario]**: [What to test] → ✅ Expected: [Outcome]
- [ ] **[Scenario]**: [What to test] → ✅ Expected: [Outcome]
- [ ] **[Scenario]**: [What to test] → ✅ Expected: [Outcome]

### Acceptance Criteria

**Functional**:
- [ ] Success criterion 1: [How to verify it passes]
- [ ] Success criterion 2: [How to verify it passes]
- [ ] Success criterion 3: [How to verify it passes]
- [ ] Edge cases handled: [Key cases verified]
- [ ] Error handling works: [Error scenarios tested]

**Non-Functional** *(if applicable)*:
- [ ] Performance: [Metric verified - e.g., < 2s response time]
- [ ] Security: [What validated - e.g., auth checks pass]
- [ ] Compatibility: [Platforms verified - e.g., works on Chrome/Firefox/Safari]

**Integration**:
- [ ] No regressions: [Existing features still work]
- [ ] Works with: [Integration points validated]

**Definition of Done**:
- [ ] All success criteria validated
- [ ] All verification commands pass
- [ ] Code follows project patterns
- [ ] No regressions in existing functionality
- [ ] Edge cases handled
- [ ] Documentation updated *(if needed)*

---

## Phase 4: Documentation Updates

### Files to Update

**`path/to/doc.md`**:
- Section: [Which section]
- Add: [What to document - bullets, not full text]

**`path/to/doc.md`**:
- Section: [Which section]
- Add: [What to document - bullets]

### New Concepts *(if any)*

**[Pattern/Utility Name]**: [Brief description - 1 line]
- Document in: `path/to/file`
- Cover: [Key point 1], [Key point 2], [Key point 3]

---

## Template Usage Guide

### For Planning Agent
- Fill all sections with specifics (1-2 sentences each)
- Success Criteria: Use ✅ format with measurable outcomes
- Architecture: Structure only, not full code
- Tasks: WHAT to accomplish, not HOW to code it
- Skip optional sections if not applicable (marked with *if needed/applicable*)

### For Implementation Agent
- Read Phase 1 for context and constraints
- Execute Phase 2 tasks sequentially
- Reference Codebase Context for patterns
- Check off task items as you complete them
- Ask for clarification if approach is ambiguous

### For Verification Agent
- Run Phase 3 automated checks
- Report results vs expected outcomes
- Execute manual verification scenarios
- Validate all acceptance criteria

### For Documentation Agent
- Update files from Phase 4
- Follow existing documentation style
- Keep updates concise (bullets, not paragraphs)

---

## Size Guidelines

**Target**: 150-250 lines total (excluding template usage guide)
- Overview: ~10 lines
- Phase 1: ~60-80 lines
- Phase 2: ~50-80 lines (8-12 lines per task × 5-8 tasks)
- Phase 3: ~40-60 lines
- Phase 4: ~15-25 lines

**What NOT to Include**:
- ❌ Full code implementations
- ❌ Complete configuration files
- ❌ Full markdown examples
- ❌ Line-by-line instructions
- ❌ Verbose decision logs (keep to 1 line)
- ❌ EARS-formatted requirements (REQ-001, REQ-002, etc.)
- ❌ "Depends on" for every task (sequence implies dependency)
- ❌ Separate "Critical" subsections (integrate into main checklist)
- ❌ Risk mitigation, success metrics, effort estimates (project management noise)
- ❌ Future Features. Focus on the now not the later.

**What TO Include**:
- ✅ Clear success criteria with ✅ checkmarks and metrics
- ✅ Architectural structure (files, models, flows)
- ✅ Checkbox task breakdown with verification commands
- ✅ Verification commands with expected outcomes
- ✅ Unified acceptance criteria (functional + non-functional + integration)
- ✅ Edge cases and constraints inline with tasks

---

## End of Template

Publish the plan at `specs/my-plan.md`
