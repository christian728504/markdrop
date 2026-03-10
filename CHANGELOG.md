# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 24-12-2024
### Added
- Initial release
- PDF to Markdown conversion
- Image extraction functionality
- Table detection using Table Transformer
- Progress tracking with tqdm


## [0.1.1] - 24-12-2024
### Added
- Fix dependency issue. (Added `timm` in `requirements.txt`).

## [0.1.2] - 25-12-2024
### Added
- PDF URL support for pdf to md, images and table extraction.
  
## [0.2.0], [0.2.1] and [0.2.2] - 26-12-2024 - Major Update
### Added
-  Fix downloading pdfs from urls (in `make_markdown`).
-  Added facility to analyze different types of image references (`XRef Id`)in a PDF from local file or URL
-  Now, package supports genration of textual descriptions of image(s).
-  ['qwen', 'gemini', 'openai', 'llama-vision', 'molmo', 'pixtral'] LLM Clients are supported for this conversion

## [0.2.3] to [0.2.7] - 27-12-2024
### Added
-  Fix `img_path` in `responder.py`
-  Optimised `setup_keys` function
-  Enhance and modified `analyze_pdf_images` function

## [0.3.0] - 30-01-2025
### Added
-  End-to-End pdf to markdown
-  End-to-End pdf to html
-  Generate descriptions of images and tables on the fly in a single traversal
-  Added `Download table(s) as Excel` functionality

## [0.3.1] - 30-01-2025
### Added
-  Fix import issue of `Fitz` package

## [0.3.1.1] - 30-01-2025
### Added
-  Fix MarkDropConfig
## [0.3.1.2] - 30-01-2025
### Added
-  Removed conflicts in apikeys setup

## [0.3.4] - 05-07-2025
### Changed
- Deprecated `make_markdown`, `extract_images`, and `extract_tables_from_pdf` functions.
- Improved requirements for better installations.
- Fixed image path error in Gemini description generations.

## [0.4.0] - 10-03-2026
### Added
- Anthropic, Groq, OpenRouter, and LiteLLM provider support.
- CLI arguments `--model` and `--text-model` to dynamically override models.
- Support for `[extras]` installation variants (`markdrop[anthropic]`, etc.).

### Changed
- Updated default models to March 2026 flagship/stable versions (`gpt-5.4`, `gemini-3.1-flash-lite`, `claude-opus-4-6`, `meta-llama/llama-4-maverick`).
- Switched default `GOOGLE_API_KEY` to `GEMINI_API_KEY` standard.
- Removed hardcoded module-level variables (e.g. `input_doc_path`) and dead blocks to allow clean importing.
- Changed default encoding logic for image uploads.

### Fixed
- SSRF Vulnerability: Prevented `download_pdf` from hitting private/local IPs.
- Path Traversal: Secured local file reading in `replace_image`.
- DoS Risk: Added 30s timeout and 200MB size limit for PDF downloads.
- Temp File Race Conditions: Enforced secure `tempfile.NamedTemporaryFile` usage.
- File Permissions: Secured auto-generated `.env` files with strict Unix permissions.
- Mutable default arguments in `img_descriptions.py`.