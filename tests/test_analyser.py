import unittest
from persona_analyzer import PersonaAnalyzer

class TestPersonaAnalyzer(unittest.TestCase):
    def test_initialization(self):
        analyzer = PersonaAnalyzer()
        self.assertIsNotNone(analyzer.model)

if __name__ == "__main__":
    unittest.main()
