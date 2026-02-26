---
name: EPUB to Markdown Splitter
description: Converts EPUB files into GitHub-flavored Markdown, extracts images, and intelligently splits the content into chapters and manageable sections.
---

# EPUB to Markdown Splitter

This SKILL automatically converts an `.epub` ebook into GitHub-Flavored Markdown (GFM), extracts all the images into a local directory with relative links, and splits the resulting markdown file into chapters, ensuring each part stays within an optimal reading length (roughly 200-300 lines).

## Prerequisites

- **Pandoc**: Must be installed on your system.
- **Python 3**: Requires Python 3 to run the splitting script.

## Directory Structure
```
ebookSkill/
├── SKILL.md
└── scripts/
    ├── clean_markdown.py
    └── epub_to_md_splitter.py
```

## How to Use

### 1. Convert and Split EPUB
1. Place your target `.epub` file in any directory.
2. Run the provided Python script, passing the path to your EPUB file as the argument:
   ```bash
   python /Volumes/外部硬盘/agent-skills/2026_Career_Data_Warehouse/ebookSkill/scripts/epub_to_md_splitter.py /path/to/your/input.epub
   ```

#### What Happens
1. **Folder Creation**: The script creates a new folder named after your EPUB file (without the extension) in the same directory as the EPUB.
2. **Pandoc Conversion & Image Extraction**: It runs `pandoc` inside this new folder to convert the EPUB to `full_content.md` while extracting all media to an `images/` subfolder.
3. **Intelligent Splitting**: 
   - It parses `full_content.md` and splits it first by main headings (`#` or `##`).
   - If a chapter exceeds 200 lines, it further splits it, trying to find natural breaks (like `###` subheadings or paragraphs) between 200-300 lines to keep related sections together.
   - The final parts are saved as numbered markdown files (e.g., `01_Chapter_Name.md`, `02_Part_1.md`).

### 2. Translate Markdown (Agent Workflow)
If you want the AI agent (e.g., Claude Code) to translate the split markdown files into Chinese, instruct the agent to follow these steps strictly:

**Agent Instructions for Translation:**
1. **Cleanup (`full_content.md`)**: The agent **MUST FIRST** locate and **DELETE** the `full_content.md` file in the project folder. *Do not ever attempt to translate the entire `full_content.md` file.*
2. **Setup Subdirectory**: Create a `Translated/` subdirectory inside the project folder.
3. **Draft Translation Logic**: The agent must create a `translation_prompt.txt` file in the project directory, setting up the translation rules. The rules should include:
   - Preserving all Markdown formatting, image paths, and tags.
   - Using terminology suitable for the book's specific domain (e.g., AI and Economics).
   - Keeping specific proper nouns or core jargon (e.g., "Deep Learning") in English or providing the English in parentheses.
   - Adopting a professional, native Chinese expression style.
4. **User Confirmation**: The agent **MUST PAUSE** here and ask the user to review, edit, and confirm the `translation_prompt.txt` file. Do not start translating until the user confirms the logic.
5. **Iterative Translation**: Once the user approves the prompt, the agent will begin reading each `0x_xxx.md` file one by one sequentially, translating the content according to the prompt's rules, and saving the output to the exactly named file in the `Translated/` directory.

### 3. Manual Cleanup (Optional)
If you find that some markdown files (such as the generated `full_content.md` or other manually edited files) still contain residual HTML tags from the EPUB (like `<span>` or `<div>`), you can use the standalone cleanup script:

```bash
python /Volumes/外部硬盘/agent-skills/2026_Career_Data_Warehouse/ebookSkill/scripts/clean_markdown.py /path/to/your/markdown_file.md
```
This script will overwrite the original markdown file with a cleaned version.

## Splitting Rules Explained
- **Rule 1 (By Chapter)**: Primary splitting occurs at Level 1 (`#`) or Level 2 (`##`) headers.
- **Rule 2 & 3 (Line Count & Sub-sections)**: If a delineated chapter is over 200 lines long, the script accumulates lines up to 200. It then looks ahead (up to around 300 lines) for a suitable breaking point, prioritizing lower-level headers (`###`, `####`) or at least a blank line separating paragraphs, so that sections aren't abruptly cut halfway.
