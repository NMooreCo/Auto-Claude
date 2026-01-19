# Content Mode Architecture Gap Analysis
 
This document analyzes the fundamental architectural disconnect in the Content Mode feature that was identified during integration testing.
 
---
 
## Executive Summary
 
Content Mode was designed as a **parallel system** to the existing code pipeline, but was integrated with the frontend as if it were **part of the same system**. This created a broken data flow where:
 
1. Frontend creates tasks expecting `implementation_plan.json`
2. Content Mode creates `content_plan.json` instead
3. Frontend cannot track or display Content Mode tasks
 
---
 
## The Two Systems
 
### Code Pipeline (Existing)
 
```
Frontend Creates Task
        ↓
    spec_runner.py
        ↓
   SpecOrchestrator
        ↓
  implementation_plan.json  ← Frontend reads this
        ↓
     run.py
        ↓
   Planner Agent
        ↓
    Coder Agent
        ↓
      QA Agent
```
 
**Key File**: `implementation_plan.json`
- Contains: phases, subtasks, status, progress
- Frontend watches this file for updates
- ProjectStore reads this to display task status
 
### Content Pipeline (New)
 
```
Frontend Creates Task
        ↓
    spec_runner.py
        ↓
  ContentProjectDetector → Detects content task
        ↓
   content_runner.py
        ↓
  ContentPlannerAgent
        ↓
    content_plan.json  ← Frontend CANNOT read this
        ↓
  ContentCreatorAgent
        ↓
  ContentReviewerAgent
        ↓
   ContentEditorAgent
```
 
**Key File**: `content_plan.json`
- Contains: phases, subtasks, different structure
- Frontend does NOT watch this file
- ProjectStore does NOT read this
 
---
 
## What Was Implemented vs What Was Needed
 
### Phase 4: Backend Integration ✅ (Implemented)
 
**What was done:**
- `spec_runner.py` routes content tasks to `content_runner.py`
- `complexity.py` detects content vs code tasks
- `enums.py` has content workflow types
 
**What was missing:**
- No bridge between `content_plan.json` and `implementation_plan.json`
- No way for frontend to track content tasks
 
### Phase 6: Frontend Integration ⚠️ (Partially Implemented)
 
**What was done:**
- Added content categories to task creation UI
- Added `ContentTaskFields` component for extra inputs
- Added i18n translations
 
**What was missing:**
- `ProjectStore` was NOT updated to read `content_plan.json`
- `file-watcher.ts` was NOT updated to watch `content_plan.json`
- `plan-file-utils.ts` was NOT updated to handle content plans
- `execution-handlers.ts` was NOT updated for content task tracking
 
---
 
## The Data Flow Problem
 
### Expected Flow (What We Thought Would Happen)
 
```
User creates "Document architecture" task
        ↓
Frontend saves to spec directory
        ↓
spec_runner.py detects content task
        ↓
content_runner.py creates content_plan.json
        ↓
Frontend reads content_plan.json (somehow?)
        ↓
Task tracked in UI
```
 
### Actual Flow (What Actually Happens)
 
```
User creates "Document architecture" task
        ↓
Frontend saves to spec directory (001-architecture/)
Frontend also creates empty implementation_plan.json
        ↓
spec_runner.py detects content task
        ↓
content_runner.py creates DIFFERENT spec (content-001/)
Creates content_plan.json in content-001/
        ↓
Frontend looks for implementation_plan.json in 001-architecture/
        ↓
NOT FOUND or EMPTY
        ↓
Task shows as "0/0 subtasks" → human_review
```
 
---
 
## Files That Need Content Mode Support
 
### Frontend Files (NOT Updated)
 
| File | Purpose | What's Missing |
|------|---------|----------------|
| `project-store.ts` | Loads tasks from disk | Doesn't read `content_plan.json` |
| `file-watcher.ts` | Watches for plan changes | Only watches `implementation_plan.json` |
| `plan-file-utils.ts` | Reads/writes plan status | Only handles `implementation_plan.json` |
| `execution-handlers.ts` | Tracks task execution | Expects `implementation_plan.json` |
 
### The Real Problem
 
The implementation plan (Phase 6) only specified:
- "Add content categories to UI" ✅
- "Add ContentTaskFields component" ✅
 
It did NOT specify:
- "Update ProjectStore to read content_plan.json" ❌
- "Update file-watcher for content plans" ❌
- "Map content phases to implementation phases" ❌
 
---
 
## Root Cause
 
The implementation plan was designed with two assumptions:
 
1. **Assumption**: Content Mode would be CLI-only initially
   - Reality: It was integrated with frontend routing
 
