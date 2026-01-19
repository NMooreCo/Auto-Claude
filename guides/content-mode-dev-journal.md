# Content Mode Development Journal

This document tracks all development work for the Content Mode feature in Auto Claude.

---

## Overview

Content Mode adds a parallel pipeline to Auto Claude's existing code-focused workflow. Instead of code -> test -> deploy, Content Mode handles concept -> draft -> review -> refine cycles for creative projects (card games, board games, TTRPGs, fiction) and documentation projects.

---

## Completed Work

### PR #1: Design & Agent Prompts (merged)
**Commit:** `e60f994` - feat(content-mode): add Content Mode design and agent prompts

**Changes:**
- Added `guides/content-mode-implementation-plan.md` - Comprehensive implementation plan with 8 phases
- Created 7 agent prompt files:
  - `apps/backend/prompts/content_planner.md` - Plans content creation workflows
  - `apps/backend/prompts/content_creator.md` - Creates content following templates
  - `apps/backend/prompts/content_reviewer.md` - Reviews content quality
  - `apps/backend/prompts/content_editor.md` - Edits and refines content
  - `apps/backend/prompts/content_consistency_checker.md` - Checks cross-reference consistency
  - `apps/backend/prompts/game_balance_analyst.md` - Analyzes game balance (cards, TTRPGs)
  - `apps/backend/prompts/doc_code_analyzer.md` - Generates docs from code analysis

---

### PR #2: Backend Implementation (merged)
**Commits:**
- `2aa9c9e` - feat(content-mode): implement Content Mode backend
- `42f62f0` - test(content-mode): add comprehensive test suite for Content Mode

**Changes:**

#### Core Enums (`apps/backend/content/enums.py`)
- `ContentProjectType` - card_game, board_game, ttrpg, worldbuilding, fiction, business, codebase_docs, api_docs, architecture, knowledge_base, general
- `ContentWorkflowType` - create, expand, iterate, generate, audit, balance, review
- `ContentPhaseType` - concept, research, outline, draft, review, revise, polish, consistency, balance, analysis, verification, finalize
- `ContentVerificationType` - template_compliance, completeness, consistency_check, style_review, accuracy_check, peer_review, balance_review, file_exists, manual
- `ContentArtifactType` - content, analysis, validation, revision, indexing, template, report, plan

#### Data Models (`apps/backend/content/models.py`)
- `ContentVerification` - Verification configuration with serialization
- `ContentSubtask` - Individual subtask in a workflow with dependencies
- `ContentPhase` - Phase containing subtasks with completion tracking
- `ContentPlan` - Complete content plan with save/load, progress tracking

#### Project Detection (`apps/backend/content/detector.py`)
- `ContentProjectDetector` class with:
  - `detect(project_dir)` - Detect from directory structure
  - `detect_from_description(desc)` - Detect from task description
  - `is_content_task(desc)` - Check if task is content vs code
  - `detect_combined(dir, desc)` - Combined detection
  - `get_project_info(dir)` - Get templates, style guides, indexes

#### Project Scaffolding (`apps/backend/content/scaffold.py`)
- `ContentProjectScaffolder` with templates for:
  - Card games (cards, rules, style-guide, formats, playtests)
  - Board games (rules, components, player-aids, playtests)
  - TTRPGs (bestiary, adventures, world, items, characters, spells)
  - Worldbuilding (world, factions, characters, locations, history)
  - Fiction (outline, characters, chapters, notes)
  - Codebase docs (docs/architecture, docs/api, docs/guides)
  - General (style-guide, _index.md)

#### Agent Classes (`apps/backend/content/agents/`)
- `BaseContentAgent` - Abstract base with prompt loading and session creation
- `ContentPlannerAgent` - Creates content workflow plans
- `ContentCreatorAgent` - Creates content following subtasks
- `ContentReviewerAgent` - Reviews content quality
- `ContentEditorAgent` - Edits and refines content
- `ConsistencyCheckerAgent` - Cross-reference consistency
- `BalanceAnalystAgent` - Game balance analysis
- `CodeAnalyzerAgent` - Code-to-docs generation

#### Test Suite (`tests/test_content_mode.py`)
- 50+ tests covering:
  - All enum values
  - Model serialization/deserialization
  - Project detection (structure and description)
  - Project scaffolding (all project types)
  - Agent imports and configuration
  - Integration workflow simulation

---

## Remaining Work

### Phase 3: Content Runner
**Files to create:**
- [ ] `apps/backend/content_runner.py` - Main entry point for Content Mode

**CLI interface:**
```bash
python content_runner.py --project ./my-project --task "Create 5 water faction cards"
python content_runner.py --project ./my-project --spec 001 --execute
python content_runner.py --project ./my-project --spec 001 --review
python content_runner.py --project ./my-project --init card_game
```

