# Content Mode Implementation Plan

This document outlines the implementation plan for adding Content Mode to Auto Claude, enabling autonomous workflows for creative projects (card games, board games, TTRPGs, fiction) and documentation projects.

## Overview

Content Mode adds a parallel pipeline to Auto Claude's existing code-focused workflow. Instead of code → test → deploy, Content Mode handles concept → draft → review → refine cycles for non-code content.

## Implementation Phases

### Phase 1: Core Enums and Models (Backend)

**Files to Create:**

#### `apps/backend/content/enums.py`
```python
"""Enumerations for Content Mode workflows."""
from enum import Enum

class ContentProjectType(str, Enum):
    """Types of content projects."""
    # Creative
    CARD_GAME = "card_game"
    BOARD_GAME = "board_game"
    TTRPG = "ttrpg"
    WORLDBUILDING = "worldbuilding"
    FICTION = "fiction"
    BUSINESS = "business"

    # Documentation
    CODEBASE_DOCS = "codebase_docs"
    API_DOCS = "api_docs"
    ARCHITECTURE = "architecture"
    KNOWLEDGE_BASE = "knowledge_base"

    # General
    GENERAL = "general"


class ContentWorkflowType(str, Enum):
    """Workflow types for content projects."""
    CREATE = "create"           # New content from scratch
    EXPAND = "expand"           # Add to existing content
    ITERATE = "iterate"         # Refine based on feedback
    GENERATE = "generate"       # Generate from source (code → docs)
    AUDIT = "audit"             # Coverage/freshness check
    BALANCE = "balance"         # Game balance pass


class ContentPhaseType(str, Enum):
    """Phase types for content workflows."""
    # Ideation
    CONCEPT = "concept"
    RESEARCH = "research"

    # Creation
    OUTLINE = "outline"
    DRAFT = "draft"

    # Refinement
    REVIEW = "review"
    REVISE = "revise"
    POLISH = "polish"

    # Validation
    CONSISTENCY = "consistency"
    BALANCE = "balance"

    # Documentation-specific
    ANALYSIS = "analysis"
    VERIFICATION = "verification"

    # Finalization
    FINALIZE = "finalize"


class ContentVerificationType(str, Enum):
    """Verification types for content subtasks."""
    TEMPLATE_COMPLIANCE = "template_compliance"
    COMPLETENESS = "completeness"
    CONSISTENCY_CHECK = "consistency_check"
    STYLE_REVIEW = "style_review"
    ACCURACY_CHECK = "accuracy_check"
    PEER_REVIEW = "peer_review"
    BALANCE_REVIEW = "balance_review"


class ContentArtifactType(str, Enum):
    """Types of content artifacts."""
    CONTENT = "content"           # Primary deliverable
    ANALYSIS = "analysis"         # Research/analysis output
    VALIDATION = "validation"     # Review/check results
    REVISION = "revision"         # Updated content
    INDEXING = "indexing"         # Index updates
    TEMPLATE = "template"         # New template
    REPORT = "report"             # Reports (balance, consistency, etc.)
```

#### `apps/backend/content/models.py`
```python
"""Data models for Content Mode."""
from dataclasses import dataclass, field
from typing import Optional
from .enums import *


@dataclass
class ContentSubtask:
    """A subtask in a content workflow."""
    id: str
    description: str
    artifact_type: ContentArtifactType
    status: str = "pending"  # pending, in_progress, completed, blocked

    # Input references
    files_to_read: list[str] = field(default_factory=list)
    template: Optional[str] = None

    # Output
    output: Optional[str] = None

    # Verification
    verification: Optional[dict] = None

    # Dependencies
    depends_on: list[str] = field(default_factory=list)


@dataclass
class ContentPhase:
    """A phase in a content workflow."""
    id: str
    name: str
    type: ContentPhaseType
    description: str
    subtasks: list[ContentSubtask] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)


@dataclass
class ContentPlan:
    """A complete content creation plan."""
    project_name: str
    project_type: ContentProjectType
    workflow_type: ContentWorkflowType
    workflow_rationale: str

    context: dict = field(default_factory=dict)
    phases: list[ContentPhase] = field(default_factory=list)
    deliverables: list[dict] = field(default_factory=list)
    quality_criteria: dict = field(default_factory=dict)

    # Domain-specific
    game_specific: Optional[dict] = None
    doc_specific: Optional[dict] = None

    summary: dict = field(default_factory=dict)
```

