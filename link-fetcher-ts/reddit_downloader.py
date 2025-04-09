# --- START OF FILE reddit_downloader.py ---

import praw
import praw.exceptions  # For InvalidURL
# Import exceptions from prawcore
from prawcore.exceptions import ResponseException, Redirect
import os
import re
import time
from datetime import datetime

# --- Configuration ---
# --- !! These credentials are confirmed working - DO NOT CHANGE !! ---
REDDIT_CLIENT_ID = "iqjfQIUm4gchkwwfNsXeVg"
REDDIT_CLIENT_SECRET = "o57GfRTWUf8L2L8EL2bOjAWj5YXQnw"
REDDIT_USER_AGENT = "python:my_post_downloader:v1.0 (by /u/TomorrowToDoer)"
# --- !! --------------------------------------------------------- !! ---

# --- Settings ---
DOWNLOAD_COMMENTS = True
MAX_COMMENT_DEPTH = 5
COMMENT_REPLACE_LIMIT = 20 # Set to 0 or None to fetch more, but can be slow/rate-limited
OUTPUT_DIR = "reddit_downloads"
DELAY_BETWEEN_POSTS = 2

# --- Helper Function ---
def sanitize_filename(text):
    """Removes characters invalid for filenames."""
    sanitized = re.sub(r'[\\/*?:"<>|]', "", text)
    sanitized = re.sub(r'\s+', '_', sanitized)
    return sanitized[:100].strip('_')

# ==============================================================================
# == Comment Formatting Function (Unchanged) ===================================
# ==============================================================================
def format_comment(comment, level=0):
    """Formats a single comment and its replies recursively for Markdown."""
    if not isinstance(comment, praw.models.Comment) or not hasattr(comment, 'body') or not comment.body:
         if isinstance(comment, praw.models.MoreComments):
             return ""
         return ""

    indent = ">" * (level + 1) + " "
    author = f"u/{comment.author.name}" if comment.author else "[deleted]"
    score_val = comment.score if hasattr(comment, 'score') and comment.score is not None else 0
    score = f"{score_val} points"
    created_time = datetime.utcfromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    permalink = f"https://www.reddit.com{comment.permalink}"

    formatted = f"{indent}{author} ({score}) - {created_time} - [link]({permalink})\n"
    body_lines = comment.body.strip().split('\n')
    formatted += "\n".join([f"{indent}{line}" for line in body_lines])
    formatted += f"\n{indent}\n"

    if hasattr(comment, 'replies') and (MAX_COMMENT_DEPTH is None or level + 1 < MAX_COMMENT_DEPTH):
        try:
            comment.replies.replace_more(limit=0)
            for reply in comment.replies:
                if isinstance(reply, (praw.models.Comment, praw.models.MoreComments)):
                    formatted += format_comment(reply, level + 1)
        except Exception as reply_e:
             print(f"  Warning: Error processing replies for comment {comment.id}: {reply_e}")
             formatted += f"{indent}> [Error fetching replies]\n"
    return formatted