2. **Assumption**: Frontend integration meant "add form fields"
   - Reality: Frontend integration means the full data loop
 
The design created a **write path** (frontend → content_runner) without a **read path** (content_plan → frontend).
 
---
 
## Solutions
 
### Option A: Create Compatibility Layer
 
Make Content Mode create files the frontend already understands.
 
```python
# In content_runner.py or ContentPlannerAgent
def save_plan(self, plan: ContentPlan, spec_dir: Path):
    # Save native content format
    plan.save(spec_dir / "content_plan.json")
 
    # ALSO create implementation_plan.json for frontend
    impl_plan = self._convert_to_implementation_plan(plan)
    (spec_dir / "implementation_plan.json").write_text(
        json.dumps(impl_plan, indent=2)
    )
```
 
**Pros**: Minimal frontend changes
**Cons**: Two files to maintain, potential sync issues
 
### Option B: Update Frontend to Read Content Plans
 
Add content_plan.json support to all frontend components.
 
```typescript
// In project-store.ts
const planPath = path.join(specDir, 'implementation_plan.json');
const contentPlanPath = path.join(specDir, 'content_plan.json');
 
// Try implementation_plan first, fall back to content_plan
let plan = await readPlan(planPath) ?? await readContentPlan(contentPlanPath);
```
 
**Pros**: Clean separation, native support
**Cons**: Many files to modify, more testing needed
 
### Option C: Disable Auto-Routing (Temporary)
 
Content Mode only works via CLI, not through frontend.
 
```python
# In spec_runner.py
# Don't auto-route to content mode from frontend
# Users must use: python content_runner.py --project ... --task ...
```
 
**Pros**: Quick fix, unblocks development
**Cons**: Feature not usable from frontend
 
---
 
## Recommended Path Forward
 
### Short Term (Unblock Users)
 
1. **Option C**: Disable auto-routing in `spec_runner.py`
2. Document that Content Mode is CLI-only for now
3. Content tasks from frontend use code pipeline (will work, just not optimized)
 
### Medium Term (Proper Fix)
 
1. **Option A**: Add compatibility layer in `content_runner.py`
2. When Content Mode creates `content_plan.json`, ALSO create `implementation_plan.json`
3. Map content phases → implementation phases
4. Map content subtasks → implementation subtasks
 
### Long Term (Full Integration)
 
1. **Option B**: Full frontend support for content plans
2. Update ProjectStore, file-watcher, plan-file-utils
3. Add content-specific UI for viewing content task progress
4. Consider unified plan format that works for both
 
---
 
## Lessons Learned
 
1. **Integration means the full loop** - Not just input, but also output/tracking
2. **Test the actual user flow** - Not just individual components
3. **Don't create parallel file formats** without a bridge between them
4. **Frontend integration plans should include data flow diagrams**
 
---
 
## Files Reference
 
### Content Mode Files (Backend)
 
```
apps/backend/
├── content/
│   ├── __init__.py
│   ├── enums.py           # ContentProjectType, ContentWorkflowType
│   ├── models.py          # ContentPlan, ContentPhase, ContentSubtask
│   ├── detector.py        # ContentProjectDetector
│   ├── scaffold.py        # Project scaffolding
│   └── agents/
│       ├── base.py        # Base ContentAgent class
│       ├── planner.py     # Creates content_plan.json ← THE PROBLEM
│       └── ...
├── content_runner.py      # CLI entry point
└── runners/
    └── spec_runner.py     # Routes to content_runner (Phase 4)
```
 
### Frontend Files (Need Updates for Full Integration)
 
```
apps/frontend/src/main/
├── project-store.ts       # Reads implementation_plan.json ONLY
├── file-watcher.ts        # Watches implementation_plan.json ONLY
└── ipc-handlers/
    └── task/
        ├── plan-file-utils.ts     # Handles implementation_plan.json ONLY
        └── execution-handlers.ts  # Expects implementation_plan.json ONLY
```
 
---
 
## Status
 
| Item | Status |
|------|--------|
| Problem identified | ✅ |
| Root cause documented | ✅ |
| Solutions proposed | ✅ |
| Fix implemented | ❌ Pending decision |
 
---
 
## Related Documents
 
- [Content Mode Implementation Plan](./content-mode-implementation-plan.md) - Original design (missing data flow)
- [Content Mode Summary](./content-mode-summary.md) - Feature documentation
- [Creative Mode Dev Journal](./creative-mode-dev-journal.md) - Implementation history
- [Content Mode Test Plan](./content-mode-test-plan.md) - Manual testing guide
