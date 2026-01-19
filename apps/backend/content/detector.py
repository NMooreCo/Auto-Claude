"""Detect content project types and characteristics."""

from pathlib import Path
from typing import Optional

from .enums import ContentProjectType


class ContentProjectDetector:
    """Detects project type from directory structure, files, and task descriptions."""

    # Indicators for each project type
    INDICATORS: dict[ContentProjectType, dict] = {
        ContentProjectType.CARD_GAME: {
            "directories": ["cards", "rules", "keywords", "sets", "formats"],
            "files": ["keywords.md", "power-levels.md", "core-rules.md"],
            "keywords": [
                "card", "deck", "mana", "cost", "rarity", "creature", "spell",
                "keyword", "ability", "set", "booster", "draft", "constructed"
            ],
            "weight": 1.0,
        },
        ContentProjectType.BOARD_GAME: {
            "directories": ["rules", "components", "boards", "player-aids"],
            "files": ["setup.md", "turn-structure.md", "winning.md"],
            "keywords": [
                "board", "token", "dice", "turn", "player", "piece", "tile",
                "victory", "setup", "component", "hex", "square"
            ],
            "weight": 1.0,
        },
        ContentProjectType.TTRPG: {
            "directories": ["bestiary", "adventures", "characters", "items", "spells", "classes"],
            "files": ["core-mechanics.md", "character-creation.md"],
            "keywords": [
                "monster", "dungeon", "campaign", "spell", "character", "dm", "gm",
                "npc", "encounter", "level", "class", "race", "stat", "hit points",
                "armor class", "saving throw", "ability score", "d20", "rpg"
            ],
            "weight": 1.0,
        },
        ContentProjectType.WORLDBUILDING: {
            "directories": ["world", "lore", "factions", "regions", "history", "cultures"],
            "files": ["history.md", "timeline.md", "overview.md"],
            "keywords": [
                "lore", "faction", "kingdom", "history", "world", "nation",
                "culture", "religion", "geography", "map", "timeline", "era"
            ],
            "weight": 1.0,
        },
        ContentProjectType.FICTION: {
            "directories": ["chapters", "characters", "outline", "drafts"],
            "files": ["outline.md", "characters.md", "plot.md"],
            "keywords": [
                "chapter", "story", "novel", "character", "plot", "narrative",
                "protagonist", "antagonist", "scene", "arc", "draft", "manuscript"
            ],
            "weight": 1.0,
        },
        ContentProjectType.BUSINESS: {
            "directories": ["plans", "analysis", "research", "pitches"],
            "files": ["business-plan.md", "market-analysis.md", "pitch.md"],
            "keywords": [
                "business", "plan", "market", "revenue", "customer", "product",
                "strategy", "competitor", "pitch", "investor", "startup", "roi"
            ],
            "weight": 1.0,
        },
        ContentProjectType.CODEBASE_DOCS: {
            "directories": ["docs/api", "docs/architecture", "docs/guides"],
            "files": ["docs/_index.md", "docs/README.md"],
            "keywords": [
                "documentation", "api", "endpoint", "component", "service",
                "architecture", "guide", "reference", "tutorial"
            ],
            "weight": 1.0,
        },
        ContentProjectType.API_DOCS: {
            "directories": ["docs/api", "api-docs"],
            "files": ["openapi.yaml", "swagger.json", "api-spec.yaml"],
            "keywords": [
                "endpoint", "request", "response", "api", "rest", "graphql",
                "authentication", "authorization", "schema", "swagger", "openapi"
            ],
            "weight": 1.0,
        },
        ContentProjectType.ARCHITECTURE: {
            "directories": ["docs/architecture", "docs/adr", "architecture"],
            "files": ["architecture.md", "system-design.md"],
            "keywords": [
                "architecture", "adr", "decision", "component", "system",
                "design", "diagram", "flow", "service", "microservice"
            ],
            "weight": 1.0,
        },
        ContentProjectType.KNOWLEDGE_BASE: {
            "directories": ["wiki", "knowledge", "runbooks", "guides"],
            "files": ["runbook.md", "troubleshooting.md"],
            "keywords": [
                "runbook", "wiki", "knowledge", "guide", "how-to", "faq",
                "troubleshooting", "procedure", "process"
            ],
            "weight": 1.0,
        },
    }

    # Keywords that suggest this is a content task (not code)
    CONTENT_TASK_KEYWORDS = [
        # Creative indicators
        "write", "create", "design", "draft", "story", "world", "lore",
        "card", "game", "rules", "campaign", "adventure", "monster",
        "character", "faction", "history", "chapter",
        # Documentation indicators
        "document", "documentation", "describe", "explain", "guide",
        # General content indicators
        "content", "creative", "brainstorm", "outline", "plan",
    ]

    # Keywords that suggest this is a code task (not content)
    CODE_TASK_KEYWORDS = [
        "implement", "fix", "bug", "refactor", "test", "deploy",
        "function", "class", "method", "api", "endpoint", "database",
        "error", "exception", "performance", "optimize", "debug",
    ]

    def detect(self, project_dir: str) -> ContentProjectType:
        """
        Detect project type from directory structure and files.

        Args:
            project_dir: Path to the project directory

        Returns:
            Detected ContentProjectType, or GENERAL if no match
        """
        project_path = Path(project_dir)
        if not project_path.exists():
            return ContentProjectType.GENERAL

        scores: dict[ContentProjectType, float] = {pt: 0.0 for pt in ContentProjectType}

        for project_type, indicators in self.INDICATORS.items():
            weight = indicators.get("weight", 1.0)

            # Check directories
            for dir_name in indicators.get("directories", []):
                dir_path = project_path / dir_name
                if dir_path.exists() and dir_path.is_dir():
                    scores[project_type] += 2.0 * weight

            # Check files
            for file_name in indicators.get("files", []):
                file_path = project_path / file_name
                if file_path.exists() and file_path.is_file():
                    scores[project_type] += 3.0 * weight

        # Return highest scoring type, or GENERAL if no matches
        best_type = max(scores, key=lambda k: scores[k])
        return best_type if scores[best_type] > 0 else ContentProjectType.GENERAL

    def detect_from_description(self, description: str) -> ContentProjectType:
        """
        Detect project type from a task description.

        Args:
            description: The task description text

        Returns:
            Detected ContentProjectType, or GENERAL if no clear match
        """
        description_lower = description.lower()
        scores: dict[ContentProjectType, float] = {pt: 0.0 for pt in ContentProjectType}

        for project_type, indicators in self.INDICATORS.items():
            keywords = indicators.get("keywords", [])
            weight = indicators.get("weight", 1.0)

            for keyword in keywords:
                if keyword.lower() in description_lower:
                    scores[project_type] += weight

        # Return highest scoring type if score is significant
        best_type = max(scores, key=lambda k: scores[k])
        return best_type if scores[best_type] >= 2.0 else ContentProjectType.GENERAL

    def is_content_task(self, description: str) -> bool:
        """
        Determine if a task description is for content work vs code work.

        Args:
            description: The task description text

        Returns:
            True if this appears to be a content task, False if code task
        """
        description_lower = description.lower()

        content_score = sum(
            1 for kw in self.CONTENT_TASK_KEYWORDS
            if kw in description_lower
        )
        code_score = sum(
            1 for kw in self.CODE_TASK_KEYWORDS
            if kw in description_lower
        )

        # If clearly more content keywords, it's a content task
        if content_score > code_score + 1:
            return True

        # If clearly more code keywords, it's a code task
        if code_score > content_score + 1:
            return False

        # Ambiguous - check for specific project type match
        detected_type = self.detect_from_description(description)
        return detected_type != ContentProjectType.GENERAL

    def detect_combined(
        self, project_dir: str, description: Optional[str] = None
    ) -> ContentProjectType:
        """
        Detect project type using both directory structure and description.

        Args:
            project_dir: Path to the project directory
            description: Optional task description for additional context

        Returns:
            Detected ContentProjectType
        """
        dir_type = self.detect(project_dir)

        if description:
            desc_type = self.detect_from_description(description)

            # If both agree, use that
            if dir_type == desc_type:
                return dir_type

            # If directory gives GENERAL but description is specific, use description
            if dir_type == ContentProjectType.GENERAL and desc_type != ContentProjectType.GENERAL:
                return desc_type

            # If description gives GENERAL but directory is specific, use directory
            if desc_type == ContentProjectType.GENERAL and dir_type != ContentProjectType.GENERAL:
                return dir_type

            # Both are specific but different - prefer directory (more concrete evidence)
            return dir_type

        return dir_type

    def get_project_info(self, project_dir: str) -> dict:
        """
        Get detailed information about a content project.

        Args:
            project_dir: Path to the project directory

        Returns:
            Dictionary with project information
        """
        project_path = Path(project_dir)
        project_type = self.detect(project_dir)

        info = {
            "project_type": project_type.value,
            "project_path": str(project_path.absolute()),
            "found_indicators": {
                "directories": [],
                "files": [],
            },
            "templates_found": [],
            "style_guides_found": [],
            "index_files": [],
        }

        # Find templates
        for template in project_path.rglob("_template.md"):
            info["templates_found"].append(str(template.relative_to(project_path)))

        # Find style guides
        style_dirs = ["style-guide", "style", "guidelines"]
        for style_dir in style_dirs:
            style_path = project_path / style_dir
            if style_path.exists():
                for md_file in style_path.glob("*.md"):
                    info["style_guides_found"].append(
                        str(md_file.relative_to(project_path))
                    )

        # Find index files
        for index_name in ["_index.md", "index.md", "README.md"]:
            for index_file in project_path.rglob(index_name):
                info["index_files"].append(str(index_file.relative_to(project_path)))

        # Record found indicators
        if project_type in self.INDICATORS:
            indicators = self.INDICATORS[project_type]
            for dir_name in indicators.get("directories", []):
                if (project_path / dir_name).exists():
                    info["found_indicators"]["directories"].append(dir_name)
            for file_name in indicators.get("files", []):
                if (project_path / file_name).exists():
                    info["found_indicators"]["files"].append(file_name)

        return info
