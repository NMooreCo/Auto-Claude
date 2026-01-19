# Creative Mode Development Journal

This journal tracks all development work on the Creative/Content Mode feature for Auto Claude.

---

## Overview

**Feature Branch**: `feature/creative-mode` (planning branch: `claude/creative-mode-planning-VrGAe`)

**Purpose**: Add a parallel pipeline to Auto Claude for creative and documentation projects. Handles concept → draft → review → refine cycles for non-code content like game design documents, worldbuilding, fiction, and documentation.

**Target Use Cases**:
- Card games (Pokemon/Magic-style)
- Board games
- TTRPGs (D&D, Pathfinder, custom systems)
- Worldbuilding (lore, factions, regions)
- Fiction (novels, stories, scripts)
- Business documents
- Codebase and API documentation

---

## Completed Work

### PR #1: Design Phase
**Branch**: `claude/add-creative-mode-9s601`
**Merged**: Yes
**Commit**: `e60f994`

**What was built**:
- 7 agent prompts in `apps/backend/prompts/`:
  - `content_planner.md` - Plans content creation workflow
  - `content_creator.md` - Creates initial content drafts
  - `content_reviewer.md` - Reviews content for quality
  - `content_editor.md` - Edits and refines content
  - `content_consistency_checker.md` - Checks cross-document consistency
  - `game_balance_analyst.md` - Analyzes game balance (for game projects)
  - `doc_code_analyzer.md` - Analyzes code for documentation projects
- Implementation plan: `guides/content-mode-implementation-plan.md`

---

### PR #2: Backend Implementation
**Branch**: `claude/implement-content-mode-9s601`
**Merged**: Yes
**Commits**: `2aa9c9e`, `42f62f0`

**What was built**:

1. **Content Module** (`apps/backend/content/`):
   - `__init__.py` - Module exports
   - `enums.py` - ContentProjectType, ContentWorkflowType, ContentPhaseType
   - `models.py` - ContentPlan, ContentPhase, ContentSubtask data classes
   - `detector.py` - Auto-detect project type from directory or task description
   - `scaffold.py` - Initialize new projects from templates

2. **Agent Implementations** (`apps/backend/content/agents/`):
   - `base.py` - Base ContentAgent class
   - `planner.py` - ContentPlannerAgent
   - `creator.py` - ContentCreatorAgent
   - `reviewer.py` - ContentReviewerAgent
   - `editor.py` - ContentEditorAgent
   - `consistency_checker.py` - ConsistencyCheckerAgent
   - `balance_analyst.py` - BalanceAnalystAgent
   - `code_analyzer.py` - CodeAnalyzerAgent

3. **CLI Entry Point**:
   - `apps/backend/content_runner.py` - Full CLI for content mode

4. **Test Suite**:
   - `tests/test_content_mode.py` - 55 tests, all passing

**Supported Project Types**:
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

**Original Implementation Plan**: See `guides/content-mode-implementation-plan.md` for detailed design.

---

## Phase Status Overview

| Phase | Description | Status | PR |
|-------|-------------|--------|-----|
| 1 | Core Enums and Models | Completed | PR #2 |
| 2 | Content Agents | Completed | PR #2 |
| 3 | Content Runner CLI | Completed | PR #2 |
| 4 | Integration with spec_runner.py | Completed | PR #3 |
| 5 | Project Templates | Completed | PR #2 |
| 6 | Frontend Integration | **Not Started** | - |
| 7 | i18n Translations | **Not Started** | - |
| 8 | Testing | Completed | PR #2 |

---

## Remaining Work

### Phase 4: Integration with spec_runner.py
**Status**: Completed (2026-01-19)
**Priority**: High

**Goal**: Auto-route content tasks to Content Mode instead of code pipeline

**Files to modify**:
1. `apps/backend/spec/complexity.py` - Add content detection
2. `apps/backend/runners/spec_runner.py` - Route to content mode
3. `apps/backend/implementation_plan/enums.py` - Add content workflow types

**Detailed Implementation Plan**:

#### 4.1 Add Content Detection to ComplexityAnalyzer (`spec/complexity.py`)

