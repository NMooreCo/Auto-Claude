"""Data models for Content Mode."""

from dataclasses import dataclass, field
from typing import Optional, Any
from pathlib import Path
from datetime import datetime
import json

from .enums import (
    ContentProjectType,
    ContentWorkflowType,
    ContentPhaseType,
    ContentVerificationType,
    ContentArtifactType,
)


@dataclass
class ContentVerification:
    """Verification criteria for a content subtask."""

    type: ContentVerificationType
    """Type of verification to perform."""

    criteria: Optional[str] = None
    """Specific criteria or description of what to verify."""

    template: Optional[str] = None
    """Template path for template_compliance verification."""

    scope: Optional[str] = None
    """Scope of verification (e.g., 'cross_references', 'terminology')."""

    style_guide: Optional[str] = None
    """Style guide path for style_review verification."""

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {"type": self.type.value}
        if self.criteria:
            result["criteria"] = self.criteria
        if self.template:
            result["template"] = self.template
        if self.scope:
            result["scope"] = self.scope
        if self.style_guide:
            result["style_guide"] = self.style_guide
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "ContentVerification":
        """Create from dictionary."""
        return cls(
            type=ContentVerificationType(data["type"]),
            criteria=data.get("criteria"),
            template=data.get("template"),
            scope=data.get("scope"),
            style_guide=data.get("style_guide"),
        )


@dataclass
class ContentSubtask:
    """A subtask in a content workflow."""

    id: str
    """Unique identifier for this subtask."""

    description: str
    """Human-readable description of what this subtask does."""

    artifact_type: ContentArtifactType
    """Type of artifact this subtask produces."""

    status: str = "pending"
    """Current status: pending, in_progress, completed, blocked, failed."""

    # Input references
    files_to_read: list[str] = field(default_factory=list)
    """Files that should be read before executing this subtask."""

    template: Optional[str] = None
    """Template file to follow when creating content."""

    # Output
    output: Optional[str] = None
    """Output file path for this subtask."""

    # Verification
    verification: Optional[ContentVerification] = None
    """How to verify this subtask was completed successfully."""

    # Dependencies
    depends_on: list[str] = field(default_factory=list)
    """IDs of subtasks that must complete before this one."""

    # Metadata
    notes: Optional[str] = None
    """Additional notes or context for this subtask."""

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "id": self.id,
            "description": self.description,
            "artifact_type": self.artifact_type.value,
            "status": self.status,
        }
        if self.files_to_read:
            result["files_to_read"] = self.files_to_read
        if self.template:
            result["template"] = self.template
        if self.output:
            result["output"] = self.output
        if self.verification:
            result["verification"] = self.verification.to_dict()
        if self.depends_on:
            result["depends_on"] = self.depends_on
        if self.notes:
            result["notes"] = self.notes
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "ContentSubtask":
        """Create from dictionary."""
        verification = None
        if "verification" in data:
            verification = ContentVerification.from_dict(data["verification"])

        return cls(
            id=data["id"],
            description=data["description"],
            artifact_type=ContentArtifactType(data["artifact_type"]),
            status=data.get("status", "pending"),
            files_to_read=data.get("files_to_read", []),
            template=data.get("template"),
            output=data.get("output"),
            verification=verification,
            depends_on=data.get("depends_on", []),
            notes=data.get("notes"),
        )


@dataclass
class ContentPhase:
    """A phase in a content workflow."""

    id: str
    """Unique identifier for this phase."""

    name: str
    """Human-readable name for this phase."""

    type: ContentPhaseType
    """Type of phase (concept, draft, review, etc.)."""

    description: str
    """Description of what this phase accomplishes."""

    subtasks: list[ContentSubtask] = field(default_factory=list)
    """Subtasks within this phase."""

    depends_on: list[str] = field(default_factory=list)
    """IDs of phases that must complete before this one."""

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "subtasks": [s.to_dict() for s in self.subtasks],
            "depends_on": self.depends_on,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ContentPhase":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            type=ContentPhaseType(data["type"]),
            description=data["description"],
            subtasks=[ContentSubtask.from_dict(s) for s in data.get("subtasks", [])],
            depends_on=data.get("depends_on", []),
        )

    def get_pending_subtasks(self) -> list[ContentSubtask]:
        """Get all pending subtasks in this phase."""
        return [s for s in self.subtasks if s.status == "pending"]

    def get_next_subtask(self) -> Optional[ContentSubtask]:
        """Get the next subtask to work on, respecting dependencies."""
        completed_ids = {s.id for s in self.subtasks if s.status == "completed"}

        for subtask in self.subtasks:
            if subtask.status != "pending":
                continue
            # Check if all dependencies are completed
            if all(dep in completed_ids for dep in subtask.depends_on):
                return subtask

        return None

    def is_complete(self) -> bool:
        """Check if all subtasks in this phase are completed."""
        return all(s.status == "completed" for s in self.subtasks)


