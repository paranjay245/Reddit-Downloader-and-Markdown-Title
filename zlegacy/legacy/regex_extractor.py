import re
import json
from pathlib import Path

def extract_regex_patterns(file_path):
    """Extract regex patterns from a Python file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find all regex patterns in the code
    patterns = []
    
    # Look for re.match, re.search, and re.compile patterns
    regex_patterns = re.finditer(r're\.(?:match|search|compile)\(r?[\'"]([^\'"]+)[\'"]', content)
    for match in regex_patterns:
        patterns.append({
            'pattern': match.group(1),
            'type': 're.match/search/compile',
            'file': file_path.name,
            'purpose': 'Regex pattern using re module'
        })
    
    # Look for string.match patterns
    string_patterns = re.finditer(r'\.match\([\'"]([^\'"]+)[\'"]', content)
    for match in string_patterns:
        patterns.append({
            'pattern': match.group(1),
            'type': 'string.match',
            'file': file_path.name,
            'purpose': 'String match pattern'
        })
    
    # Look for URL patterns in strings
    url_patterns = re.finditer(r'[\'"]https?://[^\'"]+[\'"]', content)
    for match in url_patterns:
        url = match.group(0).strip('\'"')
        if not any(p['pattern'] == url for p in patterns):  # Avoid duplicates
            patterns.append({
                'pattern': url,
                'type': 'url',
                'file': file_path.name,
                'purpose': 'URL pattern found in code'
            })
    
    # Look for common patterns like file extensions, domains, etc.
    common_patterns = [
        (r'\.([a-zA-Z0-9]+)\'', 'file_extension'),
        (r'www\.([a-zA-Z0-9.-]+)', 'domain'),
        (r'content-type[\'"]:\s*[\'"]([^\'"]+)', 'content_type')
    ]
    
    for pattern, pattern_type in common_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            patterns.append({
                'pattern': match.group(0),
                'type': pattern_type,
                'file': file_path.name,
                'purpose': f'Common {pattern_type} pattern'
            })
    
    return patterns

def save_patterns(patterns, output_file):
    """Save patterns to a JSON file."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(patterns, f, indent=2, ensure_ascii=False)

def main():
    # Create output directory if it doesn't exist
    output_dir = Path('regex_patterns')
    output_dir.mkdir(exist_ok=True)
    
    # Files to analyze
    files_to_analyze = [
        'reddit links.py',
        'other links.py'
    ]
    
    all_patterns = []
    
    # Extract patterns from each file
    for file_name in files_to_analyze:
        file_path = Path(file_name)
        if file_path.exists():
            patterns = extract_regex_patterns(file_path)
            all_patterns.extend(patterns)
            print(f"\nFound {len(patterns)} patterns in {file_name}")
    
    # Save all patterns
    save_patterns(all_patterns, output_dir / 'all_patterns.json')
    
    # Save patterns by type
    patterns_by_type = {}
    for pattern in all_patterns:
        pattern_type = pattern['type']
        if pattern_type not in patterns_by_type:
            patterns_by_type[pattern_type] = []
        patterns_by_type[pattern_type].append(pattern)
    
    for pattern_type, patterns in patterns_by_type.items():
        # Create a safe filename from the pattern type
        safe_filename = pattern_type.replace('.', '_').replace('/', '_')
        save_patterns(patterns, output_dir / f'{safe_filename}_patterns.json')
    
    # Print summary
    print(f"\nExtracted {len(all_patterns)} total patterns:")
    for pattern_type, patterns in patterns_by_type.items():
        print(f"- {pattern_type}: {len(patterns)} patterns")
    
    print(f"\nPatterns saved in {output_dir}/")
    print("\nPattern files created:")
    for pattern_file in output_dir.glob('*.json'):
        print(f"- {pattern_file.name}")

if __name__ == "__main__":
    main() 