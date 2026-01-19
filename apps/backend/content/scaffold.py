"""Scaffold new content projects from templates."""

from pathlib import Path
from typing import Optional
import logging

from .enums import ContentProjectType

logger = logging.getLogger(__name__)


class ContentProjectScaffolder:
    """Creates new content project structures from templates."""

    def scaffold(
        self,
        project_dir: str,
        project_type: ContentProjectType,
        project_name: Optional[str] = None,
    ) -> None:
        """
        Create a new content project structure.

        Args:
            project_dir: Directory to create the project in
            project_type: Type of project to scaffold
            project_name: Optional project name (defaults to directory name)
        """
        project_path = Path(project_dir)
        project_path.mkdir(parents=True, exist_ok=True)

        if project_name is None:
            project_name = project_path.name

        logger.info(f"Scaffolding {project_type.value} project: {project_name}")

        # Get the scaffolding method for this project type
        scaffold_method = getattr(
            self, f"_scaffold_{project_type.value}", self._scaffold_general
        )
        scaffold_method(project_path, project_name)

        logger.info(f"Project scaffolded at: {project_path}")

    def _create_file(self, path: Path, content: str) -> None:
        """Create a file with content."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        logger.debug(f"Created: {path}")

    def _scaffold_card_game(self, project_path: Path, project_name: str) -> None:
        """Scaffold a card game project."""
        # Index file
        self._create_file(
            project_path / "_index.md",
            f"""# {project_name}

A card game project.

## Structure

- `rules/` - Game rules and mechanics
- `cards/` - Card definitions
- `formats/` - Play formats
- `style-guide/` - Design guidelines
- `playtests/` - Playtest logs

## Getting Started

1. Define your core rules in `rules/core-rules.md`
2. Add keywords to `rules/keywords.md`
3. Create cards using the template in `cards/_template.md`
4. Set power level guidelines in `style-guide/power-levels.md`
"""
        )

        # Rules
        self._create_file(
            project_path / "rules" / "core-rules.md",
            """# Core Rules

## Game Overview

[Describe the core gameplay loop]

## Turn Structure

1. **Draw Phase** - Draw a card
2. **Main Phase** - Play cards and take actions
3. **End Phase** - Cleanup and pass turn

## Winning the Game

[Describe win conditions]

## Card Types

[Describe the types of cards in your game]
"""
        )

        self._create_file(
            project_path / "rules" / "keywords.md",
            """# Keywords

This document defines all keyword abilities in the game.

## Combat Keywords

### Rush
*Can attack the turn it enters play.*

This creature doesn't have summoning sickness.

### Shield
*Prevents the first source of damage.*

When this creature would take damage for the first time, prevent that damage and remove Shield.

## Triggered Keywords

### [Add your keywords here]

---

## Adding New Keywords

When adding a new keyword:
1. Choose a clear, evocative name
2. Write reminder text (in italics)
3. Provide full rules explanation
4. List any interactions or edge cases
"""
        )

        # Cards
        self._create_file(
            project_path / "cards" / "_template.md",
            """# {{CARD_NAME}}

```
┌─────────────────────────────────────┐
│ {{COST}}                   {{TYPE}} │
├─────────────────────────────────────┤
│                                     │
│                                     │
│           {{ASCII_ART}}             │
│                                     │
│                                     │
├─────────────────────────────────────┤
│ {{SUBTYPE}}                         │
├─────────────────────────────────────┤
│                                     │
│ {{ABILITY_TEXT}}                    │
│                                     │
├─────────────────────────────────────┤
│ {{POWER}} / {{HEALTH}}              │
│                        {{RARITY}}   │
└─────────────────────────────────────┘
```

## Design Notes

- **Intended Role**: [How should this card be used?]
- **Power Level**: [Reference power-levels.md]
- **Synergies**: [What does it combo with?]

## Version History

| Version | Change | Reason |
|---------|--------|--------|
| 1.0 | Initial design | |
"""
        )

        # Style guide
        self._create_file(
            project_path / "style-guide" / "power-levels.md",
            """# Power Level Guidelines

## Cost-to-Stats Baseline

| Cost | Vanilla Stats | Notes |
|------|---------------|-------|
| 1 | 1/1 or 2/1 | Aggressive or utility |
| 2 | 2/2 or 3/2 | Standard creature |
| 3 | 3/3 or 4/3 | Solid body |
| 4 | 4/4 or 5/4 | Strong creature |
| 5 | 5/5 or 6/5 | Late game threat |
| 6+ | 6/6+ | Finisher territory |

## Ability Costs

| Ability | Approximate Cost |
|---------|------------------|
| Rush | +0.5 |
| Shield | +1 |
| Draw a card | +1.5 |
| Deal 2 damage | +1 |

## Rarity Guidelines

