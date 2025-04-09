import requests
from bs4 import BeautifulSoup
import sys

# Define the input list of URLs
urls = [
    "https://apps.apple.com/us/app/uhf-love-your-iptv/id6443751726",
    "https://apps.apple.com/us/app/sortio/id6737292062?mt=12",
    "https://www.reddit.com/r/AskReddit/s/gUhoHN6h7j",
    "https://www.reddit.com/r/JEENEETards/s/WwYnYRcAx6",
    "https://www.youtube.com/watch?v=tELxjdWHByk",
    "https://x.com/sama",
    "https://x.com/gdb", # Example: This might redirect or require login, title might vary
    "https://1001albumsgenerator.com/",
    "https://t3.chat/chat",
    "https://help.openai.com/en/articles/6825453-chatgpt-release-notes",
    "https://invalid-url-that-will-fail.xyz/", # Intentionally invalid URL
    "https://broflix.ci/watch/movie/1290938?title=South%20Park:%20The%20End%20of%20Obesity&imdb_id=tt32375562",
    "https://www.espncricinfo.com/series/ipl-2025-1449924/lucknow-super-giants-vs-punjab-kings-13th-match-1473450/live-cricket-score",
    "https://www.hotstar.com/in/sports/cricket/lsg-vs-pbks/1540040213/video/live/watch"
]

markdown_links = []
# Use a common browser User-Agent to avoid being blocked
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
timeout_seconds = 15 # Set a timeout for requests

print("Fetching titles...", file=sys.stderr) # Print progress to stderr

for url in urls:
    title = "[Error Fetching Title]" # Default title in case of failure
    final_url = url # Use original URL in case request fails early

    try:
        # Make the request, allow redirects, set timeout
        response = requests.get(url, headers=headers, timeout=timeout_seconds, allow_redirects=True)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # Use the final URL after potential redirects
        final_url = response.url

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- Strategy to find the best title ---
        page_title = None

        # 1. Try the main <title> tag
        if soup.title and soup.title.string:
            page_title = soup.title.string.strip()

        # 2. Fallback: Open Graph title (og:title) - often cleaner
        if not page_title:
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                page_title = og_title['content'].strip()

        # 3. Fallback: Twitter title (twitter:title)
        if not page_title:
             twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
             if twitter_title and twitter_title.get('content'):
                 page_title = twitter_title['content'].strip()

        # 4. Fallback: First H1 tag (less reliable but sometimes useful)
        # if not page_title:
        #     h1 = soup.find('h1')
        #     if h1 and h1.string:
        #         page_title = h1.string.strip()

        # Clean up the title (remove extra whitespace)
        if page_title:
            # Replace multiple whitespace characters (including newlines) with a single space
            title = ' '.join(page_title.split())
            if not title: # Handle case where title was only whitespace
                 title = "[No Title Found]"
        else:
            title = "[No Title Found]" # If no title could be extracted

        print(f"  Success: {url} -> {title[:50]}...", file=sys.stderr)

    except requests.exceptions.Timeout:
        title = "[Error: Timeout]"
        print(f"  Error: Timeout fetching {url}", file=sys.stderr)
    except requests.exceptions.RequestException as e:
        # Handles connection errors, invalid URLs, HTTP errors etc.
        title = f"[Error: {type(e).__name__}]" # More specific error type
        print(f"  Error fetching {url}: {e}", file=sys.stderr)
    except Exception as e:
        # Catch any other unexpected errors (e.g., parsing issues)
        title = "[Error: Processing Failed]"
        print(f"  An unexpected error occurred for {url}: {e}", file=sys.stderr)

    # Format the Markdown link using the final URL
    markdown_links.append(f"- [{title}]({final_url})")


print("\n--- Generated Markdown Links ---")
# Print the final list of markdown links
for link in markdown_links:
    print(link)