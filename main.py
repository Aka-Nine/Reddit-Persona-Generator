#!/usr/bin/env python3
"""
Reddit User Persona Generator
Main script to generate user personas from Reddit profiles
"""

import argparse
import logging
import os
import sys
from datetime import datetime

# Ensure required NLTK resources are available
import nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config import validate_config, OUTPUT_DIR, LOG_LEVEL
from src.reddit_scraper import RedditScraper
from src.data_processor import DataProcessor
from src.persona_analyzer import PersonaAnalyzer
from src.citation_manager import CitationManager
from src.output_generator import OutputGenerator

def validate_reddit_url(url: str) -> str:
    """Validate Reddit URL and extract username"""
    if not url:
        raise ValueError("Reddit URL is required")
    
    if url.startswith('https://www.reddit.com/user/'):
        username = url.split('/user/')[1].split('/')[0]
    elif url.startswith('https://reddit.com/user/'):
        username = url.split('/user/')[1].split('/')[0]
    elif url.startswith('https://www.reddit.com/u/'):
        username = url.split('/u/')[1].split('/')[0]
    elif url.startswith('https://reddit.com/u/'):
        username = url.split('/u/')[1].split('/')[0]
    elif url.startswith('u/'):
        username = url[2:]
    elif url.startswith('/u/'):
        username = url[3:]
    else:
        # Assume it's just a username
        username = url
    
    username = username.strip('/')
    
    if not username:
        raise ValueError("Could not extract username from URL")
    
    return username

def setup_logging(log_level: str):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('persona_generator.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main function to run the persona generator"""
    
    # Setup logging
    setup_logging(LOG_LEVEL)
    logger = logging.getLogger(__name__)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate user persona from Reddit profile')
    parser.add_argument('profile_url', help='Reddit user profile URL or username (e.g., https://www.reddit.com/user/spez)')
    parser.add_argument('--output', '-o', help='Output file path (optional)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Validate configuration
        validate_config()
        logger.info("Configuration validated successfully")
        
        # Extract and validate Reddit username
        username = validate_reddit_url(args.profile_url)
        logger.info(f"Processing Reddit user: {username}")
        
        # Create output directory
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Initialize components
        scraper = RedditScraper()
        processor = DataProcessor()
        analyzer = PersonaAnalyzer()
        citation_manager = CitationManager()
        output_generator = OutputGenerator()
        
        # Step 1: Scrape Reddit data
        logger.info("Starting Reddit data scraping...")
        user_data = scraper.scrape_user_data(username)
        logger.info(f"Scraped {len(user_data['posts'])} posts and {len(user_data['comments'])} comments")
        
        # Step 2: Process data
        logger.info("Processing scraped data...")
        processed_data = processor.process_user_data(user_data)
        logger.info("Data processing completed")
        
        # Step 3: Analyze persona
        logger.info("Analyzing user persona...")
        persona_data = analyzer.analyze_persona(processed_data)
        logger.info("Persona analysis completed")
        
        # Step 4: Generate citations
        logger.info("Generating citations...")
        citations = citation_manager.generate_citations(persona_data, user_data)
        logger.info("Citations generated")
        
        # Step 5: Generate output
        output_file = args.output or f"{OUTPUT_DIR}/{username}_persona.txt"
        logger.info(f"Generating output file at: {output_file}")
        output_generator.generate_persona_file(persona_data, citations, output_file, username)
        
        logger.info(f"Persona generated successfully: {output_file}")
        print(f"✅ Persona generated successfully: {output_file}")
    
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        print("\n❌ Process interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"Error generating persona: {str(e)}")
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
