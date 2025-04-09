import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urlparse

# Common headers to mimic a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive'
}

def clean_title(title):
    """Clean and format the title string."""
    if not title:
        return None
    # Remove common suffixes
    suffixes = [' on the App Store', ' on the Mac App Store']
    for suffix in suffixes:
        if title.endswith(suffix):
            title = title[:-len(suffix)]
    return title.strip()

def get_reddit_title(url):
    """Extract title for Reddit URLs."""
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to find the post title using common selectors
        title_element = soup.find('h1')
        if title_element and title_element.text.strip():
            return title_element.text.strip()
        
        # Fallback: attempt to extract subreddit name from URL
        match = re.match(r'https?://www\.reddit\.com/r/([^/]+)/(?:comments|s)/([^/]+)', url)
        if match:
            subreddit = match.group(1)
            return f"Post in r/{subreddit}"
    except requests.exceptions.HTTPError as http_err:
        return f"Error fetching title: HTTP {http_err.response.status_code} - {url}"
    except Exception as e:
        return f"Reddit post error: {type(e).__name__} - {url}"

def get_generic_title(url):
    """Extract title for non-Reddit URLs."""
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
    except requests.exceptions.HTTPError as http_err:
        return f"Error fetching title: HTTP {http_err.response.status_code} - {url}"
    except Exception as e:
        return f"Error fetching title: {type(e).__name__} - {url}"
    
    title = None
    # Try meta title first
    meta_title = soup.find('meta', property='og:title')
    if meta_title:
        title = meta_title.get('content')
    
    # If no meta title, try h1
    if not title:
        h1 = soup.find('h1')
        if h1 and h1.text.strip():
            title = h1.text.strip()
    
    # Finally, fallback to the <title> tag
    if not title:
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            title = title_tag.string.strip()
    
    title = clean_title(title)
    
    # If still no title, use the domain name
    if not title:
        domain = urlparse(url).netloc
        title = f"Page on {domain}"
    
    return title

def create_markdown_list(urls):
    markdown_list = ""
    seen = set()  # To avoid processing duplicates
    for url in urls:
        if url in seen:
            continue
        seen.add(url)
        try:
            time.sleep(1)  # Respectful delay between requests
            if 'reddit.com' in url:
                title = get_reddit_title(url)
            else:
                title = get_generic_title(url)
        except Exception as e:
            title = f"An unexpected error occurred: {type(e).__name__} - {url}"
        
        markdown_list += f"- [{title}]({url})\n"
        print(f"Processed: {url}")
    
    return markdown_list

if __name__ == "__main__":
    urls = [
        "https://apps.apple.com/us/app/uhf-love-your-iptv/id6443751726",
        "https://apps.apple.com/us/app/sortio/id6737292062?mt=12",
        "https://www.reddit.com/r/AskReddit/s/gUhoHN6h7j",
        "https://www.reddit.com/r/JEENEETards/s/WwYnYRcAx6",
        "https://www.reddit.com/r/macapps/s/NNoDU3D3hC",
        "https://t3.chat/chat",
        "https://1001albumsgenerator.com/",
        "https://help.openai.com/en/articles/6825453-chatgpt-release-notes",
        "https://www.youtube.com/watch?v=tELxjdWHByk",  # Example additional URL
        "https://www.youtube.com/watch?v=1cFonowsaUA&list=TLPQMzEwMzIwMjUZjXwDTVtBYA&index=4",
        "https://broflix.ci/watch/movie/1290938?title=South%20Park:%20The%20End%20of%20Obesity&imdb_id=tt32375562"
    ]
    
    final_markdown = create_markdown_list(urls)
    print("\nFinal markdown list:")
    print(final_markdown)
