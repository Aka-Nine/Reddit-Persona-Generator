import re

def validate_reddit_url(url):
    match = re.match(r'https?://(www\.)?reddit\.com/user/([^/]+)/?', url)
    if match:
        return match.group(2)
    raise ValueError("Invalid Reddit profile URL")
