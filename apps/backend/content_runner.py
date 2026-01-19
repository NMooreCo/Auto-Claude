#!/usr/bin/env python3
"""
Content Mode Runner - Entry point for autonomous content creation workflows.

This script provides a CLI interface for running Content Mode workflows,
including planning, creating, reviewing, and editing content.

Usage:
    # Detect project type and get info
    python content_runner.py --project ./my-card-game --info

    # Create a content plan from a task description
    python content_runner.py --project ./my-card-game --task "Create 5 water cards"

    # Execute an existing content plan
    python content_runner.py --project ./my-card-game --spec 001 --execute

    # Run review on completed content
    python content_runner.py --project ./my-card-game --spec 001 --review

    # Run consistency check
    python content_runner.py --project ./my-card-game --spec 001 --consistency

    # Run balance analysis (games only)
    python content_runner.py --project ./my-card-game --spec 001 --balance

    # Initialize a new content project from template
    python content_runner.py --project ./new-game --init card_game
"""

import argparse
import sys
import logging
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from content import (
    ContentProjectDetector,
    ContentProjectType,
    ContentPlan,
)
from content.agents import (
    ContentPlannerAgent,
    ContentCreatorAgent,
    ContentReviewerAgent,
    ContentEditorAgent,
    ConsistencyCheckerAgent,
    BalanceAnalystAgent,
    CodeAnalyzerAgent,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_spec_dir(project_dir: Path, spec: str) -> Path:
    """Get the spec directory path."""
    # Handle numeric spec IDs
    if spec.isdigit():
        spec = f"{int(spec):03d}"

    # Check .auto-claude/specs/ first
    auto_claude_dir = project_dir / ".auto-claude" / "specs"
    if auto_claude_dir.exists():
        # Find matching spec directory
        for spec_dir in auto_claude_dir.iterdir():
            if spec_dir.is_dir() and spec_dir.name.startswith(spec):
                return spec_dir

    # Fall back to direct path
    return project_dir / spec




def cmd_info(args) -> int:
    """Show project information."""
    detector = ContentProjectDetector()
    info = detector.get_project_info(args.project)

    print(f"\n{'='*60}")
    print(f"Content Project Information")
    print(f"{'='*60}")
    print(f"Project Path: {info['project_path']}")
    print(f"Project Type: {info['project_type']}")

    if info['found_indicators']['directories']:
        print(f"\nFound Directories:")
        for d in info['found_indicators']['directories']:
            print(f"  - {d}")

    if info['found_indicators']['files']:
        print(f"\nFound Files:")
        for f in info['found_indicators']['files']:
            print(f"  - {f}")

    if info['templates_found']:
        print(f"\nTemplates Found:")
        for t in info['templates_found']:
            print(f"  - {t}")

    if info['style_guides_found']:
        print(f"\nStyle Guides Found:")
        for s in info['style_guides_found']:
            print(f"  - {s}")

    if info['index_files']:
        print(f"\nIndex Files:")
        for i in info['index_files']:
            print(f"  - {i}")

    print(f"{'='*60}\n")
    return 0


def cmd_plan(args) -> int:
    """Create a content plan from a task description."""
    project_dir = Path(args.project).resolve()

    # Detect project type
    detector = ContentProjectDetector()
    project_type = detector.detect_combined(str(project_dir), args.task)

    print(f"Detected project type: {project_type.value}")

    # Use provided spec directory or create one
    if args.spec_dir:
        spec_dir = Path(args.spec_dir).resolve()
        if not spec_dir.exists():
            print(f"Error: Spec directory does not exist: {spec_dir}")
            return 1
    else:
        # Create spec directory
        spec_dir = project_dir / ".auto-claude" / "specs" / "content-001"
        spec_dir.mkdir(parents=True, exist_ok=True)

    # Save the brief
    brief_path = spec_dir / "spec.md"
    brief_path.write_text(f"# Content Brief\n\n{args.task}\n")

    # Run the planner
    planner = ContentPlannerAgent(
        project_dir=str(project_dir),
        spec_dir=str(spec_dir),
        project_type=project_type,
    )

    print(f"\nCreating content plan...")
    plan = planner.run(brief=args.task)

    print(f"\nPlan created successfully!")
    print(f"  Project: {plan.project_name}")
    print(f"  Workflow: {plan.workflow_type.value}")
    print(f"  Phases: {len(plan.phases)}")

    total_subtasks = sum(len(p.subtasks) for p in plan.phases)
    print(f"  Total Subtasks: {total_subtasks}")

    # Output to implementation_plan.json with unified format
    # This allows the frontend to treat content plans like implementation plans
    plan_data = {
        "feature": plan.project_name,
        "description": plan.workflow_rationale,
        "workflow_type": "content",
        # Content mode discriminator - allows frontend to detect content tasks
        "planType": "content",
        # Content-specific fields for UI display
        "contentProjectType": plan.project_type.value,
        "contentWorkflowType": plan.workflow_type.value,
        # Convert content phases to implementation plan format
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
                        # Content-specific subtask fields
                        "artifact_type": subtask.artifact_type.value if subtask.artifact_type else None,
                        "output": subtask.output,
                    }
                    for subtask in phase.subtasks
                ],
                "depends_on": [int(d.replace("phase_", "")) for d in phase.depends_on if d.startswith("phase_")] if phase.depends_on else [],
            }
            for idx, phase in enumerate(plan.phases)
        ],
        # Additional content plan data
        "deliverables": plan.deliverables,
        "quality_criteria": plan.quality_criteria,
        "context": plan.context,
        "summary": plan.summary,
        # Standard implementation plan fields
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "spec_file": "spec.md",
    }

    # Add optional game/doc specific config if present
    if plan.game_specific:
        plan_data["game_specific"] = plan.game_specific
    if plan.doc_specific:
        plan_data["doc_specific"] = plan.doc_specific

    # Write to implementation_plan.json (unified format)
    impl_plan_path = spec_dir / "implementation_plan.json"
    impl_plan_path.write_text(json.dumps(plan_data, indent=2))

    print(f"\nPlan saved to: {impl_plan_path}")
    print(f"\nTo execute this plan, run:")
    print(f"  python content_runner.py --project {args.project} --spec {spec_dir.name} --execute")

    return 0


