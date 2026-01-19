"""Content Reviewer Agent - reviews content for quality and completeness."""

from pathlib import Path
from typing import Optional, List
import logging

from .base import ContentAgent
from ..models import ContentPlan

logger = logging.getLogger(__name__)


class ContentReviewerAgent(ContentAgent):
    """
    Reviews content for quality, clarity, completeness, and fitness for purpose.

    The Content Reviewer evaluates content against style guides, templates,
    and quality criteria, producing detailed review reports.
    """

    PROMPT_FILE = "content_reviewer.md"
    AGENT_TYPE = "content_reviewer"

    def run(
        self,
        content_paths: List[str],
        plan: Optional[ContentPlan] = None,
        review_type: str = "full",
    ) -> dict:
        """
        Review content files for quality.

        Args:
            content_paths: Paths to content files to review
            plan: Optional content plan for context
            review_type: Type of review ('full', 'quick', 'style', 'completeness')

        Returns:
            Dictionary with review results
        """
        # Load the prompt
        prompt = self._load_prompt()

        # Build context
        context = self._build_review_context(content_paths, plan, review_type)

        starting_message = f"""{prompt}

## REVIEW CONTEXT

{context}

## INSTRUCTIONS

Review the specified content files according to the review type.
Generate a comprehensive review report saved as `review_report.md`.

Focus on:
- Clarity and readability
- Completeness of required sections
- Style guide adherence
- Quality and usefulness
- Fitness for purpose
"""

        logger.info(f"Reviewing {len(content_paths)} content files...")

        # Run the agent session
        response = self._create_session(
            starting_message=starting_message,
            session_name="content-reviewer-session",
        )

        # Parse review results
        return self._parse_review_results(response)

    def _build_review_context(
        self,
        content_paths: List[str],
        plan: Optional[ContentPlan],
        review_type: str,
    ) -> str:
        """Build context for the review."""
        context_parts = [
            f"Review Type: {review_type}",
            f"Files to Review: {len(content_paths)}",
            "",
            "Content Files:",
        ]

        for path in content_paths:
            context_parts.append(f"  - {path}")

        if plan:
            context_parts.extend([
                "",
                f"Project: {plan.project_name}",
                f"Project Type: {plan.project_type.value}",
            ])

            if plan.quality_criteria:
                context_parts.append("")
                context_parts.append("Quality Criteria:")
                for key, value in plan.quality_criteria.items():
                    context_parts.append(f"  - {key}: {value}")

        return "\n".join(context_parts)

    def _parse_review_results(self, response) -> dict:
        """Parse review results from agent response."""
        # Check for review report file
        report_path = self.spec_dir / "review_report.md" if self.spec_dir else None

        if report_path and report_path.exists():
            report_content = report_path.read_text()
            return {
                "status": "completed",
                "report_path": str(report_path),
                "report_content": report_content,
                "verdict": self._extract_verdict(report_content),
            }

        return {
            "status": "completed",
            "report_path": None,
            "message": "Review completed, check agent output for details",
        }

    def _extract_verdict(self, report_content: str) -> str:
        """Extract the review verdict from report content."""
        content_lower = report_content.lower()

        if "ready for use?: yes" in content_lower:
            return "approved"
        elif "needs revision" in content_lower or "ready for use?: no" in content_lower:
            return "needs_revision"
        elif "minor fixes" in content_lower:
            return "approved_with_fixes"

        return "unknown"

    def quick_review(self, content_path: str) -> dict:
        """
        Perform a quick review of a single content file.

        Args:
            content_path: Path to the content file

        Returns:
            Dictionary with quick review results
        """
        return self.run([content_path], review_type="quick")

    def review_against_plan(self, plan: ContentPlan) -> dict:
        """
        Review all deliverables in a content plan.

        Args:
            plan: The content plan with deliverables

        Returns:
            Dictionary with review results for all deliverables
        """
        content_paths = [d["path"] for d in plan.deliverables if "path" in d]
        return self.run(content_paths, plan=plan, review_type="full")
