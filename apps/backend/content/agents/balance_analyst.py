"""Balance Analyst Agent - analyzes game content for balance issues."""

from pathlib import Path
from typing import Optional, List
import logging

from .base import ContentAgent
from ..models import ContentPlan
from ..enums import ContentProjectType

logger = logging.getLogger(__name__)


class BalanceAnalystAgent(ContentAgent):
    """
    Analyzes game content for balance issues.

    The Balance Analyst evaluates power levels, cost efficiency,
    synergies, and meta impact for card games, board games, and TTRPGs.
    """

    PROMPT_FILE = "game_balance_analyst.md"
    AGENT_TYPE = "balance_analyst"

    # Project types that support balance analysis
    SUPPORTED_TYPES = [
        ContentProjectType.CARD_GAME,
        ContentProjectType.BOARD_GAME,
        ContentProjectType.TTRPG,
    ]

    def run(
        self,
        content_paths: Optional[List[str]] = None,
        plan: Optional[ContentPlan] = None,
        analysis_type: str = "full",
    ) -> dict:
        """
        Run balance analysis on game content.

        Args:
            content_paths: Specific content paths to analyze (optional)
            plan: Content plan for context
            analysis_type: Type of analysis ('full', 'power_level', 'synergy', 'meta')

        Returns:
            Dictionary with balance analysis results
        """
        # Validate project type
        if plan and plan.project_type not in self.SUPPORTED_TYPES:
            return {
                "status": "skipped",
                "message": f"Balance analysis not applicable for {plan.project_type.value}",
            }

        # Load the prompt
        prompt = self._load_prompt()

        # Build context
        context = self._build_analysis_context(content_paths, plan, analysis_type)

        starting_message = f"""{prompt}

## ANALYSIS CONTEXT

{context}

## INSTRUCTIONS

Perform {analysis_type} balance analysis on the specified content.
Generate a comprehensive balance report saved as `balance_report.md`.

For each issue found, provide:
- Content item (card, monster, ability, etc.)
- Current stats/values
- Issue identified (overtuned, undertuned, problematic synergy, etc.)
- Severity (critical, moderate, minor)
- Recommended adjustment
"""

        logger.info(f"Running {analysis_type} balance analysis...")

        # Run the agent session
        response = self._create_session(
            starting_message=starting_message,
            session_name="balance-analyst-session",
        )

        return self._parse_analysis_results(response)

    def _build_analysis_context(
        self,
        content_paths: Optional[List[str]],
        plan: Optional[ContentPlan],
        analysis_type: str,
    ) -> str:
        """Build context for balance analysis."""
        context_parts = [
            f"Analysis Type: {analysis_type}",
        ]

        if content_paths:
            context_parts.append(f"Files to Analyze: {len(content_paths)}")
            context_parts.append("")
            context_parts.append("Content Files:")
            for path in content_paths:
                context_parts.append(f"  - {path}")

        if plan:
            context_parts.extend([
                "",
                f"Project: {plan.project_name}",
                f"Project Type: {plan.project_type.value}",
            ])

            # Add game-specific context
            if plan.game_specific:
                context_parts.append("")
                context_parts.append("Game-Specific Configuration:")

                if "power_level_guide" in plan.game_specific:
                    context_parts.append(
                        f"  Power Level Guide: {plan.game_specific['power_level_guide']}"
                    )

                if "keyword_validation" in plan.game_specific:
                    kv = plan.game_specific["keyword_validation"]
                    context_parts.append(f"  Keyword Glossary: {kv.get('glossary', 'N/A')}")

                if "balance_check" in plan.game_specific:
                    bc = plan.game_specific["balance_check"]
                    context_parts.append(
                        f"  Comparison Set: {bc.get('comparison_set', 'N/A')}"
                    )

        return "\n".join(context_parts)

    def _parse_analysis_results(self, response) -> dict:
        """Parse balance analysis results."""
        report_path = self.spec_dir / "balance_report.md" if self.spec_dir else None

        issues = {
            "overtuned": 0,
            "undertuned": 0,
            "problematic_synergy": 0,
            "other": 0,
        }

        if report_path and report_path.exists():
            content = report_path.read_text().lower()

            # Count issues by type
            issues["overtuned"] = content.count("overtuned") + content.count("overpowered")
            issues["undertuned"] = content.count("undertuned") + content.count("underpowered")
            issues["problematic_synergy"] = content.count("problematic") + content.count("degenerate")

            return {
                "status": "completed",
                "report_path": str(report_path),
                "issues": issues,
                "total_issues": sum(issues.values()),
                "has_critical": "critical" in content or "must address" in content,
            }

        return {
            "status": "completed",
            "report_path": None,
            "message": "Analysis completed, see agent output for details",
        }

    def analyze_card_set(
        self,
        cards_dir: str,
        plan: Optional[ContentPlan] = None,
    ) -> dict:
        """
        Analyze a complete card set for balance.

        Args:
            cards_dir: Directory containing card files
            plan: Optional content plan

        Returns:
            Dictionary with analysis results
        """
        cards_path = Path(cards_dir)
        card_files = list(cards_path.rglob("*.md"))
        card_paths = [str(f) for f in card_files if not f.name.startswith("_")]

        return self.run(
            content_paths=card_paths,
            plan=plan,
            analysis_type="full",
        )

    def analyze_power_levels(
        self,
        content_paths: List[str],
        plan: Optional[ContentPlan] = None,
    ) -> dict:
        """
        Analyze only power levels.

        Args:
            content_paths: Paths to analyze
            plan: Optional content plan

        Returns:
            Dictionary with analysis results
        """
        return self.run(
            content_paths=content_paths,
            plan=plan,
            analysis_type="power_level",
        )

    def analyze_synergies(
        self,
        content_paths: List[str],
        plan: Optional[ContentPlan] = None,
    ) -> dict:
        """
        Analyze synergies and combos.

        Args:
            content_paths: Paths to analyze
            plan: Optional content plan

        Returns:
            Dictionary with analysis results
        """
        return self.run(
            content_paths=content_paths,
            plan=plan,
            analysis_type="synergy",
        )
