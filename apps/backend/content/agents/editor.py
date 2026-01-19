"""Content Editor Agent - refines content based on review feedback."""

from pathlib import Path
from typing import Optional, List
import logging

from .base import ContentAgent
from ..models import ContentPlan

logger = logging.getLogger(__name__)


class ContentEditorAgent(ContentAgent):
    """
    Edits and refines content based on review feedback.

    The Content Editor applies targeted fixes, improves clarity,
    and polishes content while preserving voice and intent.
    """

    PROMPT_FILE = "content_editor.md"
    AGENT_TYPE = "content_editor"

    def run(
        self,
        content_paths: List[str],
        feedback_path: Optional[str] = None,
        feedback_text: Optional[str] = None,
        plan: Optional[ContentPlan] = None,
    ) -> dict:
        """
        Edit content based on feedback.

        Args:
            content_paths: Paths to content files to edit
            feedback_path: Path to review/feedback report
            feedback_text: Direct feedback text (if no file)
            plan: Optional content plan for context

        Returns:
            Dictionary with editing results
        """
        # Load feedback
        feedback = self._load_feedback(feedback_path, feedback_text)

        # Load the prompt
        prompt = self._load_prompt()

        # Build context
        context = self._build_edit_context(content_paths, feedback, plan)

        starting_message = f"""{prompt}

## EDITING CONTEXT

{context}

## FEEDBACK TO ADDRESS

{feedback}

## INSTRUCTIONS

Apply the feedback to improve the content. Make targeted fixes that:
- Address the specific issues raised
- Preserve the original voice and intent
- Maintain consistency with the project style

Document all changes made.
"""

        logger.info(f"Editing {len(content_paths)} content files based on feedback...")

        # Run the agent session
        response = self._create_session(
            starting_message=starting_message,
            session_name="content-editor-session",
        )

        return {
            "status": "completed",
            "files_edited": content_paths,
            "message": "Content edited based on feedback",
        }

    def _load_feedback(
        self,
        feedback_path: Optional[str],
        feedback_text: Optional[str],
    ) -> str:
        """Load feedback from file or text."""
        if feedback_path:
            path = Path(feedback_path)
            if path.exists():
                return path.read_text()

        if feedback_text:
            return feedback_text

        # Check for standard feedback files
        standard_paths = [
            self.spec_dir / "review_report.md" if self.spec_dir else None,
            self.spec_dir / "consistency_report.md" if self.spec_dir else None,
            self.spec_dir / "balance_report.md" if self.spec_dir else None,
        ]

        for path in standard_paths:
            if path and path.exists():
                return path.read_text()

        raise ValueError(
            "No feedback provided. Specify feedback_path, feedback_text, "
            "or ensure a review report exists in the spec directory."
        )

    def _build_edit_context(
        self,
        content_paths: List[str],
        feedback: str,
        plan: Optional[ContentPlan],
    ) -> str:
        """Build context for editing."""
        context_parts = [
            f"Files to Edit: {len(content_paths)}",
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

            if plan.context.get("style_guide"):
                context_parts.append(f"Style Guide: {plan.context['style_guide']}")

        return "\n".join(context_parts)

    def apply_review_feedback(
        self,
        plan: ContentPlan,
        review_report_path: str,
    ) -> dict:
        """
        Apply feedback from a review report to plan deliverables.

        Args:
            plan: The content plan
            review_report_path: Path to the review report

        Returns:
            Dictionary with editing results
        """
        content_paths = [d["path"] for d in plan.deliverables if "path" in d]
        return self.run(
            content_paths=content_paths,
            feedback_path=review_report_path,
            plan=plan,
        )

    def polish(self, content_path: str) -> dict:
        """
        Polish a single content file for final delivery.

        Args:
            content_path: Path to the content file

        Returns:
            Dictionary with polishing results
        """
        return self.run(
            content_paths=[content_path],
            feedback_text="Please polish this content for final delivery. "
                         "Focus on clarity, flow, and professional presentation.",
        )
