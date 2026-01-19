# Content Mode Test Plan

Manual testing guide for verifying Content Mode functionality using codebase documentation as the test case.

## Overview

This test plan validates the Content Mode feature by using it to document the Auto-Claude codebase itself. This exercises all major components: detection, routing, planning, UI integration, and i18n.

---

## Prerequisites

- [ ] Backend dependencies installed: `cd apps/backend && uv pip install -r requirements.txt`
- [ ] Frontend dependencies installed: `cd apps/frontend && npm install`
- [ ] All tests passing: `PYTHONPATH=apps/backend pytest tests/test_content_mode.py -v`

---

## Test 1: Content Detection (CLI)

**Purpose:** Verify the ContentProjectDetector correctly identifies content tasks.

### Steps

```bash
cd apps/backend

python -c "
from content import ContentProjectDetector

detector = ContentProjectDetector()

# Test cases
tasks = [
    'Document the architecture of this codebase',
    'Create 5 water element cards with mana costs',
    'Write a new monster for the bestiary',
    'Fix the login button bug',  # Should be False
    'Add user authentication',   # Should be False
]

for task in tasks:
    is_content = detector.is_content_task(task)
    project_type = detector.detect_from_description(task) if is_content else 'N/A'
    print(f'{is_content:<6} | {str(project_type):<35} | {task[:50]}')
"
```

### Expected Results

| Is Content | Project Type | Task |
|------------|--------------|------|
| True | CODEBASE_DOCS | Document the architecture... |
| True | CARD_GAME | Create 5 water element cards... |
| True | TTRPG | Write a new monster for the bestiary |
| False | N/A | Fix the login button bug |
| False | N/A | Add user authentication |

### Verification

- [ ] Documentation tasks detected as `codebase_docs`
- [ ] Game content tasks detected correctly
- [ ] Code tasks NOT detected as content

---

## Test 2: Project Structure Detection (CLI)

**Purpose:** Verify detection from directory structure.

### Steps

```bash
cd apps/backend

# Test on Auto-Claude codebase
python content_runner.py --project /home/user/Auto-Claude --info
```

### Expected Results

```
Project Information:
  Path: /home/user/Auto-Claude
  Detected Type: codebase_docs (or general)
  Has existing content specs: No
```

### Verification

- [ ] Command runs without error
- [ ] Project type detected (codebase_docs or general)
- [ ] Path displayed correctly

---

## Test 3: Content Plan Creation (CLI)

**Purpose:** Verify content plans are created with correct structure.

### Steps

```bash
cd apps/backend

# Create a documentation plan
python content_runner.py \
  --project /home/user/Auto-Claude \
  --task "Create an architecture overview document for Auto-Claude including the agent pipeline, spec creation flow, and frontend-backend communication"
```

### Expected Results

1. Console shows: `Detected content task (codebase_docs) - using Content Mode`
2. Plan created at `.auto-claude/specs/content-XXX/content_plan.json`
3. Plan contains phases: Research → Draft → Review → Edit

### Verification

- [ ] "using Content Mode" message displayed
- [ ] `content_plan.json` file created
- [ ] Plan has `project_type: "codebase_docs"`
- [ ] Plan has `workflow_type: "create"` or `"document"`
- [ ] Plan has multiple phases with subtasks

### Inspect the Plan

```bash
# View the created plan
cat /home/user/Auto-Claude/.auto-claude/specs/content-*/content_plan.json | head -50
```

---

## Test 4: spec_runner.py Routing

**Purpose:** Verify content tasks route to Content Mode instead of code pipeline.

### Steps

```bash
cd apps/backend

# Run spec_runner with a content task
python runners/spec_runner.py \
  --task "Document the security model and authentication flow" \
  --project-dir /home/user/Auto-Claude \
  --no-build
```

### Expected Results

Console output should include:
```
Detected content task (codebase_docs) - using Content Mode
```

### Verification

- [ ] Task detected as content
- [ ] Routing message displayed
- [ ] Content Mode pipeline invoked (not code pipeline)

---

## Test 5: Frontend UI - Content Categories

**Purpose:** Verify content categories appear in task creation UI.

### Steps

1. Start the frontend:
   ```bash
   npm run dev
   ```

2. Click "Create New Task" or the + button

3. Look at the Category dropdown in Classification section