@dataclass
class ContentPlan:
    """A complete content creation plan."""

    project_name: str
    """Name of this content project."""

    project_type: ContentProjectType
    """Type of content project."""

    workflow_type: ContentWorkflowType
    """Type of workflow being executed."""

    workflow_rationale: str
    """Explanation of why this workflow type was chosen."""

    # Context
    context: dict = field(default_factory=dict)
    """Project context (existing content, templates, style guides, etc.)."""

    # Phases
    phases: list[ContentPhase] = field(default_factory=list)
    """Ordered list of phases in this workflow."""

    # Deliverables
    deliverables: list[dict] = field(default_factory=list)
    """Expected deliverables from this plan."""

    # Quality
    quality_criteria: dict = field(default_factory=dict)
    """Quality criteria that must be met."""

    # Domain-specific configuration
    game_specific: Optional[dict] = None
    """Game-specific configuration (balance checks, keywords, etc.)."""

    doc_specific: Optional[dict] = None
    """Documentation-specific configuration (code linkage, freshness, etc.)."""

    # Summary
    summary: dict = field(default_factory=dict)
    """Summary statistics and metadata."""

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "project_name": self.project_name,
            "project_type": self.project_type.value,
            "workflow_type": self.workflow_type.value,
            "workflow_rationale": self.workflow_rationale,
            "context": self.context,
            "phases": [p.to_dict() for p in self.phases],
            "deliverables": self.deliverables,
            "quality_criteria": self.quality_criteria,
            "summary": self.summary,
        }
        if self.game_specific:
            result["game_specific"] = self.game_specific
        if self.doc_specific:
            result["doc_specific"] = self.doc_specific
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "ContentPlan":
        """Create from dictionary."""
        return cls(
            project_name=data["project_name"],
            project_type=ContentProjectType(data["project_type"]),
            workflow_type=ContentWorkflowType(data["workflow_type"]),
            workflow_rationale=data["workflow_rationale"],
            context=data.get("context", {}),
            phases=[ContentPhase.from_dict(p) for p in data.get("phases", [])],
            deliverables=data.get("deliverables", []),
            quality_criteria=data.get("quality_criteria", {}),
            game_specific=data.get("game_specific"),
            doc_specific=data.get("doc_specific"),
            summary=data.get("summary", {}),
        )

    @classmethod
    def load(cls, path: Path | str) -> "ContentPlan":
        """Load a content plan from a JSON file."""
        path = Path(path)
        with open(path) as f:
            data = json.load(f)
        return cls.from_dict(data)

    def save(self, path: Path | str) -> None:
        """Save the content plan to a JSON file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    def save_to_unified(self, path: Path | str) -> None:
        """Save the content plan to unified implementation_plan.json format."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Read existing data to preserve any fields we didn't modify
        existing_data = {}
        if path.exists():
            with open(path) as f:
                existing_data = json.load(f)

        # Update with current plan state
        plan_data = {
            **existing_data,
            "feature": self.project_name,
            "description": self.workflow_rationale,
            "workflow_type": "content",
            "planType": "content",
            "contentProjectType": self.project_type.value,
            "contentWorkflowType": self.workflow_type.value,
            "phases": [
                {
                    "phase": idx + 1,
                    "name": phase.name,
                    "type": phase.type.value,
                    "description": phase.description,
                    "subtasks": [
                        {
                            "id": subtask.id,
                            "description": subtask.description,
                            "status": subtask.status,
                            "artifact_type": subtask.artifact_type.value if subtask.artifact_type else None,
                            "output": subtask.output,
                        }
                        for subtask in phase.subtasks
                    ],
                    "depends_on": [int(d.replace("phase_", "")) for d in phase.depends_on if d.startswith("phase_")] if phase.depends_on else [],
                }
                for idx, phase in enumerate(self.phases)
            ],
            "deliverables": self.deliverables,
            "quality_criteria": self.quality_criteria,
            "context": self.context,
            "summary": self.summary,
            "updated_at": datetime.now().isoformat(),
        }

        if self.game_specific:
            plan_data["game_specific"] = self.game_specific
        if self.doc_specific:
            plan_data["doc_specific"] = self.doc_specific

        with open(path, "w") as f:
            json.dump(plan_data, f, indent=2)

    @classmethod
    def load_from_unified(cls, path: Path | str) -> "ContentPlan":
        """Load ContentPlan from unified implementation_plan.json format."""
        path = Path(path)
        with open(path) as f:
            data = json.load(f)

        # Convert unified format back to ContentPlan structure
        return cls(
            project_name=data.get("feature", "Untitled"),
            project_type=ContentProjectType(data.get("contentProjectType", "general")),
            workflow_type=ContentWorkflowType(data.get("contentWorkflowType", "create")),
            workflow_rationale=data.get("description", ""),
            context=data.get("context", {}),
            phases=[
                ContentPhase(
                    id=f"phase_{p['phase']}",
                    name=p["name"],
                    type=ContentPhaseType(p.get("type", "draft")),
                    description=p.get("description", ""),
                    subtasks=[
                        ContentSubtask(
                            id=s["id"],
                            description=s["description"],
                            artifact_type=ContentArtifactType(s.get("artifact_type", "document")),
                            status=s.get("status", "pending"),
                            output=s.get("output"),
                        )
                        for s in p.get("subtasks", [])
                    ],
                )
                for p in data.get("phases", [])
            ],
            deliverables=data.get("deliverables", []),
            quality_criteria=data.get("quality_criteria", {}),
            game_specific=data.get("game_specific"),
            doc_specific=data.get("doc_specific"),
            summary=data.get("summary", {}),
        )

    def get_current_phase(self) -> Optional[ContentPhase]:
        """Get the current phase (first incomplete phase with completed dependencies)."""
        completed_phase_ids = {p.id for p in self.phases if p.is_complete()}

        for phase in self.phases:
            if phase.is_complete():
                continue
            # Check if all dependencies are completed
            if all(dep in completed_phase_ids for dep in phase.depends_on):
                return phase

        return None

    def get_next_subtask(self) -> Optional[tuple[ContentPhase, ContentSubtask]]:
        """Get the next subtask to work on across all phases."""
        current_phase = self.get_current_phase()
        if not current_phase:
            return None

        next_subtask = current_phase.get_next_subtask()
        if next_subtask:
            return (current_phase, next_subtask)

        return None

    def get_progress(self) -> dict:
        """Get progress statistics for this plan."""
        total_subtasks = sum(len(p.subtasks) for p in self.phases)
        completed_subtasks = sum(
            len([s for s in p.subtasks if s.status == "completed"])
            for p in self.phases
        )
        in_progress_subtasks = sum(
            len([s for s in p.subtasks if s.status == "in_progress"])
            for p in self.phases
        )

        completed_phases = len([p for p in self.phases if p.is_complete()])

        return {
            "total_phases": len(self.phases),
            "completed_phases": completed_phases,
            "total_subtasks": total_subtasks,
            "completed_subtasks": completed_subtasks,
            "in_progress_subtasks": in_progress_subtasks,
            "pending_subtasks": total_subtasks - completed_subtasks - in_progress_subtasks,
            "percent_complete": (
                round(completed_subtasks / total_subtasks * 100, 1)
                if total_subtasks > 0
                else 0
            ),
        }

    def mark_subtask_status(self, subtask_id: str, status: str) -> bool:
        """Mark a subtask's status. Returns True if found and updated."""
        for phase in self.phases:
            for subtask in phase.subtasks:
                if subtask.id == subtask_id:
                    subtask.status = status
                    return True
        return False

    def is_complete(self) -> bool:
        """Check if the entire plan is complete."""
        return all(p.is_complete() for p in self.phases)
