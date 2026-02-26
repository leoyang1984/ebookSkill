import sys
import os
import subprocess
import shutil
import re
import argparse
import logging
from pathlib import Path

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def check_pandoc():
    """Checks if pandoc is installed and available in the PATH."""
    try:
        subprocess.run(["pandoc", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def slugify(text):
    """
    Simplifies text to be used in a safe filename or directory name.
    """
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text).strip()
    text = re.sub(r'[-\s]+', '_', text)
    return text

def convert_epub_to_md(epub_path, project_dir_name=None):
    """
    Creates a directory for the epub and runs pandoc to extract
    images and convert the epub to markdown in that directory.
    """
    epub_file = Path(epub_path)
    if not epub_file.exists():
        logging.error(f"File {epub_path} does not exist.")
        sys.exit(1)
        
    base_dir = epub_file.parent
    # Use slugified name for the project directory to ensure cross-platform compatibility
    folder_name = project_dir_name if project_dir_name else slugify(epub_file.stem)
    project_dir = base_dir / folder_name
    
    if project_dir.exists():
        logging.warning(f"Directory {project_dir} already exists. Overwriting content in 'full_content.md'.")
    else:
        project_dir.mkdir(parents=True, exist_ok=True)
    
    full_md_path = project_dir / "full_content.md"
    
    logging.info(f"Converting: {epub_file.name} to {project_dir.name}/full_content.md...")
    
    # Run Pandoc command: convert to GFM, extract media, prevent line wrapping
    cmd = [
        "pandoc", 
        str(epub_file.absolute()), 
        "-o", 
        "full_content.md", 
        "--extract-media=.", 
        "-t", 
        "gfm",
        "--wrap=none" 
    ]
    
    try:
        subprocess.run(cmd, cwd=str(project_dir), check=True, capture_output=True)
        logging.info("Pandoc conversion successful.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Pandoc conversion failed: {e.stderr.decode()}")
        sys.exit(1)
        
    return project_dir, full_md_path

def clean_content(content):
    """
    Removes residual HTML tags often left by EPUB-to-Markdown conversion.
    """
    # Remove spans, divs, and a tags but keep their inner content
    tags_to_strip = [r'<span[^>]*>', r'</span>', r'<div[^>]*>', r'</div>', r'<a href="[^"]*"[^>]*>', r'</a>']
    for tag in tags_to_strip:
        content = re.sub(tag, '', content, flags=re.IGNORECASE)
    
    # Optionally remove empty lines or repetitive whitespace here if needed
    return content

def split_markdown(project_dir, full_md_path, min_lines=200, max_lines=300, clean=True):
    """
    Splits a large markdown file into smaller, manageable chunks.
    """
    if not full_md_path.exists():
        logging.error(f"{full_md_path} not found.")
        return

    logging.info(f"Splitting content with limits: {min_lines}-{max_lines} lines per chunk.")

    with open(full_md_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if clean:
        content = clean_content(content)
        
    lines = content.splitlines(keepends=True)
        
    chapter_pattern = re.compile(r'^(#|##)\s+(.+)$')
    sub_header_pattern = re.compile(r'^(###|####|#####)\s+(.+)$')

    chapters = []
    current_chapter_title_prefix = "000_Intro"
    current_chapter_lines = []
    
    # Group into Chapters
    for line in lines:
        match = chapter_pattern.match(line)
        if match:
            if current_chapter_lines:
                chapters.append((current_chapter_title_prefix, current_chapter_lines))
            
            raw_title = match.group(2).strip()
            safe_title = slugify(raw_title)
            if not safe_title:
                safe_title = "Chapter"
                
            current_chapter_title_prefix = safe_title
            current_chapter_lines = [line]
        else:
            current_chapter_lines.append(line)
            
    if current_chapter_lines:
        chapters.append((current_chapter_title_prefix, current_chapter_lines))
        
    file_counter = 1
    
    for title_prefix, chapter_lines in chapters:
        total_lines = len(chapter_lines)
        
        if total_lines <= min_lines:
            save_chunk(project_dir, file_counter, title_prefix, chapter_lines)
            file_counter += 1
        else:
            current_chunk = []
            part_number = 1
            
            for line in chapter_lines:
                current_chunk.append(line)
                chunk_len = len(current_chunk)
                
                if chunk_len >= min_lines:
                    is_blank = line.strip() == ""
                    is_subheader = bool(sub_header_pattern.match(line))
                    
                    if (is_blank or is_subheader) or chunk_len >= max_lines:
                        # Logic to keep subheaders at the START of a new chunk
                        if is_subheader and chunk_len < max_lines:
                             popped_header = current_chunk.pop()
                             title = f"{title_prefix}_part_{part_number}"
                             save_chunk(project_dir, file_counter, title, current_chunk)
                             current_chunk = [popped_header]
                        else:
                             title = f"{title_prefix}_part_{part_number}"
                             save_chunk(project_dir, file_counter, title, current_chunk)
                             current_chunk = []
                             
                        part_number += 1
                        file_counter += 1
                        
            if current_chunk and any(l.strip() for l in current_chunk):
                title = f"{title_prefix}_part_{part_number}"
                save_chunk(project_dir, file_counter, title, current_chunk)
                file_counter += 1

    logging.info(f"Done! Created {file_counter - 1} files in '{project_dir.name}/'.")
    
def save_chunk(directory, counter, title, lines):
    # Using 03d to support books with hundreds of sections
    safe_title = title[:60]
    filename = f"{counter:03d}_{safe_title}.md"
    filepath = directory / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)
        
def main():
    parser = argparse.ArgumentParser(description="Convert EPUB to Markdown and split into AI-friendly chunks.")
    parser.add_argument("epub", help="Path to the source EPUB file.")
    parser.add_argument("--min", type=int, default=200, help="Minimum lines per chunk (default: 200).")
    parser.add_argument("--max", type=int, default=300, help="Maximum lines per chunk (default: 300).")
    parser.add_argument("--no-clean", action="store_false", dest="clean", help="Do not strip residual HTML tags.")
    parser.add_argument("--name", help="Custom folder name for the output.")
    
    args = parser.parse_args()

    if not check_pandoc():
        logging.error("Pandoc is not installed or not in your PATH. Please install it (e.g., 'brew install pandoc').")
        sys.exit(1)
        
    project_dir, full_md_path = convert_epub_to_md(args.epub, args.name)
    split_markdown(project_dir, full_md_path, args.min, args.max, args.clean)

if __name__ == "__main__":
    main()
