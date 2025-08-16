# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a TXT to EPUB conversion tool written in Python with both command-line and GUI interfaces. The tool automatically detects chapter structures in Chinese/English texts and converts them to properly formatted EPUB ebooks.

## Project Structure

```
txt2epub/
├── txt2epub.py          # Command-line interface main program
├── txt2epub_gui.py      # GUI interface using tkinter
├── utils/
│   ├── txt_reader.py    # TXT file reading and processing
│   ├── epub_builder.py  # EPUB construction
│   └── logger.py        # Logging utilities
├── build_exe.py         # PyInstaller packaging script
└── pyproject.toml       # Project dependencies and metadata
```

## Key Architecture Components

### Core Modules

1. **txt_reader.py**: Handles TXT file reading with automatic encoding detection (using charset-normalizer) and chapter splitting using regex patterns. The `read_txt` function identifies chapters and returns structured content.

2. **epub_builder.py**: Uses ebooklib to construct EPUB files with proper formatting, CSS styling, and chapter organization. Includes responsive design and dark mode support.

3. **txt2epub.py**: Command-line interface that parses arguments and orchestrates the conversion process.

4. **txt2epub_gui.py**: GUI interface built with tkinter featuring high DPI support, cover preview, and integrated logging.

### Key Features

- Automatic chapter detection (Chinese "第X章" and English "Chapter X" patterns)
- Encoding detection and handling
- Cover image support with preview
- Responsive CSS styling for EPUB output
- Both CLI and GUI interfaces
- PyInstaller packaging support

## Development Commands

### Install dependencies
```bash
uv sync
```

### Run command-line version
```bash
python txt2epub.py input.txt
python txt2epub.py input.txt output.epub
python txt2epub.py input.txt -t "Title" -a "Author" -c cover.jpg
```

### Run GUI version
```bash
uv run txt2epub_gui.py
```

### Build executable
```bash
uv run build_exe.py
```

### Run tests
```bash
# No specific test command found, but would typically be:
python -m pytest  # if pytest were configured
```

## Dependencies

- ebooklib: EPUB file processing
- charset-normalizer: Character encoding detection
- pillow: Image processing for cover preview
- PyInstaller: Executable packaging

Entry points are defined in pyproject.toml for both CLI and GUI versions.