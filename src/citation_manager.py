import logging
from config import CITATION_LIMIT

class CitationManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def generate_citations(self, persona_data, user_data):
        citations = []
        try:
            for item in user_data.get('posts', [])[:CITATION_LIMIT]:
                citations.append({
                    "type": "post",
                    "title": item.get("title", ""),
                    "url": item.get("permalink", "")
                })
            for item in user_data.get('comments', [])[:CITATION_LIMIT]:
                citations.append({
                    "type": "comment",
                    "text": item.get("text", "")[:100],
                    "url": item.get("permalink", "")
                })
        except Exception as e:
            self.logger.warning(f"Error generating citations: {str(e)}")
        return citations
