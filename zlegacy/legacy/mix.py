import requests
from bs4 import BeautifulSoup
import time
import re

# Add headers to mimic a browser with more realistic headers
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
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to find the post title in the HTML
        title_element = soup.find('h1')
        if title_element and title_element.text.strip():
            return title_element.text.strip()
            
        # If we can't find the title, extract subreddit name
        match = re.match(r'https://www\.reddit\.com/r/([^/]+)/s/([^/]+)', url)
        if match:
            subreddit = match.group(1)
            post_id = match.group(2)
            return f"Post in r/{subreddit}"
    except Exception as e:
        return f"Reddit post"

# Test with just the first 3 URLs
urls = [
    "https://www.reddit.com/r/JEENEETards/s/WwYnYRcAx6",
    "https://www.reddit.com/r/macapps/s/NNoDU3D3hC",
    "https://t3.chat/chat"
]

markdown_list = ""

for url in urls:
    try:
        if 'reddit.com' in url:
            # For Reddit posts, try to get the title directly
            title = get_reddit_title(url)
            time.sleep(1)  # Be nice to Reddit's servers
        else:
            # For non-Reddit URLs, fetch the page
            time.sleep(1)
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find the title in multiple ways
            title = None
            # First try meta title
            meta_title = soup.find('meta', property='og:title')
            if meta_title:
                title = meta_title.get('content')
            
            # If no meta title, try h1
            if not title:
                h1 = soup.find('h1')
                if h1:
                    title = h1.text.strip()
            
            # Finally, fall back to regular title tag
            if not title:
                title_tag = soup.find('title')
                if title_tag:
                    title = title_tag.string.strip()
                    
            # If still no title, use the domain name
            if not title:
                from urllib.parse import urlparse
                domain = urlparse(url).netloc
                title = f"Page on {domain}"
            
            if 'apps.apple.com' in url:
                # For App Store pages
                if ' on the App Store' in title:
                    title = title.replace(' on the App Store', '')
                elif ' on the Mac App Store' in title:
                    title = title.replace(' on the Mac App Store', '')
            elif not title:
                # If we still don't have a title, use the domain name
                from urllib.parse import urlparse
                domain = urlparse(url).netloc
                title = f"Page on {domain}"
            
    except requests.exceptions.RequestException as e:
        title = f"Error fetching title: {type(e).__name__} - {url}"
    except AttributeError:
        title = f"Title not found - {url}"
    except Exception as e:
        title = f"An unexpected error occurred: {type(e).__name__} - {url}"

    markdown_list += f"- [{title}]({url})\n"
    print(f"Processed: {url}")

print("\nFinal markdown list:")
print(markdown_list)