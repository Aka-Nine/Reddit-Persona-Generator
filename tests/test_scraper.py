import unittest
from reddit_scraper import RedditScraper

class TestRedditScraper(unittest.TestCase):
    def test_initialization(self):
        scraper = RedditScraper()
        self.assertIsNotNone(scraper.reddit)

if __name__ == "__main__":
    unittest.main()
