"""
Persona Analyzer Module
Uses LLM to analyze user data and generate persona characteristics
"""

import json
import logging
from typing import Dict, List, Optional
from groq import Groq
import google.generativeai as genai

from config import (
    LLM_PROVIDER, GROQ_API_KEY, GOOGLE_API_KEY, 
    GROQ_MODEL, GOOGLE_MODEL, CONFIDENCE_THRESHOLD
)

class PersonaAnalyzer:
    """Analyzes user data to generate persona using LLM"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.provider = LLM_PROVIDER
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LLM client"""
        try:
            if self.provider == 'groq':
                self.client = Groq(api_key=GROQ_API_KEY)
                self.model = GROQ_MODEL
                self.logger.info("Groq client initialized")
            elif self.provider == 'google':
                genai.configure(api_key=GOOGLE_API_KEY)
                self.client = genai.GenerativeModel(GOOGLE_MODEL)
                self.model = GOOGLE_MODEL
                self.logger.info("Google Generative AI client initialized")
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM: {str(e)}")
            raise
    
    def analyze_persona(self, processed_data: Dict) -> Dict:
        """
        Analyze processed user data to generate persona
        
        Args:
            processed_data: Processed user data from DataProcessor
            
        Returns:
            Dictionary containing persona characteristics
        """
        try:
            # Prepare data for analysis
            analysis_data = self._prepare_analysis_data(processed_data)
            
            # Generate different aspects of persona
            demographics = self._analyze_demographics(analysis_data)
            personality = self._analyze_personality(analysis_data)
            motivations = self._analyze_motivations(analysis_data)
            behaviors = self._analyze_behaviors(analysis_data)
            frustrations = self._analyze_frustrations(analysis_data)
            goals = self._analyze_goals(analysis_data)
            
            # Combine all aspects
            persona = {
                'username': processed_data.get('username'),
                'demographics': demographics,
                'personality': personality,
                'motivations': motivations,
                'behaviors_habits': behaviors,
                'frustrations': frustrations,
                'goals_needs': goals,
                'confidence_score': self._calculate_confidence_score(analysis_data),
                'analysis_summary': self._generate_summary(analysis_data)
            }
            
            return persona
            
        except Exception as e:
            self.logger.error(f"Error analyzing persona: {str(e)}")
            raise
    
    def _prepare_analysis_data(self, processed_data: Dict) -> Dict:
        """Prepare data for LLM analysis"""
        
        # Extract key information
        features = processed_data.get('features', {})
        sentiment = processed_data.get('sentiment_patterns', {})
        topics = processed_data.get('topics', {})
        activity = processed_data.get('activity_patterns', {})
        user_info = processed_data.get('user_info', {})
        
        # Sample posts and comments for context
        posts = processed_data.get('posts', [])[:10]  # Top 10 posts
        comments = processed_data.get('comments', [])[:20]  # Top 20 comments
        
        # Create summary statistics
        summary = {
            'total_posts': len(processed_data.get('posts', [])),
            'total_comments': len(processed_data.get('comments', [])),
            'account_age_days': user_info.get('account_age_days', 0),
            'karma_ratio': user_info.get('comment_karma', 0) / max(1, user_info.get('link_karma', 1)),
            'avg_sentiment': sentiment.get('overall_sentiment', {}).get('posts_compound', 0),
            'primary_topic': topics.get('primary_interest', 'general'),
            'top_subreddits': activity.get('top_subreddits', [])[:5],
            'posting_frequency': activity.get('posting_frequency', 0)
        }
        
        return {
            'features': features,
            'sentiment_patterns': sentiment,
            'topics': topics,
            'activity_patterns': activity,
            'user_info': user_info,
            'sample_posts': posts,
            'sample_comments': comments,
            'summary': summary
        }
    
    def _analyze_demographics(self, data: Dict) -> Dict:
        """Analyze demographic characteristics"""
        
        prompt = f"""
        Analyze the following Reddit user data and infer demographic characteristics.
        Be conservative in your estimates and indicate confidence levels.
        
        User Summary:
        - Account age: {data['summary']['account_age_days']} days
        - Total posts: {data['summary']['total_posts']}
        - Total comments: {data['summary']['total_comments']}
        - Primary topics: {data['topics'].get('primary_interest', 'general')}
        - Top subreddits: {[sub[0] for sub in data['summary']['top_subreddits']]}
        - Average sentiment: {data['summary']['avg_sentiment']}
        
        Sample content:
        {self._format_sample_content(data['sample_posts'][:3], data['sample_comments'][:5])}
        
        Provide demographic analysis in JSON format:
        {{
            "age_range": "estimated age range (e.g., '25-35')",
            "age_confidence": 0.5,
            "likely_gender": "inferred gender or 'unknown'",
            "gender_confidence": 0.3,
            "likely_location": "inferred location or 'unknown'",
            "location_confidence": 0.2,
            "occupation_category": "inferred occupation category",
            "occupation_confidence": 0.4,
            "education_level": "inferred education level",
            "education_confidence": 0.3,
            "relationship_status": "inferred status or 'unknown'",
            "status_confidence": 0.2
        }}
        """
        
        response = self._query_llm(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return self._extract_json_from_response(response)
    
    def _analyze_personality(self, data: Dict) -> Dict:
        """Analyze personality traits"""
        
        prompt = f"""
        Analyze the following Reddit user data and determine personality traits.
        Use established personality frameworks (Big Five, Myers-Briggs indicators).
        
        User Data:
        - Writing style: {data['features']}
        - Sentiment patterns: {data['sentiment_patterns']}
        - Activity patterns: {data['activity_patterns']}
        - Topics of interest: {data['topics']}
        
        Sample content:
        {self._format_sample_content(data['sample_posts'][:3], data['sample_comments'][:5])}
        
        Provide personality analysis in JSON format:
        {{
            "big_five": {{
                "openness": 0.7,
                "conscientiousness": 0.6,
                "extraversion": 0.5,
                "agreeableness": 0.8,
                "neuroticism": 0.4
            }},
            "communication_style": "description of communication style",
            "social_tendencies": "introverted/extraverted tendencies",
            "decision_making": "thinking vs feeling preference",
            "information_processing": "sensing vs intuition preference",
            "lifestyle_approach": "judging vs perceiving preference",
            "key_traits": ["analytical", "curious", "helpful", "detailed"],
            "archetype": "The Analyst"
        }}
        """
        
        response = self._query_llm(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return self._extract_json_from_response(response)
    
    def _analyze_motivations(self, data: Dict) -> Dict:
        """Analyze user motivations"""
        
        prompt = f"""
        Analyze what motivates this Reddit user based on their posting patterns and content.
        
        User Data:
        - Topics: {data['topics']}
        - Activity patterns: {data['activity_patterns']}
        - Engagement metrics: {data['features']}
        
        Sample content:
        {self._format_sample_content(data['sample_posts'][:3], data['sample_comments'][:5])}
        
        Provide motivations analysis in JSON format:
        {{
            "primary_motivations": ["knowledge_sharing", "community_building", "entertainment"],
            "convenience_importance": 0.6,
            "social_connection": 0.8,
            "knowledge_sharing": 0.9,
            "entertainment": 0.7,
            "self_expression": 0.5,
            "community_belonging": 0.8,
            "achievement_recognition": 0.4,
            "motivational_quote": "Knowledge shared is knowledge multiplied"
        }}
        """
        
        response = self._query_llm(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return self._extract_json_from_response(response)
    
    def _analyze_behaviors(self, data: Dict) -> Dict:
        """Analyze user behaviors and habits"""
        
        prompt = f"""
        Analyze behavioral patterns and habits of this Reddit user.
        
        Activity Data:
        - Posting frequency: {data['activity_patterns'].get('posting_frequency', 0)}
        - Most active time: {data['activity_patterns'].get('most_active_hour', 0)}:00
        - Post vs comment ratio: {data['activity_patterns'].get('posts_vs_comments', 0)}
        - Top subreddits: {data['activity_patterns'].get('top_subreddits', [])[:5]}
        
        Content Analysis:
        - Average post length: {data['features'].get('avg_post_length', 0)}
        - Question ratio: {data['features'].get('question_ratio', 0)}
        - Exclamation ratio: {data['features'].get('exclamation_ratio', 0)}
        
        Provide behavioral analysis in JSON format:
        {{
            "posting_habits": ["consistent_daily_posting", "prefers_comments_over_posts"],
            "content_preferences": ["technical_discussions", "helpful_responses"],
            "interaction_style": "helpful and analytical",
            "time_patterns": "most active during evening hours",
            "platform_usage": "primarily uses Reddit for learning and sharing knowledge",
            "engagement_behavior": "responds thoughtfully to questions",
            "routine_indicators": ["daily_check_ins", "weekend_longer_posts"]
        }}
        """
        
        response = self._query_llm(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return self._extract_json_from_response(response)
    
    def _analyze_frustrations(self, data: Dict) -> Dict:
        """Analyze user frustrations"""
        
        prompt = f"""
        Identify potential frustrations and pain points for this Reddit user.
        
        Sentiment Data:
        - Overall sentiment: {data['sentiment_patterns'].get('overall_sentiment', {})}
        - Negative posts ratio: {data['sentiment_patterns'].get('overall_sentiment', {}).get('posts_negative', 0)}
        
        Activity Data:
        - Average scores: Posts {data['features'].get('avg_post_score', 0)}, Comments {data['features'].get('avg_comment_score', 0)}
        - Subreddit diversity: {len(data['activity_patterns'].get('top_subreddits', []))}
        
        Sample content with negative sentiment:
        {self._format_sample_content(data['sample_posts'][:2], data['sample_comments'][:3])}
        
        Provide frustrations analysis in JSON format:
        {{
            "main_frustrations": ["information_overload", "repetitive_questions"],
            "technology_frustrations": ["slow_loading_times", "poor_search_functionality"],
            "social_frustrations": ["toxic_comments", "lack_of_constructive_discussion"],
            "platform_frustrations": ["unclear_moderation", "limited_formatting_options"],
            "time_management_issues": ["spending_too_much_time_scrolling"],
            "information_overload": true,
            "engagement_disappointment": false
        }}
        """
        
        response = self._query_llm(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return self._extract_json_from_response(response)
    
    def _analyze_goals(self, data: Dict) -> Dict:
        """Analyze user goals and needs"""
        
        prompt = f"""
        Identify the goals and needs of this Reddit user based on their activity.
        
        User Activity:
        - Primary interests: {data['topics'].get('primary_interest', 'general')}
        - Engagement level: {data['features'].get('avg_post_score', 0) + data['features'].get('avg_comment_score', 0)}
        - Community involvement: {len(data['activity_patterns'].get('top_subreddits', []))}
        
        Content Analysis:
        - Question asking behavior: {data['features'].get('question_ratio', 0)}
        - Knowledge sharing: {data['features'].get('avg_post_length', 0)}
        
        Provide goals analysis in JSON format:
        {{
            "primary_goals": ["learn_new_skills", "help_others", "stay_informed"],
            "information_needs": ["technical_tutorials", "industry_news", "best_practices"],
            "social_needs": ["expert_validation", "peer_discussion", "mentorship"],
            "entertainment_needs": ["interesting_content", "humor", "community_events"],
            "learning_objectives": ["skill_development", "career_advancement", "hobby_improvement"],
            "community_goals": ["build_reputation", "contribute_knowledge", "network"],
            "personal_development": ["critical_thinking", "communication_skills", "expertise"],
            "long_term_aspirations": ["become_expert", "build_influence", "create_impact"]
        }}
        """
        
        response = self._query_llm(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return self._extract_json_from_response(response)
    
    def _format_sample_content(self, posts: List[Dict], comments: List[Dict]) -> str:
        """Format sample content for LLM analysis"""
        content = []
        
        for post in posts[:3]:
            content.append(f"POST: {post.get('clean_title', '')} - {post.get('clean_text', '')[:200]}...")
        
        for comment in comments[:3]:
            content.append(f"COMMENT: {comment.get('clean_text', '')[:200]}...")
        
        return '\n'.join(content)
    
    def _query_llm(self, prompt: str) -> str:
        """Query the LLM with the given prompt"""
        try:
            if self.provider == 'groq':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert user experience researcher and psychologist specializing in digital behavior analysis. Provide accurate, evidence-based insights. Always return valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.3
                )
                return response.choices[0].message.content
            
            elif self.provider == 'google':
                response = self.client.generate_content(prompt)
                return response.text
            
        except Exception as e:
            self.logger.error(f"Error querying LLM: {str(e)}")
            raise
    
    def _extract_json_from_response(self, response: str) -> Dict:
        """Extract JSON from LLM response if direct parsing fails"""
        try:
            # Try to find JSON in the response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                return json.loads(json_str)
        except:
            pass
        
        # Return default structure if extraction fails
        self.logger.warning("Failed to extract JSON from LLM response, using default structure")
        return {
            "error": "Failed to parse LLM response",
            "raw_response": response[:200]
        }
    
    def _calculate_confidence_score(self, data: Dict) -> float:
        """Calculate overall confidence score for the analysis"""
        
        factors = []
        
        # Data volume factor
        total_content = data['summary']['total_posts'] + data['summary']['total_comments']
        volume_factor = min(1.0, total_content / 50)  # Normalize to 50 items
        factors.append(volume_factor)
        
        # Account age factor
        age_factor = min(1.0, data['summary']['account_age_days'] / 365)  # Normalize to 1 year
        factors.append(age_factor)
        
        # Activity diversity factor
        subreddit_count = len(data['activity_patterns'].get('top_subreddits', []))
        diversity_factor = min(1.0, subreddit_count / 10)  # Normalize to 10 subreddits
        factors.append(diversity_factor)
        
        # Content quality factor (based on average scores)
        avg_score = (data['features'].get('avg_post_score', 0) + data['features'].get('avg_comment_score', 0)) / 2
        quality_factor = min(1.0, max(0, avg_score) / 10)  # Normalize to score of 10
        factors.append(quality_factor)
        
        return sum(factors) / len(factors)
    
    def _generate_summary(self, data: Dict) -> str:
        """Generate a brief summary of the analysis"""
        
        summary = f"""
        Analysis Summary for {data.get('username', 'Unknown User')}:
        
        Account Age: {data['summary']['account_age_days']} days
        Activity Level: {data['summary']['total_posts']} posts, {data['summary']['total_comments']} comments
        Primary Interest: {data['topics'].get('primary_interest', 'General')}
        Engagement: Average sentiment {data['summary']['avg_sentiment']:.2f}
        Top Communities: {', '.join([sub[0] for sub in data['summary']['top_subreddits'][:3]])}
        
        This analysis is based on publicly available Reddit activity and should be considered
        an approximation of user characteristics rather than definitive personality assessment.
        """
        
        return summary.strip()