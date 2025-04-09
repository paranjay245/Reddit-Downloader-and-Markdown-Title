import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urlparse

# Simplified Headers - Let's see if this avoids triggering weird responses
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9', # Keep language preference
}

# --- URLs to Test ---
urls = [
    "https://x.com/sama", # JS Heavy - Expected to fail gracefully
    "https://apps.apple.com/us/app/uhf-love-your-iptv/id6443751726", # JS Heavy? Expected to fail or be generic
    "https://apps.apple.com/us/app/sortio/id6737292062?mt=12", # JS Heavy? Expected to fail or be generic
    "https://www.reddit.com/r/AskReddit/s/gUhoHN6h7j", # Should work
    "https://www.reddit.com/r/JEENEETards/s/WwYnYRcAx6", # Should work
    "https://www.reddit.com/r/macapps/s/NNoDU3D3hC", # Should work
    "https://t3.chat/chat", # JS Heavy - Expected to fail gracefully
    "https://1001albumsgenerator.com/", # Should work
    "https://help.openai.com/en/articles/6825453-chatgpt-release-notes", # Expected 403
    "https://www.youtube.com/watch?v=tELxjdWHByk", # Should work
    "https://www.youtube.com/watch?v=1cFonowsaUA&list=TLPQMzEwMzIwMjUZjXwDTVtBYA&index=4", # Should work
    "https://broflix.ci/watch/movie/1290938?title=South%20Park:%20The%20End%20of%20Obesity&imdb_id=tt32375562" # Potentially JS Heavy
]

# --- Helper Functions ---

def clean_and_validate_title(title_str, url):
    """Cleans the title and checks if it's generic or invalid."""
    if not title_str:
        return None

    title = title_str.strip()

    # --- Common Suffixes/Prefixes to Remove ---
    suffixes_to_remove = [
        ' on the App Store',
        ' on the Mac App Store',
        '- YouTube',
        '| YouTube',
        # Add more suffixes if needed
    ]
    prefixes_to_remove = [
        # Add prefixes if needed
    ]

    for suffix in suffixes_to_remove:
        if title.endswith(suffix):
            title = title[:-len(suffix)].strip()
            break # Remove only one suffix match

    for prefix in prefixes_to_remove:
        if title.startswith(prefix):
            title = title[len(prefix):].strip()
            break # Remove only one prefix match

    # --- Generic Titles to Discard ---
    # Check for titles that are essentially useless placeholders
    generic_titles = [
        "reddit",
        "reddit.com",
        "youtube",
        "twitter",
        "x",
        "log in",
        "sign in",
        "just a moment...", # Cloudflare/JS checks
        "javascript is not available.",
        "enable javascript and cookies to continue",
        "page not found",
        "404 not found",
        "error",
        # Add more generic/error titles
    ]
    # Special case for Reddit's generic title
    if 'reddit.com' in urlparse(url).netloc and title.lower() == 'reddit - the heart of the internet':
        print(f"    [Cleaner] Discarding generic Reddit title: '{title_str}'")
        return None # Discard this specific generic title for Reddit URLs

    # General check for generic words/phrases
    if title.lower() in generic_titles:
         print(f"    [Cleaner] Discarding generic title: '{title_str}'")
         return None

    # --- Final Cleanup ---
    # Replace multiple spaces with one
    title = re.sub(r'\s+', ' ', title).strip()

    # If cleaning resulted in an empty string, discard
    if not title:
        print(f"    [Cleaner] Discarding title - became empty after cleaning: '{title_str}'")
        return None

    return title

def get_title_from_soup(soup):
    """Attempts to extract title preferentially from meta tags, then title tag."""
    title = None
    source = "N/A"

    # 1. Try OpenGraph title
    og_title = soup.find('meta', property='og:title')
    if og_title and og_title.get('content'):
        title = og_title.get('content')
        source = "og:title"

    # 2. Try Twitter title (if og:title failed)
    if not title:
        tw_title = soup.find('meta', attrs={'name': 'twitter:title'}) # Common variant
        if tw_title and tw_title.get('content'):
            title = tw_title.get('content')
            source = "twitter:title [name]"
        else:
             tw_title_prop = soup.find('meta', property='twitter:title') # Property variant
             if tw_title_prop and tw_title_prop.get('content'):
                 title = tw_title_prop.get('content')
                 source = "twitter:title [prop]"

    # 3. Try regular <title> tag (if meta tags failed)
    if not title:
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            title = title_tag.string
            source = "title tag"

    print(f"    [Extractor] Found potential raw title via '{source}': '{title}'")
    return title


