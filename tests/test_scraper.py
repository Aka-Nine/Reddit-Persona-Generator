import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.reddit_scraper import RedditScraper

class TestRedditScraper(unittest.TestCase):
    def test_initialization(self):
        scraper = RedditScraper()
        self.assertIsNotNone(scraper.reddit)

if __name__ == "__main__":
    unittest.main()
