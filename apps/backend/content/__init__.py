"""
Content Mode - Autonomous workflows for creative and documentation projects.

This module provides a parallel pipeline to Auto Claude's code-focused workflow,
enabling autonomous handling of:
- Creative projects (card games, board games, TTRPGs, fiction, worldbuilding)
- Documentation projects (API docs, architecture docs, knowledge bases)
- Business projects (plans, pitches, analysis)
"""

from .enums import (
    ContentProjectType,
    ContentWorkflowType,
    ContentPhaseType,
    ContentVerificationType,
    ContentArtifactType,
)
from .models import (
    ContentSubtask,
    ContentPhase,
    ContentPlan,
)
from .detector import ContentProjectDetector

__all__ = [
    # Enums
    "ContentProjectType",
    "ContentWorkflowType",
    "ContentPhaseType",
    "ContentVerificationType",
    "ContentArtifactType",
    # Models
    "ContentSubtask",
    "ContentPhase",
    "ContentPlan",
    # Detector
    "ContentProjectDetector",
]