def get_fallback_title(url):
    """Generates a fallback title based on the domain or URL path."""
    try:
        parsed_url = urlparse(url)
        if parsed_url.netloc:
            # Try to get a hint from the path if it's not just '/'
            path_part = parsed_url.path.strip('/')
            if path_part and len(path_part.split('/')) <= 2: # Avoid overly long paths
                # Simple heuristic: use last part of path if it looks like a word
                last_part = path_part.split('/')[-1]
                if last_part and not re.match(r'^[a-f0-9-]+$', last_part.lower()): # Avoid IDs
                    return f"{last_part.replace('-', ' ').replace('_', ' ').title()} on {parsed_url.netloc}"

            return f"Page on {parsed_url.netloc}"
        else:
            # Handle cases without clear netloc (e.g., file:// paths?)
            return f"Resource at {url[:50]}{'...' if len(url)>50 else ''}"
    except Exception:
        return f"Invalid URL or Page - {url[:50]}{'...' if len(url)>50 else ''}"

# --- Main Processing Logic ---
markdown_list = ""

print("Starting URL processing...")
print("NOTE: Sites heavily reliant on JavaScript (e.g., X.com, App Store) may not yield accurate titles.")

for url in urls:
    final_title = None
    print(f"Processing: {url}")
    try:
        time.sleep(1.2) # Small delay

        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True) # Follow redirects

        if not response.ok:
            response.raise_for_status() # Raise HTTPError for 4xx/5xx

        content_type = response.headers.get('Content-Type', '').lower()
        if 'html' not in content_type:
            print(f"  Skipping non-HTML content: {content_type}")
            final_title = get_fallback_title(url) # Use fallback for non-html
        else:
            response.encoding = response.apparent_encoding
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract raw title
            raw_title = get_title_from_soup(soup)

            # Clean and validate
            final_title = clean_and_validate_title(raw_title, url)

            # Apply Reddit-specific fallback if needed
            if 'reddit.com' in urlparse(url).netloc and not final_title:
                print("    [Fallback] Applying Reddit-specific fallback.")
                match = re.search(r'https://www\.reddit\.com/r/([^/]+)/', url)
                if match:
                    subreddit = match.group(1)
                    final_title = f"Reddit Post in r/{subreddit}"
                else:
                    final_title = "Reddit Post" # Ultimate Reddit fallback

            # If still no title after cleaning/Reddit fallback, use general fallback
            if not final_title:
                 print("    [Fallback] Applying general fallback.")
                 final_title = get_fallback_title(url)


    except requests.exceptions.Timeout:
        error_msg = f"Error: Timeout fetching title"
        print(f"  {error_msg} - {url}")
        final_title = f"{error_msg} - {url.split('//')[-1]}" # Shorten URL in error title
    except requests.exceptions.HTTPError as e:
        error_msg = f"Error: HTTP {e.response.status_code} {e.response.reason}"
        print(f"  {error_msg} - {url}")
        final_title = f"{error_msg} - {url.split('//')[-1]}"
    except requests.exceptions.ConnectionError as e:
        error_msg = f"Error: Connection Failed"
        print(f"  {error_msg} - {url} ({e})")
        final_title = f"{error_msg} - {url.split('//')[-1]}"
    except requests.exceptions.RequestException as e:
        error_msg = f"Error: Request Failed ({type(e).__name__})"
        print(f"  {error_msg} - {url}")
        final_title = f"{error_msg} - {url.split('//')[-1]}"
    except Exception as e:
        error_msg = f"Error: Processing Failed ({type(e).__name__})"
        print(f"  {error_msg} - {url} - {e}")
        final_title = f"{error_msg} - {url.split('//')[-1]}"

    # Final safety net: ensure final_title is never None
    if final_title is None:
        print("    [Error] Title determination failed unexpectedly, using basic fallback.")
        final_title = get_fallback_title(url)

    markdown_list += f"- [{final_title.strip()}]({url})\n"

print("\n--- Final Markdown List ---")
print(markdown_list)