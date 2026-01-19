# Content Mode for Auto Claude - Complete Documentation

## What Was Built

Content Mode adds a parallel pipeline to Auto Claude for creative and documentation projects instead of just code. It handles concept → draft → review → refine cycles for non-code content.

### All Phases Complete ✅

**PR #1 - Design Phase (Merged)**
- 7 agent prompts in `apps/backend/prompts/`
- Implementation plan in `guides/content-mode-implementation-plan.md`

**PR #2 - Backend Implementation (Merged)**
- Full backend module: `apps/backend/content/` (14 files)
- CLI entry point: `apps/backend/content_runner.py`
- Project scaffolding with templates
- Test suite: `tests/test_content_mode.py` (55 tests, all passing)

**PR #3 - Integration & Frontend (Merged)**
- Phase 4: spec_runner.py integration - auto-routes content tasks to Content Mode
- Phase 6: Frontend UI - content categories and ContentTaskFields component
- Phase 7: i18n translations for English and French

---

## Supported Project Types

| Type | Use Case |
|------|----------|
| `card_game` | Pokemon/Magic-style card games |
| `board_game` | Board games with components |
| `ttrpg` | D&D, Pathfinder, custom TTRPGs |
| `worldbuilding` | Lore, factions, regions |
| `fiction` | Novels, stories, scripts |
| `business` | Business plans, pitches |
| `codebase_docs` | Full codebase documentation |
| `api_docs` | API endpoint documentation |
| `general` | Any creative content |

---

## File Structure Created

```
apps/backend/
├── content/
│   ├── __init__.py           # Module exports
│   ├── enums.py              # ContentProjectType, ContentWorkflowType, etc.
│   ├── models.py             # ContentPlan, ContentPhase, ContentSubtask
│   ├── detector.py           # Auto-detect project type
│   ├── scaffold.py           # Initialize new projects from templates
│   └── agents/
│       ├── __init__.py
│       ├── base.py           # Base ContentAgent class
│       ├── planner.py        # ContentPlannerAgent
│       ├── creator.py        # ContentCreatorAgent
│       ├── reviewer.py       # ContentReviewerAgent
│       ├── editor.py         # ContentEditorAgent
│       ├── consistency_checker.py
│       ├── balance_analyst.py
│       └── code_analyzer.py
├── content_runner.py         # CLI entry point
└── prompts/
    ├── content_planner.md
    ├── content_creator.md
    ├── content_reviewer.md
    ├── content_editor.md
    ├── content_consistency_checker.md
    ├── game_balance_analyst.md
    └── doc_code_analyzer.md

tests/
└── test_content_mode.py      # 55 tests
```

---

## CLI Usage

```bash
cd apps/backend

# Show project info (auto-detects type)
python content_runner.py --project ./my-card-game --info

# Initialize new project from template
python content_runner.py --project ./new-game --init card_game

# Create content plan from task description
python content_runner.py --project ./my-card-game --task "Create 5 water element cards"

# Execute existing plan
python content_runner.py --project ./my-card-game --spec content-001 --execute

# List all content specs
python content_runner.py --project ./my-card-game --list
```

---

## Key Classes

### ContentProjectDetector
```python
from content import ContentProjectDetector

detector = ContentProjectDetector()

# Detect from directory structure
project_type = detector.detect("./my-card-game")  # Returns ContentProjectType.CARD_GAME

# Detect from task description
project_type = detector.detect_from_description("Create 5 creature cards with mana costs")

# Check if task is content (vs code)
is_content = detector.is_content_task("Write a new monster for the bestiary")
```

### ContentPlan
```python
from content import ContentPlan, ContentProjectType, ContentWorkflowType

# Create plan
plan = ContentPlan(
    project_name="Water Faction Expansion",
    project_type=ContentProjectType.CARD_GAME,
    workflow_type=ContentWorkflowType.CREATE,
    workflow_rationale="Creating new cards from scratch"
)

# Save/load JSON
plan.save("/path/to/content_plan.json")
loaded_plan = ContentPlan.load("/path/to/content_plan.json")

# Track progress
progress = plan.get_progress()  # Returns {"completed": 3, "total": 10, "percentage": 30.0}

# Get next available subtask
next_subtask = plan.get_next_subtask()
```

