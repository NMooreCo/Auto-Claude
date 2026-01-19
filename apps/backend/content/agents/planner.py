"""Content Planner Agent - creates content workflow plans."""

import json
import re
from pathlib import Path
from typing import Optional
import logging

from .base import ContentAgent
from ..models import ContentPlan
from ..enums import ContentProjectType

logger = logging.getLogger(__name__)


class ContentPlannerAgent(ContentAgent):
    """
    Plans content creation workflows.

    The Content Planner analyzes the project structure, reads the content brief,
    and creates a phase-based plan with subtasks for content creation.
    """

    PROMPT_FILE = "content_planner.md"
    AGENT_TYPE = "content_planner"

    def __init__(
        self,
        project_dir: str,
        spec_dir: Optional[str] = None,
        model: Optional[str] = None,
        project_type: Optional[ContentProjectType] = None,
    ):
        """
        Initialize the Content Planner agent.

        Args:
            project_dir: Path to the content project directory
            spec_dir: Optional path to the spec directory
            model: Optional model override
            project_type: Optional project type (auto-detected if not provided)
        """
        super().__init__(project_dir, spec_dir, model)
        self.project_type = project_type

    def run(
        self,
        brief: str,
        output_path: Optional[str] = None,
    ) -> ContentPlan:
        """
        Create a content plan from a brief.

        Args:
            brief: The content brief describing what to create
            output_path: Optional path to save the plan JSON

        Returns:
            ContentPlan instance
        """
        # Load the prompt
        prompt = self._load_prompt()

        # Build the starting message
        context = self._build_context(
            project_type=self.project_type.value if self.project_type else "auto-detect"
        )

        starting_message = f"""{prompt}

## PROJECT CONTEXT

{context}

## CONTENT BRIEF

{brief}

## INSTRUCTIONS

Please analyze this project and create a comprehensive content plan.
Save the plan to `implementation_plan.json` in the spec directory.
"""

        # Run the agent session
        logger.info(f"Creating content plan for: {brief[:100]}...")
        response = self._create_session(
            starting_message=starting_message,
            session_name="content-planner-session",
        )

        # Parse the plan from the response or from the saved file
        plan = self._parse_plan(response, output_path)

        return plan

    def _parse_plan(
        self, response, output_path: Optional[str] = None
    ) -> ContentPlan:
        """
        Parse the content plan from the agent response.

        Args:
            response: The agent session response
            output_path: Optional path where plan was saved

        Returns:
            ContentPlan instance
        """
        # Try to load from file first (unified format)
        plan_paths = [
            self.spec_dir / "implementation_plan.json" if self.spec_dir else None,
            self.project_dir / "implementation_plan.json",
            Path(output_path) if output_path else None,
        ]

        for plan_path in plan_paths:
            if plan_path and plan_path.exists():
                logger.info(f"Loading plan from: {plan_path}")
                return ContentPlan.load(plan_path)

        # If no file found, try to parse from response
        logger.warning("Plan file not found, attempting to parse from response")
        return self._parse_plan_from_response(response)

    def _parse_plan_from_response(self, response) -> ContentPlan:
        """
        Attempt to parse plan JSON from agent response text.

        Args:
            response: The agent session response

        Returns:
            ContentPlan instance
        """
        # Get response text (handle different response formats)
        if hasattr(response, "text"):
            text = response.text
        elif hasattr(response, "content"):
            text = response.content
        elif isinstance(response, str):
            text = response
        else:
            text = str(response)

        # Try to find JSON in the response
        json_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                return ContentPlan.from_dict(data)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from response: {e}")

        # If we can't parse, raise an error
        raise ValueError(
            "Could not parse content plan from agent response. "
            "The agent should have saved implementation_plan.json."
        )

    def create_plan_interactive(
        self,
        initial_brief: str,
        clarification_callback=None,
    ) -> ContentPlan:
        """
        Create a content plan with interactive clarification.

        Args:
            initial_brief: The initial content brief
            clarification_callback: Optional callback for clarification questions

        Returns:
            ContentPlan instance
        """
        # For now, just run the standard planning
        # Future: Add interactive clarification loop
        return self.run(initial_brief)
