# ebookSkill: EPUB to Markdown Splitter & Translator

A specialized AI-Agent skill for converting EPUB ebooks into clean, well-structured, and intelligently split Markdown files, optimized for reading, knowledge management (Obsidian), and AI-driven translation workflows.

---

## 🚀 Overview

`ebookSkill` solves the problem of "monolithic" ebook conversions. Instead of one massive, unmanageable Markdown file, this tool:
1.  **Converts** EPUB to GitHub-Flavored Markdown using Pandoc.
2.  **Extracts** all images into a local folder with relative links.
3.  **Splits** the content intelligently by chapters (H1/H2) and manageable line counts (200-300 lines) to prevent context window exhaustion during AI processing.
4.  **Cleans** residual HTML tags (like `<span>`, `<div>`) often left behind by conversion tools.
5.  **Standardizes** an AI translation workflow for high-quality, chapter-by-chapter translation.

## 📂 Directory Structure

```text
ebookSkill/
├── SKILL.md                # AI-Agent instructions and workflow logic
├── README.md               # This file
└── scripts/
    ├── epub_to_md_splitter.py  # Core conversion and splitting engine
    └── clean_markdown.py       # HTML tag cleanup utility
```

## 🛠 Prerequisites

- **Pandoc**: Required for initial EPUB to MD conversion.
- **Python 3**: Required to run the processing scripts.

## 📖 Usage Guide

### 1. Basic Conversion & Splitting
Run the core script on any `.epub` file:
```bash
python scripts/epub_to_md_splitter.py /path/to/your/ebook.epub
```
**Output:** A new folder named after the book containing:
- `images/`: All extracted media.
- `01_Chapter_Name.md`, `02_Part_1.md`, etc.: The split content.
- `full_content.md`: The raw, un-split conversion.

### 2. Markdown Cleanup
If your Markdown files contain messy HTML tags:
```bash
python scripts/clean_markdown.py path/to/file.md
```

### 3. AI-Driven Translation Workflow
This skill defines a specific SOP for AI agents (like Claude or Gemini):
1.  **Delete** `full_content.md` to avoid accidental massive processing.
2.  **Generate** a `translation_prompt.txt` for domain-specific terminology.
3.  **Confirm** the prompt with the user.
4.  **Translate** split files sequentially into a `Translated/` folder.

## ⚙️ Splitting Logic
- **Primary Split**: Triggered by `#` or `##` headers.
- **Secondary Split**: Triggered if a section exceeds 200 lines. The script looks ahead for natural breaks (sub-headers or paragraph ends) between 200-300 lines to ensure structural integrity.

---

# ebookSkill: EPUB 转 Markdown 切分与翻译工具 (ZH)

这是一个专门为 AI Agent 设计的技能，用于将 EPUB 电子书转换为干净、结构化且智能切分的 Markdown 文件。针对阅读、知识管理（Obsidian）以及 AI 驱动的翻译工作流进行了深度优化。

## 🚀 概述

`ebookSkill` 解决了电子书转换中“大一统”文件的痛点。与其产出一个巨大且难以处理的 Markdown 文件，本工具可以：
1.  **转换**：使用 Pandoc 将 EPUB 转换为 GitHub 风格的 Markdown (GFM)。
2.  **提取**：将所有图片提取到本地文件夹，并保持相对链接。
3.  **切分**：按章节 (H1/H2) 和可控行数（200-300 行）智能切分内容，防止 AI 处理时超出上下文窗口。
4.  **清理**：清除转换工具常残留的 HTML 标签（如 `<span>`, `<div>`）。
5.  **标准化**：定义了 AI 翻译 SOP，实现高质量的逐章翻译。

## 📂 目录结构

```text
ebookSkill/
├── SKILL.md                # AI Agent 指令与工作流逻辑
├── README.md               # 本文件
└── scripts/
    ├── epub_to_md_splitter.py  # 核心转换与切分引擎
    └── clean_markdown.py       # HTML 标签清理工具
```

## 🛠 前置条件

- **Pandoc**：用于初始的 EPUB 到 MD 转换。
- **Python 3**：运行处理脚本所需。

## 📖 使用指南

### 1. 基础转换与切分
对任何 `.epub` 文件运行核心脚本：
```bash
python scripts/epub_to_md_splitter.py /path/to/your/ebook.epub
```
**产出**：一个以书名命名的文件夹，包含：
- `images/`：所有提取出的媒体文件。
- `01_Chapter_Name.md`, `02_Part_1.md` 等：切分后的内容。
- `full_content.md`：未切分的原始转换文件。

### 2. Markdown 清理
如果 Markdown 文件包含杂乱的 HTML 标签：
```bash
python scripts/clean_markdown.py path/to/file.md
```

### 3. AI 驱动的翻译工作流
本技能为 AI Agent（如 Claude 或 Gemini）定义了具体的 SOP：
1.  **删除** `full_content.md` 以避免意外触发海量数据处理。
2.  **生成** `translation_prompt.txt` 以设定领域特定术语。
3.  **确认** 提示词（Prompt）并由用户审核。
4.  **翻译** 将切分后的文件按顺序翻译至 `Translated/` 文件夹。

## ⚙️ 切分逻辑
- **一级切分**：由 `#` 或 `##` 标题触发。
- **二级切分**：如果某个章节超过 200 行，脚本会在 200-300 行之间寻找自然停顿点（如下级标题或段落结尾），以确保结构完整性。

---
*Part of the 2026 Career Data Warehouse Skill Arsenal / 隶属于 2026 Career Data Warehouse 技能武库。*
