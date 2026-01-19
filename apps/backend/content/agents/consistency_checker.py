"""Consistency Checker Agent - validates cross-references and consistency."""

from pathlib import Path
from typing import Optional, List
import logging

from .base import ContentAgent
from ..models import ContentPlan
from ..enums import ContentProjectType

logger = logging.getLogger(__name__)


class ConsistencyCheckerAgent(ContentAgent):
    """
    Validates content consistency, cross-references, and terminology.

    The Consistency Checker ensures all content is internally consistent,
    cross-references are valid, and terminology is used correctly.
    """

    PROMPT_FILE = "content_consistency_checker.md"
    AGENT_TYPE = "consistency_checker"

    def run(
        self,
        scope: str = "all",
        plan: Optional[ContentPlan] = None,
        check_types: Optional[List[str]] = None,
    ) -> dict:
        """
        Run consistency checks on project content.

        Args:
            scope: Scope of check ('all', 'recent', or specific directory)
            plan: Optional content plan for context
            check_types: Optional list of check types to run

        Returns:
            Dictionary with consistency check results
        """
        # Default check types if not specified
        if check_types is None:
            check_types = [
                "cross_references",
                "terminology",
                "template_compliance",
                "style_consistency",
            ]

            # Add domain-specific checks based on project type
            if plan:
                if plan.project_type in [
                    ContentProjectType.CARD_GAME,
                    ContentProjectType.BOARD_GAME,
                    ContentProjectType.TTRPG,
                ]:
                    check_types.append("game_consistency")
                elif plan.project_type in [
                    ContentProjectType.WORLDBUILDING,
                    ContentProjectType.FICTION,
                ]:
                    check_types.append("lore_consistency")
                elif plan.project_type in [
                    ContentProjectType.CODEBASE_DOCS,
                    ContentProjectType.API_DOCS,
                ]:
                    check_types.append("code_doc_sync")

        # Load the prompt
        prompt = self._load_prompt()

        # Build context
        context = self._build_check_context(scope, plan, check_types)

        starting_message = f"""{prompt}

## CHECK CONTEXT

{context}

## INSTRUCTIONS

Perform the specified consistency checks on the project content.
Generate a comprehensive consistency report saved as `consistency_report.md`.

For each issue found, provide:
- Location (file and line/section)
- Problem description
- Severity (critical, moderate, minor)
- Suggested fix
"""

        logger.info(f"Running consistency checks: {', '.join(check_types)}")

        # Run the agent session
        response = self._create_session(
            starting_message=starting_message,
            session_name="consistency-checker-session",
        )

        return self._parse_check_results(response)

    def _build_check_context(
        self,
        scope: str,
        plan: Optional[ContentPlan],
        check_types: List[str],
    ) -> str:
        """Build context for consistency checking."""
        context_parts = [
            f"Check Scope: {scope}",
            f"Check Types: {', '.join(check_types)}",
        ]

        if plan:
            context_parts.extend([
                "",
                f"Project: {plan.project_name}",
                f"Project Type: {plan.project_type.value}",
            ])

            if plan.context.get("cross_reference_conventions"):
                context_parts.append(
                    f"Cross-Reference Format: {plan.context['cross_reference_conventions']}"
                )

            if plan.context.get("templates_in_use"):
                context_parts.append(
                    f"Templates: {', '.join(plan.context['templates_in_use'])}"
                )

        return "\n".join(context_parts)

    def _parse_check_results(self, response) -> dict:
        """Parse consistency check results."""
        report_path = self.spec_dir / "consistency_report.md" if self.spec_dir else None

        issues = {
            "critical": 0,
            "moderate": 0,
            "minor": 0,
        }

        if report_path and report_path.exists():
            content = report_path.read_text().lower()
            # Simple heuristic to count issues
            issues["critical"] = content.count("critical")
            issues["moderate"] = content.count("moderate")
            issues["minor"] = content.count("minor")

            return {
                "status": "completed",
                "report_path": str(report_path),
                "issues": issues,
                "total_issues": sum(issues.values()),
                "has_critical": issues["critical"] > 0,
            }

        return {
            "status": "completed",
            "report_path": None,
            "message": "Check completed, see agent output for details",
        }

    def check_cross_references(self, plan: Optional[ContentPlan] = None) -> dict:
        """
        Check only cross-references.

        Args:
            plan: Optional content plan for context

        Returns:
            Dictionary with check results
        """
        return self.run(
            scope="all",
            plan=plan,
            check_types=["cross_references"],
        )

    def check_terminology(self, plan: Optional[ContentPlan] = None) -> dict:
        """
        Check only terminology consistency.

        Args:
            plan: Optional content plan for context

        Returns:
            Dictionary with check results
        """
        return self.run(
            scope="all",
            plan=plan,
            check_types=["terminology"],
        )

    def quick_check(self, content_paths: List[str]) -> dict:
        """
        Quick consistency check on specific files.

        Args:
            content_paths: Paths to check

        Returns:
            Dictionary with check results
        """
        return self.run(
            scope=",".join(content_paths),
            check_types=["cross_references", "terminology"],
        )