```python
# Add new class constants to ComplexityAnalyzer
CONTENT_KEYWORDS = {
    "card_game": ["card", "deck", "mana", "creature", "spell", "element", "faction"],
    "board_game": ["board", "tile", "piece", "turn", "component", "dice"],
    "ttrpg": ["monster", "dungeon", "campaign", "quest", "npc", "encounter", "dm", "gm"],
    "worldbuilding": ["lore", "faction", "region", "history", "timeline", "character"],
    "fiction": ["story", "chapter", "character", "plot", "narrative", "scene"],
    "documentation": ["document", "api", "endpoint", "guide", "readme", "docs"],
}

# Add method to ComplexityAnalyzer
def is_content_task(self, task_description: str) -> bool:
    """Check if task is content rather than code."""
    from content import ContentProjectDetector
    detector = ContentProjectDetector()
    return detector.is_content_task(task_description)

def get_content_project_type(self, task_description: str, project_dir: Path) -> Optional[str]:
    """Get detected content project type if this is a content task."""
    from content import ContentProjectDetector
    detector = ContentProjectDetector()
    return detector.detect_combined(str(project_dir), task_description)
```

#### 4.2 Route to Content Mode in spec_runner.py

```python
# Add to imports at top
from content import ContentProjectDetector
from content_runner import cmd_plan as run_content_planning

# Add detection before creating SpecOrchestrator
def main():
    # ... existing arg parsing ...

    # Check if this is a content task
    if task_description:
        detector = ContentProjectDetector()
        if detector.is_content_task(task_description):
            project_type = detector.detect_combined(str(project_dir), task_description)
            print(f"Detected content task ({project_type.value}) - using Content Mode")

            # Create args namespace for content_runner
            content_args = argparse.Namespace(
                project=str(project_dir),
                task=task_description,
                spec=None,
            )
            return run_content_planning(content_args)

    # ... existing code orchestrator logic ...
```

#### 4.3 Add Content Workflow Types (`implementation_plan/enums.py`)

```python
class WorkflowType(str, Enum):
    # Existing code workflows
    FEATURE = "feature"
    REFACTOR = "refactor"
    INVESTIGATION = "investigation"
    MIGRATION = "migration"
    SIMPLE = "simple"
    DEVELOPMENT = "development"
    ENHANCEMENT = "enhancement"

    # Content workflows
    CONTENT_CREATE = "content_create"      # Building new content from scratch
    CONTENT_EXPAND = "content_expand"      # Adding to existing content
    CONTENT_ITERATE = "content_iterate"    # Refining existing content
    CONTENT_DOCUMENT = "content_document"  # Generating docs from code
```

#### 4.4 Testing Checklist

- [ ] Test content detection with card game task descriptions
- [ ] Test content detection with TTRPG task descriptions
- [ ] Test content detection with documentation tasks
- [ ] Verify code tasks still route to SpecOrchestrator
- [ ] Test mixed tasks (e.g., "document the API") route correctly
- [ ] Test --complexity override still works with content tasks

---

### Phase 6: Frontend Integration
**Status**: Not Started
**Priority**: Medium
**Depends On**: Phase 4 (backend must route content tasks first)

**Goal**: Add "creative" category to task creation form in Electron app

**Files to modify**:
1. `apps/frontend/src/shared/types/index.ts` - Add TaskCategory types
2. `apps/frontend/src/renderer/components/task-form/ClassificationFields.tsx` - Add category options
3. `apps/frontend/src/renderer/components/TaskCreationWizard.tsx` - Conditional rendering

**Files to create**:
1. `apps/frontend/src/renderer/components/task-form/ContentTaskFields.tsx` - Content-specific form fields

**Detailed Implementation Plan**:

#### 6.1 Add Types (`shared/types/index.ts`)

```typescript
// Add to existing TaskCategory type
export type TaskCategory =
  | 'feature'
  | 'bug_fix'
  | 'refactoring'
  | 'documentation'
  | 'security'
  // Content categories
  | 'creative'
  | 'game_design'
  | 'worldbuilding'
  | 'content_docs';

// Add new ContentProjectType
export type ContentProjectType =
  | 'card_game'
  | 'board_game'
  | 'ttrpg'
  | 'worldbuilding'
  | 'fiction'
  | 'business'
  | 'codebase_docs'
  | 'api_docs'
  | 'general';

// Helper to check if category is content-based
export const isContentCategory = (category: TaskCategory): boolean => {
  return ['creative', 'game_design', 'worldbuilding', 'content_docs'].includes(category);
};
```

#### 6.2 Update ClassificationFields Component

