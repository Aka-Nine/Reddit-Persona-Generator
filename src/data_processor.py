"""
Data Processing Module
Handles data cleaning, preprocessing, and feature extraction
"""

import re
import logging
from typing import Dict, List
from datetime import datetime
import pandas as pd
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Ensure punkt is available
import nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

from config import MIN_TEXT_LENGTH, MAX_TEXT_LENGTH
from utils.text_utils import clean_text, extract_keywords, calculate_readability

class DataProcessor:
    """Handles data cleaning and preprocessing"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

    def process_user_data(self, user_data: Dict) -> Dict:
        try:
            processed_posts = self._process_posts(user_data.get('posts', []))
            processed_comments = self._process_comments(user_data.get('comments', []))
            combined_text = self._combine_text(processed_posts, processed_comments)
            features = self._extract_features(combined_text, processed_posts, processed_comments)
            sentiment_patterns = self._analyze_sentiment_patterns(processed_posts, processed_comments)
            topics = self._extract_topics(combined_text)
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
        processed_posts = []
        for post in posts:
            clean_title = clean_text(post.get('title', ''))
            clean_text_content = clean_text(post.get('text', ''))
            total_text = f"{clean_title} {clean_text_content}"
            if len(total_text) < MIN_TEXT_LENGTH or len(total_text) > MAX_TEXT_LENGTH:
                continue
            sentiment = self._calculate_sentiment(total_text)
            keywords = extract_keywords(total_text)
            processed_posts.append({
                **post,
                'clean_title': clean_title,
                'clean_text': clean_text_content,
                'total_text': total_text,
                'text_length': len(total_text),
                'sentiment': sentiment,
                'keywords': keywords,
                'readability': calculate_readability(total_text),
                'timestamp': datetime.fromtimestamp(post.get('created_utc', 0))
            })
        return processed_posts

    def _process_comments(self, comments: List[Dict]) -> List[Dict]:
        processed_comments = []
        for comment in comments:
            clean_text_content = clean_text(comment.get('text', ''))
            if len(clean_text_content) < MIN_TEXT_LENGTH or len(clean_text_content) > MAX_TEXT_LENGTH:
                continue
            sentiment = self._calculate_sentiment(clean_text_content)
            keywords = extract_keywords(clean_text_content)
            processed_comments.append({
                **comment,
                'clean_text': clean_text_content,
                'text_length': len(clean_text_content),
                'sentiment': sentiment,
                'keywords': keywords,
                'readability': calculate_readability(clean_text_content),
                'timestamp': datetime.fromtimestamp(comment.get('created_utc', 0))
            })
        return processed_comments

    def _combine_text(self, posts: List[Dict], comments: List[Dict]) -> str:
        return '\n\n'.join(
            [p.get('total_text', '') for p in posts] +
            [c.get('clean_text', '') for c in comments]
        )

    def _calculate_sentiment(self, text: str) -> Dict:
        scores = self.sentiment_analyzer.polarity_scores(text)
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
        word_count = len(text.split())
        char_count = len(text)
        sentence_count = len(re.findall(r'[.!?]+', text))
        question_count = text.count('?')
        exclamation_count = text.count('!')
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        avg_post_length = sum(p.get('text_length', 0) for p in posts) / len(posts) if posts else 0
        avg_comment_length = sum(c.get('text_length', 0) for c in comments) / len(comments) if comments else 0
        avg_post_score = sum(p.get('score', 0) for p in posts) / len(posts) if posts else 0
        avg_comment_score = sum(c.get('score', 0) for c in comments) / len(comments) if comments else 0

        return {
            'word_count': word_count,
            'char_count': char_count,
            'sentence_count': sentence_count,
            'question_ratio': question_count / sentence_count if sentence_count else 0,
            'exclamation_ratio': exclamation_count / sentence_count if sentence_count else 0,
            'caps_ratio': caps_ratio,
            'avg_post_length': avg_post_length,
            'avg_comment_length': avg_comment_length,
            'avg_post_score': avg_post_score,
            'avg_comment_score': avg_comment_score,
            'post_to_comment_ratio': len(posts) / len(comments) if comments else float('inf')
        }

    def _analyze_sentiment_patterns(self, posts: List[Dict], comments: List[Dict]) -> Dict:
        def avg(key, data):
            vals = [item['sentiment'].get(key) for item in data if 'sentiment' in item and key in item['sentiment']]
            return sum(vals) / len(vals) if vals else 0

        return {
            'overall_sentiment': {
                'posts_positive': avg('vader_positive', posts),
                'posts_negative': avg('vader_negative', posts),
                'posts_compound': avg('vader_compound', posts),
                'comments_positive': avg('vader_positive', comments),
                'comments_negative': avg('vader_negative', comments),
                'comments_compound': avg('vader_compound', comments)
            },
            'subjectivity': {
                'posts_avg': avg('textblob_subjectivity', posts),
                'comments_avg': avg('textblob_subjectivity', comments)
            }
        }

    def _extract_topics(self, text: str) -> Dict:
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
        scores = {k: sum(text_lower.count(word) for word in words) for k, words in topic_keywords.items()}
        sorted_topics = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return {
            'topic_scores': scores,
            'top_topics': sorted_topics[:5],
            'primary_interest': sorted_topics[0][0] if sorted_topics and sorted_topics[0][1] > 0 else 'general'
        }

    def _analyze_activity_patterns(self, posts: List[Dict], comments: List[Dict]) -> Dict:
        all_items = posts + comments
        if not all_items:
            return {}
        timestamps = [i['timestamp'] for i in all_items if 'timestamp' in i]
        days = [ts.weekday() for ts in timestamps]
        hours = [ts.hour for ts in timestamps]
        day_counts = {i: days.count(i) for i in range(7)}
        hour_counts = {i: hours.count(i) for i in range(24)}
        subreddit_counts = {}
        for i in all_items:
            sub = i.get('subreddit', 'unknown')
            subreddit_counts[sub] = subreddit_counts.get(sub, 0) + 1
        most_active_day = max(day_counts, key=day_counts.get)
        most_active_hour = max(hour_counts, key=hour_counts.get)
        variance = sum((count - len(all_items)/7)**2 for count in day_counts.values()) / 7
        posting_days = (max(timestamps) - min(timestamps)).days or 1
        return {
            'total_activity': len(all_items),
            'posts_vs_comments': len(posts) / len(comments) if comments else float('inf'),
            'most_active_day': most_active_day,
            'most_active_hour': most_active_hour,
            'day_distribution': day_counts,
            'hour_distribution': hour_counts,
            'top_subreddits': sorted(subreddit_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            'activity_consistency': 1 / (1 + variance),
            'posting_frequency': len(all_items) / posting_days
        }
