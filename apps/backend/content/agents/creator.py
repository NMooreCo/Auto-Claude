"""Content Creator Agent - creates content following plans and templates."""

from pathlib import Path
from typing import Optional
import logging

from .base import ContentAgent
from ..models import ContentPlan, ContentSubtask, ContentPhase

logger = logging.getLogger(__name__)


class ContentCreatorAgent(ContentAgent):
    """
    Creates content following plans, templates, and style guides.

    The Content Creator is the primary agent for producing content artifacts.
    It follows templates, matches existing style, and maintains consistency.
    """

    PROMPT_FILE = "content_creator.md"
    AGENT_TYPE = "content_creator"

    def run(
        self,
        plan: ContentPlan,
        subtask: Optional[ContentSubtask] = None,
    ) -> dict:
        """
        Execute content creation for a plan or specific subtask.

        Args:
            plan: The content plan to execute
            subtask: Optional specific subtask to execute (auto-selects if not provided)

        Returns:
            Dictionary with execution results
        """
        # If no subtask specified, get the next one from the plan
        if subtask is None:
            result = plan.get_next_subtask()
            if result is None:
                return {
                    "status": "complete",
                    "message": "All subtasks completed",
                }
            phase, subtask = result
        else:
            phase = self._find_phase_for_subtask(plan, subtask)

        logger.info(f"Executing subtask: {subtask.id} - {subtask.description}")

        # Mark subtask as in progress
        plan.mark_subtask_status(subtask.id, "in_progress")

        # Load the prompt
        prompt = self._load_prompt()

        # Build context
        context = self._build_subtask_context(plan, phase, subtask)

        starting_message = f"""{prompt}

## CURRENT TASK CONTEXT

{context}

## INSTRUCTIONS

Execute the subtask described above. Follow the template if provided,
match the project's style guide, and maintain consistency with existing content.

Mark the subtask as complete when finished.
"""

        # Run the agent session
        response = self._create_session(
            starting_message=starting_message,
            session_name=f"content-creator-{subtask.id}",
        )

        # Mark subtask as completed (agent should verify this)
        plan.mark_subtask_status(subtask.id, "completed")

        # Save updated plan to unified implementation_plan.json format
        if self.spec_dir:
            plan.save_to_unified(self.spec_dir / "implementation_plan.json")

        return {
            "status": "completed",
            "subtask_id": subtask.id,
            "phase_id": phase.id if phase else None,
            "output": subtask.output,
            "progress": plan.get_progress(),
        }

    def _find_phase_for_subtask(
        self, plan: ContentPlan, subtask: ContentSubtask
    ) -> Optional[ContentPhase]:
        """Find the phase containing a subtask."""
        for phase in plan.phases:
            for s in phase.subtasks:
                if s.id == subtask.id:
                    return phase
        return None

    def _build_subtask_context(
        self,
        plan: ContentPlan,
        phase: Optional[ContentPhase],
        subtask: ContentSubtask,
    ) -> str:
        """Build detailed context for executing a subtask."""
        context_parts = [
            f"Project: {plan.project_name}",
            f"Project Type: {plan.project_type.value}",
            "",
            f"Phase: {phase.name if phase else 'N/A'}",
            f"Phase Type: {phase.type.value if phase else 'N/A'}",
            "",
            f"Subtask ID: {subtask.id}",
            f"Description: {subtask.description}",
            f"Artifact Type: {subtask.artifact_type.value}",
        ]

        if subtask.template:
            context_parts.append(f"Template: {subtask.template}")

        if subtask.output:
            context_parts.append(f"Output Path: {subtask.output}")

        if subtask.files_to_read:
            context_parts.append(f"Files to Read: {', '.join(subtask.files_to_read)}")

        if subtask.verification:
            context_parts.append(
                f"Verification: {subtask.verification.type.value}"
            )

        if subtask.notes:
            context_parts.append(f"Notes: {subtask.notes}")

        # Add plan context
        if plan.context:
            context_parts.append("")
            context_parts.append("## Project Context")
            if "templates_in_use" in plan.context:
                context_parts.append(
                    f"Templates: {', '.join(plan.context['templates_in_use'])}"
                )
            if "style_guide" in plan.context:
                context_parts.append(f"Style Guide: {plan.context['style_guide']}")

        return "\n".join(context_parts)

    def execute_phase(self, plan: ContentPlan, phase_id: str) -> dict:
        """
        Execute all subtasks in a phase.

        Args:
            plan: The content plan
            phase_id: ID of the phase to execute

        Returns:
            Dictionary with phase execution results
        """
        phase = next((p for p in plan.phases if p.id == phase_id), None)
        if not phase:
            return {"status": "error", "message": f"Phase not found: {phase_id}"}

        results = []
        for subtask in phase.subtasks:
            if subtask.status == "completed":
                continue

            result = self.run(plan, subtask)
            results.append(result)

            if result.get("status") == "error":
                break

        return {
            "status": "completed" if phase.is_complete() else "partial",
            "phase_id": phase_id,
            "subtask_results": results,
            "progress": plan.get_progress(),
        }
