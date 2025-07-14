"""
Data Processing Module
Handles data cleaning, preprocessing, and feature extraction
"""

import re
import logging
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from config import MIN_TEXT_LENGTH, MAX_TEXT_LENGTH
from utils.text_utils import clean_text, extract_keywords, calculate_readability

class DataProcessor:
    """Handles data cleaning and preprocessing"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        
    def process_user_data(self, user_data: Dict) -> Dict:
        """
        Process raw user data into structured format
        
        Args:
            user_data: Raw data from Reddit scraper
            
        Returns:
            Processed user data
        """
        try:
            # Clean and filter posts
            processed_posts = self._process_posts(user_data.get('posts', []))
            
            # Clean and filter comments
            processed_comments = self._process_comments(user_data.get('comments', []))
            
            # Combine all text for analysis
            combined_text = self._combine_text(processed_posts, processed_comments)
            
            # Extract features
            features = self._extract_features(combined_text, processed_posts, processed_comments)
            
            # Analyze sentiment patterns
            sentiment_patterns = self._analyze_sentiment_patterns(processed_posts, processed_comments)
            
            # Extract topics and interests
            topics = self._extract_topics(combined_text)
            
            # Calculate activity patterns
            activity_patterns = self._analyze_activity_patterns(processed_posts, processed_comments)
            
            return {
                'username': user_data.get('username'),
                'user_info': user_data.get('user_info', {}),
                'posts': processed_posts,
                'comments': processed_comments,
                'combined_text': combined_text,
                'features': features,
                'sentiment_patterns': sentiment_patterns,
                'topics': topics,
                'activity_patterns': activity_patterns,
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing user data: {str(e)}")
            raise
    
    def _process_posts(self, posts: List[Dict]) -> List[Dict]:
        """Process and clean posts"""
        processed_posts = []
        
        for post in posts:
            # Clean title and text
            clean_title = clean_text(post.get('title', ''))
            clean_text_content = clean_text(post.get('text', ''))
            
            # Skip if too short or too long
            total_text = f"{clean_title} {clean_text_content}"
            if len(total_text) < MIN_TEXT_LENGTH or len(total_text) > MAX_TEXT_LENGTH:
                continue
            
            # Calculate sentiment
            sentiment = self._calculate_sentiment(total_text)
            
            # Extract keywords
            keywords = extract_keywords(total_text)
            
            processed_post = {
                **post,
                'clean_title': clean_title,
                'clean_text': clean_text_content,
                'total_text': total_text,
                'text_length': len(total_text),
                'sentiment': sentiment,
                'keywords': keywords,
                'readability': calculate_readability(total_text),
                'timestamp': datetime.fromtimestamp(post.get('created_utc', 0))
            }
            
            processed_posts.append(processed_post)
        
        return processed_posts
    
    def _process_comments(self, comments: List[Dict]) -> List[Dict]:
        """Process and clean comments"""
        processed_comments = []
        
        for comment in comments:
            # Clean text
            clean_text_content = clean_text(comment.get('text', ''))
            
            # Skip if too short or too long
            if len(clean_text_content) < MIN_TEXT_LENGTH or len(clean_text_content) > MAX_TEXT_LENGTH:
                continue
            
            # Calculate sentiment
            sentiment = self._calculate_sentiment(clean_text_content)
            
            # Extract keywords
            keywords = extract_keywords(clean_text_content)
            
            processed_comment = {
                **comment,
                'clean_text': clean_text_content,
                'text_length': len(clean_text_content),
                'sentiment': sentiment,
                'keywords': keywords,
                'readability': calculate_readability(clean_text_content),
                'timestamp': datetime.fromtimestamp(comment.get('created_utc', 0))
            }
            
            processed_comments.append(processed_comment)
        
        return processed_comments
    
    def _combine_text(self, posts: List[Dict], comments: List[Dict]) -> str:
        """Combine all text content"""
        all_text = []
        
        for post in posts:
            all_text.append(post.get('total_text', ''))
        
        for comment in comments:
            all_text.append(comment.get('clean_text', ''))
        
        return '\n\n'.join(all_text)
    
    def _calculate_sentiment(self, text: str) -> Dict:
        """Calculate sentiment using VADER"""
        scores = self.sentiment_analyzer.polarity_scores(text)
        
        # Also use TextBlob for additional analysis
        blob = TextBlob(text)
        
        return {
            'vader_compound': scores['compound'],
            'vader_positive': scores['pos'],
            'vader_negative': scores['neg'],
            'vader_neutral': scores['neu'],
            'textblob_polarity': blob.sentiment.polarity,
            'textblob_subjectivity': blob.sentiment.subjectivity
        }
    
    def _extract_features(self, text: str, posts: List[Dict], comments: List[Dict]) -> Dict:
        """Extract various features from the text"""
        
        # Text statistics
        word_count = len(text.split())
        char_count = len(text)
        sentence_count = len(re.findall(r'[.!?]+', text))
        
        # Linguistic features
        question_count = text.count('?')
        exclamation_count = text.count('!')
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        
        # Behavioral features
        avg_post_length = sum(p.get('text_length', 0) for p in posts) / len(posts) if posts else 0
        avg_comment_length = sum(c.get('text_length', 0) for c in comments) / len(comments) if comments else 0
        
        # Engagement features
        avg_post_score = sum(p.get('score', 0) for p in posts) / len(posts) if posts else 0
        avg_comment_score = sum(c.get('score', 0) for c in comments) / len(comments) if comments else 0
        
        return {
            'word_count': word_count,
            'char_count': char_count,
            'sentence_count': sentence_count,
            'question_ratio': question_count / sentence_count if sentence_count > 0 else 0,
            'exclamation_ratio': exclamation_count / sentence_count if sentence_count > 0 else 0,
            'caps_ratio': caps_ratio,
            'avg_post_length': avg_post_length,
            'avg_comment_length': avg_comment_length,
            'avg_post_score': avg_post_score,
            'avg_comment_score': avg_comment_score,
            'post_to_comment_ratio': len(posts) / len(comments) if comments else float('inf')
        }
    
    def _analyze_sentiment_patterns(self, posts: List[Dict], comments: List[Dict]) -> Dict:
        """Analyze sentiment patterns across posts and comments"""
        
        post_sentiments = [p.get('sentiment', {}) for p in posts]
        comment_sentiments = [c.get('sentiment', {}) for c in comments]
        
        def avg_sentiment(sentiments, key):
            values = [s.get(key, 0) for s in sentiments if s.get(key) is not None]
            return sum(values) / len(values) if values else 0
        
        return {
            'overall_sentiment': {
                'posts_positive': avg_sentiment(post_sentiments, 'vader_positive'),
                'posts_negative': avg_sentiment(post_sentiments, 'vader_negative'),
                'posts_compound': avg_sentiment(post_sentiments, 'vader_compound'),
                'comments_positive': avg_sentiment(comment_sentiments, 'vader_positive'),
                'comments_negative': avg_sentiment(comment_sentiments, 'vader_negative'),
                'comments_compound': avg_sentiment(comment_sentiments, 'vader_compound')
            },
            'subjectivity': {
                'posts_avg': avg_sentiment(post_sentiments, 'textblob_subjectivity'),
                'comments_avg': avg_sentiment(comment_sentiments, 'textblob_subjectivity')
            }
        }
    
    def _extract_topics(self, text: str) -> Dict:
        """Extract topics and interests from text"""
        
        # Common topic keywords
        topic_keywords = {
            'technology': ['tech', 'programming', 'software', 'computer', 'code', 'app', 'digital'],
            'gaming': ['game', 'gaming', 'play', 'xbox', 'playstation', 'pc', 'steam'],
            'sports': ['sport', 'team', 'game', 'player', 'season', 'match', 'win'],
            'politics': ['political', 'government', 'election', 'vote', 'policy', 'democrat', 'republican'],
            'entertainment': ['movie', 'show', 'tv', 'film', 'actor', 'music', 'band'],
            'finance': ['money', 'investment', 'stock', 'crypto', 'bitcoin', 'financial', 'economy'],
            'health': ['health', 'medical', 'doctor', 'fitness', 'exercise', 'diet', 'wellness'],
            'education': ['school', 'university', 'student', 'learn', 'study', 'education', 'teacher']
        }
        
        text_lower = text.lower()
        topic_scores = {}
        
        for topic, keywords in topic_keywords.items():
            score = sum(text_lower.count(keyword) for keyword in keywords)
            topic_scores[topic] = score
        
        # Get top topics
        sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'topic_scores': topic_scores,
            'top_topics': sorted_topics[:5],
            'primary_interest': sorted_topics[0][0] if sorted_topics and sorted_topics[0][1] > 0 else 'general'
        }
    
    def _analyze_activity_patterns(self, posts: List[Dict], comments: List[Dict]) -> Dict:
        """Analyze user activity patterns"""
        
        all_items = posts + comments
        
        if not all_items:
            return {}
        
        # Time-based analysis
        timestamps = [item.get('timestamp') for item in all_items if item.get('timestamp')]
        
        if not timestamps:
            return {}
        
        # Day of week analysis
        days = [ts.weekday() for ts in timestamps]
        day_counts = {i: days.count(i) for i in range(7)}
        
        # Hour analysis
        hours = [ts.hour for ts in timestamps]
        hour_counts = {i: hours.count(i) for i in range(24)}
        
        # Subreddit analysis
        subreddits = {}
        for item in all_items:
            subreddit = item.get('subreddit', 'unknown')
            subreddits[subreddit] = subreddits.get(subreddit, 0) + 1
        
        # Most active times
        most_active_day = max(day_counts.items(), key=lambda x: x[1])[0]
        most_active_hour = max(hour_counts.items(), key=lambda x: x[1])[0]
        
        # Activity consistency
        activity_variance = sum((count - (len(all_items) / 7))**2 for count in day_counts.values()) / 7
        
        return {
            'total_activity': len(all_items),
            'posts_vs_comments': len(posts) / len(comments) if comments else float('inf'),
            'most_active_day': most_active_day,  # 0=Monday, 6=Sunday
            'most_active_hour': most_active_hour,
            'day_distribution': day_counts,
            'hour_distribution': hour_counts,
            'top_subreddits': sorted(subreddits.items(), key=lambda x: x[1], reverse=True)[:10],
            'activity_consistency': 1 / (1 + activity_variance),  # Higher = more consistent
            'posting_frequency': len(all_items) / max(1, (max(timestamps) - min(timestamps)).days or 1)
        }