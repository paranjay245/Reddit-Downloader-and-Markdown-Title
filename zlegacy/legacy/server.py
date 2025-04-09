from flask import Flask, render_template, request, jsonify
from test_titles import get_reddit_title, get_other_title
import re

app = Flask(__name__)

def extract_urls(text):
    # URL pattern that matches both Reddit and other URLs, excluding trailing commas
    url_pattern = r'https?://(?:www\.)?(?:reddit\.com|apps\.apple\.com|t3\.chat)[^\s<>",]+|https?://[^\s<>",]+'
    return re.findall(url_pattern, text)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_urls():
    text = request.form.get('urls', '')
    urls = extract_urls(text)
    
    results = []
    for url in urls:
        if 'reddit.com' in url:
            title = get_reddit_title(url)
        else:
            title = get_other_title(url)
        results.append({
            'title': title,
            'url': url,
            'markdown': f"[{title}]({url})"
        })
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5001) 