### Expected Results

Category dropdown should include:
- Feature
- Bug Fix
- Refactoring
- Documentation
- Security
- **Creative** ← Content Mode
- **Game Design** ← Content Mode
- **Worldbuilding** ← Content Mode
- **Content Docs** ← Content Mode

### Verification

- [ ] All 4 content categories visible
- [ ] Categories have correct labels
- [ ] Categories are selectable

---

## Test 6: Frontend UI - Content Fields

**Purpose:** Verify ContentTaskFields component renders when content category selected.

### Steps

1. In task creation wizard, select **"Content Docs"** category

2. Observe that new fields appear below the classification section

### Expected Results

New "Content Details" section should appear with:
- **Project Type** dropdown (9 options)
- **Target Audience** text input
- **Content Type** text input

### Verification

- [ ] "Content Details" section appears
- [ ] Project Type dropdown has all 9 options:
  - Card Game
  - Board Game
  - TTRPG
  - Worldbuilding
  - Fiction/Creative Writing
  - Business Document
  - Codebase Docs
  - API Docs
  - General
- [ ] Target Audience field accepts text
- [ ] Content Type field accepts text
- [ ] Fields disappear when non-content category selected

---

## Test 7: Frontend UI - i18n Translations

**Purpose:** Verify all content mode labels are translated.

### Steps

1. Open Settings (gear icon)
2. Change language to French
3. Navigate back to task creation
4. Select a content category

### Expected Results (French)

| English | French |
|---------|--------|
| Creative | Créatif |
| Game Design | Conception de jeu |
| Worldbuilding | Création d'univers |
| Content Docs | Docs de contenu |
| Content Details | Détails du contenu |
| Project Type | Type de projet |
| Target Audience | Public cible |
| Content Type | Type de contenu |
| Card Game | Jeu de cartes |
| TTRPG | JDR sur table |

### Verification

- [ ] Category labels translated
- [ ] Content Details section title translated
- [ ] All project type options translated
- [ ] Field labels translated
- [ ] Placeholder text translated

---

## Test 8: End-to-End Task Creation

**Purpose:** Full workflow test creating a documentation task.

### Steps

1. Start frontend: `npm run dev`

2. Create new task with:
   - **Description:** "Create comprehensive documentation for the Auto-Claude codebase including architecture overview, module descriptions, and developer setup guide"
   - **Category:** Content Docs
   - **Project Type:** Codebase Docs
   - **Target Audience:** "Developers new to Auto-Claude"
   - **Content Type:** "Architecture docs, API reference, setup guide"

3. Submit the task

### Expected Results

1. Task created successfully
2. Task appears in backlog
3. Console/logs show Content Mode routing
4. Spec directory created with content_plan.json

### Verification

- [ ] Task created without errors
- [ ] Task visible in kanban board
- [ ] Content metadata saved correctly
- [ ] Content plan generated (check spec directory)

---

## Test 9: Project Scaffolding

**Purpose:** Verify project templates are created correctly.

### Steps

```bash
cd apps/backend

# Create a test directory
mkdir -p /tmp/test-card-game

# Scaffold a card game project
python content_runner.py --project /tmp/test-card-game --init card_game

# Inspect the structure
find /tmp/test-card-game -type f | head -20
```

### Expected Results

```
/tmp/test-card-game/
├── _index.md
├── rules/
│   ├── core-rules.md
│   └── keywords.md
├── cards/
│   └── _template.md
├── style-guide/
│   ├── naming-conventions.md
│   └── power-levels.md
└── playtests/
```

### Verification

- [ ] Directory structure created
- [ ] Template files have content
- [ ] _index.md exists with project overview

### Cleanup

```bash
rm -rf /tmp/test-card-game
```

---

## Test 10: Verify Content Spec Directory

**Purpose:** Verify content specs are stored correctly.

### Steps

```bash
cd apps/backend

# After creating a content spec, check the directory structure
ls -la /home/user/Auto-Claude/.auto-claude/specs/content-*/

# View content plan structure
cat /home/user/Auto-Claude/.auto-claude/specs/content-*/content_plan.json | head -30
```

### Expected Results

Content spec directory should contain:
- `content_plan.json` - The content plan with phases and subtasks
- Additional files created during execution

### Verification

