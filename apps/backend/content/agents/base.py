"""Base class for Content Mode agents."""

import asyncio
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Any
import logging

from phase_config import get_thinking_budget

logger = logging.getLogger(__name__)


class ContentAgent(ABC):
    """
    Base class for all Content Mode agents.

    Content agents handle autonomous content creation workflows,
    including planning, creating, reviewing, and editing content.
    """

    # Subclasses should set this to the prompt file name
    PROMPT_FILE: str = ""

    # Agent type identifier for the Claude SDK client
    AGENT_TYPE: str = "content"

    # Default model to use
    DEFAULT_MODEL: str = "claude-sonnet-4-5-20250929"

    # Default thinking level for extended thinking
    DEFAULT_THINKING_LEVEL: str = "medium"

    def __init__(
        self,
        project_dir: str,
        spec_dir: Optional[str] = None,
        model: Optional[str] = None,
        thinking_level: Optional[str] = None,
    ):
        """
        Initialize the content agent.

        Args:
            project_dir: Path to the content project directory
            spec_dir: Optional path to the spec directory for this task
            model: Optional model override (defaults to DEFAULT_MODEL)
            thinking_level: Optional thinking level (none, low, medium, high, ultrathink)
        """
        self.project_dir = Path(project_dir)
        self.spec_dir = Path(spec_dir) if spec_dir else None
        self.model = model or self.DEFAULT_MODEL
        self.thinking_level = thinking_level or self.DEFAULT_THINKING_LEVEL

        # Validate project directory exists
        if not self.project_dir.exists():
            raise ValueError(f"Project directory does not exist: {self.project_dir}")

        # Get the prompts directory path
        self.prompts_dir = Path(__file__).parent.parent.parent / "prompts"

    def _load_prompt(self) -> str:
        """Load the agent's prompt from the prompts directory."""
        if not self.PROMPT_FILE:
            raise NotImplementedError(
                f"{self.__class__.__name__} must define PROMPT_FILE"
            )

        prompt_path = self.prompts_dir / self.PROMPT_FILE
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

        return prompt_path.read_text()

    def _get_client(self):
        """
        Get a configured Claude SDK client for this agent.

        Returns:
            Configured ClaudeSDKClient instance
        """
        # Import here to avoid circular imports
        from core.client import create_client

        # Convert thinking level to token budget
        thinking_budget = get_thinking_budget(self.thinking_level)

        return create_client(
            project_dir=str(self.project_dir),
            spec_dir=str(self.spec_dir) if self.spec_dir else None,
            model=self.model,
            agent_type=self.AGENT_TYPE,
            max_thinking_tokens=thinking_budget,
        )

    def _create_session(self, starting_message: str, session_name: Optional[str] = None) -> str:
        """
        Create an agent session with the Claude SDK.

        Args:
            starting_message: The initial message/prompt for the agent
            session_name: Optional name for the session

        Returns:
            The agent session response text
        """
        name = session_name or f"{self.AGENT_TYPE}-session"
        logger.info(f"Starting {name} for project: {self.project_dir}")

        # Run the async session synchronously
        return asyncio.run(self._run_async_session(starting_message, name))

    async def _run_async_session(self, prompt: str, session_name: str) -> str:
        """
        Run an async agent session with the Claude SDK.

        Args:
            prompt: The prompt/message for the agent
            session_name: Name for the session

        Returns:
            The complete response text
        """
        client = self._get_client()
        response_text = ""

        try:
            async with client:
                logger.debug(f"Sending query for {session_name}...")
                await client.query(prompt)

                async for msg in client.receive_response():
                    msg_type = type(msg).__name__

                    if msg_type == "AssistantMessage" and hasattr(msg, "content"):
                        for block in msg.content:
                            block_type = type(block).__name__
                            if block_type == "TextBlock" and hasattr(block, "text"):
                                response_text += block.text
                                print(block.text, end="", flush=True)

                print()  # Newline after response
                logger.info(f"Session {session_name} completed successfully")

        except Exception as e:
            logger.error(f"Session {session_name} failed: {e}")
            raise

        return response_text

    def _build_context(self, **kwargs) -> str:
        """
        Build context string for the agent.

        Subclasses can override this to add specific context.

        Args:
            **kwargs: Additional context parameters

        Returns:
            Formatted context string
        """
        context_parts = [
            f"Project Directory: {self.project_dir}",
        ]

        if self.spec_dir:
            context_parts.append(f"Spec Directory: {self.spec_dir}")

        for key, value in kwargs.items():
            if value is not None:
                context_parts.append(f"{key}: {value}")

        return "\n".join(context_parts)

    @abstractmethod
    def run(self, **kwargs) -> Any:
        """
        Run the agent's main task.

        Subclasses must implement this method.

        Args:
            **kwargs: Task-specific parameters

        Returns:
            Task result (varies by agent type)
        """
        pass

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"project_dir={self.project_dir!r}, "
            f"spec_dir={self.spec_dir!r}, "
            f"model={self.model!r})"
        )
