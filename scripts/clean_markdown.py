import sys
import os
import re

def clean_markdown_file(filepath):
    """
    Reads a markdown file, cleans up unnecessary HTML tags (spans, divs, links),
    and overwrites the file with the cleaned content.
    """
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return

    print(f"Cleaning HTML tags from: {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Clean up EPUB leftover HTML tags
    # Remove <span ...> and </span>
    content = re.sub(r'<span[^>]*>', '', content)
    content = re.sub(r'</span>', '', content)
    
    # Remove <div ...> and </div>
    content = re.sub(r'<div[^>]*>', '', content)
    content = re.sub(r'</div>', '', content)
    
    # Remove <a href="..."> and </a>
    content = re.sub(r'<a href="[^"]*"[^>]*>', '', content)
    content = re.sub(r'</a>', '', content)
    
    # Overwrite the original file with cleaned content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Successfully cleaned: {filepath}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python clean_markdown.py <path_to_markdown_file>")
        sys.exit(1)
        
    filepath = sys.argv[1]
    clean_markdown_file(filepath)

if __name__ == "__main__":
    main()
