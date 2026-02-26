import sys
import os
import subprocess
import shutil
import re
from pathlib import Path

def convert_epub_to_md(epub_path):
    """
    Creates a directory for the epub and runs pandoc to extract
    images and convert the epub to markdown in that directory.
    Returns the path to the newly created directory and the generated markdown file.
    """
    # 1. Prepare directory
    epub_file = Path(epub_path)
    if not epub_file.exists():
        print(f"Error: File {epub_path} does not exist.")
        sys.exit(1)
        
    base_dir = epub_file.parent
    project_name = epub_file.stem
    project_dir = base_dir / project_name
    
    if project_dir.exists():
        print(f"Warning: Directory {project_dir} already exists. Might overwrite contents.")
    else:
        project_dir.mkdir(parents=True, exist_ok=True)
    
    # Target full markdown file
    full_md_path = project_dir / "full_content.md"
    
    print(f"Running pandoc conversion for: {epub_file.name}...")
    # 2. Run Pandoc command
    # pandoc input.epub -o output.md --extract-media=images -t gfm
    cmd = [
        "pandoc", 
        str(epub_file.absolute()), 
        "-o", 
        "full_content.md", 
        "--extract-media=.", 
        "-t", 
        "gfm",
        "--wrap=none" # Prevent pandoc from hard-wrapping text to 80 chars
    ]
    
    # Run the command from within the new project directory
    # so that paths to extracted media are inherently relative
    try:
        subprocess.run(cmd, cwd=str(project_dir), check=True)
        print("Pandoc conversion successful. Extracting media and creating full_content.md.")
    except subprocess.CalledProcessError as e:
        print(f"Pandoc conversion failed: {e}")
        sys.exit(1)
        
    return project_dir, full_md_path

def split_markdown(project_dir, full_md_path):
    """
    Reads the full markdown file, cleans up unnecessary HTML tags (spans, divs, links),
    and splits it into multiple smaller markdown files
    in the project directory, respecting chapters and line limits (200-300 lines).
    """
    if not full_md_path.exists():
        print(f"Error: {full_md_path} not found for splitting.")
        return

    with open(full_md_path, 'r', encoding='utf-8') as f:
        # Read the entire file as a single string to perform global regex substitutions
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
    
    # Pandoc sometimes escapes underscores and brackets, optionally clean those too
    
    # Split back into lines, keeping the newline character at the end of each line
    lines = content.splitlines(keepends=True)
        
    # Regex to catch top level headers for Chapter breaks
    chapter_pattern = re.compile(r'^(#|##)\s+(.+)$')
    # Regex for lower level subheaders
    sub_header_pattern = re.compile(r'^(###|####|#####)\s+(.+)$')

    chapters = []
    current_chapter_title_prefix = "00_Intro"
    current_chapter_lines = []
    
    # 1. Group into coarse Chapters first
    for i, line in enumerate(lines):
        match = chapter_pattern.match(line)
        if match:
            # We found a new chapter
            if current_chapter_lines:
                chapters.append((current_chapter_title_prefix, current_chapter_lines))
            
            # Clean up the title for the filename
            raw_title = match.group(2).strip()
            safe_title = re.sub(r'[^\w\s-]', '', raw_title).strip().replace(' ', '_')
            if not safe_title:
                safe_title = "Chapter"
                
            current_chapter_title_prefix = safe_title
            current_chapter_lines = [line]
        else:
            current_chapter_lines.append(line)
            
    # Add the last chapter
    if current_chapter_lines:
        chapters.append((current_chapter_title_prefix, current_chapter_lines))
        
    file_counter = 1
    
    # 2. Process each chapter and apply line count rules
    for current_chapter_title_prefix, current_chapter_lines in chapters:
        total_lines = len(current_chapter_lines)
        
        if total_lines <= 200:
            # Short enough, save as is
            save_chunk(project_dir, file_counter, current_chapter_title_prefix, current_chapter_lines)
            file_counter += 1
        else:
            # Chunk it up
            current_chunk = []
            part_number = 1
            
            for line in current_chapter_lines:
                current_chunk.append(line)
                chunk_len = len(current_chunk)
                
                # Rule 2 & 3: If > 200 lines, look for boundaries between 200-300 lines
                if chunk_len >= 200:
                    # Is this a good breaking point? (Blank line or a subheader)
                    is_blank = line.strip() == ""
                    is_subheader = bool(sub_header_pattern.match(line))
                    
                    if (is_blank or is_subheader) or chunk_len >= 300:
                        # Time to break
                        # If the current line is a subheader, we should probably start the NEW chunk with it,
                        # so pop it from current and put it back in the next.
                        if is_subheader and chunk_len < 300:
                             popped_header = current_chunk.pop()
                             
                             title = f"{current_chapter_title_prefix}_Part_{part_number}"
                             save_chunk(project_dir, file_counter, title, current_chunk)
                             
                             current_chunk = [popped_header]
                        else:
                             title = f"{current_chapter_title_prefix}_Part_{part_number}"
                             save_chunk(project_dir, file_counter, title, current_chunk)
                             current_chunk = []
                             
                        part_number += 1
                        file_counter += 1
                        
            # Save any remaining lines
            if current_chunk:
                # If the remaining chunk is just whitespace, ignore it
                if any(l.strip() for l in current_chunk):
                     title = f"{current_chapter_title_prefix}_Part_{part_number}"
                     save_chunk(project_dir, file_counter, title, current_chunk)
                     file_counter += 1

    print(f"Splitting complete. Created {file_counter - 1} sections in {project_dir.name}/")
    
def save_chunk(directory, counter, title, lines):
    """
    Helper to save a list of lines to a numbered markdown file.
    """
    # Ensure title is safe and not too long
    safe_title = title[:50]
    filename = f"{counter:02d}_{safe_title}.md"
    filepath = directory / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)
        
def main():
    if len(sys.argv) < 2:
        print("Usage: python epub_to_md_splitter.py <path_to_epub_file>")
        sys.exit(1)
        
    epub_file = sys.argv[1]
    project_dir, full_md_path = convert_epub_to_md(epub_file)
    split_markdown(project_dir, full_md_path)

if __name__ == "__main__":
    main()