- [ ] Spec directory created with `content-` prefix
- [ ] `content_plan.json` exists with valid JSON
- [ ] Plan contains project_type, workflow_type, phases

### Note

The `--list` flag is documented but not yet implemented in content_runner.py.
Use `ls .auto-claude/specs/content-*` to list content specs manually.

---

## Test Summary Checklist

### Backend Components

| Component | Test | Status |
|-----------|------|--------|
| ContentProjectDetector | Test 1, 2 | ☐ |
| Content routing | Test 4 | ☐ |
| ContentPlan creation | Test 3 | ☐ |
| Project scaffolding | Test 9 | ☐ |
| Spec listing | Test 10 | ☐ |

### Frontend Components

| Component | Test | Status |
|-----------|------|--------|
| Content categories | Test 5 | ☐ |
| ContentTaskFields | Test 6 | ☐ |
| i18n translations | Test 7 | ☐ |
| End-to-end flow | Test 8 | ☐ |

### Integration

| Integration | Test | Status |
|-------------|------|--------|
| spec_runner routing | Test 4 | ☐ |
| Frontend → Backend | Test 8 | ☐ |

---

## Sample Test Tasks

Use these task descriptions for testing different content types:

### Codebase Documentation
```
Document the high-level architecture of Auto-Claude including:
- Agent pipeline (planner → coder → QA)
- Spec creation flow
- Frontend-backend communication
- Security model
```

### API Reference
```
Generate API documentation for the backend Python modules:
- core/client.py - Claude SDK client
- core/security.py - Command allowlisting
- core/auth.py - OAuth token management
```

### Developer Guide
```
Create a getting started guide for new contributors including:
- Environment setup (Python, Node.js)
- Running tests
- Understanding the codebase structure
- Making your first contribution
```

### Card Game (Alternative Test)
```
Create 5 water element creature cards for a Pokemon-style card game:
- 2 basic creatures
- 2 evolution creatures
- 1 legendary creature
Include mana costs, HP, and abilities.
```

---

## Known Issues & Gaps

Issues discovered during testing:

### 1. Detection Threshold Too High

Some documentation tasks aren't detected as content tasks because `is_content_task()` requires `content_score > code_score + 1`.

**Examples that fail detection:**
- "Document the architecture" (1 content keyword)
- "Write a README for the project" (1 content keyword)
- "Generate API docs for the backend" (contains "api" which is in CODE_TASK_KEYWORDS)

**Workaround:** Use more descriptive task text with multiple content keywords:
- "Create comprehensive documentation for the codebase architecture" ✅
- "Write a developer guide with setup instructions" ✅

### 2. `--list` Flag Not Implemented

The `--list` flag is documented but not implemented in `content_runner.py`.

**Workaround:** Use `ls .auto-claude/specs/content-*` to list content specs.

### 3. Project Type Detection

Auto-Claude codebase is detected as `knowledge_base` (not `codebase_docs`) because:
- Has `guides/` directory which matches knowledge_base indicators
- Missing `docs/api/` or `docs/architecture/` directories that would match codebase_docs

This is acceptable behavior - knowledge_base is a valid type for this use case.

---

## Troubleshooting

### Content task not detected

Check the detection keywords in `apps/backend/content/detector.py`:
- Documentation: "document", "docs", "readme", "guide"
- Creative: "write", "story", "world", "lore"
- Game: "card", "game", "creature", "ability"

### ContentTaskFields not appearing

1. Verify category is a content category (creative, game_design, worldbuilding, content_docs)
2. Check browser console for errors
3. Verify `CONTENT_CATEGORIES` in `apps/frontend/src/shared/types/task.ts`

### i18n keys missing

Check translation files:
- `apps/frontend/src/shared/i18n/locales/en/tasks.json`
- `apps/frontend/src/shared/i18n/locales/fr/tasks.json`

Look for `form.content.*` and `form.classification.values.category.*` keys.

---

## Test Results

| Date | Tester | Tests Passed | Tests Failed | Notes |
|------|--------|--------------|--------------|-------|
| | | /10 | | |

---

## Related Documentation

- [Content Mode Summary](./content-mode-summary.md)
- [Content Mode Implementation Plan](./content-mode-implementation-plan.md)
- [Creative Mode Dev Journal](./creative-mode-dev-journal.md)
