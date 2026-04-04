import logging
import os
from string import Template
from datetime import datetime

class OutputGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Default template if file doesn't exist
        self.default_template = """
USER PERSONA ANALYSIS
=====================

Username: $username
Generated: $generated_time

ANALYSIS SUMMARY
================
$summary

DEMOGRAPHICS
============
$demographics

PERSONALITY TRAITS
==================
$personality

MOTIVATIONS
===========
$motivations

BEHAVIORS & HABITS
==================
$behaviors_habits

FRUSTRATIONS
============
$frustrations

GOALS & NEEDS
=============
$goals_needs

CITATIONS
=========
$citations

Confidence Score: $confidence_score

Note: This analysis is based on publicly available Reddit activity.
"""

    def _load_template_content(self) -> str:
        template_content = self.default_template
        template_path = "templates/persona_template.txt"
        if os.path.exists(template_path):
            try:
                with open(template_path, "r", encoding="utf-8") as f:
                    template_content = f.read()
            except Exception as e:
                self.logger.warning("Could not read template file: %s, using default", e)
        return template_content

    def render_persona_text(self, persona, citations, username) -> str:
        """Build the full persona .txt string in memory (no disk I/O)."""
        template_content = self._load_template_content()
        template = Template(template_content)

        citations_text = "\n".join([
            f"{c.get('type', 'unknown').capitalize()}: {c.get('url', 'No URL available')}"
            for c in citations
        ]) if citations else "No citations available"

        return template.safe_substitute(
            username=username,
            generated_time=datetime.now().strftime("%B %d, %Y · %H:%M"),
            summary=persona.get("analysis_summary", "No summary available"),
            demographics=self._format_dict(persona.get("demographics", {})),
            personality=self._format_dict(persona.get("personality", {})),
            motivations=self._format_dict(persona.get("motivations", {})),
            behaviors_habits=self._format_dict(persona.get("behaviors_habits", {})),
            frustrations=self._format_dict(persona.get("frustrations", {})),
            goals_needs=self._format_dict(persona.get("goals_needs", {})),
            citations=citations_text,
            confidence_score=persona.get("confidence_score", 0.0),
        )

    def generate_persona_file(self, persona, citations, output_path, username):
        """Write persona report to disk (CLI / optional server persistence)."""
        try:
            content = self.render_persona_text(persona, citations, username)
            out_dir = os.path.dirname(output_path)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            self.logger.info("Persona file generated: %s", output_path)
        except Exception as e:
            self.logger.error("Failed to generate output file: %s", e)
            raise

    def _format_dict(self, data):
        """Format nested dict/list persona fields as readable text (not one-line Python repr)."""
        if not data:
            return "No data available"
        if not isinstance(data, dict):
            return str(data)
        lines = []
        for key, value in data.items():
            lines.append(self._format_field(str(key), value, 0))
        return "\n".join(lines)

    def _format_field(self, key: str, value, depth: int) -> str:
        pad = "  " * depth
        max_depth = 8
        if depth > max_depth:
            return f"{pad}{key}: {value!s}"

        if isinstance(value, dict):
            inner = "\n".join(
                self._format_field(str(k), v, depth + 1) for k, v in value.items()
            )
            return f"{pad}{key}:\n{inner}"

        if isinstance(value, list):
            if not value:
                return f"{pad}{key}: (none)"
            rows = []
            for item in value:
                if isinstance(item, dict):
                    inner = "\n".join(
                        self._format_field(str(k), v, depth + 2)
                        for k, v in item.items()
                    )
                    rows.append(f"{pad}  •\n{inner}")
                elif isinstance(item, list):
                    flat = ", ".join(str(x) for x in item)
                    rows.append(f"{pad}  • {flat}")
                else:
                    rows.append(f"{pad}  • {item}")
            return f"{pad}{key}:\n" + "\n".join(rows)

        return f"{pad}{key}: {value}"