#### `apps/backend/content/detector.py`
```python
"""Detect content project types and characteristics."""
import os
from pathlib import Path
from .enums import ContentProjectType


class ContentProjectDetector:
    """Detects project type from directory structure and files."""

    INDICATORS = {
        ContentProjectType.CARD_GAME: {
            "directories": ["cards", "rules", "keywords", "sets"],
            "files": ["keywords.md", "power-levels.md"],
            "keywords": ["card", "deck", "mana", "cost", "rarity"]
        },
        ContentProjectType.BOARD_GAME: {
            "directories": ["rules", "components", "boards"],
            "files": ["setup.md", "turn-structure.md"],
            "keywords": ["board", "token", "dice", "player"]
        },
        ContentProjectType.TTRPG: {
            "directories": ["bestiary", "adventures", "characters", "items"],
            "files": ["core-mechanics.md"],
            "keywords": ["monster", "spell", "dungeon", "campaign", "dm", "gm"]
        },
        ContentProjectType.WORLDBUILDING: {
            "directories": ["world", "lore", "factions", "regions"],
            "files": ["history.md", "timeline.md"],
            "keywords": ["lore", "faction", "kingdom", "history"]
        },
        ContentProjectType.FICTION: {
            "directories": ["chapters", "characters", "outline"],
            "files": ["outline.md", "characters.md"],
            "keywords": ["chapter", "story", "novel", "character arc"]
        },
        ContentProjectType.CODEBASE_DOCS: {
            "directories": ["docs/api", "docs/architecture"],
            "files": ["docs/_index.md"],
            "keywords": ["endpoint", "api", "component", "service"]
        },
        ContentProjectType.API_DOCS: {
            "directories": ["docs/api"],
            "files": ["openapi.yaml", "swagger.json"],
            "keywords": ["endpoint", "request", "response", "api"]
        },
    }

    def detect(self, project_dir: str) -> ContentProjectType:
        """Detect project type from directory."""
        scores = {pt: 0 for pt in ContentProjectType}

        for project_type, indicators in self.INDICATORS.items():
            # Check directories
            for dir_name in indicators.get("directories", []):
                if (Path(project_dir) / dir_name).exists():
                    scores[project_type] += 2

            # Check files
            for file_name in indicators.get("files", []):
                if (Path(project_dir) / file_name).exists():
                    scores[project_type] += 3

        # Return highest scoring type, or GENERAL if no matches
        best_type = max(scores, key=scores.get)
        return best_type if scores[best_type] > 0 else ContentProjectType.GENERAL

    def detect_from_description(self, description: str) -> ContentProjectType:
        """Detect project type from task description."""
        description_lower = description.lower()

        for project_type, indicators in self.INDICATORS.items():
            keywords = indicators.get("keywords", [])
            matches = sum(1 for kw in keywords if kw in description_lower)
            if matches >= 2:
                return project_type

        return ContentProjectType.GENERAL
```

---

### Phase 2: Content Agents (Backend)

**Files to Create:**

#### `apps/backend/content/agents/__init__.py`
```python
"""Content Mode agents."""
from .planner import ContentPlannerAgent
from .creator import ContentCreatorAgent
from .reviewer import ContentReviewerAgent
from .editor import ContentEditorAgent
from .consistency_checker import ConsistencyCheckerAgent
from .balance_analyst import BalanceAnalystAgent
from .code_analyzer import CodeAnalyzerAgent
```

#### `apps/backend/content/agents/planner.py`
```python
"""Content Planner Agent - creates content workflow plans."""
from pathlib import Path
from core.client import create_client


class ContentPlannerAgent:
    """Plans content creation workflows."""

    def __init__(self, project_dir: str, spec_dir: str):
        self.project_dir = project_dir
        self.spec_dir = spec_dir
        self.prompt_path = Path(__file__).parent.parent.parent / "prompts" / "content_planner.md"

    def create_plan(self, brief: str) -> dict:
        """Create a content plan from a brief."""
        client = create_client(
            project_dir=self.project_dir,
            spec_dir=self.spec_dir,
            model="claude-sonnet-4-5-20250929",
            agent_type="content_planner",
        )

        prompt = self._load_prompt()
        response = client.create_agent_session(
            name="content-planner-session",
            starting_message=f"{prompt}\n\n## CONTENT BRIEF\n\n{brief}"
        )

        return self._parse_plan(response)

    def _load_prompt(self) -> str:
        return self.prompt_path.read_text()

    def _parse_plan(self, response) -> dict:
        # Parse content_plan.json from agent output
        pass
```

