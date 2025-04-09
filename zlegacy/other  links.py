import requests
from bs4 import BeautifulSoup
import time

# Add headers to mimic a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

urls = [
    "https://apps.apple.com/us/app/uhf-love-your-iptv/id6443751726",
    "https://apps.apple.com/us/app/sortio/id6737292062?mt=12",
    "https://www.reddit.com/r/AskReddit/s/gUhoHN6h7j",
    "https://www.reddit.com/r/JEENEETards/s/WwYnYRcAx6",
    "https://www.reddit.com/r/macapps/s/NNoDU3D3hC",
    "https://t3.chat/chat",
    "https://1001albumsgenerator.com/",
    "https://help.openai.com/en/articles/6825453-chatgpt-release-notes"
]

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

markdown_list = ""

for url in urls:
    try:
        # Add a small delay between requests to avoid rate limiting
        time.sleep(1)
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Handle different types of pages
        if 'reddit.com' in url:
            # For Reddit posts, use the dedicated function
            from reddit_url import get_reddit_title
            title = get_reddit_title(url)
        else:
            # For other pages, try different title selectors
            title = None
            # Try meta title first
            meta_title = soup.find('meta', property='og:title')
            if meta_title:
                title = meta_title.get('content')
            
            # If no meta title, try regular title tag
            if not title:
                title_tag = soup.find('title')
                if title_tag and title_tag.string:
                    title = title_tag.string
            
            # Clean and format the title
            title = clean_title(title)
            
            # If still no title, use a generic one
            if not title:
                title = "Page at " + url.split('//')[1].split('/')[0]
            
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