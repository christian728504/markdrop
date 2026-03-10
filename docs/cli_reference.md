# Command Line Interface (CLI)

The Markdrop CLI is accessed using the `markdrop` prefix.

## 1. `convert`
The entry-point for turning PDFs into digital mediums.

```bash
markdrop convert [FILE_OR_URL] --output_dir [DIR] [--add_tables]
```
* **`[FILE_OR_URL]`**: Can be an absolute path, relative path, or `https://` secure link. SSRF blocks are in place to ensure local IP ranges aren't targeted by malicious documents.
* **`--output_dir`**: The destination directory for the generated `.md`, `.html`, and an `/images/` subfolder.
* **`--add_tables`**: Forces the parser to evaluate and embed interactive downloadable Excel workbooks of tables into the `.html` visualization.

## 2. `describe`
Triggers Markdrop's internal AI processor asynchronously parse your Markdown text, reading standard `![alt](image_path)` syntaxes and running inference over the local assets.

```bash
markdrop describe [MARKDOWN_FILE] \
    --ai_provider [PROVIDER] \
    [--remove_images] [--remove_tables] \
    [--model] [--text-model]
```
* **`[MARKDOWN_FILE]`**: The Markdown file produced by `convert`.
* **`--ai_provider`**: One of `gemini`, `openai`, `anthropic`, `groq`, `openrouter`, or `litellm`.
* **`--remove_images`**: Strips the raw visual elements completely from the Markdown, replacing the space entirely with the generated semantic AI text description. Great for raw ML training data ingestion.
* **`--model`**: Overrides the vision model parsing the images.
* **`--text-model`**: Overrides the text model parsing the markdown tables.

## 3. `setup`
Writes API Keys permanently into a secure `<root>/.env` file. These are never committed and feature restricted user access (`chmod 0x600`).

```bash
markdrop setup [PROVIDER]
```
* **`[PROVIDER]`**: e.g., `gemini`, `openai`.

## 4. `analyze`
A utility command targeting pure PDF image extraction without the Markdown synthesis overhead.
```bash
markdrop analyze [PDF_FILE] --output_dir [DIR] --save_images
```

## 5. `generate`
A batch-utility command. Points at a raw directory of images and runs an arbitrary prompt against them, saving the output in a timestamped `.csv`.

```bash
markdrop generate [IMAGES_DIRECTORY] \
    --output_dir [DIR] \
    --prompt "Transcribe the equation inside this image using LateX syntax." \
    --llm_client gemini
```
