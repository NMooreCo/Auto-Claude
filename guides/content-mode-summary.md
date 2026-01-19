# Content Mode for Auto Claude - Complete Documentation

## What Was Built

Content Mode adds a parallel pipeline to Auto Claude for creative and documentation projects instead of just code. It handles concept → draft → review → refine cycles for non-code content.

### Completed (Phases 1-3, 5, 8)

**PR #1 - Design Phase (Merged)**
- 7 agent prompts in `apps/backend/prompts/`
- Implementation plan in `guides/content-mode-implementation-plan.md`

**PR #2 - Implementation Phase (Merged)**
- Full backend module: `apps/backend/content/` (14 files)
- CLI entry point: `apps/backend/content_runner.py`
- Project scaffolding with templates
- Test suite: `tests/test_content_mode.py` (55 tests, all passing)

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

## Remaining Work (Phases 4, 6, 7)

### Phase 4: Integration with spec_runner.py

**Purpose**: Auto-route content tasks to Content Mode instead of code pipeline

**Files to Modify**:

1. `apps/backend/spec/complexity.py` - Add content detection:
```python
CONTENT_KEYWORDS = {
    "card_game": ["card", "deck", "mana", "creature", "spell"],
    "ttrpg": ["monster", "dungeon", "campaign", "spell", "dm"],
    "documentation": ["document", "api", "endpoint", "guide"],
}

def is_content_task(self, description: str) -> bool:
    """Check if task is content rather than code."""
    # Use ContentProjectDetector
    from content import ContentProjectDetector
    detector = ContentProjectDetector()
    return detector.is_content_task(description)
```

2. `apps/backend/spec_runner.py` - Route to content mode:
```python
from content import ContentProjectDetector
from content_runner import run_planning as run_content_planning

def create_spec(task: str, project_dir: str):
    detector = ContentProjectDetector()

    if detector.is_content_task(task):
        print("Detected content task - using Content Mode")
        return run_content_planning(project_dir, task)
    else:
        return run_code_planning(project_dir, task)
```

3. `apps/backend/implementation_plan/enums.py` - Add workflow types:
```python
class WorkflowType(str, Enum):
    # Existing
    FEATURE = "feature"
    REFACTOR = "refactor"
    # ...

    # NEW: Content workflows
    CONTENT_CREATE = "content_create"
    CONTENT_EXPAND = "content_expand"
    CONTENT_ITERATE = "content_iterate"
    CONTENT_DOCUMENT = "content_document"
```

---

### Phase 6: Frontend Integration

**Purpose**: Add "creative" category to task creation form

**Files to Modify**:

1. `apps/frontend/src/shared/types/index.ts`:
```typescript
export type TaskCategory =
  | 'feature'
  | 'bug_fix'
  | 'refactoring'
  | 'documentation'
  | 'security'
  // NEW
  | 'creative'
  | 'game_design'
  | 'worldbuilding'
  | 'content_docs';

export type ContentProjectType =
  | 'card_game'
  | 'board_game'
  | 'ttrpg'
  | 'worldbuilding'
  | 'fiction'
  | 'codebase_docs'
  | 'general';
```

2. `apps/frontend/src/renderer/components/task-form/ClassificationFields.tsx`:
```typescript
const CATEGORY_OPTIONS: TaskCategory[] = [
  'feature',
  'bug_fix',
  // ...existing...
  'creative',      // NEW
  'game_design',   // NEW
  'worldbuilding', // NEW
  'content_docs'   // NEW
];
```

3. **Create** `apps/frontend/src/renderer/components/task-form/ContentTaskFields.tsx`:
```typescript
// New component showing project type dropdown, target audience, content type
// when a content category is selected
```

4. `apps/frontend/src/renderer/components/TaskCreationWizard.tsx`:
```typescript
{isContentCategory(category) && (
  <ContentTaskFields
    projectType={contentProjectType}
    onProjectTypeChange={setContentProjectType}
    // ...
  />
)}
```

---

### Phase 7: i18n Translations

**Files to Modify**:

1. `apps/frontend/src/shared/i18n/locales/en/tasks.json`:
```json
{
  "form": {
    "content": {
      "title": "Content Details",
      "projectType": "Project Type",
      "selectProjectType": "Select project type...",
      "targetAudience": "Target Audience",
      "targetAudiencePlaceholder": "e.g., Players familiar with MTG",
      "contentType": "Content Type",
      "contentTypePlaceholder": "e.g., New creature cards for water faction"
    },
    "classification": {
      "values": {
        "category": {
          "creative": "Creative",
          "game_design": "Game Design",
          "worldbuilding": "Worldbuilding",
          "content_docs": "Documentation"
        }
      }
    }
  }
}
```

2. `apps/frontend/src/shared/i18n/locales/fr/tasks.json` - French translations

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

## Branch Information

- Work completed on: `claude/implement-content-mode-9s601`
- PRs merged to: `feature/creative-mode`
- All 55 tests passing
