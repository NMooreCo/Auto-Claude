#!/usr/bin/env python3
"""
Tests for Content Mode
======================

Tests the Content Mode implementation including:
- Enums and their values
- Models (ContentSubtask, ContentPhase, ContentPlan)
- Project type detection
- Project scaffolding
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import content module components
from content import (
    ContentProjectType,
    ContentWorkflowType,
    ContentPhaseType,
    ContentVerificationType,
    ContentArtifactType,
    ContentSubtask,
    ContentPhase,
    ContentPlan,
    ContentProjectDetector,
)
from content.models import ContentVerification
from content.scaffold import ContentProjectScaffolder


# =============================================================================
# ENUM TESTS
# =============================================================================


class TestContentEnums:
    """Tests for Content Mode enumerations."""

    def test_content_project_type_values(self):
        """Verify all expected project types exist."""
        expected_types = [
            "card_game",
            "board_game",
            "ttrpg",
            "worldbuilding",
            "fiction",
            "business",
            "codebase_docs",
            "api_docs",
            "architecture",
            "knowledge_base",
            "general",
        ]
        actual_types = [t.value for t in ContentProjectType]
        for expected in expected_types:
            assert expected in actual_types, f"Missing project type: {expected}"

    def test_content_workflow_type_values(self):
        """Verify all expected workflow types exist."""
        expected_types = [
            "create",
            "expand",
            "iterate",
            "generate",
            "audit",
            "balance",
            "review",
        ]
        actual_types = [t.value for t in ContentWorkflowType]
        for expected in expected_types:
            assert expected in actual_types, f"Missing workflow type: {expected}"

    def test_content_phase_type_values(self):
        """Verify all expected phase types exist."""
        expected_types = [
            "concept",
            "research",
            "outline",
            "draft",
            "review",
            "revise",
            "polish",
            "consistency",
            "balance",
            "analysis",
            "verification",
            "finalize",
        ]
        actual_types = [t.value for t in ContentPhaseType]
        for expected in expected_types:
            assert expected in actual_types, f"Missing phase type: {expected}"

    def test_content_verification_type_values(self):
        """Verify all expected verification types exist."""
        expected_types = [
            "template_compliance",
            "completeness",
            "consistency_check",
            "style_review",
            "accuracy_check",
            "peer_review",
            "balance_review",
            "file_exists",
            "manual",
        ]
        actual_types = [t.value for t in ContentVerificationType]
        for expected in expected_types:
            assert expected in actual_types, f"Missing verification type: {expected}"

    def test_content_artifact_type_values(self):
        """Verify all expected artifact types exist."""
        expected_types = [
            "content",
            "analysis",
            "validation",
            "revision",
            "indexing",
            "template",
            "report",
            "plan",
        ]
        actual_types = [t.value for t in ContentArtifactType]
        for expected in expected_types:
            assert expected in actual_types, f"Missing artifact type: {expected}"

    def test_enum_string_conversion(self):
        """Verify enums convert to strings properly."""
        assert ContentProjectType.CARD_GAME.value == "card_game"
        assert str(ContentProjectType.CARD_GAME) == "ContentProjectType.CARD_GAME"
        assert ContentWorkflowType.CREATE.value == "create"


# =============================================================================
# MODEL TESTS
# =============================================================================


class TestContentVerification:
    """Tests for ContentVerification model."""

    def test_verification_creation(self):
        """Test creating a verification object."""
        verification = ContentVerification(
            type=ContentVerificationType.TEMPLATE_COMPLIANCE,
            template="cards/_template.md",
        )
        assert verification.type == ContentVerificationType.TEMPLATE_COMPLIANCE
        assert verification.template == "cards/_template.md"

    def test_verification_to_dict(self):
        """Test serializing verification to dictionary."""
        verification = ContentVerification(
            type=ContentVerificationType.STYLE_REVIEW,
            style_guide="style-guide/style.md",
            criteria="Match tone",
        )
        result = verification.to_dict()
        assert result["type"] == "style_review"
        assert result["style_guide"] == "style-guide/style.md"
        assert result["criteria"] == "Match tone"

    def test_verification_from_dict(self):
        """Test deserializing verification from dictionary."""
        data = {
            "type": "completeness",
            "criteria": "All sections filled",
        }
        verification = ContentVerification.from_dict(data)
        assert verification.type == ContentVerificationType.COMPLETENESS
        assert verification.criteria == "All sections filled"


class TestContentSubtask:
    """Tests for ContentSubtask model."""

    def test_subtask_creation(self):
        """Test creating a subtask."""
        subtask = ContentSubtask(
            id="subtask-1",
            description="Create flame elemental card",
            artifact_type=ContentArtifactType.CONTENT,
            template="cards/_template.md",
            output="cards/fire/flame-elemental.md",
        )
        assert subtask.id == "subtask-1"
        assert subtask.status == "pending"
        assert subtask.artifact_type == ContentArtifactType.CONTENT

    def test_subtask_to_dict(self):
        """Test serializing subtask to dictionary."""
        subtask = ContentSubtask(
            id="subtask-1",
            description="Test subtask",
            artifact_type=ContentArtifactType.CONTENT,
            files_to_read=["rules/keywords.md"],
            verification=ContentVerification(
                type=ContentVerificationType.FILE_EXISTS,
            ),
        )
        result = subtask.to_dict()
        assert result["id"] == "subtask-1"
        assert result["artifact_type"] == "content"
        assert result["files_to_read"] == ["rules/keywords.md"]
        assert result["verification"]["type"] == "file_exists"

    def test_subtask_from_dict(self):
        """Test deserializing subtask from dictionary."""
        data = {
            "id": "subtask-2",
            "description": "Review cards",
            "artifact_type": "validation",
            "status": "completed",
            "depends_on": ["subtask-1"],
        }
        subtask = ContentSubtask.from_dict(data)
        assert subtask.id == "subtask-2"
        assert subtask.status == "completed"
        assert subtask.artifact_type == ContentArtifactType.VALIDATION
        assert subtask.depends_on == ["subtask-1"]


class TestContentPhase:
    """Tests for ContentPhase model."""

    def test_phase_creation(self):
        """Test creating a phase."""
        phase = ContentPhase(
            id="phase-1",
            name="Drafting",
            type=ContentPhaseType.DRAFT,
            description="Create initial drafts",
        )
        assert phase.id == "phase-1"
        assert phase.type == ContentPhaseType.DRAFT
        assert phase.subtasks == []

    def test_phase_with_subtasks(self):
        """Test phase with subtasks."""
        subtask1 = ContentSubtask(
            id="s1",
            description="First task",
            artifact_type=ContentArtifactType.CONTENT,
            status="completed",
        )
        subtask2 = ContentSubtask(
            id="s2",
            description="Second task",
            artifact_type=ContentArtifactType.CONTENT,
            status="pending",
        )
        phase = ContentPhase(
            id="phase-1",
            name="Test Phase",
            type=ContentPhaseType.DRAFT,
            description="Test",
            subtasks=[subtask1, subtask2],
        )
        assert len(phase.subtasks) == 2
        assert not phase.is_complete()

    def test_phase_is_complete(self):
        """Test phase completion check."""
        subtask1 = ContentSubtask(
            id="s1",
            description="Task",
            artifact_type=ContentArtifactType.CONTENT,
            status="completed",
        )
        subtask2 = ContentSubtask(
            id="s2",
            description="Task",
            artifact_type=ContentArtifactType.CONTENT,
            status="completed",
        )
        phase = ContentPhase(
            id="phase-1",
            name="Test",
            type=ContentPhaseType.DRAFT,
            description="Test",
            subtasks=[subtask1, subtask2],
        )
        assert phase.is_complete()

    def test_phase_get_next_subtask(self):
        """Test getting next subtask respects dependencies."""
        subtask1 = ContentSubtask(
            id="s1",
            description="First",
            artifact_type=ContentArtifactType.CONTENT,
            status="pending",
        )
        subtask2 = ContentSubtask(
            id="s2",
            description="Second",
            artifact_type=ContentArtifactType.CONTENT,
            status="pending",
            depends_on=["s1"],
        )
        phase = ContentPhase(
            id="phase-1",
            name="Test",
            type=ContentPhaseType.DRAFT,
            description="Test",
            subtasks=[subtask1, subtask2],
        )
        next_subtask = phase.get_next_subtask()
        assert next_subtask.id == "s1"

    def test_phase_to_dict_and_from_dict(self):
        """Test phase serialization round-trip."""
        subtask = ContentSubtask(
            id="s1",
            description="Task",
            artifact_type=ContentArtifactType.CONTENT,
        )
        phase = ContentPhase(
            id="phase-1",
            name="Test Phase",
            type=ContentPhaseType.DRAFT,
            description="A test phase",
            subtasks=[subtask],
            depends_on=["phase-0"],
        )
        data = phase.to_dict()
        restored = ContentPhase.from_dict(data)
        assert restored.id == phase.id
        assert restored.name == phase.name
        assert restored.type == phase.type
        assert len(restored.subtasks) == 1
        assert restored.depends_on == ["phase-0"]


class TestContentPlan:
    """Tests for ContentPlan model."""

    def test_plan_creation(self):
        """Test creating a content plan."""
        plan = ContentPlan(
            project_name="Test Card Game",
            project_type=ContentProjectType.CARD_GAME,
            workflow_type=ContentWorkflowType.CREATE,
            workflow_rationale="Creating new cards from scratch",
        )
        assert plan.project_name == "Test Card Game"
        assert plan.project_type == ContentProjectType.CARD_GAME
        assert plan.phases == []

    def test_plan_with_phases(self):
        """Test plan with phases."""
        phase = ContentPhase(
            id="phase-1",
            name="Draft",
            type=ContentPhaseType.DRAFT,
            description="Draft content",
            subtasks=[
                ContentSubtask(
                    id="s1",
                    description="Task",
                    artifact_type=ContentArtifactType.CONTENT,
                )
            ],
        )
        plan = ContentPlan(
            project_name="Test",
            project_type=ContentProjectType.CARD_GAME,
            workflow_type=ContentWorkflowType.CREATE,
            workflow_rationale="Test",
            phases=[phase],
        )
        assert len(plan.phases) == 1

    def test_plan_get_progress(self):
        """Test progress calculation."""
        subtask1 = ContentSubtask(
            id="s1",
            description="Task 1",
            artifact_type=ContentArtifactType.CONTENT,
            status="completed",
        )
        subtask2 = ContentSubtask(
            id="s2",
            description="Task 2",
            artifact_type=ContentArtifactType.CONTENT,
            status="pending",
        )
        phase = ContentPhase(
            id="phase-1",
            name="Draft",
            type=ContentPhaseType.DRAFT,
            description="Draft",
            subtasks=[subtask1, subtask2],
        )
        plan = ContentPlan(
            project_name="Test",
            project_type=ContentProjectType.CARD_GAME,
            workflow_type=ContentWorkflowType.CREATE,
            workflow_rationale="Test",
            phases=[phase],
        )
        progress = plan.get_progress()
        assert progress["total_subtasks"] == 2
        assert progress["completed_subtasks"] == 1
        assert progress["percent_complete"] == 50.0

    def test_plan_save_and_load(self, tmp_path):
        """Test saving and loading plan from JSON."""
        plan = ContentPlan(
            project_name="Test Project",
            project_type=ContentProjectType.TTRPG,
            workflow_type=ContentWorkflowType.EXPAND,
            workflow_rationale="Adding new content",
            context={"templates_in_use": ["bestiary/_template.md"]},
            phases=[
                ContentPhase(
                    id="phase-1",
                    name="Draft",
                    type=ContentPhaseType.DRAFT,
                    description="Create drafts",
                    subtasks=[
                        ContentSubtask(
                            id="s1",
                            description="Create monster",
                            artifact_type=ContentArtifactType.CONTENT,
                        )
                    ],
                )
            ],
        )

        # Save
        plan_path = tmp_path / "content_plan.json"
        plan.save(plan_path)
        assert plan_path.exists()

        # Load
        loaded = ContentPlan.load(plan_path)
        assert loaded.project_name == "Test Project"
        assert loaded.project_type == ContentProjectType.TTRPG
        assert len(loaded.phases) == 1
        assert loaded.phases[0].subtasks[0].id == "s1"

    def test_plan_mark_subtask_status(self):
        """Test marking subtask status."""
        plan = ContentPlan(
            project_name="Test",
            project_type=ContentProjectType.CARD_GAME,
            workflow_type=ContentWorkflowType.CREATE,
            workflow_rationale="Test",
            phases=[
                ContentPhase(
                    id="phase-1",
                    name="Draft",
                    type=ContentPhaseType.DRAFT,
                    description="Draft",
                    subtasks=[
                        ContentSubtask(
                            id="s1",
                            description="Task",
                            artifact_type=ContentArtifactType.CONTENT,
                        )
                    ],
                )
            ],
        )
        result = plan.mark_subtask_status("s1", "completed")
        assert result is True
        assert plan.phases[0].subtasks[0].status == "completed"

    def test_plan_get_next_subtask(self):
        """Test getting next subtask across phases."""
        plan = ContentPlan(
            project_name="Test",
            project_type=ContentProjectType.CARD_GAME,
            workflow_type=ContentWorkflowType.CREATE,
            workflow_rationale="Test",
            phases=[
                ContentPhase(
                    id="phase-1",
                    name="Draft",
                    type=ContentPhaseType.DRAFT,
                    description="Draft",
                    subtasks=[
                        ContentSubtask(
                            id="s1",
                            description="Task",
                            artifact_type=ContentArtifactType.CONTENT,
                            status="pending",
                        )
                    ],
                ),
                ContentPhase(
                    id="phase-2",
                    name="Review",
                    type=ContentPhaseType.REVIEW,
                    description="Review",
                    depends_on=["phase-1"],
                    subtasks=[
                        ContentSubtask(
                            id="s2",
                            description="Review",
                            artifact_type=ContentArtifactType.VALIDATION,
                            status="pending",
                        )
                    ],
                ),
            ],
        )
        result = plan.get_next_subtask()
        assert result is not None
        phase, subtask = result
        assert subtask.id == "s1"  # Should get first phase's subtask


# =============================================================================
# DETECTOR TESTS
# =============================================================================


class TestContentProjectDetector:
    """Tests for ContentProjectDetector."""

    def test_detect_card_game_by_structure(self, tmp_path):
        """Test detecting card game from directory structure."""
        # Create card game structure
        (tmp_path / "cards").mkdir()
        (tmp_path / "rules").mkdir()
        (tmp_path / "keywords.md").write_text("# Keywords")

        detector = ContentProjectDetector()
        result = detector.detect(str(tmp_path))
        assert result == ContentProjectType.CARD_GAME

    def test_detect_ttrpg_by_structure(self, tmp_path):
        """Test detecting TTRPG from directory structure."""
        (tmp_path / "bestiary").mkdir()
        (tmp_path / "adventures").mkdir()
        (tmp_path / "characters").mkdir()

        detector = ContentProjectDetector()
        result = detector.detect(str(tmp_path))
        assert result == ContentProjectType.TTRPG

    def test_detect_board_game_by_structure(self, tmp_path):
        """Test detecting board game from directory structure."""
        (tmp_path / "rules").mkdir()
        (tmp_path / "components").mkdir()
        (tmp_path / "setup.md").write_text("# Setup")

        detector = ContentProjectDetector()
        result = detector.detect(str(tmp_path))
        assert result == ContentProjectType.BOARD_GAME

    def test_detect_worldbuilding_by_structure(self, tmp_path):
        """Test detecting worldbuilding from directory structure."""
        (tmp_path / "world").mkdir()
        (tmp_path / "factions").mkdir()
        (tmp_path / "history.md").write_text("# History")

        detector = ContentProjectDetector()
        result = detector.detect(str(tmp_path))
        assert result == ContentProjectType.WORLDBUILDING

    def test_detect_codebase_docs_by_structure(self, tmp_path):
        """Test detecting codebase docs from directory structure."""
        (tmp_path / "docs" / "api").mkdir(parents=True)
        (tmp_path / "docs" / "architecture").mkdir()

        detector = ContentProjectDetector()
        result = detector.detect(str(tmp_path))
        assert result == ContentProjectType.CODEBASE_DOCS

    def test_detect_general_for_empty_dir(self, tmp_path):
        """Test detecting general for empty directory."""
        detector = ContentProjectDetector()
        result = detector.detect(str(tmp_path))
        assert result == ContentProjectType.GENERAL

    def test_detect_from_description_card_game(self):
        """Test detecting card game from description."""
        detector = ContentProjectDetector()
        result = detector.detect_from_description(
            "Create 5 new creature cards with mana costs for the fire deck"
        )
        assert result == ContentProjectType.CARD_GAME

    def test_detect_from_description_ttrpg(self):
        """Test detecting TTRPG from description."""
        detector = ContentProjectDetector()
        result = detector.detect_from_description(
            "Design a new dungeon with monsters for the campaign"
        )
        assert result == ContentProjectType.TTRPG

    def test_detect_from_description_documentation(self):
        """Test detecting documentation from description."""
        detector = ContentProjectDetector()
        result = detector.detect_from_description(
            "Document the API endpoints for the authentication service"
        )
        # Both CODEBASE_DOCS and API_DOCS are valid documentation types
        assert result in [ContentProjectType.CODEBASE_DOCS, ContentProjectType.API_DOCS]

    def test_detect_from_description_general(self):
        """Test detecting general for vague description."""
        detector = ContentProjectDetector()
        result = detector.detect_from_description("Do something")
        assert result == ContentProjectType.GENERAL

    def test_is_content_task_true(self):
        """Test identifying content tasks."""
        detector = ContentProjectDetector()
        assert detector.is_content_task("Write a story about dragons")
        assert detector.is_content_task("Create cards for the water faction")
        assert detector.is_content_task("Design a new monster for the campaign")
        assert detector.is_content_task("Write documentation for the API")

    def test_is_content_task_false(self):
        """Test identifying code tasks."""
        detector = ContentProjectDetector()
        assert not detector.is_content_task("Fix the authentication bug")
        assert not detector.is_content_task("Implement the user service")
        assert not detector.is_content_task("Refactor the database module")

    def test_detect_combined(self, tmp_path):
        """Test combined detection using both structure and description."""
        # Create ambiguous structure
        (tmp_path / "docs").mkdir()

        detector = ContentProjectDetector()

        # With card game description, should detect card game
        result = detector.detect_combined(
            str(tmp_path), "Create new cards for the expansion set"
        )
        assert result == ContentProjectType.CARD_GAME

    def test_get_project_info(self, tmp_path):
        """Test getting detailed project info."""
        # Create a card game project
        (tmp_path / "cards").mkdir()
        (tmp_path / "cards" / "_template.md").write_text("# Template")
        (tmp_path / "rules").mkdir()
        (tmp_path / "style-guide").mkdir()
        (tmp_path / "style-guide" / "naming.md").write_text("# Naming")
        (tmp_path / "_index.md").write_text("# Index")

        detector = ContentProjectDetector()
        info = detector.get_project_info(str(tmp_path))

        assert info["project_type"] == "card_game"
        assert "cards/_template.md" in info["templates_found"]
        assert "_index.md" in info["index_files"]
        assert "style-guide/naming.md" in info["style_guides_found"]


# =============================================================================
# SCAFFOLD TESTS
# =============================================================================


class TestContentProjectScaffolder:
    """Tests for ContentProjectScaffolder."""

    def test_scaffold_card_game(self, tmp_path):
        """Test scaffolding a card game project."""
        scaffolder = ContentProjectScaffolder()
        scaffolder.scaffold(str(tmp_path), ContentProjectType.CARD_GAME)

        # Check directories created
        assert (tmp_path / "cards").is_dir()
        assert (tmp_path / "rules").is_dir()
        assert (tmp_path / "style-guide").is_dir()
        assert (tmp_path / "formats").is_dir()
        assert (tmp_path / "playtests").is_dir()

        # Check files created
        assert (tmp_path / "_index.md").exists()
        assert (tmp_path / "rules" / "core-rules.md").exists()
        assert (tmp_path / "rules" / "keywords.md").exists()
        assert (tmp_path / "cards" / "_template.md").exists()
        assert (tmp_path / "style-guide" / "power-levels.md").exists()

    def test_scaffold_ttrpg(self, tmp_path):
        """Test scaffolding a TTRPG project."""
        scaffolder = ContentProjectScaffolder()
        scaffolder.scaffold(str(tmp_path), ContentProjectType.TTRPG)

        assert (tmp_path / "bestiary").is_dir()
        assert (tmp_path / "adventures").is_dir()
        assert (tmp_path / "world").is_dir()
        assert (tmp_path / "items").is_dir()
        assert (tmp_path / "_index.md").exists()
        assert (tmp_path / "bestiary" / "_template.md").exists()

    def test_scaffold_board_game(self, tmp_path):
        """Test scaffolding a board game project."""
        scaffolder = ContentProjectScaffolder()
        scaffolder.scaffold(str(tmp_path), ContentProjectType.BOARD_GAME)

        assert (tmp_path / "rules").is_dir()
        assert (tmp_path / "components").is_dir()
        assert (tmp_path / "player-aids").is_dir()
        assert (tmp_path / "rules" / "setup.md").exists()
        assert (tmp_path / "rules" / "turn-structure.md").exists()

    def test_scaffold_worldbuilding(self, tmp_path):
        """Test scaffolding a worldbuilding project."""
        scaffolder = ContentProjectScaffolder()
        scaffolder.scaffold(str(tmp_path), ContentProjectType.WORLDBUILDING)

        assert (tmp_path / "world").is_dir()
        assert (tmp_path / "factions").is_dir()
        assert (tmp_path / "characters").is_dir()
        assert (tmp_path / "locations").is_dir()
        assert (tmp_path / "history").is_dir()

    def test_scaffold_fiction(self, tmp_path):
        """Test scaffolding a fiction project."""
        scaffolder = ContentProjectScaffolder()
        scaffolder.scaffold(str(tmp_path), ContentProjectType.FICTION)

        assert (tmp_path / "outline").is_dir()
        assert (tmp_path / "characters").is_dir()
        assert (tmp_path / "chapters").is_dir()
        assert (tmp_path / "outline" / "plot.md").exists()
        assert (tmp_path / "characters" / "_template.md").exists()

    def test_scaffold_codebase_docs(self, tmp_path):
        """Test scaffolding a codebase docs project."""
        scaffolder = ContentProjectScaffolder()
        scaffolder.scaffold(str(tmp_path), ContentProjectType.CODEBASE_DOCS)

        assert (tmp_path / "docs").is_dir()
        assert (tmp_path / "docs" / "architecture").is_dir()
        assert (tmp_path / "docs" / "api").is_dir()
        assert (tmp_path / "docs" / "_index.md").exists()
        assert (tmp_path / "docs" / "api" / "_template.md").exists()

    def test_scaffold_general(self, tmp_path):
        """Test scaffolding a general project."""
        scaffolder = ContentProjectScaffolder()
        scaffolder.scaffold(str(tmp_path), ContentProjectType.GENERAL)

        assert (tmp_path / "_index.md").exists()
        assert (tmp_path / "style-guide").is_dir()

    def test_scaffold_creates_directories(self, tmp_path):
        """Test that scaffold creates necessary directories."""
        project_dir = tmp_path / "new_project" / "nested"
        scaffolder = ContentProjectScaffolder()
        scaffolder.scaffold(str(project_dir), ContentProjectType.CARD_GAME)

        assert project_dir.is_dir()
        assert (project_dir / "_index.md").exists()

    def test_scaffold_with_custom_name(self, tmp_path):
        """Test scaffolding with custom project name."""
        scaffolder = ContentProjectScaffolder()
        scaffolder.scaffold(
            str(tmp_path), ContentProjectType.CARD_GAME, project_name="My Card Game"
        )

        index_content = (tmp_path / "_index.md").read_text()
        assert "My Card Game" in index_content


# =============================================================================
# AGENT IMPORT TESTS
# =============================================================================


class TestAgentImports:
    """Tests that agent classes can be imported correctly."""

    def test_import_content_planner_agent(self):
        """Test importing ContentPlannerAgent."""
        from content.agents import ContentPlannerAgent

        assert ContentPlannerAgent is not None
        assert ContentPlannerAgent.PROMPT_FILE == "content_planner.md"

    def test_import_content_creator_agent(self):
        """Test importing ContentCreatorAgent."""
        from content.agents import ContentCreatorAgent

        assert ContentCreatorAgent is not None
        assert ContentCreatorAgent.PROMPT_FILE == "content_creator.md"

    def test_import_content_reviewer_agent(self):
        """Test importing ContentReviewerAgent."""
        from content.agents import ContentReviewerAgent

        assert ContentReviewerAgent is not None
        assert ContentReviewerAgent.PROMPT_FILE == "content_reviewer.md"

    def test_import_content_editor_agent(self):
        """Test importing ContentEditorAgent."""
        from content.agents import ContentEditorAgent

        assert ContentEditorAgent is not None
        assert ContentEditorAgent.PROMPT_FILE == "content_editor.md"

    def test_import_consistency_checker_agent(self):
        """Test importing ConsistencyCheckerAgent."""
        from content.agents import ConsistencyCheckerAgent

        assert ConsistencyCheckerAgent is not None
        assert ConsistencyCheckerAgent.PROMPT_FILE == "content_consistency_checker.md"

    def test_import_balance_analyst_agent(self):
        """Test importing BalanceAnalystAgent."""
        from content.agents import BalanceAnalystAgent

        assert BalanceAnalystAgent is not None
        assert BalanceAnalystAgent.PROMPT_FILE == "game_balance_analyst.md"

    def test_import_code_analyzer_agent(self):
        """Test importing CodeAnalyzerAgent."""
        from content.agents import CodeAnalyzerAgent

        assert CodeAnalyzerAgent is not None
        assert CodeAnalyzerAgent.PROMPT_FILE == "doc_code_analyzer.md"

    def test_all_agents_have_agent_type(self):
        """Test that all agents have AGENT_TYPE defined."""
        from content.agents import (
            ContentPlannerAgent,
            ContentCreatorAgent,
            ContentReviewerAgent,
            ContentEditorAgent,
            ConsistencyCheckerAgent,
            BalanceAnalystAgent,
            CodeAnalyzerAgent,
        )

        agents = [
            ContentPlannerAgent,
            ContentCreatorAgent,
            ContentReviewerAgent,
            ContentEditorAgent,
            ConsistencyCheckerAgent,
            BalanceAnalystAgent,
            CodeAnalyzerAgent,
        ]

        for agent_class in agents:
            assert hasattr(agent_class, "AGENT_TYPE")
            assert agent_class.AGENT_TYPE is not None


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestContentModeIntegration:
    """Integration tests for Content Mode."""

    def test_full_workflow_simulation(self, tmp_path):
        """Test simulating a full content workflow."""
        # 1. Scaffold a project
        scaffolder = ContentProjectScaffolder()
        scaffolder.scaffold(str(tmp_path), ContentProjectType.CARD_GAME)

        # 2. Detect project type
        detector = ContentProjectDetector()
        detected_type = detector.detect(str(tmp_path))
        assert detected_type == ContentProjectType.CARD_GAME

        # 3. Create a plan
        plan = ContentPlan(
            project_name="Test Card Game",
            project_type=detected_type,
            workflow_type=ContentWorkflowType.CREATE,
            workflow_rationale="Creating initial card set",
            phases=[
                ContentPhase(
                    id="phase-1-draft",
                    name="Card Drafting",
                    type=ContentPhaseType.DRAFT,
                    description="Create initial card drafts",
                    subtasks=[
                        ContentSubtask(
                            id="s1",
                            description="Create fire elemental card",
                            artifact_type=ContentArtifactType.CONTENT,
                            template="cards/_template.md",
                            output="cards/fire/fire-elemental.md",
                        ),
                        ContentSubtask(
                            id="s2",
                            description="Create water spirit card",
                            artifact_type=ContentArtifactType.CONTENT,
                            template="cards/_template.md",
                            output="cards/water/water-spirit.md",
                            depends_on=["s1"],
                        ),
                    ],
                ),
                ContentPhase(
                    id="phase-2-review",
                    name="Review",
                    type=ContentPhaseType.REVIEW,
                    description="Review card balance",
                    depends_on=["phase-1-draft"],
                    subtasks=[
                        ContentSubtask(
                            id="s3",
                            description="Review card balance",
                            artifact_type=ContentArtifactType.VALIDATION,
                        ),
                    ],
                ),
            ],
        )

        # 4. Save and load plan
        plan_path = tmp_path / ".auto-claude" / "specs" / "001" / "content_plan.json"
        plan.save(plan_path)
        loaded_plan = ContentPlan.load(plan_path)

        assert loaded_plan.project_name == "Test Card Game"
        assert len(loaded_plan.phases) == 2

        # 5. Simulate execution
        next_result = loaded_plan.get_next_subtask()
        assert next_result is not None
        phase, subtask = next_result
        assert subtask.id == "s1"

        # Mark complete
        loaded_plan.mark_subtask_status("s1", "completed")

        # Next should be s2
        next_result = loaded_plan.get_next_subtask()
        phase, subtask = next_result
        assert subtask.id == "s2"

        # 6. Check progress
        progress = loaded_plan.get_progress()
        assert progress["completed_subtasks"] == 1
        assert progress["total_subtasks"] == 3
