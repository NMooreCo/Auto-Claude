"""Enumerations for Content Mode workflows."""

from enum import Enum


class ContentProjectType(str, Enum):
    """Types of content projects supported by Content Mode."""

    # Creative Projects
    CARD_GAME = "card_game"
    """Card collecting/trading games (Pokemon, Magic: The Gathering style)."""

    BOARD_GAME = "board_game"
    """Board games with rules, components, and player interactions."""

    TTRPG = "ttrpg"
    """Tabletop RPGs like D&D - campaigns, monsters, items, adventures."""

    WORLDBUILDING = "worldbuilding"
    """Fiction world creation - lore, maps, factions, history."""

    FICTION = "fiction"
    """Creative writing - novels, short stories, series."""

    BUSINESS = "business"
    """Business content - plans, pitches, analysis, roadmaps."""

    # Documentation Projects
    CODEBASE_DOCS = "codebase_docs"
    """Full codebase documentation - architecture, guides, references."""

    API_DOCS = "api_docs"
    """API reference documentation - endpoints, schemas, examples."""

    ARCHITECTURE = "architecture"
    """Architecture documentation - ADRs, component docs, diagrams."""

    KNOWLEDGE_BASE = "knowledge_base"
    """Internal knowledge bases - runbooks, guides, wikis."""

    # General
    GENERAL = "general"
    """General creative/content work not fitting other categories."""


class ContentWorkflowType(str, Enum):
    """Workflow types for content projects."""

    # Creation workflows
    CREATE = "create"
    """Create new content from scratch."""

    EXPAND = "expand"
    """Add to existing content, extending what's there."""

    GENERATE = "generate"
    """Generate content from a source (e.g., code → documentation)."""

    # Refinement workflows
    ITERATE = "iterate"
    """Refine content based on feedback or review."""

    BALANCE = "balance"
    """Game balance pass - adjust power levels, costs, etc."""

    # Quality workflows
    AUDIT = "audit"
    """Audit content for coverage, freshness, accuracy."""

    REVIEW = "review"
    """Quality review of existing content."""


class ContentPhaseType(str, Enum):
    """Phase types for content workflows."""

    # Ideation phases
    CONCEPT = "concept"
    """Brainstorming, ideation, high-level concept development."""

    RESEARCH = "research"
    """Research gathering, competitive analysis, reference collection."""

    # Creation phases
    OUTLINE = "outline"
    """Structure and outline before full drafting."""

    DRAFT = "draft"
    """First-pass content creation."""

    # Refinement phases
    REVIEW = "review"
    """Quality review and critique."""

    REVISE = "revise"
    """Apply feedback and make improvements."""

    POLISH = "polish"
    """Final cleanup and polish."""

    # Validation phases
    CONSISTENCY = "consistency"
    """Cross-reference and terminology consistency check."""

    BALANCE = "balance"
    """Game balance analysis and adjustment."""

    # Documentation-specific phases
    ANALYSIS = "analysis"
    """Code analysis for documentation generation."""

    VERIFICATION = "verification"
    """Verify documentation matches code/reality."""

    # Finalization
    FINALIZE = "finalize"
    """Final checks, indexing, and completion."""


class ContentVerificationType(str, Enum):
    """Verification types for content subtasks."""

    TEMPLATE_COMPLIANCE = "template_compliance"
    """Verify content follows the required template structure."""

    COMPLETENESS = "completeness"
    """Verify all required sections/fields are present."""

    CONSISTENCY_CHECK = "consistency_check"
    """Verify cross-references and terminology are consistent."""

    STYLE_REVIEW = "style_review"
    """Verify content matches style guide tone and voice."""

    ACCURACY_CHECK = "accuracy_check"
    """Verify content is factually accurate (for docs: matches code)."""

    PEER_REVIEW = "peer_review"
    """Requires review by another agent."""

    BALANCE_REVIEW = "balance_review"
    """Verify game balance is appropriate."""

    FILE_EXISTS = "file_exists"
    """Simply verify the output file was created."""

    MANUAL = "manual"
    """Requires manual human verification."""


class ContentArtifactType(str, Enum):
    """Types of content artifacts produced by subtasks."""

    CONTENT = "content"
    """Primary content deliverable (card, chapter, doc page, etc.)."""

    ANALYSIS = "analysis"
    """Research or analysis output."""

    VALIDATION = "validation"
    """Review or validation results."""

    REVISION = "revision"
    """Updated version of existing content."""

    INDEXING = "indexing"
    """Index or cross-reference updates."""

    TEMPLATE = "template"
    """New or updated template."""

    REPORT = "report"
    """Reports (balance report, consistency report, etc.)."""

    PLAN = "plan"
    """Planning documents or outlines."""