- **Common**: Simple, straightforward effects
- **Uncommon**: One interesting ability or synergy
- **Rare**: Powerful or complex effects
- **Legendary**: Build-around or game-changing
"""
        )

        self._create_file(
            project_path / "style-guide" / "naming.md",
            """# Naming Conventions

## Card Names

- Use evocative, thematic names
- Avoid generic names like "Fire Creature"
- Names should hint at the card's function

## Faction/Color Naming

[Define naming patterns for each faction]

## Keyword Naming

- Keywords should be single words when possible
- The name should suggest the mechanical effect
"""
        )

        # Formats
        self._create_file(
            project_path / "formats" / "standard.md",
            """# Standard Format

## Overview

The default way to play.

## Deck Building Rules

- **Deck Size**: 40 cards minimum
- **Card Copies**: Maximum 3 copies of any card
- **Restricted List**: None currently

## Card Pool

All cards from:
- Core Set

## Ban List

None currently.
"""
        )

        # Playtests directory
        self._create_file(
            project_path / "playtests" / ".gitkeep",
            ""
        )

    def _scaffold_ttrpg(self, project_path: Path, project_name: str) -> None:
        """Scaffold a TTRPG project."""
        self._create_file(
            project_path / "_index.md",
            f"""# {project_name}

A tabletop RPG project.

## Structure

- `rules/` - Game mechanics and systems
- `world/` - Setting and lore
- `bestiary/` - Monsters and creatures
- `items/` - Equipment and magic items
- `adventures/` - Campaigns and encounters
- `characters/` - NPCs and pregens
"""
        )

        # Rules
        self._create_file(
            project_path / "rules" / "core-mechanics.md",
            """# Core Mechanics

## Ability Scores

[Define your ability scores]

## Making Checks

[Describe how to resolve actions]

## Combat

[Combat rules]

## Advancement

[How characters level up]
"""
        )

        # Bestiary
        self._create_file(
            project_path / "bestiary" / "_template.md",
            """# {{MONSTER_NAME}}
*{{SIZE}} {{TYPE}}, {{ALIGNMENT}}*

---

**Armor Class** {{AC}}
**Hit Points** {{HP}} ({{HIT_DICE}})
**Speed** {{SPEED}}

---

| STR | DEX | CON | INT | WIS | CHA |
|-----|-----|-----|-----|-----|-----|
| {{STR}} | {{DEX}} | {{CON}} | {{INT}} | {{WIS}} | {{CHA}} |

---

**Skills** {{SKILLS}}
**Senses** {{SENSES}}
**Languages** {{LANGUAGES}}
**Challenge** {{CR}} ({{XP}} XP)

---

## Abilities

### {{ABILITY_NAME}}
{{ABILITY_DESCRIPTION}}

## Actions

### {{ACTION_NAME}}
{{ACTION_DESCRIPTION}}

---

## Lore

{{LORE_DESCRIPTION}}

## Tactics

{{TACTICS_DESCRIPTION}}

## Encounter Ideas

- {{ENCOUNTER_IDEA_1}}
- {{ENCOUNTER_IDEA_2}}
"""
        )

        # World
        self._create_file(
            project_path / "world" / "overview.md",
            """# World Overview

## Setting Summary

[Brief description of the world]

## Major Regions

[List and describe major regions]

## History

[Key historical events]

## Factions

[Major factions and their goals]
"""
        )

        # Items
        self._create_file(
            project_path / "items" / "_template.md",
            """# {{ITEM_NAME}}
*{{ITEM_TYPE}}, {{RARITY}}*

{{DESCRIPTION}}

## Properties

{{PROPERTIES}}

## History

{{HISTORY}}
"""
        )

        # Adventures
        self._create_file(
            project_path / "adventures" / "_template.md",
            """# {{ADVENTURE_NAME}}

*A {{LEVEL_RANGE}} adventure for {{PARTY_SIZE}} players*

## Overview

{{OVERVIEW}}

## Background

{{BACKGROUND}}

## Adventure Hooks

{{HOOKS}}

## Encounters

### {{ENCOUNTER_NAME}}
{{ENCOUNTER_DESCRIPTION}}

## Rewards

{{REWARDS}}
"""
        )

        # Characters
        (project_path / "characters" / "npcs").mkdir(parents=True, exist_ok=True)
        (project_path / "characters" / "pregens").mkdir(parents=True, exist_ok=True)

    def _scaffold_board_game(self, project_path: Path, project_name: str) -> None:
        """Scaffold a board game project."""
        self._create_file(
            project_path / "_index.md",
            f"""# {project_name}

A board game project.

## Structure

- `rules/` - Game rules
- `components/` - Game components
- `player-aids/` - Quick reference materials
- `playtests/` - Playtest logs
"""
        )

        self._create_file(
            project_path / "rules" / "setup.md",
            """# Setup

## Components

[List all components]

## Setup Steps

