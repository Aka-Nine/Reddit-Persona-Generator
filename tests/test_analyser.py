import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.persona_analyzer import PersonaAnalyzer

class TestPersonaAnalyzer(unittest.TestCase):
    def test_initialization(self):
        analyzer = PersonaAnalyzer()
        self.assertIsNotNone(analyzer.model)

if __name__ == "__main__":
    unittest.main()
