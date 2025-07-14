
import praw
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional

class RedditScraper:
    """Handles Reddit data scraping using PRAW"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.reddit = self._initialize_reddit()
    
    def _initialize_reddit(self) -> praw.Reddit:
        """Initialize Reddit API client"""
        try:
            from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
            
            reddit = praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                user_agent=REDDIT_USER_AGENT,
                read_only=True
            )
            
            # Test the connection with a simple request
            try:
                list(reddit.subreddit('test').hot(limit=1))
                self.logger.info("Reddit API initialized successfully")
            except Exception as e:
                self.logger.warning(f"Reddit API test failed: {e}")
            
            return reddit
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Reddit API: {str(e)}")
            raise
    
    def scrape_user_data(self, username: str) -> Dict:
        """
        Scrape posts and comments from a Reddit user
        
        Args:
            username: Reddit username (without u/ prefix)
            
        Returns:
            Dictionary containing user data
        """
        try:
            user = self.reddit.redditor(username)
            
            # Check if user exists by trying to access name
            try:
                _ = user.name
                if user.name != username:
                    raise ValueError(f"User {username} not found")
            except Exception:
                raise ValueError(f"User {username} not found or suspended")
            
            self.logger.info(f"Scraping data for user: {username}")
            
            # Get user info first
            user_info = self._get_user_info(user)
            
            # Scrape posts
            posts = self._scrape_posts(user)
            self.logger.info(f"Scraped {len(posts)} posts")
            
            # Scrape comments
            comments = self._scrape_comments(user)
            self.logger.info(f"Scraped {len(comments)} comments")
            
            if not posts and not comments:
                raise ValueError(f"No posts or comments found for user {username}")
            
            return {
                'username': username,
                'user_info': user_info,
                'posts': posts,
                'comments': comments,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error scraping user data: {str(e)}")
            raise
    
    def _scrape_posts(self, user) -> List[Dict]:
        """Scrape user posts"""
        posts = []
        
        try:
            from config import MAX_POSTS, SCRAPING_DELAY
            
            for i, post in enumerate(user.submissions.new(limit=MAX_POSTS)):
                if i >= MAX_POSTS:
                    break
                    
                try:
                    post_data = {
                        'id': post.id,
                        'title': post.title or '',
                        'text': post.selftext or '',
                        'score': getattr(post, 'score', 0),
                        'upvote_ratio': getattr(post, 'upvote_ratio', 0.5),
                        'subreddit': str(post.subreddit),
                        'created_utc': post.created_utc,
                        'num_comments': getattr(post, 'num_comments', 0),
                        'url': getattr(post, 'url', ''),
                        'permalink': f"https://reddit.com{post.permalink}",
                        'type': 'post'
                    }
                    posts.append(post_data)
                    
                    # Add delay to respect rate limits
                    time.sleep(SCRAPING_DELAY)
                    
                except Exception as e:
                    self.logger.warning(f"Error processing post {post.id}: {e}")
                    continue
                    
        except Exception as e:
            self.logger.warning(f"Error scraping posts: {str(e)}")
        
        return posts
    
    def _scrape_comments(self, user) -> List[Dict]:
        """Scrape user comments"""
        comments = []
        
        try:
            from config import MAX_COMMENTS, SCRAPING_DELAY
            
            for i, comment in enumerate(user.comments.new(limit=MAX_COMMENTS)):
                if i >= MAX_COMMENTS:
                    break
                    
                try:
                    comment_data = {
                        'id': comment.id,
                        'text': comment.body or '',
                        'score': getattr(comment, 'score', 0),
                        'subreddit': str(comment.subreddit),
                        'created_utc': comment.created_utc,
                        'permalink': f"https://reddit.com{comment.permalink}",
                        'parent_id': getattr(comment, 'parent_id', ''),
                        'type': 'comment'
                    }
                    comments.append(comment_data)
                    
                    # Add delay to respect rate limits
                    time.sleep(SCRAPING_DELAY)
                    
                except Exception as e:
                    self.logger.warning(f"Error processing comment {comment.id}: {e}")
                    continue
                    
        except Exception as e:
            self.logger.warning(f"Error scraping comments: {str(e)}")
        
        return comments
    
    def _get_user_info(self, user) -> Dict:
        """Get basic user information"""
        try:
            return {
                'name': user.name,
                'created_utc': getattr(user, 'created_utc', 0),
                'comment_karma': getattr(user, 'comment_karma', 0),
                'link_karma': getattr(user, 'link_karma', 0),
                'is_gold': getattr(user, 'is_gold', False),
                'is_mod': getattr(user, 'is_mod', False),
                'has_verified_email': getattr(user, 'has_verified_email', False),
                'account_age_days': (datetime.now().timestamp() - getattr(user, 'created_utc', 0)) / 86400
            }
        except Exception as e:
            self.logger.warning(f"Error getting user info: {str(e)}")
            return {'name': user.name}