#### `apps/backend/content/agents/creator.py`
```python
"""Content Creator Agent - creates content following plans."""
from pathlib import Path
from core.client import create_client


class ContentCreatorAgent:
    """Creates content following templates and style guides."""

    def __init__(self, project_dir: str, spec_dir: str):
        self.project_dir = project_dir
        self.spec_dir = spec_dir
        self.prompt_path = Path(__file__).parent.parent.parent / "prompts" / "content_creator.md"

    def execute_subtask(self, subtask: dict, plan: dict) -> dict:
        """Execute a content creation subtask."""
        client = create_client(
            project_dir=self.project_dir,
            spec_dir=self.spec_dir,
            model="claude-sonnet-4-5-20250929",
            agent_type="content_creator",
        )

        prompt = self._load_prompt()
        context = self._build_context(subtask, plan)

        response = client.create_agent_session(
            name="content-creator-session",
            starting_message=f"{prompt}\n\n## CURRENT SUBTASK\n\n{context}"
        )

        return self._parse_result(response)

    def _load_prompt(self) -> str:
        return self.prompt_path.read_text()

    def _build_context(self, subtask: dict, plan: dict) -> str:
        # Build context from subtask and plan
        pass

    def _parse_result(self, response) -> dict:
        pass
```

*Similar structure for:*
- `apps/backend/content/agents/reviewer.py` (ContentReviewerAgent)
- `apps/backend/content/agents/editor.py` (ContentEditorAgent)
- `apps/backend/content/agents/consistency_checker.py` (ConsistencyCheckerAgent)
- `apps/backend/content/agents/balance_analyst.py` (BalanceAnalystAgent)
- `apps/backend/content/agents/code_analyzer.py` (CodeAnalyzerAgent)

---

### Phase 3: Content Runner (Backend)

**Files to Create:**

#### `apps/backend/content_runner.py`
```python
"""Main entry point for Content Mode."""
import argparse
from pathlib import Path
from content.detector import ContentProjectDetector
from content.agents import (
    ContentPlannerAgent,
    ContentCreatorAgent,
    ContentReviewerAgent,
    ContentEditorAgent,
)


def main():
    parser = argparse.ArgumentParser(description="Auto Claude Content Mode")
    parser.add_argument("--project", required=True, help="Project directory")
    parser.add_argument("--spec", help="Spec directory or number")
    parser.add_argument("--task", help="Task description for new content")
    parser.add_argument("--plan", action="store_true", help="Create plan only")
    parser.add_argument("--execute", action="store_true", help="Execute existing plan")
    parser.add_argument("--review", action="store_true", help="Run review phase")

    args = parser.parse_args()

    # Detect project type
    detector = ContentProjectDetector()
    project_type = detector.detect(args.project)

    print(f"Detected project type: {project_type.value}")

    if args.task:
        # Create new spec and plan
        run_planning(args.project, args.task, project_type)
    elif args.execute:
        # Execute existing plan
        run_execution(args.project, args.spec)
    elif args.review:
        # Run review phase
        run_review(args.project, args.spec)


def run_planning(project_dir: str, task: str, project_type):
    """Create a content plan for a task."""
    # Implementation
    pass


def run_execution(project_dir: str, spec: str):
    """Execute a content plan."""
    # Implementation
    pass


def run_review(project_dir: str, spec: str):
    """Run content review."""
    # Implementation
    pass


if __name__ == "__main__":
    main()
```

---

### Phase 4: Integration with Existing System

**Files to Modify:**

#### `apps/backend/implementation_plan/enums.py`
Add content workflow types to existing enums:
```python
class WorkflowType(str, Enum):
    # Existing
    FEATURE = "feature"
    REFACTOR = "refactor"
    INVESTIGATION = "investigation"
    MIGRATION = "migration"
    SIMPLE = "simple"

    # NEW: Content workflows
    CONTENT_CREATE = "content_create"
    CONTENT_EXPAND = "content_expand"
    CONTENT_ITERATE = "content_iterate"
    CONTENT_DOCUMENT = "content_document"
```