# ==============================================================================
# == Main Post Downloading Function (Body Logic Updated) =======================
# ==============================================================================
def download_reddit_post(reddit, url, download_comments=True):
    """Downloads a single Reddit post and optionally its comments."""
    print(f"Processing URL: {url}")
    filepath = ""
    try:
        submission = reddit.submission(url=url)

        # --- Access attributes to trigger loading ---
        title = submission.title
        author = f"u/{submission.author.name}" if submission.author else "[deleted]"
        subreddit_name = submission.subreddit.display_name
        subreddit_prefixed = f"r/{subreddit_name}"
        score = submission.score
        created_time = datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        post_id = submission.id
        permalink = f"https://www.reddit.com{submission.permalink}"
        is_self = submission.is_self
        # --- Fetch URL and Selftext regardless of post type ---
        link_url = submission.url
        selftext = submission.selftext
        # -----------------------------------------------------

        # --- Create Markdown Content ---
        markdown_content = f"# {title}\n\n"
        markdown_content += f"**Subreddit:** {subreddit_prefixed}\n"
        markdown_content += f"**Author:** {author}\n"
        markdown_content += f"**Score:** {score}\n"
        markdown_content += f"**Created:** {created_time}\n"
        markdown_content += f"**Post ID:** {post_id}\n"
        markdown_content += f"**Permalink:** [{permalink}]({permalink})\n\n"
        markdown_content += "---\n\n" # Separator after metadata

        # --- *** UPDATED Post Body Logic *** ---
        # Handle Link posts (non-self posts) first
        if not is_self:
            markdown_content += f"## Link Post\n\n"
            markdown_content += f"**URL:** [{link_url}]({link_url})\n\n"
            # Add a separator if there's *also* text content
            if selftext:
                markdown_content += "---\n\n"

        # Handle Self Text (present in both self posts AND potentially link posts)
        if selftext:
            markdown_content += f"## Post Text\n\n"
            markdown_content += f"{selftext}\n\n"
        # Handle edge case: A true self post that somehow has NO text
        elif is_self and not selftext:
             markdown_content += f"## Post Text\n\n"
             markdown_content += "*No self text.*\n\n"
        # --- *** End of UPDATED Post Body Logic *** ---


        # --- Comments (Unchanged) ---
        if download_comments:
            markdown_content += "---\n\n## Comments\n\n"
            print(f"  Fetching comments for post {post_id} (limit={COMMENT_REPLACE_LIMIT}, depth={MAX_COMMENT_DEPTH})...")
            try:
                submission.comments.replace_more(limit=COMMENT_REPLACE_LIMIT)
                comment_count = 0
                print("  Starting comment formatting loop...")
                for top_level_comment in submission.comments.list():
                    formatted_comment = format_comment(top_level_comment, level=0)
                    if formatted_comment:
                         markdown_content += formatted_comment
                         if isinstance(top_level_comment, praw.models.Comment):
                              comment_count += 1
                    elif isinstance(top_level_comment, praw.models.MoreComments):
                         markdown_content += f"> [More comments available - limit: {COMMENT_REPLACE_LIMIT} reached?]\n\n"
                print(f"  Finished formatting loop. Formatted {comment_count} top-level comment threads.")

                if not submission.comments.list():
                     markdown_content += "*No comments found.*\n"
                elif comment_count == 0:
                     markdown_content += "*No displayable comments found (may be deleted or only 'more comments' links).*\n"

            except Exception as comment_e:
                print(f"  ERROR during comment processing for {post_id}: {type(comment_e).__name__} - {comment_e}")
                markdown_content += f"\n\n---\n*ERROR during comment processing: {type(comment_e).__name__} - {comment_e}*\n---\n"
        else:
            markdown_content += "---\n\n*Comments were not downloaded.*\n"

        # --- Save to File (Unchanged) ---
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        safe_subreddit = subreddit_prefixed.replace('/', '_')
        safe_title = sanitize_filename(title)
        filename = f"{safe_subreddit}_{post_id}_{safe_title}.md"
        filepath = os.path.join(OUTPUT_DIR, filename)

        print(f"  Attempting to save to: {filepath}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"  Successfully saved post to: {filepath}")
        return True # Indicate success

    # --- General Exception Handling (Unchanged) ---
    except praw.exceptions.InvalidURL:
        print(f"  Error: Invalid Reddit URL: {url}")
    except ResponseException as e:
        status_code = getattr(getattr(e, 'response', None), 'status_code', 'N/A')
        print(f"  Error: API Response Error ({status_code}): {e} for URL: {url}")
        if status_code == 404: print("  -> Post or Subreddit Not Found.")
        elif status_code == 403: print("  -> Access Forbidden (Private Subreddit?).")
        elif status_code == 401: print(f"  >> CRITICAL: Unauthorized. Check CLIENT_ID/SECRET. <<")
    except Redirect as e:
         print(f"  Error: URL redirected to {e.path}, cannot process automatically: {url}")
    except AttributeError as ae:
        print(f"  Error: Could not access expected data for URL {url}. Details: {ae}")
    except FileNotFoundError as fnfe:
        print(f"  Error saving file: {fnfe}")
        print(f"  >> Check path/filename: {filepath}")
    except OSError as ose:
        print(f"  Error saving file (OS Error): {ose}")
        print(f"  >> Check permissions/path: {filepath}")
    except Exception as e:
        print(f"  An unexpected error occurred for URL {url}: {type(e).__name__} - {e}")

    return False # Return False if any exception caused failure

# --- Script Execution ---
if __name__ == "__main__":

    # --- Optional Diagnostic Print ---
    # print(f"DEBUG: Using Client ID starting with: {REDDIT_CLIENT_ID[:5]}...")
    # print(f"DEBUG: Using Client Secret starting with: {REDDIT_CLIENT_SECRET[:5]}...")

    # --- URL List including the new text post ---
    urls_to_download = [
        "https://www.reddit.com/r/macapps/comments/1jea4ua/my_list_of_macos_apps_because_people_love_these/", # New Text Post
        "https://www.reddit.com/r/JEENEETards/s/WwYnYRcAx6", # Hug your friends (Text Post)
        "https://www.reddit.com/r/macgaming/comments/1jjplh5/my_games_library_in_launchpad_as_of_march_2025/", # My Games Library (Gallery Link + Text)
        "https://www.reddit.com/r/NSFW_Caption/comments/1b0t5y1/thought_it_was_time/", # Thought it was time (Image Link)
        "https://www.reddit.com/r/starsector/comments/1asvgrp/played_starsector_and_kept_running_out_of/", # Played starsector (Image Link)
        "https://t3.chat/chat" # Non-reddit URL
    ]
    # --- ------------------------------------------- ---


    reddit = None
    try:
        # Initialization (Unchanged)
        if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET or not REDDIT_USER_AGENT:
             raise ValueError("Reddit API credentials or User Agent are empty.")

        print("Initializing Reddit connection...")
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT,
        )
        print(f"Attempting to authenticate using User Agent: '{reddit.config.user_agent}'")
        _ = reddit.user.me()
        print("Reddit connection object created. Initial authentication check passed (or deferred to first request).")

    # Initialization exception handling (Unchanged)
    except ValueError as ve: print(f"Configuration Error: {ve}"); exit(1)
    except ResponseException as e:
         status_code = getattr(getattr(e, 'response', None), 'status_code', 'N/A')
         print(f"Error initializing PRAW (API Response Error: {status_code}): {e}")
         if status_code == 401: print(">> CRITICAL: Authentication failed! Check CLIENT_ID/SECRET. <<")
         print("Please check credentials and network."); exit(1)
    except Exception as e: print(f"Error initializing PRAW: {type(e).__name__} - {e}"); exit(1)


    if reddit is None: print("Reddit connection could not be established."); exit(1)

    # --- Process URLs (Unchanged structure) ---
    print(f"\nStarting download process... Output directory: '{OUTPUT_DIR}'")
    print(f"Download comments: {DOWNLOAD_COMMENTS}")
    if DOWNLOAD_COMMENTS: print(f"Comment depth limit: {MAX_COMMENT_DEPTH}, Replace more limit: {COMMENT_REPLACE_LIMIT}")

    successful_downloads = 0; failed_downloads = 0
    total_reddit_urls = sum(1 for u in urls_to_download if "reddit.com" in u) # Pre-calculate count

    for i, url in enumerate(urls_to_download):
        print(f"\n--- Processing URL {i+1}/{len(urls_to_download)}: {url} ---")
        if "reddit.com" in url:
            if download_reddit_post(reddit, url, download_comments=DOWNLOAD_COMMENTS):
                successful_downloads += 1
                print(f"--- RESULT: Success for {url} ---")
            else:
                failed_downloads += 1
                print(f"--- RESULT: Failed/Skipped for {url} ---")
        else:
            print(f"Skipping non-Reddit URL: {url}")

        if i < len(urls_to_download) - 1: print(f"  Waiting {DELAY_BETWEEN_POSTS} seconds..."); time.sleep(DELAY_BETWEEN_POSTS)

    # Summary (Unchanged)
    print("\n--- Download Summary ---")
    print(f"Successfully downloaded: {successful_downloads}")
    print(f"Failed/Skipped Downloads: {failed_downloads}")
    print(f"Total Reddit URLs attempted:  {total_reddit_urls}") # Use pre-calculated count
    print(f"Downloads saved in directory: '{os.path.abspath(OUTPUT_DIR)}'")

# --- END OF FILE reddit_downloader.py ---