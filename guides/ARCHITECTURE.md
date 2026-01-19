# Auto Claude Architecture Overview

This guide provides a high-level overview of Auto Claude's architecture, designed to help new contributors understand the system quickly.

## Table of Contents

- [System Overview](#system-overview)
- [Key Components](#key-components)
- [Agent Pipeline](#agent-pipeline)
- [Spec Creation Flow](#spec-creation-flow)
- [Frontend-Backend Communication](#frontend-backend-communication)
- [Directory Structure](#directory-structure)

---

## System Overview

Auto Claude is a **multi-agent autonomous coding framework** that builds software through coordinated AI agent sessions. It uses the Claude Agent SDK to run agents in isolated workspaces with security controls.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AUTO CLAUDE                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────────────┐         ┌──────────────────────────────────┐  │
│   │                 │   IPC   │                                  │  │
│   │  Electron UI    │◄───────►│  Python Backend                  │  │
│   │  (React/TS)     │         │  (Claude Agent SDK)              │  │
│   │                 │         │                                  │  │
│   └─────────────────┘         └──────────────────────────────────┘  │
│           │                              │                           │
│           │                              ▼                           │
│           │                   ┌──────────────────────────────────┐  │
│           │                   │  AI Agents                       │  │
│           │                   │  • Planner                       │  │
│           │                   │  • Coder                         │  │
│           │                   │  • QA Reviewer                   │  │
│           │                   │  • QA Fixer                      │  │
│           │                   └──────────────────────────────────┘  │
│           │                              │                           │
│           ▼                              ▼                           │
│   ┌─────────────────┐         ┌──────────────────────────────────┐  │
│   │  User Interface │         │  Isolated Worktrees              │  │
│   │  • Task List    │         │  (.worktrees/{spec-name}/)       │  │
│   │  • Terminals    │         │                                  │  │
│   │  • Code Review  │         │  Safe, sandboxed development     │  │
│   └─────────────────┘         └──────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Principles

1. **Isolated Development** - Each spec runs in its own git worktree, preventing unreviewed changes from affecting your main branch
2. **Multi-Agent Orchestration** - Specialized agents handle different phases of development
3. **Human-in-the-Loop** - All changes require human review before merging
4. **Security First** - Three-layer defense: OS sandbox, filesystem permissions, and command allowlists

---

## Key Components

### Backend (`apps/backend/`)

All agent logic and AI interactions live in the Python backend:

| Component | Location | Purpose |
|-----------|----------|---------|
| **Core Client** | `core/client.py` | Claude Agent SDK factory with security hooks |
| **Security** | `core/security.py` | Dynamic command allowlisting |
| **Agents** | `agents/` | Implementation agents (planner, coder, QA) |
| **Prompts** | `prompts/` | System prompts for each agent role |
| **Integrations** | `integrations/` | Graphiti memory, Linear, GitHub |

### Frontend (`apps/frontend/`)

The Electron desktop app provides the user interface:

| Component | Location | Purpose |
|-----------|----------|---------|
| **Main Process** | `src/main/` | IPC handlers, file watching, process management |
| **Renderer** | `src/renderer/` | React UI components |
| **Preload** | `src/preload/` | Secure bridge between main and renderer |
| **Shared** | `src/shared/` | Types, constants, utilities |

---

## Agent Pipeline

The implementation pipeline orchestrates multiple AI agents to build features:

```
                    IMPLEMENTATION PIPELINE
                    ═══════════════════════

    ┌──────────────────────────────────────────────────────────┐
    │                                                          │
    │  1. PLANNER AGENT                                        │
    │  ─────────────────                                       │
    │  • Reads spec.md and context.json                        │
    │  • Creates implementation_plan.json with subtasks        │
    │  • Organizes work into phases (e.g., Backend, Frontend)  │
    │                                                          │
    └────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
    ┌──────────────────────────────────────────────────────────┐
    │                                                          │
    │  2. CODER AGENT                                          │
    │  ────────────────                                        │
    │  • Implements one subtask at a time                      │
    │  • Can spawn subagents for parallel work                 │
    │  • Commits changes incrementally                         │
    │  • Uses recovery hints if stuck                          │
    │                                                          │
    │  Loop: While subtasks remain                             │
    │  ┌──────────────────────────────────────────────────┐   │
    │  │ Get next subtask → Implement → Commit → Update   │   │
    │  └──────────────────────────────────────────────────┘   │
    │                                                          │
    └────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
    ┌──────────────────────────────────────────────────────────┐
    │                                                          │
    │  3. QA REVIEWER AGENT                                    │
    │  ────────────────────                                    │
    │  • Validates all acceptance criteria from spec.md        │
    │  • Can perform E2E testing via Electron MCP              │
    │  • Creates QA_REPORT.md with findings                    │
    │                                                          │
    │  Result: APPROVED or REJECTED                            │
    │                                                          │
    └────────────────────────┬─────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
    ┌─────────────────┐           ┌─────────────────────────────┐
    │   APPROVED      │           │   REJECTED                  │
    │                 │           │                             │
    │   → Human       │           │   4. QA FIXER AGENT         │
    │     Review      │           │   ──────────────────        │
    │   → Merge       │           │   • Reads QA_FIX_REQUEST.md │
    │                 │           │   • Fixes identified issues │
    │                 │           │   • Returns to QA Reviewer  │
    └─────────────────┘           │                             │
                                  │   (Loop until approved)     │
                                  └─────────────────────────────┘
```

### Agent Prompts

Each agent has a specialized prompt in `apps/backend/prompts/`:

| Prompt File | Agent Role |
|-------------|------------|
| `planner.md` | Creates implementation plans with subtasks |
| `coder.md` | Implements individual subtasks |
| `coder_recovery.md` | Recovers from stuck/failed subtasks |
| `qa_reviewer.md` | Validates acceptance criteria |
| `qa_fixer.md` | Fixes QA-reported issues |

### Session Management

The coder agent runs in a loop, processing subtasks one at a time:

```python
# Simplified flow from agents/coder.py
while True:
    next_subtask = get_next_subtask(spec_dir)
    if not next_subtask:
        break  # All done!

    prompt = generate_subtask_prompt(subtask, phase)

    async with client:
        status, response = await run_agent_session(client, prompt)

    await post_session_processing(subtask_id, ...)
```

---

## Spec Creation Flow

Before implementation, a spec must be created. The spec creation process adapts to task complexity:

```
                     SPEC CREATION PIPELINE
                     ══════════════════════

    ┌────────────────────────────────────────────────────────────────┐
    │                                                                │
    │  COMPLEXITY ASSESSMENT                                         │
    │  ─────────────────────                                         │
    │  AI evaluates: scope, integrations, infrastructure, risk       │
    │                                                                │
    └────────────────────────────┬───────────────────────────────────┘
                                 │
           ┌─────────────────────┼─────────────────────┐
           │                     │                     │
           ▼                     ▼                     ▼
    ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
    │   SIMPLE    │       │  STANDARD   │       │   COMPLEX   │
    │  (1-2 files)│       │ (3-10 files)│       │ (10+ files) │
    └──────┬──────┘       └──────┬──────┘       └──────┬──────┘
           │                     │                     │
           ▼                     ▼                     ▼

    ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
    │ 3 PHASES:   │       │ 6-7 PHASES: │       │ 8 PHASES:   │
    │             │       │             │       │             │
    │ 1. Discovery│       │ 1. Discovery│       │ 1. Discovery│
    │ 2. QuickSpec│       │ 2. Requirem.│       │ 2. Requirem.│
    │ 3. Validate │       │ 3. [Research]       │ 3. Research │
    │             │       │ 4. Context  │       │ 4. Context  │
    │             │       │ 5. Spec     │       │ 5. Spec     │
    │             │       │ 6. Plan     │       │ 6. Critique │
    │             │       │ 7. Validate │       │ 7. Plan     │
    │             │       │             │       │ 8. Validate │
    └─────────────┘       └─────────────┘       └─────────────┘
```

### Phase Details

| Phase | Purpose | Output |
|-------|---------|--------|
| **Discovery** | Analyze codebase structure | Initial context |
| **Requirements** | Gather user requirements | `requirements.json` |
| **Research** | Validate external integrations | Research notes |
| **Context** | Deep codebase analysis | `context.json` |
| **Spec** | Write specification | `spec.md` |
| **Critique** | Self-review using ultrathink | Refined spec |
| **Plan** | Create implementation plan | `implementation_plan.json` |
| **Validate** | Verify spec completeness | Validation report |

### Spec Directory Structure

Each spec lives in `.auto-claude/specs/XXX-name/`:

```
.auto-claude/specs/001-add-auth/
├── spec.md                  # Feature specification
├── requirements.json        # Structured requirements
├── context.json             # Codebase context
├── implementation_plan.json # Subtask-based plan
├── qa_report.md             # QA validation results
├── QA_FIX_REQUEST.md        # Issues to fix (when rejected)
└── build-progress.txt       # Build progress log
```

---

## Frontend-Backend Communication

The Electron app uses a secure IPC (Inter-Process Communication) pattern:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ELECTRON ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │  RENDERER PROCESS (React UI)                                │   │
│   │  ─────────────────────────────                              │   │
│   │  • React components (TypeScript)                            │   │
│   │  • Calls window.electronAPI.* methods                       │   │
│   │  • Receives events via callbacks                            │   │
│   └─────────────────────────┬───────────────────────────────────┘   │
│                             │                                        │
│                             │ contextBridge                          │
│                             │ (secure bridge)                        │
│                             ▼                                        │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │  PRELOAD SCRIPT (Bridge)                                    │   │
│   │  ─────────────────────────                                  │   │
│   │  • Exposes safe APIs via contextBridge                      │   │
│   │  • Maps to IPC channels                                     │   │
│   │  • Type-safe interface                                      │   │
│   │                                                             │   │
│   │  Location: apps/frontend/src/preload/api/                   │   │
│   └─────────────────────────┬───────────────────────────────────┘   │
│                             │                                        │
│                             │ ipcRenderer.invoke / ipcRenderer.on    │
│                             ▼                                        │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │  MAIN PROCESS (Node.js)                                     │   │
│   │  ───────────────────────                                    │   │
│   │  • IPC handlers (ipcMain.handle)                            │   │
│   │  • File system access                                       │   │
│   │  • Process spawning (Python backend)                        │   │
│   │  • File watchers                                            │   │
│   │                                                             │   │
│   │  Location: apps/frontend/src/main/ipc-handlers/             │   │
│   └─────────────────────────┬───────────────────────────────────┘   │
│                             │                                        │
│                             │ child_process.spawn                    │
│                             ▼                                        │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │  PYTHON BACKEND                                             │   │
│   │  ────────────────                                           │   │
│   │  • Agent orchestration                                      │   │
│   │  • Claude Agent SDK                                         │   │
│   │  • Graphiti memory                                          │   │
│   │                                                             │   │
│   │  Location: apps/backend/                                    │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### IPC Channel Categories

The IPC channels are organized by domain (see `apps/frontend/src/shared/constants/ipc.ts`):

| Category | Example Channels | Purpose |
|----------|------------------|---------|
| **Project** | `project:add`, `project:list` | Project management |
| **Task** | `task:create`, `task:start`, `task:stop` | Task lifecycle |
| **Terminal** | `terminal:create`, `terminal:input` | PTY management |
| **Agent Events** | `task:progress`, `task:log` | Real-time updates |
| **GitHub** | `github:pr:review`, `github:autofix:start` | GitHub integration |
| **Memory** | `context:get`, `memory:status` | Graphiti queries |

### API Structure

The preload API is organized into domain-specific modules:

```typescript
// apps/frontend/src/preload/api/index.ts
export const createElectronAPI = (): ElectronAPI => ({
  ...createProjectAPI(),    // Project operations
  ...createTaskAPI(),       // Task operations
  ...createTerminalAPI(),   // Terminal management
  ...createAgentAPI(),      // Agent events & control
  ...createSettingsAPI(),   // App settings
  github: createGitHubAPI() // GitHub integration
});
```

### Event Flow Example: Starting a Task

```
┌──────────────────────────────────────────────────────────────────────┐
│  User clicks "Start Build" button                                    │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Renderer: window.electronAPI.startTask(projectId, taskId)           │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Preload: ipcRenderer.invoke('task:start', projectId, taskId)        │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Main: ipcMain.handle('task:start', handler)                         │
│        → AgentManager.startAgent(...)                                │
│        → spawn('python', ['run.py', '--spec', taskId])               │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Python Backend: run_autonomous_agent(...)                           │
│        → Creates implementation plan                                 │
│        → Implements subtasks                                         │
│        → Emits phase events                                          │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Main: AgentManager listens for stdout/stderr                        │
│        → Parses phase events                                         │
│        → Emits to renderer via IPC                                   │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Renderer: Updates UI with progress, logs, status changes            │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
Auto-Claude/
├── apps/
│   ├── backend/                    # Python backend (ALL agent logic)
│   │   ├── agents/                 # Agent implementations
│   │   │   ├── coder.py            # Main coding agent loop
│   │   │   ├── planner.py          # Follow-up planner
│   │   │   ├── memory_manager.py   # Graphiti memory orchestration
│   │   │   └── session.py          # Agent session management
│   │   │
│   │   ├── core/                   # Core infrastructure
│   │   │   ├── client.py           # Claude SDK client factory
│   │   │   ├── security.py         # Command allowlisting
│   │   │   ├── auth.py             # OAuth token management
│   │   │   └── platform/           # Cross-platform utilities
│   │   │
│   │   ├── prompts/                # Agent system prompts
│   │   │   ├── planner.md
│   │   │   ├── coder.md
│   │   │   ├── qa_reviewer.md
│   │   │   └── qa_fixer.md
│   │   │
│   │   ├── spec/                   # Spec creation
│   │   │   ├── orchestrator.py     # Spec creation orchestrator
│   │   │   ├── phases/             # Spec phase implementations
│   │   │   └── validate_pkg/       # Spec validation
│   │   │
│   │   ├── integrations/           # External integrations
│   │   │   ├── graphiti/           # Memory system
│   │   │   └── linear/             # Linear integration
│   │   │
│   │   ├── runners/                # Entry points
│   │   │   ├── spec_runner.py      # Spec creation CLI
│   │   │   └── github/             # GitHub automation
│   │   │
│   │   └── run.py                  # Main build entry point
│   │
│   └── frontend/                   # Electron desktop app
│       ├── src/
│       │   ├── main/               # Main process (Node.js)
│       │   │   ├── ipc-handlers/   # IPC handler modules
│       │   │   ├── agent/          # Agent process management
│       │   │   └── platform/       # Platform-specific code
│       │   │
│       │   ├── preload/            # Preload scripts
│       │   │   └── api/            # API modules exposed to renderer
│       │   │
│       │   ├── renderer/           # React UI
│       │   │   ├── components/     # UI components
│       │   │   ├── pages/          # Page components
│       │   │   └── hooks/          # React hooks
│       │   │
│       │   └── shared/             # Shared code
│       │       ├── constants/      # IPC channels, types
│       │       └── types/          # TypeScript types
│       │
│       └── package.json
│
├── guides/                         # Documentation
│   ├── README.md                   # Guide index
│   ├── ARCHITECTURE.md             # This file
│   └── CLI-USAGE.md                # CLI usage guide
│
├── tests/                          # Test suite
│
├── scripts/                        # Build/utility scripts
│
├── .auto-claude/                   # Per-project data (gitignored)
│   ├── specs/                      # Spec directories
│   └── worktrees/                  # Isolated git worktrees
│
├── CLAUDE.md                       # AI assistant instructions
├── README.md                       # Getting started
└── CONTRIBUTING.md                 # Contribution guide
```

---

## Next Steps

- **New Contributors**: Start with [CONTRIBUTING.md](../CONTRIBUTING.md) for setup instructions
- **CLI Users**: See [CLI-USAGE.md](CLI-USAGE.md) for terminal-only usage
- **API Integration**: Check `CLAUDE.md` for detailed component documentation