#### `apps/backend/spec/complexity.py`
Add content detection keywords:
```python
# Add to ComplexityAnalyzer class

CONTENT_KEYWORDS = {
    "card_game": ["card", "deck", "mana", "creature", "spell", "keyword"],
    "board_game": ["board", "token", "dice", "turn", "player", "setup"],
    "ttrpg": ["monster", "dungeon", "campaign", "spell", "character", "dm"],
    "documentation": ["document", "api", "endpoint", "guide", "architecture"],
    "creative": ["write", "story", "world", "lore", "design", "create"],
}

def is_content_task(self, description: str) -> bool:
    """Check if task is a content task rather than code task."""
    description_lower = description.lower()
    for category, keywords in self.CONTENT_KEYWORDS.items():
        matches = sum(1 for kw in keywords if kw in description_lower)
        if matches >= 2:
            return True
    return False
```

#### `apps/backend/spec_runner.py`
Add content mode detection and routing:
```python
# Add to spec creation flow

from spec.complexity import ComplexityAnalyzer
from content_runner import run_planning as run_content_planning

def create_spec(task: str, project_dir: str):
    analyzer = ComplexityAnalyzer()

    # Check if this is a content task
    if analyzer.is_content_task(task):
        print("Detected content task - using Content Mode")
        return run_content_planning(project_dir, task)
    else:
        # Existing code workflow
        return run_code_planning(project_dir, task)
```

---

### Phase 5: Project Templates (Backend)

**Files to Create:**

#### `apps/backend/content/templates/`
Directory containing scaffolding templates for new content projects:

```
templates/
├── card_game/
│   ├── _index.md
│   ├── rules/
│   │   ├── core-rules.md
│   │   └── keywords.md
│   ├── cards/
│   │   └── _template.md
│   ├── style-guide/
│   │   ├── naming.md
│   │   └── power-levels.md
│   └── playtests/
│       └── .gitkeep
├── ttrpg/
│   ├── _index.md
│   ├── rules/
│   ├── bestiary/
│   │   └── _template.md
│   ├── adventures/
│   │   └── _template.md
│   └── world/
├── board_game/
│   └── ...
├── codebase_docs/
│   ├── _index.md
│   ├── architecture/
│   │   ├── decisions/
│   │   │   └── _template.md
│   │   └── components/
│   │       └── _template.md
│   ├── api/
│   │   └── _template.md
│   └── guides/
└── general/
    └── _index.md
```

#### `apps/backend/content/scaffold.py`
```python
"""Scaffold new content projects."""
import shutil
from pathlib import Path
from .enums import ContentProjectType


class ContentProjectScaffolder:
    """Create new content project from templates."""

    TEMPLATES_DIR = Path(__file__).parent / "templates"

    def scaffold(self, project_dir: str, project_type: ContentProjectType):
        """Create project structure from template."""
        template_dir = self.TEMPLATES_DIR / project_type.value

        if not template_dir.exists():
            template_dir = self.TEMPLATES_DIR / "general"

        # Copy template to project
        for item in template_dir.rglob("*"):
            if item.is_file():
                relative = item.relative_to(template_dir)
                dest = Path(project_dir) / relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(item, dest)

        print(f"Scaffolded {project_type.value} project in {project_dir}")
```

---

### Phase 6: Frontend Integration

**Files to Modify:**

#### `apps/frontend/src/shared/types/index.ts`
Add content task types:
```typescript
export type TaskCategory =
  | 'feature'
  | 'bug_fix'
  | 'refactoring'
  | 'documentation'
  | 'security'
  // NEW: Content categories
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
  | 'business'
  | 'codebase_docs'
  | 'api_docs'
  | 'general';
```

#### `apps/frontend/src/renderer/components/task-form/ClassificationFields.tsx`
Add content categories:
```typescript
const CATEGORY_OPTIONS: TaskCategory[] = [
  'feature',
  'bug_fix',
  'refactoring',
  'documentation',
  'security',
  // NEW
  'creative',
  'game_design',
  'worldbuilding',
  'content_docs'
];
```

#### `apps/frontend/src/renderer/components/TaskCreationWizard.tsx`
Add content-specific form fields:
```typescript
// Show different fields based on category
{isContentCategory(category) && (
  <ContentTaskFields
    projectType={contentProjectType}
    onProjectTypeChange={setContentProjectType}
    targetAudience={targetAudience}
    onTargetAudienceChange={setTargetAudience}
    contentType={contentType}
    onContentTypeChange={setContentType}
  />
)}
```

