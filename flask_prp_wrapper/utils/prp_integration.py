"""Integration utilities for existing PRPs-agentic-eng system."""

import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class PRPExecutionResult:
    """Result of PRP execution."""

    success: bool
    output: str
    error_output: str
    exit_code: int
    execution_time_seconds: float
    validation_results: List[Dict[str, Any]]
    generated_files: List[str]


@dataclass
class ValidationResult:
    """Result of individual validation step."""

    step_name: str
    command: str
    success: bool
    output: str
    error_output: str
    execution_time: float


class PRPIntegrationService:
    """Service for integrating with existing PRP system."""

    def __init__(
        self,
        prps_root_path: str = ".",
        prp_runner_script: str = "PRPs/scripts/prp_runner.py",
    ):
        """Initialize PRP integration service.

        Args:
            prps_root_path: Path to PRPs project root
            prp_runner_script: Path to PRP runner script
        """
        self.prps_root = Path(prps_root_path).resolve()
        self.prp_runner = Path(prp_runner_script)

        if not self.prp_runner.exists():
            logger.warning(f"PRP runner script not found at {self.prp_runner}")

        # Validate environment
        self._validate_environment()

    def _validate_environment(self):
        """Validate that the PRP execution environment is available."""
        try:
            # Check if uv is available
            result = subprocess.run(
                ["uv", "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                logger.warning(
                    "UV package manager not available - PRP execution may fail"
                )

            # Check if Claude Code CLI is available
            result = subprocess.run(
                ["claude", "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                logger.warning("Claude CLI not available - PRP execution will fail")

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.warning(f"Environment validation failed: {e}")

    async def save_prp_to_file(self, prp_content: str, prp_id: str) -> Path:
        """Save generated PRP content to a file.

        Args:
            prp_content: The PRP markdown content
            prp_id: Unique identifier for the PRP

        Returns:
            Path to the saved PRP file
        """
        try:
            # Create filename
            filename = f"{prp_id}.md"
            prp_file_path = self.prps_root / "PRPs" / filename

            # Ensure PRPs directory exists
            prp_file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write PRP content
            prp_file_path.write_text(prp_content, encoding="utf-8")

            logger.info(f"Saved PRP to {prp_file_path}")
            return prp_file_path

        except Exception as e:
            logger.error(f"Error saving PRP to file: {e}")
            raise

    async def execute_prp(
        self,
        prp_file_path: Path,
        interactive: bool = False,
        timeout_seconds: int = 1800,  # 30 minutes
    ) -> PRPExecutionResult:
        """Execute a PRP using the existing PRP runner.

        Args:
            prp_file_path: Path to the PRP file
            interactive: Whether to run in interactive mode
            timeout_seconds: Maximum execution time

        Returns:
            PRPExecutionResult with execution details
        """
        start_time = datetime.utcnow()

        try:
            if not prp_file_path.exists():
                raise FileNotFoundError(f"PRP file not found: {prp_file_path}")

            # Build command
            cmd = ["uv", "run", str(self.prp_runner), "--prp-path", str(prp_file_path)]

            if interactive:
                cmd.append("--interactive")
            else:
                cmd.extend(["--output-format", "json"])

            logger.info(f"Executing PRP: {' '.join(cmd)}")

            # Change to project root directory
            original_cwd = Path.cwd()
            try:
                # Execute command
                result = subprocess.run(
                    cmd,
                    cwd=self.prps_root,
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds,
                )

                execution_time = (datetime.utcnow() - start_time).total_seconds()

                # Parse output for file generation info
                generated_files = self._extract_generated_files(
                    result.stdout, result.stderr
                )

                return PRPExecutionResult(
                    success=result.returncode == 0,
                    output=result.stdout,
                    error_output=result.stderr,
                    exit_code=result.returncode,
                    execution_time_seconds=execution_time,
                    validation_results=[],  # Would be populated from detailed output parsing
                    generated_files=generated_files,
                )

            finally:
                # Restore original working directory
                if original_cwd != Path.cwd():
                    import os

                    os.chdir(original_cwd)

        except subprocess.TimeoutExpired:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"PRP execution timed out after {execution_time} seconds")

            return PRPExecutionResult(
                success=False,
                output="",
                error_output=f"Execution timed out after {timeout_seconds} seconds",
                exit_code=-1,
                execution_time_seconds=execution_time,
                validation_results=[],
                generated_files=[],
            )

        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Error executing PRP: {e}")

            return PRPExecutionResult(
                success=False,
                output="",
                error_output=str(e),
                exit_code=-1,
                execution_time_seconds=execution_time,
                validation_results=[],
                generated_files=[],
            )

    async def validate_prp_commands(
        self, validation_commands: List[str], working_directory: Optional[Path] = None
    ) -> List[ValidationResult]:
        """Execute validation commands and return results.

        Args:
            validation_commands: List of validation commands to execute
            working_directory: Directory to execute commands in

        Returns:
            List of ValidationResult objects
        """
        if working_directory is None:
            working_directory = self.prps_root

        results = []

        for i, command in enumerate(validation_commands):
            step_name = f"Validation Step {i + 1}"
            start_time = datetime.utcnow()

            try:
                logger.info(f"Executing validation command: {command}")

                # Split command for subprocess
                cmd_parts = command.split()

                result = subprocess.run(
                    cmd_parts,
                    cwd=working_directory,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minute timeout per command
                )

                execution_time = (datetime.utcnow() - start_time).total_seconds()

                validation_result = ValidationResult(
                    step_name=step_name,
                    command=command,
                    success=result.returncode == 0,
                    output=result.stdout,
                    error_output=result.stderr,
                    execution_time=execution_time,
                )

                results.append(validation_result)

                logger.info(
                    f"Validation command completed: {command} (success: {validation_result.success})"
                )

            except subprocess.TimeoutExpired:
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                logger.warning(f"Validation command timed out: {command}")

                results.append(
                    ValidationResult(
                        step_name=step_name,
                        command=command,
                        success=False,
                        output="",
                        error_output="Command timed out after 5 minutes",
                        execution_time=execution_time,
                    )
                )

            except Exception as e:
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                logger.error(f"Error executing validation command '{command}': {e}")

                results.append(
                    ValidationResult(
                        step_name=step_name,
                        command=command,
                        success=False,
                        output="",
                        error_output=str(e),
                        execution_time=execution_time,
                    )
                )

        return results

    def _extract_generated_files(self, stdout: str, stderr: str) -> List[str]:
        """Extract list of generated files from command output.

        Args:
            stdout: Standard output from command
            stderr: Standard error from command

        Returns:
            List of file paths that were generated
        """
        generated_files = []

        # Look for common patterns indicating file creation
        file_patterns = [
            r"Created file: (.+)",
            r"Generated (.+\.py)",
            r"Writing to (.+)",
            r"Saved (.+\.md)",
            r"File created: (.+)",
        ]

        import re

        combined_output = stdout + "\n" + stderr

        for pattern in file_patterns:
            matches = re.findall(pattern, combined_output, re.IGNORECASE)
            generated_files.extend(matches)

        # Remove duplicates and clean paths
        unique_files = []
        for file_path in generated_files:
            cleaned_path = file_path.strip().strip("\"'")
            if cleaned_path not in unique_files:
                unique_files.append(cleaned_path)

        return unique_files

    async def create_prp_summary(
        self,
        prp_execution_result: PRPExecutionResult,
        validation_results: List[ValidationResult],
    ) -> Dict[str, Any]:
        """Create summary of PRP execution and validation.

        Args:
            prp_execution_result: Result of PRP execution
            validation_results: Results of validation commands

        Returns:
            Summary dictionary with execution details
        """
        successful_validations = [r for r in validation_results if r.success]
        failed_validations = [r for r in validation_results if not r.success]

        return {
            "execution_summary": {
                "success": prp_execution_result.success,
                "execution_time": prp_execution_result.execution_time_seconds,
                "exit_code": prp_execution_result.exit_code,
                "generated_files_count": len(prp_execution_result.generated_files),
            },
            "validation_summary": {
                "total_validations": len(validation_results),
                "successful_validations": len(successful_validations),
                "failed_validations": len(failed_validations),
                "success_rate": len(successful_validations) / len(validation_results)
                if validation_results
                else 0,
            },
            "generated_files": prp_execution_result.generated_files,
            "validation_details": [
                {
                    "step": result.step_name,
                    "command": result.command,
                    "success": result.success,
                    "execution_time": result.execution_time,
                    "error": result.error_output if not result.success else None,
                }
                for result in validation_results
            ],
            "recommendations": self._generate_recommendations(
                prp_execution_result, validation_results
            ),
        }

    def _generate_recommendations(
        self,
        execution_result: PRPExecutionResult,
        validation_results: List[ValidationResult],
    ) -> List[str]:
        """Generate recommendations based on execution and validation results.

        Args:
            execution_result: PRP execution result
            validation_results: Validation results

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Execution-based recommendations
        if not execution_result.success:
            if "timeout" in execution_result.error_output.lower():
                recommendations.append(
                    "Consider breaking down complex PRPs into smaller, more focused tasks"
                )
            elif "permission" in execution_result.error_output.lower():
                recommendations.append(
                    "Check file permissions and ensure proper access to project directories"
                )
            elif "command not found" in execution_result.error_output.lower():
                recommendations.append(
                    "Verify that all required tools (uv, claude) are installed and accessible"
                )

        # Validation-based recommendations
        failed_validations = [r for r in validation_results if not r.success]

        if failed_validations:
            syntax_failures = [
                r
                for r in failed_validations
                if "ruff" in r.command or "mypy" in r.command
            ]
            if syntax_failures:
                recommendations.append(
                    "Address syntax and type checking issues before proceeding"
                )

            test_failures = [
                r
                for r in failed_validations
                if "pytest" in r.command or "test" in r.command
            ]
            if test_failures:
                recommendations.append(
                    "Review and fix failing tests - they indicate implementation issues"
                )

            if len(failed_validations) > len(validation_results) / 2:
                recommendations.append(
                    "Consider revising the PRP with more detailed implementation guidance"
                )

        # Performance recommendations
        if execution_result.execution_time_seconds > 600:  # 10 minutes
            recommendations.append(
                "Long execution time - consider optimizing the implementation approach"
            )

        # Success recommendations
        if execution_result.success and len(failed_validations) == 0:
            recommendations.append(
                "Excellent! All validations passed - ready for production deployment"
            )
        elif execution_result.success and len(failed_validations) < 3:
            recommendations.append(
                "Good progress - address remaining validation issues for production readiness"
            )

        return recommendations

    async def cleanup_generated_prp_file(self, prp_file_path: Path) -> bool:
        """Clean up generated PRP file.

        Args:
            prp_file_path: Path to PRP file to clean up

        Returns:
            True if cleanup successful, False otherwise
        """
        try:
            if prp_file_path.exists():
                prp_file_path.unlink()
                logger.info(f"Cleaned up PRP file: {prp_file_path}")
                return True
            return True  # File doesn't exist, consider it cleaned up

        except Exception as e:
            logger.error(f"Error cleaning up PRP file {prp_file_path}: {e}")
            return False

    def get_prp_templates(self) -> List[Dict[str, str]]:
        """Get available PRP templates.

        Returns:
            List of template information dictionaries
        """
        templates = []
        templates_path = self.prps_root / "PRPs" / "templates"

        if templates_path.exists():
            for template_file in templates_path.glob("*.md"):
                try:
                    content = template_file.read_text(encoding="utf-8")
                    # Extract name and description from template
                    name_match = (
                        content.split("\n")[0] if content else template_file.stem
                    )
                    if name_match.startswith("name:"):
                        name = name_match.replace("name:", "").strip().strip("\"'")
                    else:
                        name = template_file.stem

                    # Extract description
                    description = "PRP template"
                    if "description:" in content:
                        desc_lines = []
                        in_description = False
                        for line in content.split("\n"):
                            if line.strip().startswith("description:"):
                                in_description = True
                                desc_part = line.replace("description:", "").strip()
                                if desc_part:
                                    desc_lines.append(desc_part)
                            elif in_description:
                                if line.strip() and not line.startswith("---"):
                                    desc_lines.append(line.strip())
                                elif line.startswith("---"):
                                    break

                        if desc_lines:
                            description = " ".join(desc_lines).strip()

                    templates.append(
                        {
                            "name": name,
                            "filename": template_file.name,
                            "description": description,
                            "path": str(template_file),
                        }
                    )

                except Exception as e:
                    logger.warning(f"Error reading template {template_file}: {e}")

        return templates

    async def validate_prp_content(self, prp_content: str) -> Dict[str, Any]:
        """Validate PRP content structure and completeness.

        Args:
            prp_content: PRP markdown content to validate

        Returns:
            Validation result dictionary
        """
        validation_result = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "completeness_score": 0.0,
            "sections_found": [],
            "missing_sections": [],
        }

        # Required sections for a complete PRP
        required_sections = [
            "goal",
            "why",
            "what",
            "context",
            "implementation",
            "validation",
        ]

        sections_found = []
        content_lower = prp_content.lower()

        # Check for required sections
        for section in required_sections:
            if f"## {section}" in content_lower or f"# {section}" in content_lower:
                sections_found.append(section)

        validation_result["sections_found"] = sections_found
        validation_result["missing_sections"] = [
            s for s in required_sections if s not in sections_found
        ]

        # Calculate completeness score
        validation_result["completeness_score"] = len(sections_found) / len(
            required_sections
        )

        # Check for critical content
        if len(prp_content) < 1000:
            validation_result["warnings"].append(
                "PRP content seems quite short - consider adding more detail"
            )

        if "validation loop" not in content_lower:
            validation_result["warnings"].append(
                "No validation loop section found - validation commands may be missing"
            )

        if len(validation_result["missing_sections"]) > 2:
            validation_result["errors"].append(
                f"Missing critical sections: {', '.join(validation_result['missing_sections'])}"
            )
            validation_result["is_valid"] = False

        # Check for validation commands
        import re

        bash_blocks = re.findall(r"```bash\n(.*?)\n```", prp_content, re.DOTALL)
        if not bash_blocks:
            validation_result["warnings"].append(
                "No bash code blocks found - validation commands may be missing"
            )

        return validation_result
