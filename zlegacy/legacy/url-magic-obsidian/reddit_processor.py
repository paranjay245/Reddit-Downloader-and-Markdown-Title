import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1'
}

def get_reddit_title(url):
    try:
        # Clean up the URL by removing extra parentheses
        url = url.rstrip(')')
        
        # Extract subreddit and post ID using the exact regex from reddit links.py
        match = re.match(r'https://www\.reddit\.com/r/([^/]+)/s/([^/]+)', url)
        if match:
            subreddit = match.group(1)
            post_id = match.group(2)
            
            # Try to get the title from the page
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to find the post title in the HTML (exact same logic as Python)
            title_element = soup.find('h1')
            if title_element and title_element.text.strip():
                return title_element.text.strip()
            
            # If we can't find the title, return subreddit-based format
            return f"Post in r/{subreddit}"
        
        return "Reddit post"
    except Exception as e:
        print(f"Error fetching Reddit title: {e}")
        return "Reddit post"

if __name__ == "__main__":
    # Test the function
    test_url = "https://www.reddit.com/r/JEENEETards/s/WwYnYRcAx6"
    print(get_reddit_title(test_url)) 