def cmd_execute(args) -> int:
    """Execute a content plan."""
    project_dir = Path(args.project).resolve()
    spec_dir = get_spec_dir(project_dir, args.spec)

    # Load the plan from unified implementation_plan.json
    plan_path = spec_dir / "implementation_plan.json"
    if not plan_path.exists():
        print(f"Error: No implementation plan found at {plan_path}")
        return 1

    plan = ContentPlan.load_from_unified(plan_path)

    print(f"\nExecuting content plan: {plan.project_name}")
    print(f"Progress: {plan.get_progress()['percent_complete']}% complete")

    # Create the content creator agent
    creator = ContentCreatorAgent(
        project_dir=str(project_dir),
        spec_dir=str(spec_dir),
    )

    # Execute until done or error
    while not plan.is_complete():
        result = creator.run(plan)

        if result["status"] == "complete":
            break

        if result["status"] == "error":
            print(f"Error: {result.get('message', 'Unknown error')}")
            return 1

        progress = result.get("progress", {})
        print(f"  Completed: {result.get('subtask_id', 'N/A')}")
        print(f"  Progress: {progress.get('percent_complete', 0)}%")

    # Save final plan state to unified format
    plan.save_to_unified(plan_path)

    print(f"\nExecution complete!")
    print(f"Final progress: {plan.get_progress()}")

    return 0


def cmd_review(args) -> int:
    """Review completed content."""
    project_dir = Path(args.project).resolve()
    spec_dir = get_spec_dir(project_dir, args.spec)

    # Load the plan from unified implementation_plan.json
    plan_path = spec_dir / "implementation_plan.json"
    if not plan_path.exists():
        print(f"Error: No implementation plan found at {plan_path}")
        return 1

    plan = ContentPlan.load_from_unified(plan_path)

    # Get deliverable paths
    content_paths = [d["path"] for d in plan.deliverables if "path" in d]

    if not content_paths:
        print("Warning: No deliverables found in plan, reviewing all content files")
        content_paths = [str(p) for p in project_dir.rglob("*.md") if not p.name.startswith("_")]

    print(f"\nReviewing {len(content_paths)} content files...")

    # Run the reviewer
    reviewer = ContentReviewerAgent(
        project_dir=str(project_dir),
        spec_dir=str(spec_dir),
    )

    result = reviewer.run(content_paths, plan=plan)

    print(f"\nReview complete!")
    print(f"  Status: {result['status']}")
    if result.get('verdict'):
        print(f"  Verdict: {result['verdict']}")
    if result.get('report_path'):
        print(f"  Report: {result['report_path']}")

    return 0