**Files to Create:**

#### `apps/frontend/src/renderer/components/task-form/ContentTaskFields.tsx`
```typescript
/**
 * Additional form fields for content tasks
 */
import { useTranslation } from 'react-i18next';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Input } from '../ui/input';

interface ContentTaskFieldsProps {
  projectType: string;
  onProjectTypeChange: (value: string) => void;
  targetAudience: string;
  onTargetAudienceChange: (value: string) => void;
  contentType: string;
  onContentTypeChange: (value: string) => void;
}

export function ContentTaskFields({
  projectType,
  onProjectTypeChange,
  targetAudience,
  onTargetAudienceChange,
  contentType,
  onContentTypeChange,
}: ContentTaskFieldsProps) {
  const { t } = useTranslation('tasks');

  return (
    <div className="space-y-4 p-4 rounded-lg border border-border bg-muted/30">
      <h4 className="text-sm font-medium">{t('form.content.title')}</h4>

      {/* Project Type */}
      <div className="space-y-2">
        <Label>{t('form.content.projectType')}</Label>
        <Select value={projectType} onValueChange={onProjectTypeChange}>
          <SelectTrigger>
            <SelectValue placeholder={t('form.content.selectProjectType')} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="card_game">Card Game</SelectItem>
            <SelectItem value="board_game">Board Game</SelectItem>
            <SelectItem value="ttrpg">TTRPG / D&D</SelectItem>
            <SelectItem value="worldbuilding">Worldbuilding</SelectItem>
            <SelectItem value="fiction">Fiction</SelectItem>
            <SelectItem value="codebase_docs">Codebase Documentation</SelectItem>
            <SelectItem value="general">General Creative</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Target Audience */}
      <div className="space-y-2">
        <Label>{t('form.content.targetAudience')}</Label>
        <Input
          value={targetAudience}
          onChange={(e) => onTargetAudienceChange(e.target.value)}
          placeholder={t('form.content.targetAudiencePlaceholder')}
        />
      </div>

      {/* Content Type */}
      <div className="space-y-2">
        <Label>{t('form.content.contentType')}</Label>
        <Input
          value={contentType}
          onChange={(e) => onContentTypeChange(e.target.value)}
          placeholder={t('form.content.contentTypePlaceholder')}
        />
      </div>
    </div>
  );
}
```

---

### Phase 7: i18n Updates

**Files to Modify:**

#### `apps/frontend/src/shared/i18n/locales/en/tasks.json`
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

---

### Phase 8: Testing

**Files to Create:**

#### `tests/test_content_mode.py`
```python
"""Tests for Content Mode."""
import pytest
from apps.backend.content.enums import ContentProjectType, ContentWorkflowType
from apps.backend.content.detector import ContentProjectDetector
from apps.backend.content.models import ContentPlan, ContentPhase, ContentSubtask


class TestContentProjectDetector:
    def test_detect_card_game(self, tmp_path):
        # Create card game structure
        (tmp_path / "cards").mkdir()
        (tmp_path / "rules").mkdir()
        (tmp_path / "keywords.md").touch()

        detector = ContentProjectDetector()
        result = detector.detect(str(tmp_path))

        assert result == ContentProjectType.CARD_GAME

    def test_detect_ttrpg(self, tmp_path):
        (tmp_path / "bestiary").mkdir()
        (tmp_path / "adventures").mkdir()

        detector = ContentProjectDetector()
        result = detector.detect(str(tmp_path))

        assert result == ContentProjectType.TTRPG

    def test_detect_from_description(self):
        detector = ContentProjectDetector()

        assert detector.detect_from_description(
            "Create 5 new creature cards with mana costs"
        ) == ContentProjectType.CARD_GAME

        assert detector.detect_from_description(
            "Design a new dungeon for the campaign"
        ) == ContentProjectType.TTRPG


class TestContentModels:
    def test_content_subtask(self):
        subtask = ContentSubtask(
            id="subtask-1",
            description="Create flame elemental card",
            artifact_type="content",
            template="cards/_template.md",
            output="cards/fire/flame-elemental.md"
        )

        assert subtask.status == "pending"
        assert subtask.template == "cards/_template.md"

    def test_content_plan(self):
        plan = ContentPlan(
            project_name="Core Set Expansion",
            project_type=ContentProjectType.CARD_GAME,
            workflow_type=ContentWorkflowType.CREATE,
            workflow_rationale="Creating new cards from scratch"
        )

        assert plan.project_type == ContentProjectType.CARD_GAME
```

