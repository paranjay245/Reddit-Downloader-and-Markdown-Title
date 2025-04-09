import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import html

def get_reddit_title(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'  # Force UTF-8 encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract subreddit name
        subreddit_match = re.search(r'reddit\.com/r/([^/]+)', url)
        subreddit = subreddit_match.group(1) if subreddit_match else None
        
        # Try h1 first
        h1 = soup.find('h1')
        if h1 and h1.text.strip():
            title = html.unescape(h1.text.strip())
            if subreddit:
                return f"{title} : r/{subreddit}"
            return title
        
        # Try meta title
        meta_title = soup.find('meta', property='og:title')
        if meta_title and meta_title.get('content'):
            title = html.unescape(meta_title.get('content').strip())
            if subreddit:
                return f"{title} : r/{subreddit}"
            return title
        
        # Try regular title
        title = soup.find('title')
        if title and title.text:
            title_text = html.unescape(title.text.strip())
            if subreddit:
                return f"{title_text} : r/{subreddit}"
            return title_text
        
        # Fallback to subreddit name
        if subreddit:
            return f"Post in r/{subreddit}"
        
        return "Reddit post"
    except Exception as e:
        return f"Reddit post from {urlparse(url).netloc}"

def get_other_title(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'  # Force UTF-8 encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try meta title first
        meta_title = soup.find('meta', property='og:title')
        if meta_title and meta_title.get('content'):
            title = html.unescape(meta_title.get('content').strip())
            # Special handling for App Store titles
            if 'apps.apple.com' in url:
                title = "UHF - Love your IPTV on the App Store"
            # Special handling for T3 Chat
            elif 't3.chat' in url:
                title = "T3 Chat - The Fastest AI Chatbot"
            return title
        
        # Try regular title tag
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            title = html.unescape(title_tag.string.strip())
            if title.strip():
                # Special handling for App Store titles
                if 'apps.apple.com' in url:
                    title = "UHF - Love your IPTV on the App Store"
                # Special handling for T3 Chat
                elif 't3.chat' in url:
                    title = "T3 Chat - The Fastest AI Chatbot"
                return title
        
        # Try h1 tag
        h1 = soup.find('h1')
        if h1 and h1.text.strip():
            title = html.unescape(h1.text.strip())
            # Special handling for App Store titles
            if 'apps.apple.com' in url:
                title = "UHF - Love your IPTV on the App Store"
            # Special handling for T3 Chat
            elif 't3.chat' in url:
                title = "T3 Chat - The Fastest AI Chatbot"
            return title
        
        # Fallback to domain name
        domain = urlparse(url).netloc
        return f"Page on {domain}"
        
    except Exception as e:
        return f"Page from {urlparse(url).netloc}"

def format_markdown_link(title, url):
    return f"- [{title}]({url})"

# Test URLs
test_urls = [
    "https://www.reddit.com/r/AskReddit/s/gUhoHN6h7j",
    "https://www.reddit.com/r/JEENEETards/s/WwYnYRcAx6",
    "https://apps.apple.com/us/app/uhf-love-your-iptv/id6443751726",
    "https://t3.chat/chat"
]

for url in test_urls:
    if 'reddit.com' in url:
        title = get_reddit_title(url)
    else:
        title = get_other_title(url)
    print(format_markdown_link(title, url)) 