def cmd_consistency(args) -> int:
    """Run consistency checks."""
    project_dir = Path(args.project).resolve()
    spec_dir = get_spec_dir(project_dir, args.spec) if args.spec else None

    # Load plan if available from unified implementation_plan.json
    plan = None
    if spec_dir:
        plan_path = spec_dir / "implementation_plan.json"
        if plan_path.exists():
            plan = ContentPlan.load_from_unified(plan_path)

    print(f"\nRunning consistency checks...")

    # Run the consistency checker
    checker = ConsistencyCheckerAgent(
        project_dir=str(project_dir),
        spec_dir=str(spec_dir) if spec_dir else None,
    )

    result = checker.run(plan=plan)

    print(f"\nConsistency check complete!")
    print(f"  Status: {result['status']}")
    print(f"  Total Issues: {result.get('total_issues', 'N/A')}")
    if result.get('has_critical'):
        print(f"  WARNING: Critical issues found!")
    if result.get('report_path'):
        print(f"  Report: {result['report_path']}")

    return 0


def cmd_balance(args) -> int:
    """Run balance analysis (games only)."""
    project_dir = Path(args.project).resolve()
    spec_dir = get_spec_dir(project_dir, args.spec) if args.spec else None

    # Detect project type
    detector = ContentProjectDetector()
    project_type = detector.detect(str(project_dir))

    if project_type not in BalanceAnalystAgent.SUPPORTED_TYPES:
        print(f"Error: Balance analysis not supported for {project_type.value}")
        print(f"Supported types: {', '.join(t.value for t in BalanceAnalystAgent.SUPPORTED_TYPES)}")
        return 1

    # Load plan if available from unified implementation_plan.json
    plan = None
    if spec_dir:
        plan_path = spec_dir / "implementation_plan.json"
        if plan_path.exists():
            plan = ContentPlan.load_from_unified(plan_path)

    print(f"\nRunning balance analysis...")

    # Run the balance analyst
    analyst = BalanceAnalystAgent(
        project_dir=str(project_dir),
        spec_dir=str(spec_dir) if spec_dir else None,
    )

    result = analyst.run(plan=plan)

    print(f"\nBalance analysis complete!")
    print(f"  Status: {result['status']}")
    if result.get('issues'):
        print(f"  Overtuned: {result['issues'].get('overtuned', 0)}")
        print(f"  Undertuned: {result['issues'].get('undertuned', 0)}")
    if result.get('has_critical'):
        print(f"  WARNING: Critical balance issues found!")
    if result.get('report_path'):
        print(f"  Report: {result['report_path']}")

    return 0


def cmd_init(args) -> int:
    """Initialize a new content project from template."""
    project_dir = Path(args.project).resolve()
    project_type = ContentProjectType(args.init)

    print(f"\nInitializing {project_type.value} project at {project_dir}...")

    # Import scaffolder
    from content.scaffold import ContentProjectScaffolder

    scaffolder = ContentProjectScaffolder()
    scaffolder.scaffold(str(project_dir), project_type)

    print(f"\nProject initialized!")
    print(f"\nNext steps:")
    print(f"  1. Review the created structure")
    print(f"  2. Customize templates in _template.md files")
    print(f"  3. Add your style guide")
    print(f"  4. Start creating content with:")
    print(f"     python content_runner.py --project {args.project} --task 'Your task'")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Auto Claude Content Mode - Autonomous content creation workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--project", "-p",
        required=True,
        help="Path to the content project directory",
    )

    parser.add_argument(
        "--spec", "-s",
        help="Spec ID or directory for existing plans",
    )

    parser.add_argument(
        "--spec-dir",
        type=Path,
        help="Use existing spec directory (for frontend integration)",
    )

    # Commands
    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "--info",
        action="store_true",
        help="Show project information and detected type",
    )

    group.add_argument(
        "--task", "-t",
        help="Create a new content plan from task description",
    )

    group.add_argument(
        "--execute", "-x",
        action="store_true",
        help="Execute an existing content plan",
    )

    group.add_argument(
        "--review", "-r",
        action="store_true",
        help="Review completed content",
    )

    group.add_argument(
        "--consistency", "-c",
        action="store_true",
        help="Run consistency checks",
    )

    group.add_argument(
        "--balance", "-b",
        action="store_true",
        help="Run balance analysis (games only)",
    )

    group.add_argument(
        "--init",
        choices=[t.value for t in ContentProjectType if t != ContentProjectType.GENERAL],
        help="Initialize a new content project from template",
    )

    # Parse arguments
    args = parser.parse_args()

    # Route to appropriate command
    if args.info:
        return cmd_info(args)
    elif args.task:
        return cmd_plan(args)
    elif args.execute:
        if not args.spec:
            parser.error("--execute requires --spec")
        return cmd_execute(args)
    elif args.review:
        if not args.spec:
            parser.error("--review requires --spec")
        return cmd_review(args)
    elif args.consistency:
        return cmd_consistency(args)
    elif args.balance:
        return cmd_balance(args)
    elif args.init:
        return cmd_init(args)
    else:
        # Default: show info
        return cmd_info(args)


if __name__ == "__main__":
    sys.exit(main())
