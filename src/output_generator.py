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

    def generate_persona_file(self, persona, citations, output_path, username):
        try:
            # Try to load template file, fall back to default
            template_content = self.default_template
            template_path = "templates/persona_template.txt"
            
            if os.path.exists(template_path):
                try:
                    with open(template_path, "r", encoding="utf-8") as f:
                        template_content = f.read()
                except Exception as e:
                    self.logger.warning(f"Could not read template file: {e}, using default")
            
            template = Template(template_content)
            
            # Format citations
            citations_text = "\n".join([
                f"{c.get('type', 'unknown').capitalize()}: {c.get('url', 'No URL available')}"
                for c in citations
            ]) if citations else "No citations available"
            
            # Generate content
            content = template.safe_substitute(
                username=username,
                generated_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                summary=persona.get('analysis_summary', 'No summary available'),
                demographics=self._format_dict(persona.get('demographics', {})),
                personality=self._format_dict(persona.get('personality', {})),
                motivations=self._format_dict(persona.get('motivations', {})),
                behaviors_habits=self._format_dict(persona.get('behaviors_habits', {})),
                frustrations=self._format_dict(persona.get('frustrations', {})),
                goals_needs=self._format_dict(persona.get('goals_needs', {})),
                citations=citations_text,
                confidence_score=persona.get('confidence_score', 0.0)
            )
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write output file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
                
            self.logger.info(f"Persona file generated: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate output file: {str(e)}")
            raise
    
    def _format_dict(self, data):
        """Format dictionary data for display"""
        if not data:
            return "No data available"
        
        if isinstance(data, dict):
            lines = []
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    lines.append(f"{key}: {str(value)}")
                else:
                    lines.append(f"{key}: {value}")
            return "\n".join(lines)
        else:
            return str(data)