1. [Step 1]
2. [Step 2]
3. [Step 3]
"""
        )

        self._create_file(
            project_path / "rules" / "turn-structure.md",
            """# Turn Structure

## Overview

[Brief turn overview]

## Phase 1: [Name]

[Description]

## Phase 2: [Name]

[Description]
"""
        )

        self._create_file(
            project_path / "rules" / "winning.md",
            """# Winning the Game

## Victory Conditions

[How to win]

## Game End Triggers

[When does the game end]
"""
        )

        (project_path / "components").mkdir(exist_ok=True)
        (project_path / "player-aids").mkdir(exist_ok=True)
        (project_path / "playtests").mkdir(exist_ok=True)

    def _scaffold_worldbuilding(self, project_path: Path, project_name: str) -> None:
        """Scaffold a worldbuilding project."""
        self._create_file(
            project_path / "_index.md",
            f"""# {project_name}

A worldbuilding project.

## Structure

- `world/` - Core world information
- `factions/` - Organizations and groups
- `characters/` - Notable figures
- `locations/` - Places of interest
- `history/` - Timeline and events
"""
        )

        self._create_file(
            project_path / "world" / "overview.md",
            """# World Overview

## The World

[Describe your world]

## Themes

[Key themes to explore]

## Tone

[The feel of your world]
"""
        )

        (project_path / "factions").mkdir(exist_ok=True)
        (project_path / "characters").mkdir(exist_ok=True)
        (project_path / "locations").mkdir(exist_ok=True)
        (project_path / "history").mkdir(exist_ok=True)

    def _scaffold_fiction(self, project_path: Path, project_name: str) -> None:
        """Scaffold a fiction writing project."""
        self._create_file(
            project_path / "_index.md",
            f"""# {project_name}

A fiction project.

## Structure

- `outline/` - Story structure
- `characters/` - Character profiles
- `chapters/` - Written chapters
- `notes/` - Research and notes
"""
        )

        self._create_file(
            project_path / "outline" / "plot.md",
            """# Plot Outline

## Premise

[One sentence premise]

## Act 1

[Setup]

## Act 2

[Confrontation]

## Act 3

[Resolution]
"""
        )

        self._create_file(
            project_path / "characters" / "_template.md",
            """# {{CHARACTER_NAME}}

## Basic Info

- **Age**:
- **Role**:

## Description

[Physical and personality description]

## Background

[Character history]

## Goals

[What they want]

## Arc

[How they change]
"""
        )

        (project_path / "chapters").mkdir(exist_ok=True)
        (project_path / "notes").mkdir(exist_ok=True)

    def _scaffold_codebase_docs(self, project_path: Path, project_name: str) -> None:
        """Scaffold a codebase documentation project."""
        self._create_file(
            project_path / "docs" / "_index.md",
            f"""# {project_name} Documentation

## Sections

- [Getting Started](getting-started/)
- [Architecture](architecture/)
- [API Reference](api/)
- [Guides](guides/)
"""
        )

        self._create_file(
            project_path / "docs" / "architecture" / "decisions" / "_template.md",
            """# ADR-{{NUMBER}}: {{TITLE}}

## Status

{{STATUS}}

## Context

{{CONTEXT}}

## Decision

{{DECISION}}

## Consequences

### Positive
-

### Negative
-

## Alternatives Considered

### {{ALTERNATIVE}}
{{WHY_NOT}}
"""
        )

        self._create_file(
            project_path / "docs" / "api" / "_template.md",
            """# {{ENDPOINT_NAME}}

## Endpoint

```
{{METHOD}} {{PATH}}
```

## Description

{{DESCRIPTION}}

## Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| | | | |

## Response

```json
{{RESPONSE_EXAMPLE}}
```

## Errors

| Code | Description |
|------|-------------|
| | |
"""
        )

        (project_path / "docs" / "getting-started").mkdir(parents=True, exist_ok=True)
        (project_path / "docs" / "guides").mkdir(exist_ok=True)

    def _scaffold_general(self, project_path: Path, project_name: str) -> None:
        """Scaffold a general content project."""
        self._create_file(
            project_path / "_index.md",
            f"""# {project_name}

A content project.

## Structure

Customize this structure for your needs.

## Getting Started

1. Add your content files
2. Create templates for repeated structures
3. Add a style guide if needed
"""
        )

        self._create_file(
            project_path / "style-guide" / "style.md",
            """# Style Guide

## Tone

[Describe the tone]

## Formatting

[Formatting guidelines]

## Terminology

[Key terms and definitions]
"""
        )

    # Alias methods for project types with underscores
    _scaffold_api_docs = _scaffold_codebase_docs
    _scaffold_architecture = _scaffold_codebase_docs
    _scaffold_knowledge_base = _scaffold_codebase_docs
    _scaffold_business = _scaffold_general
