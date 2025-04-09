import re
import json
from pathlib import Path

def extract_urls_from_text(text):
    """Extract URLs from any text content, handling various formats."""
    # Pattern to match URLs in various formats
    url_pattern = r'https?://[^\s\'"<>)\]]+(?:\([^\s]+\)|[^\s\'"<>)\]]*)'
    
    # Find all URLs in the text
    urls = re.findall(url_pattern, text)
    
    # Clean up URLs
    cleaned_urls = []
    for url in urls:
        # Remove trailing punctuation and parentheses
        url = url.rstrip('.,!?;:"\')]')
        # Handle markdown links if present
        if '(' in url and ')' in url:
            url = url.split('(')[1].rstrip(')')
        cleaned_urls.append(url)
    
    return cleaned_urls

def process_text_file(file_path):
    """Process a text file and extract URLs."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract URLs
    urls = extract_urls_from_text(content)
    
    # Create output directory
    output_dir = Path('extracted_urls')
    output_dir.mkdir(exist_ok=True)
    
    # Save URLs to JSON
    output = {
        'source_file': file_path.name,
        'urls': urls,
        'count': len(urls)
    }
    
    output_file = output_dir / f'{file_path.stem}_urls.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    return urls

def main():
    # Test with sample text
    sample_text = """
    hey motherfucker 
    "https://www.reddit.com/r/JEENEETards/s/WwYnYRcAx6",
    "https://www.reddit.com/r/macapps/s/NNoDU3D3hC",
    "https://t3.chat/chat","https://1001albumsgenerator.com/","https://help.openai.com/en/articles/6825453-chatgpt-release-notes", https://www.youtube.com/watch?v=tELxjdWHByk,

    https://www.reddit.com/r/macapps/comments/1je84tz/mac_website_builder_blocs_61/

    https://www.youtube.com/watch?v=1cFonowsaUA&list=TLPQMzEwMzIwMjUZjXwDTVtBYA&index=4

    https://broflix.ci/watch/movie/1290938?title=South%20Park:%20The%20End%20of%20Obesity&imdb_id=tt32375562

    you are big asshole
    """
    
    # Extract URLs from sample text
    urls = extract_urls_from_text(sample_text)
    
    print("Extracted URLs:")
    for i, url in enumerate(urls, 1):
        print(f"{i}. {url}")
    
    # Save to file
    output_dir = Path('extracted_urls')
    output_dir.mkdir(exist_ok=True)
    
    output = {
        'source': 'sample_text',
        'urls': urls,
        'count': len(urls)
    }
    
    with open(output_dir / 'sample_urls.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nURLs saved to {output_dir}/sample_urls.json")

if __name__ == "__main__":
    main() 