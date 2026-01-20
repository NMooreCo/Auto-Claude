# Auto Claude Architecture Overview

This document provides a comprehensive technical overview of Auto Claude's architecture, including its agent system, pipelines, security model, and integrations.

> **Related Documentation:**
> - [CLAUDE.md](../CLAUDE.md) - Development guidance and quick reference
> - [CLI-USAGE.md](CLI-USAGE.md) - Terminal-only usage guide
> - [CONTRIBUTING.md](../CONTRIBUTING.md) - How to contribute

---

## Table of Contents

1. [Introduction](#introduction)
2. [System Overview](#system-overview)
3. [High-Level Architecture](#high-level-architecture)
4. [Spec Creation Pipeline](#spec-creation-pipeline)
5. [Implementation Pipeline](#implementation-pipeline)
6. [Agent System](#agent-system)
7. [Security Model](#security-model)
8. [Workspace Isolation](#workspace-isolation)
9. [Frontend-Backend Communication](#frontend-backend-communication)
10. [Integrations](#integrations)
11. [Data Flow and File Structure](#data-flow-and-file-structure)

---

## Introduction

Auto Claude is a **multi-agent autonomous coding framework** that builds software through coordinated AI agent sessions. Rather than using a single AI conversation to write code, Auto Claude orchestrates multiple specialized agents in a structured pipeline—from understanding requirements to writing code to validating the result.

### What Makes Auto Claude Different

Traditional AI coding assistants work in a single conversation where context accumulates and can be lost. Auto Claude takes a fundamentally different approach:

| Traditional AI Coding | Auto Claude |
|----------------------|-------------|
| Single conversation | Multi-session pipeline |
| Context accumulates | Fresh context per session |
| Manual task tracking | Automatic subtask management |
| No persistent memory | Cross-session memory via knowledge graph |
| Trust the output | Automated QA validation loop |
| Direct file changes | Isolated workspace (git worktrees) |

### Core Principles

1. **Structured Pipelines** - Tasks flow through well-defined phases: spec creation → planning → implementation → QA validation
2. **Fresh Context Windows** - Each agent session starts fresh, loading state from files rather than accumulating context
3. **Subtask-Based Work** - Large features are broken into atomic subtasks with individual verification
4. **Isolated Workspaces** - AI-generated code lives in git worktrees until explicitly merged by the user
5. **Defense in Depth** - Three-layer security model protects against unintended actions
6. **Cross-Session Memory** - Knowledge graph persists patterns, gotchas, and discoveries across sessions

### Primary Use Cases

- **Feature Development** - Transform a task description into implemented, tested code
- **Code Maintenance** - Handle bug fixes, refactoring, and code cleanup
- **GitHub Automation** - Automated PR reviews, issue triage, and auto-fixing
- **Documentation** - Generate and update documentation from code analysis

---

## System Overview

Auto Claude consists of two main components: a **Python backend** that orchestrates AI agents and manages the build process, and an optional **Electron desktop frontend** that provides a graphical interface for project management.

### Component Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Auto Claude System                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────┐    ┌─────────────────────────────┐ │
│  │       Electron Frontend         │    │       Python Backend        │ │
│  │  (Optional Desktop UI)          │    │   (Required - CLI/Agent)    │ │
│  │                                 │    │                             │ │
│  │  ┌───────────────────────────┐  │    │  ┌───────────────────────┐  │ │
│  │  │ React + TypeScript        │  │    │  │ Spec Creation         │  │ │
│  │  │ • Project Management      │  │    │  │ Pipeline              │  │ │
│  │  │ • Task Visualization      │  │◄──►│  │ (3-8 phases)          │  │ │
│  │  │ • Terminal Integration    │  │IPC │  └───────────────────────┘  │ │
│  │  └───────────────────────────┘  │    │                             │ │
│  │                                 │    │  ┌───────────────────────┐  │ │
│  │  ┌───────────────────────────┐  │    │  │ Implementation        │  │ │
│  │  │ Main Process (Node.js)    │  │    │  │ Pipeline              │  │ │
│  │  │ • Agent Process Manager   │  │───►│  │ (Planner→Coder→QA)    │  │ │
│  │  │ • PTY Terminal Manager    │  │    │  └───────────────────────┘  │ │
│  │  │ • IPC Handlers            │  │    │                             │ │
│  │  └───────────────────────────┘  │    │  ┌───────────────────────┐  │ │
│  │                                 │    │  │ Claude Agent SDK      │  │ │
│  └─────────────────────────────────┘    │  │ • Security Hooks      │  │ │
│                                         │  │ • MCP Servers         │  │ │
│                                         │  │ • Tool Permissions    │  │ │
│                                         │  └───────────────────────┘  │ │
│                                         │                             │ │
│                                         └─────────────────────────────┘ │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                           External Services                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌───────────────┐  │
│  │ Claude API   │ │ Graphiti     │ │ Linear       │ │ GitHub        │  │
│  │ (via SDK)    │ │ Memory       │ │ (optional)   │ │ (optional)    │  │
│  └──────────────┘ └──────────────┘ └──────────────┘ └───────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Backend Architecture (`apps/backend/`)

The Python backend is the core of Auto Claude. It can run standalone via CLI or be orchestrated by the Electron frontend.

| Directory | Purpose |
|-----------|---------|
| `core/` | Client factory, authentication, security, platform abstraction |
| `agents/` | Implementation agents (planner, coder, session management) |
| `qa/` | QA validation agents (reviewer, fixer, loop orchestration) |
| `spec/` | Spec creation pipeline (phases, orchestrator, discovery) |
| `spec_agents/` | Spec creation agents (gatherer, researcher, writer, critic) |
| `cli/` | Command-line interface and command handlers |
| `integrations/` | External service integrations (Graphiti, Linear, GitHub) |
| `prompts/` | Agent system prompts (markdown files) |
| `project/` | Project analysis for security profile generation |
| `security/` | Command validation and security hooks |

### Frontend Architecture (`apps/frontend/`)

The Electron desktop app provides a visual interface for managing projects and tasks.

| Directory | Purpose |
|-----------|---------|
| `src/main/` | Electron main process, IPC handlers, process managers |
| `src/renderer/` | React components, Zustand stores, hooks |
| `src/preload/` | Secure bridge between main and renderer processes |
| `src/shared/` | TypeScript types, i18n translations, constants |

### Key Technology Choices

| Component | Technology | Rationale |
|-----------|------------|-----------|
| AI Integration | Claude Agent SDK | Pre-configured security, MCP support, session management |
| Backend Runtime | Python 3.12+ | Rich AI/ML ecosystem, async support, cross-platform |
| Frontend Runtime | Electron + React | Desktop-class features, cross-platform, rich UI |
| State Management | Zustand (frontend) | Lightweight, TypeScript-first, no boilerplate |
| Memory System | Graphiti + LadybugDB | Knowledge graph for semantic search, no Docker required |
| Workspace Isolation | Git Worktrees | Native git feature, clean separation, easy cleanup |
| Process Communication | IPC (Electron) | Type-safe, bidirectional, secure context isolation |

### Operational Modes

Auto Claude can operate in several modes:

1. **CLI Mode** - Direct command-line usage without the desktop app
   ```bash
   python run.py --spec 001  # Run a spec
   python spec_runner.py --task "Add login feature"  # Create a spec
   ```

2. **Desktop Mode** - Full GUI experience via Electron
   ```bash
   npm start  # Launch desktop app
   ```

3. **GitHub Runner Mode** - Automated PR review and issue triage
   ```bash
   python run.py --pr 123 --review  # Review a PR
   python run.py --issue 456 --auto-fix  # Auto-fix an issue
   ```

### Data Flow Summary

```
User Task Description
        │
        ▼
┌───────────────────┐
│ Spec Creation     │ ──► requirements.json, context.json, spec.md
│ Pipeline          │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Planner Agent     │ ──► implementation_plan.json
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Coder Agent       │ ──► Code changes in isolated worktree
│ (multiple sessions)│
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ QA Validation     │ ──► qa_report.md, QA_FIX_REQUEST.md
│ Loop              │
└───────────────────┘
        │
        ▼
User Review & Merge
```

This overview sets the foundation for understanding the detailed architecture sections that follow. Each subsequent section dives deep into specific components, their interactions, and the design decisions behind them.

---

<!-- Subsequent sections will be added in following subtasks -->
