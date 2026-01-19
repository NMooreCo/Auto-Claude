"""Code Analyzer Agent - generates and verifies documentation from code."""

from pathlib import Path
from typing import Optional, List
import logging

from .base import ContentAgent
from ..models import ContentPlan
from ..enums import ContentProjectType

logger = logging.getLogger(__name__)


class CodeAnalyzerAgent(ContentAgent):
    """
    Analyzes source code to generate and verify documentation.

    The Code Analyzer reads code to extract documentation, verify
    existing docs match code reality, and track documentation freshness.
    """

    PROMPT_FILE = "doc_code_analyzer.md"
    AGENT_TYPE = "code_analyzer"

    # Project types that support code analysis
    SUPPORTED_TYPES = [
        ContentProjectType.CODEBASE_DOCS,
        ContentProjectType.API_DOCS,
        ContentProjectType.ARCHITECTURE,
        ContentProjectType.KNOWLEDGE_BASE,
    ]

    def run(
        self,
        source_dirs: Optional[List[str]] = None,
        doc_dirs: Optional[List[str]] = None,
        plan: Optional[ContentPlan] = None,
        mode: str = "analyze",
    ) -> dict:
        """
        Run code analysis for documentation.

        Args:
            source_dirs: Source code directories to analyze
            doc_dirs: Documentation directories to verify
            plan: Content plan for context
            mode: Analysis mode ('analyze', 'generate', 'verify', 'freshness')

        Returns:
            Dictionary with analysis results
        """
        # Load the prompt
        prompt = self._load_prompt()

        # Build context
        context = self._build_analysis_context(source_dirs, doc_dirs, plan, mode)

        starting_message = f"""{prompt}

## ANALYSIS CONTEXT

{context}

## INSTRUCTIONS

Run code analysis in '{mode}' mode.

Mode descriptions:
- analyze: Map code structure and identify documentable elements
- generate: Generate missing documentation from code
- verify: Verify existing docs match code reality
- freshness: Check if docs are up-to-date with code changes

Generate a report saved as `code_analysis_report.md`.
"""

        logger.info(f"Running code analysis in {mode} mode...")

        # Run the agent session
        response = self._create_session(
            starting_message=starting_message,
            session_name="code-analyzer-session",
        )

        return self._parse_analysis_results(response, mode)

    def _build_analysis_context(
        self,
        source_dirs: Optional[List[str]],
        doc_dirs: Optional[List[str]],
        plan: Optional[ContentPlan],
        mode: str,
    ) -> str:
        """Build context for code analysis."""
        context_parts = [
            f"Analysis Mode: {mode}",
        ]

        if source_dirs:
            context_parts.append(f"Source Directories: {', '.join(source_dirs)}")
        else:
            context_parts.append("Source Directories: auto-detect (src/, lib/, app/)")

        if doc_dirs:
            context_parts.append(f"Documentation Directories: {', '.join(doc_dirs)}")
        else:
            context_parts.append("Documentation Directories: auto-detect (docs/)")

        if plan:
            context_parts.extend([
                "",
                f"Project: {plan.project_name}",
                f"Project Type: {plan.project_type.value}",
            ])

            # Add doc-specific context
            if plan.doc_specific:
                context_parts.append("")
                context_parts.append("Documentation Configuration:")

                if "source_directories" in plan.doc_specific:
                    context_parts.append(
                        f"  Configured Sources: {', '.join(plan.doc_specific['source_directories'])}"
                    )

                if "component_mapping" in plan.doc_specific:
                    context_parts.append("  Component Mapping: defined")

                if plan.doc_specific.get("track_freshness"):
                    context_parts.append("  Freshness Tracking: enabled")

        return "\n".join(context_parts)

    def _parse_analysis_results(self, response, mode: str) -> dict:
        """Parse code analysis results."""
        report_path = (
            self.spec_dir / "code_analysis_report.md" if self.spec_dir else None
        )

        results = {
            "status": "completed",
            "mode": mode,
        }

        if report_path and report_path.exists():
            content = report_path.read_text()
            content_lower = content.lower()

            results["report_path"] = str(report_path)

            # Extract metrics based on mode
            if mode == "analyze":
                results["metrics"] = {
                    "endpoints_found": content_lower.count("endpoint"),
                    "components_found": content_lower.count("component"),
                    "classes_found": content_lower.count("class"),
                }
            elif mode == "verify":
                results["metrics"] = {
                    "docs_verified": content_lower.count("verified") + content_lower.count("✓"),
                    "discrepancies": content_lower.count("discrepancy") + content_lower.count("mismatch"),
                    "missing_docs": content_lower.count("missing"),
                }
            elif mode == "freshness":
                results["metrics"] = {
                    "stale_docs": content_lower.count("stale") + content_lower.count("outdated"),
                    "fresh_docs": content_lower.count("fresh") + content_lower.count("up-to-date"),
                }

            results["has_issues"] = (
                "issue" in content_lower
                or "discrepancy" in content_lower
                or "missing" in content_lower
                or "stale" in content_lower
            )

        return results

    def generate_api_docs(
        self,
        source_dir: str,
        output_dir: str,
        plan: Optional[ContentPlan] = None,
    ) -> dict:
        """
        Generate API documentation from source code.

        Args:
            source_dir: Directory containing API route definitions
            output_dir: Directory to output documentation
            plan: Optional content plan

        Returns:
            Dictionary with generation results
        """
        return self.run(
            source_dirs=[source_dir],
            doc_dirs=[output_dir],
            plan=plan,
            mode="generate",
        )

    def verify_docs(
        self,
        source_dirs: List[str],
        doc_dirs: List[str],
        plan: Optional[ContentPlan] = None,
    ) -> dict:
        """
        Verify documentation matches code.

        Args:
            source_dirs: Source code directories
            doc_dirs: Documentation directories
            plan: Optional content plan

        Returns:
            Dictionary with verification results
        """
        return self.run(
            source_dirs=source_dirs,
            doc_dirs=doc_dirs,
            plan=plan,
            mode="verify",
        )

    def check_freshness(
        self,
        source_dirs: Optional[List[str]] = None,
        doc_dirs: Optional[List[str]] = None,
        plan: Optional[ContentPlan] = None,
    ) -> dict:
        """
        Check documentation freshness relative to code changes.

        Args:
            source_dirs: Source code directories
            doc_dirs: Documentation directories
            plan: Optional content plan

        Returns:
            Dictionary with freshness check results
        """
        return self.run(
            source_dirs=source_dirs,
            doc_dirs=doc_dirs,
            plan=plan,
            mode="freshness",
        )

    def document_component(
        self,
        component_path: str,
        output_path: str,
        plan: Optional[ContentPlan] = None,
    ) -> dict:
        """
        Generate documentation for a specific component.

        Args:
            component_path: Path to the component source
            output_path: Path for the output documentation
            plan: Optional content plan

        Returns:
            Dictionary with generation results
        """
        return self.run(
            source_dirs=[component_path],
            doc_dirs=[str(Path(output_path).parent)],
            plan=plan,
            mode="generate",
        )