### ContentProjectScaffolder
```python
from content import ContentProjectScaffolder, ContentProjectType

scaffolder = ContentProjectScaffolder()
scaffolder.scaffold("./new-game", ContentProjectType.CARD_GAME)

# Creates:
# ./new-game/
# ├── _index.md
# ├── rules/
# │   ├── core-rules.md
# │   └── keywords.md
# ├── cards/
# │   └── _template.md
# ├── style-guide/
# │   ├── naming-conventions.md
# │   └── power-levels.md
# └── playtests/
```

---

## Implementation Details

### Phase 4: spec_runner.py Integration ✅

Auto-routes content tasks to Content Mode instead of code pipeline.

**Files Modified**:
- `apps/backend/spec/complexity.py` - Added `is_content_task()` and `get_content_project_type()` methods
- `apps/backend/runners/spec_runner.py` - Routes content tasks to `content_runner.cmd_plan()`
- `apps/backend/implementation_plan/enums.py` - Added content workflow types

**How it works**: When a task is submitted, `ContentProjectDetector` checks if it's a content task. If so, it's routed to Content Mode instead of the code pipeline.

---

### Phase 6: Frontend Integration ✅

Added content categories and ContentTaskFields component to the UI.

**Files Created**:
- `apps/frontend/src/renderer/components/task-form/ContentTaskFields.tsx` - Project type, target audience, content type fields

**Files Modified**:
- `apps/frontend/src/shared/types/task.ts` - Added `TaskCategory` content types, `ContentProjectType`, `CONTENT_CATEGORIES`
- `apps/frontend/src/renderer/components/task-form/ClassificationFields.tsx` - Added content categories
- `apps/frontend/src/renderer/components/task-form/TaskFormFields.tsx` - Conditional ContentTaskFields rendering
- `apps/frontend/src/renderer/components/TaskCreationWizard.tsx` - Content field state management
- `apps/frontend/src/renderer/components/TaskEditDialog.tsx` - Content field support for editing

**UI Flow**: When user selects a content category (Creative, Game Design, Worldbuilding, Content Docs), the ContentTaskFields section appears with project type dropdown, target audience, and content type inputs.

---

### Phase 7: i18n Translations ✅

Added English and French translations for content mode UI.

**Files Modified**:
- `apps/frontend/src/shared/i18n/locales/en/tasks.json` - English translations
- `apps/frontend/src/shared/i18n/locales/fr/tasks.json` - French translations

**Translation Keys Added**:
- `form.classification.values.category.creative/game_design/worldbuilding/content_docs`
- `form.content.title/projectType/targetAudience/contentType`
- `form.content.projectTypes.*` - All 9 project types

---

## Testing

```bash
# Run all Content Mode tests
cd apps/backend
python -m pytest tests/test_content_mode.py -v

# Verify imports work
python -c "from content import ContentProjectType, ContentPlan, ContentProjectDetector; print('OK')"
```

---

## User Context

The user is building a card collecting game (Pokemon/Magic style) using:
- Markdown documents as source of truth
- ASCII art for card visuals in markdown
- External system for actual art generation
- Iterative refinement workflow

This system also applies to board games, D&D/TTRPGs, and codebase documentation.

---

## Phase Status

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Core Enums and Models | ✅ Complete |
| 2 | Content Agents | ✅ Complete |
| 3 | Content Runner CLI | ✅ Complete |
| 4 | spec_runner.py Integration | ✅ Complete |
| 5 | Project Templates | ✅ Complete |
| 6 | Frontend Integration | ✅ Complete |
| 7 | i18n Translations | ✅ Complete |
| 8 | Testing | ✅ Complete |

---

## Branch Information

- Design work: `claude/add-creative-mode-9s601` (PR #1)
- Backend implementation: `claude/implement-content-mode-9s601` (PR #2)
- Integration & frontend: `claude/creative-mode-planning-VrGAe` (PR #3)
- All merged to: `feature/creative-mode`
- All 55 backend tests passing