---

## File Summary

### New Files to Create

| File | Purpose |
|------|---------|
| `apps/backend/content/__init__.py` | Content module init |
| `apps/backend/content/enums.py` | Content enumerations |
| `apps/backend/content/models.py` | Content data models |
| `apps/backend/content/detector.py` | Project type detection |
| `apps/backend/content/scaffold.py` | Project scaffolding |
| `apps/backend/content/agents/__init__.py` | Agents module init |
| `apps/backend/content/agents/planner.py` | Content Planner agent |
| `apps/backend/content/agents/creator.py` | Content Creator agent |
| `apps/backend/content/agents/reviewer.py` | Content Reviewer agent |
| `apps/backend/content/agents/editor.py` | Content Editor agent |
| `apps/backend/content/agents/consistency_checker.py` | Consistency Checker agent |
| `apps/backend/content/agents/balance_analyst.py` | Balance Analyst agent |
| `apps/backend/content/agents/code_analyzer.py` | Code Analyzer agent |
| `apps/backend/content_runner.py` | Content Mode entry point |
| `apps/backend/content/templates/` | Project templates directory |
| `apps/backend/prompts/content_planner.md` | ✅ Created |
| `apps/backend/prompts/content_creator.md` | ✅ Created |
| `apps/backend/prompts/content_reviewer.md` | ✅ Created |
| `apps/backend/prompts/content_editor.md` | ✅ Created |
| `apps/backend/prompts/content_consistency_checker.md` | ✅ Created |
| `apps/backend/prompts/game_balance_analyst.md` | ✅ Created |
| `apps/backend/prompts/doc_code_analyzer.md` | ✅ Created |
| `apps/frontend/src/renderer/components/task-form/ContentTaskFields.tsx` | Content form fields |
| `tests/test_content_mode.py` | Content Mode tests |

### Files to Modify

| File | Changes |
|------|---------|
| `apps/backend/implementation_plan/enums.py` | Add content workflow types |
| `apps/backend/spec/complexity.py` | Add content detection |
| `apps/backend/spec_runner.py` | Route to content mode |
| `apps/frontend/src/shared/types/index.ts` | Add content types |
| `apps/frontend/src/renderer/components/task-form/ClassificationFields.tsx` | Add content categories |
| `apps/frontend/src/renderer/components/TaskCreationWizard.tsx` | Add content fields |
| `apps/frontend/src/shared/i18n/locales/en/tasks.json` | Add translations |
| `apps/frontend/src/shared/i18n/locales/fr/tasks.json` | Add translations |

---

## Implementation Order

1. **Week 1**: Core enums, models, detector (Phase 1)
2. **Week 2**: Agent implementations (Phase 2)
3. **Week 3**: Content runner and integration (Phase 3-4)
4. **Week 4**: Project templates (Phase 5)
5. **Week 5**: Frontend integration (Phase 6-7)
6. **Week 6**: Testing and polish (Phase 8)

---

## CLI Usage (Target)

```bash
# Create new content project
python content_runner.py --project ./my-card-game --init card_game

# Create content plan from task
python content_runner.py --project ./my-card-game --task "Create 5 water faction cards"

# Execute content plan
python content_runner.py --project ./my-card-game --spec 001 --execute

# Run review
python content_runner.py --project ./my-card-game --spec 001 --review

# Run consistency check
python content_runner.py --project ./my-card-game --spec 001 --consistency

# Run balance analysis (games only)
python content_runner.py --project ./my-card-game --spec 001 --balance
```

---

## Success Criteria

1. **Detection**: System correctly identifies content vs code tasks
2. **Planning**: Content Planner creates appropriate phase-based plans
3. **Execution**: Content Creator follows templates and style guides
4. **Quality**: Reviewer and Editor improve content quality
5. **Consistency**: Consistency Checker catches cross-reference issues
6. **Balance**: Balance Analyst identifies power level issues (games)
7. **Documentation**: Code Analyzer generates accurate docs from code
8. **Frontend**: Users can create content tasks through UI