```typescript
// Add content categories to CATEGORY_OPTIONS
const CATEGORY_OPTIONS: TaskCategory[] = [
  'feature',
  'bug_fix',
  'refactoring',
  'documentation',
  'security',
  // Divider conceptually here
  'creative',
  'game_design',
  'worldbuilding',
  'content_docs',
];

// Add project type dropdown for content categories
{isContentCategory(category) && (
  <ContentTaskFields
    projectType={contentProjectType}
    onProjectTypeChange={setContentProjectType}
    targetAudience={targetAudience}
    onTargetAudienceChange={setTargetAudience}
  />
)}
```

#### 6.3 Create ContentTaskFields Component

```typescript
// apps/frontend/src/renderer/components/task-form/ContentTaskFields.tsx
interface ContentTaskFieldsProps {
  projectType: ContentProjectType;
  onProjectTypeChange: (type: ContentProjectType) => void;
  targetAudience?: string;
  onTargetAudienceChange?: (audience: string) => void;
}

export function ContentTaskFields({
  projectType,
  onProjectTypeChange,
  targetAudience,
  onTargetAudienceChange,
}: ContentTaskFieldsProps) {
  const { t } = useTranslation(['tasks', 'common']);

  return (
    <div className="content-task-fields">
      <FormField label={t('tasks:form.content.projectType')}>
        <Select
          value={projectType}
          onChange={onProjectTypeChange}
          options={PROJECT_TYPE_OPTIONS}
        />
      </FormField>

      <FormField label={t('tasks:form.content.targetAudience')}>
        <Input
          value={targetAudience}
          onChange={onTargetAudienceChange}
          placeholder={t('tasks:form.content.targetAudiencePlaceholder')}
        />
      </FormField>
    </div>
  );
}
```

#### 6.4 Testing Checklist

- [ ] Verify category dropdown shows content options
- [ ] Verify ContentTaskFields appears when content category selected
- [ ] Verify project type selection works
- [ ] Verify target audience field works
- [ ] Test form submission with content categories
- [ ] Verify task routes to content_runner in backend

---

### Phase 7: i18n Translations
**Status**: Not Started
**Priority**: Medium (blocks Phase 6 frontend work)

**Goal**: Add translation keys for content mode UI

**Files to modify**:
1. `apps/frontend/src/shared/i18n/locales/en/tasks.json` - English translations
2. `apps/frontend/src/shared/i18n/locales/fr/tasks.json` - French translations

**Detailed Implementation Plan**:

#### 7.1 English Translations (`en/tasks.json`)

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
      "contentTypePlaceholder": "e.g., New creature cards for water faction",
      "projectTypes": {
        "card_game": "Card Game",
        "board_game": "Board Game",
        "ttrpg": "Tabletop RPG",
        "worldbuilding": "Worldbuilding",
        "fiction": "Fiction/Creative Writing",
        "business": "Business Document",
        "codebase_docs": "Codebase Documentation",
        "api_docs": "API Documentation",
        "general": "General Content"
      }
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

#### 7.2 French Translations (`fr/tasks.json`)

```json
{
  "form": {
    "content": {
      "title": "Details du contenu",
      "projectType": "Type de projet",
      "selectProjectType": "Selectionnez le type de projet...",
      "targetAudience": "Public cible",
      "targetAudiencePlaceholder": "ex: Joueurs familiers avec MTG",
      "contentType": "Type de contenu",
      "contentTypePlaceholder": "ex: Nouvelles cartes de creatures pour la faction eau",
      "projectTypes": {
        "card_game": "Jeu de cartes",
        "board_game": "Jeu de plateau",
        "ttrpg": "JDR sur table",
        "worldbuilding": "Creation d'univers",
        "fiction": "Fiction/Ecriture creative",
        "business": "Document commercial",
        "codebase_docs": "Documentation du code",
        "api_docs": "Documentation API",
        "general": "Contenu general"
      }
    },
    "classification": {
      "values": {
        "category": {
          "creative": "Creatif",
          "game_design": "Conception de jeu",
          "worldbuilding": "Creation d'univers",
          "content_docs": "Documentation"
        }
      }
    }
  }
}
```

#### 7.3 Testing Checklist

- [ ] Verify all keys are present in both en and fr files
- [ ] Verify no hardcoded strings in ContentTaskFields component
- [ ] Test switching between languages shows correct translations
- [ ] Verify project type names translate correctly

---

## Recommended Implementation Order

Based on dependencies and risk, implement in this order:

```
┌─────────────────────────────────────────────────────────┐
│                  PHASE 4 (Backend)                       │
│  spec_runner.py integration + complexity.py              │
│  ↓                                                       │
│  Test: Content tasks route to content_runner             │
│  Test: Code tasks still work normally                    │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                 PHASE 7 (i18n)                           │
│  Add translation keys to en/fr files                     │
│  Required before Phase 6 can use translated strings      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              PHASE 6 (Frontend)                          │
│  Add content categories and ContentTaskFields            │
│  Wire up to backend content routing                      │
└─────────────────────────────────────────────────────────┘
```

