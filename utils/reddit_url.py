"""Reddit profile URL / username parsing (shared by CLI and web server)."""


def validate_reddit_url(url: str) -> str:
    """Validate Reddit URL or plain username; return username without u/ prefix."""
    if not url:
        raise ValueError("Reddit URL is required")

    u = url.strip()

    if u.startswith("https://www.reddit.com/user/"):
        username = u.split("/user/")[1].split("/")[0]
    elif u.startswith("https://reddit.com/user/"):
        username = u.split("/user/")[1].split("/")[0]
    elif u.startswith("https://www.reddit.com/u/"):
        username = u.split("/u/")[1].split("/")[0]
    elif u.startswith("https://reddit.com/u/"):
        username = u.split("/u/")[1].split("/")[0]
    elif u.startswith("u/"):
        username = u[2:]
    elif u.startswith("/u/"):
        username = u[3:]
    else:
        username = u

    username = username.strip("/")

    if not username:
        raise ValueError("Could not extract username from URL")

    return username
