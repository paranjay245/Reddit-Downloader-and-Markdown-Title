from flask import Flask, render_template, request, jsonify
import re
from pathlib import Path

app = Flask(__name__)

def extract_urls_from_text(text):
    """Extract URLs from text using regex pattern."""
    url_pattern = r'https?://[^\s\'"<>)\]]+(?:\([^\s]+\)|[^\s\'"<>)\]]*)'
    urls = re.findall(url_pattern, text)
    
    # Clean up URLs by removing trailing punctuation
    cleaned_urls = []
    for url in urls:
        # Remove trailing punctuation
        url = re.sub(r'[.,;:!?]$', '', url)
        # Remove markdown link if present
        url = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\2', url)
        cleaned_urls.append(url)
    
    return cleaned_urls

def extract_regex_patterns(text):
    """Extract regex patterns from text."""
    patterns = []
    
    # Find regex patterns in the text
    regex_patterns = re.findall(r're\.(?:match|search|compile)\([\'"]([^\'"]+)[\'"]\)', text)
    for pattern in regex_patterns:
        patterns.append({
            'pattern': pattern,
            'type': 're.match/search/compile',
            'purpose': 'Regex pattern found in code'
        })
    
    # Find URL patterns
    url_patterns = re.findall(r'[\'"]https?://[^\'"]+[\'"]', text)
    for pattern in url_patterns:
        patterns.append({
            'pattern': pattern.strip('"\''),
            'type': 'URL pattern',
            'purpose': 'URL pattern found in code'
        })
    
    # Find domain patterns
    domain_patterns = re.findall(r'[\'"]www\.[^\'"]+[\'"]', text)
    for pattern in domain_patterns:
        patterns.append({
            'pattern': pattern.strip('"\''),
            'type': 'Domain pattern',
            'purpose': 'Domain pattern found in code'
        })
    
    return patterns

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    text = request.form.get('text', '')
    
    # Extract URLs and patterns
    urls = extract_urls_from_text(text)
    patterns = extract_regex_patterns(text)
    
    return jsonify({
        'urls': urls,
        'patterns': patterns
    })

if __name__ == '__main__':
    app.run(debug=True) 