**Risk Assessment**:
- **Phase 4**: Low risk - adds new path, doesn't modify existing code pipeline
- **Phase 7**: No risk - only adds new translation keys
- **Phase 6**: Medium risk - modifies existing task creation UI

---

## Session Log

### 2026-01-19 - Planning Session

**Session Branch**: `claude/creative-mode-planning-VrGAe`

**Work Done**:
- Created this dev journal (`guides/creative-mode-dev-journal.md`)
- Reviewed `guides/content-mode-summary.md` for completed work
- Documented all completed PRs and remaining phases (PR #1, PR #2)
- Created detailed implementation plans for Phases 4, 6, and 7
- Identified file locations and code structure for each phase
- Established recommended implementation order based on dependencies

**Key Findings**:
- `spec_runner.py` is in `apps/backend/runners/` not root
- `ComplexityAnalyzer` already has keyword-based detection we can extend
- Frontend uses i18n with react-i18next and namespace-based keys
- Existing test suite has 55 tests covering Content Mode core

**Files Reviewed**:
- `guides/content-mode-summary.md` - Feature documentation
- `guides/content-mode-implementation-plan.md` - Original design document (8 phases)
- `apps/backend/spec/complexity.py` - Complexity analysis (extend for content)
- `apps/backend/runners/spec_runner.py` - Main entry point (add content routing)
- `apps/backend/implementation_plan/enums.py` - Workflow types (add content types)
- `apps/backend/content_runner.py` - Content mode CLI (already complete)

**Next Steps**:
1. ~~Start Phase 4 implementation (spec_runner integration)~~ - DONE
2. ~~Test content task detection with real project directories~~ - DONE
3. Add i18n translations (Phase 7)
4. Implement frontend changes (Phase 6) after backend works

---

### 2026-01-19 - Phase 4 Implementation

**Session Branch**: `claude/creative-mode-planning-VrGAe`

**Work Done**:
- Implemented Phase 4: Integration with spec_runner.py
- Added content workflow types to `implementation_plan/enums.py`:
  - `CONTENT_CREATE`, `CONTENT_EXPAND`, `CONTENT_ITERATE`, `CONTENT_DOCUMENT`
- Added content detection to `spec/complexity.py`:
  - `is_content_task()` method using ContentProjectDetector
  - `get_content_project_type()` method for project type detection
  - Fallback keyword matching if content module unavailable
- Added content routing to `runners/spec_runner.py`:
  - Detects content tasks before creating SpecOrchestrator
  - Routes to `content_runner.cmd_plan()` for content tasks
  - Preserves existing code pipeline for non-content tasks

**Testing Results**:
- All content task descriptions correctly detected (5/5)
- All code task descriptions correctly NOT detected (5/5)
- All imports verified working
- Project type detection working correctly

**Files Modified**:
- `apps/backend/implementation_plan/enums.py` - Added 4 content workflow types
- `apps/backend/spec/complexity.py` - Added content detection methods
- `apps/backend/runners/spec_runner.py` - Added content routing logic

---

## Technical Notes

### Content Detection Logic

The `ContentProjectDetector` uses multiple signals:
1. Directory structure (looks for `cards/`, `rules/`, `characters/`, etc.)
2. File patterns (`.md` files with game/content keywords)
3. Task description keywords (card, deck, monster, campaign, etc.)

### Workflow Types

| Workflow | When to Use |
|----------|-------------|
| CREATE | Building new content from scratch |
| EXPAND | Adding to existing content |
| ITERATE | Refining/improving existing content |
| DOCUMENT | Generating documentation from code |

### Agent Pipeline

```
Content Task
    ↓
ContentPlannerAgent (creates plan)
    ↓
ContentCreatorAgent (creates drafts)
    ↓
ContentReviewerAgent (reviews quality)
    ↓
ContentEditorAgent (refines content)
    ↓
[Optional: ConsistencyCheckerAgent, BalanceAnalystAgent]
    ↓
Final Content
```

---

## References

- [Content Mode Summary](./content-mode-summary.md) - Complete feature documentation
- [Implementation Plan](./content-mode-implementation-plan.md) - Original design document
- [CLAUDE.md](../CLAUDE.md) - Project instructions and architecture