### Phase 4: Integration with Existing System
**Files to modify:**
- [ ] `apps/backend/implementation_plan/enums.py` - Add content workflow types
- [ ] `apps/backend/spec/complexity.py` - Add content detection keywords
- [ ] `apps/backend/spec_runner.py` - Route to content mode when detected

### Phase 5: Project Templates
**Files to create:**
- [ ] `apps/backend/content/templates/card_game/` - Card game template files
- [ ] `apps/backend/content/templates/ttrpg/` - TTRPG template files
- [ ] `apps/backend/content/templates/board_game/` - Board game template files
- [ ] `apps/backend/content/templates/codebase_docs/` - Documentation template files
- [ ] `apps/backend/content/templates/general/` - General template files

### Phase 6-7: Frontend Integration & i18n
**Files to create:**
- [ ] `apps/frontend/src/renderer/components/task-form/ContentTaskFields.tsx`

**Files to modify:**
- [ ] `apps/frontend/src/shared/types/index.ts` - Add content types
- [ ] `apps/frontend/src/renderer/components/task-form/ClassificationFields.tsx`
- [ ] `apps/frontend/src/renderer/components/TaskCreationWizard.tsx`
- [ ] `apps/frontend/src/shared/i18n/locales/en/tasks.json`
- [ ] `apps/frontend/src/shared/i18n/locales/fr/tasks.json`

### Phase 8: Additional Testing
- [ ] Integration tests with actual Claude SDK
- [ ] E2E tests via Electron MCP
- [ ] Manual testing with real content projects

---

## Architecture Notes

### Content Mode vs Code Mode

| Aspect | Code Mode | Content Mode |
|--------|-----------|--------------|
| Entry point | `run.py` | `content_runner.py` |
| Planning | `planner.py` | `content/agents/planner.py` |
| Execution | `coder.py` | `content/agents/creator.py` |
| Validation | `qa_reviewer.py` | `content/agents/reviewer.py` |
| Fixes | `qa_fixer.py` | `content/agents/editor.py` |
| Output | Code changes | Markdown/content files |
| Verification | Tests pass | Template compliance |

### Detection Flow

```
Task Description
       │
       v
ContentProjectDetector.is_content_task()
       │
       ├── True: Content Mode
       │     └── ContentProjectDetector.detect_combined()
       │           └── Route to content_runner.py
       │
       └── False: Code Mode
             └── Existing spec_runner.py flow
```

### Content Plan Lifecycle

```
1. detect() → ContentProjectType
2. ContentPlannerAgent.create_plan() → ContentPlan
3. ContentPlan.save() → content_plan.json
4. Loop:
   a. ContentPlan.get_next_subtask() → (phase, subtask)
   b. ContentCreatorAgent.execute_subtask()
   c. ContentPlan.mark_subtask_status("completed")
5. ContentReviewerAgent.review()
6. ContentEditorAgent.refine() (if needed)
7. Finalize
```

---

## Session Log

### Session 1 (2026-01-19)
- Reviewed completed work from PRs #1 and #2
- Created this dev journal
- Analyzed existing CLI architecture (`cli/main.py`, `run.py`)
- Studied `ContentAgent` base class implementation

**Planning for Phase 3 (Content Runner):**

The content runner should follow the existing CLI pattern but be optimized for content workflows:

```python
# Target CLI interface
python content_runner.py --project ./my-project --task "Create 5 water faction cards"  # New content
python content_runner.py --project ./my-project --spec 001 --execute                   # Execute plan
python content_runner.py --project ./my-project --spec 001 --review                    # Review content
python content_runner.py --project ./my-project --init card_game                       # Scaffold project
python content_runner.py --project ./my-project --spec 001 --consistency               # Run consistency check
python content_runner.py --project ./my-project --spec 001 --balance                   # Run balance analysis
```

**Key components to implement:**

1. **Argument parsing** - Similar to `cli/main.py` but content-focused
2. **Planning flow** - Call `ContentPlannerAgent.run()` with task description
3. **Execution flow** - Loop through `ContentPlan.get_next_subtask()`, call `ContentCreatorAgent`
4. **Review flow** - Call `ContentReviewerAgent` then `ContentEditorAgent` if needed
5. **Consistency/Balance** - Call specialized agents for validation

**Priority for next session:**
- [ ] Implement `content_runner.py` with basic --task and --execute flows
- [ ] Test with a sample card game project

---

## Notes

- Content Mode uses the same Claude Agent SDK as Code Mode
- All agents inherit from `BaseContentAgent` for consistent behavior
- Project scaffolding creates template structures, not just empty directories
- The detector uses a scoring system to handle ambiguous projects
- Plans support dependencies between phases and subtasks
