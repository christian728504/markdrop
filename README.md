<p align="left">
  <img src="https://raw.githubusercontent.com/shoryasethia/markdrop/main/markdrop/src/markdrop-logo.png" alt="Markdrop Logo" width="200" height="200"/>
  <h1 style="display: inline; font-size: 2em; vertical-align: middle; padding-left: 10px; margin: 0;">Markdrop</h1>
</p>

[![Downloads](https://static.pepy.tech/badge/markdrop)](https://pepy.tech/projects/markdrop)
[![PyPI Version](https://img.shields.io/pypi/v/markdrop)](https://pypi.org/project/markdrop/)
[![License](https://img.shields.io/github/license/shoryasethia/markdrop)](https://github.com/shoryasethia/markdrop/blob/main/LICENSE)
[![Stars](https://img.shields.io/github/stars/shoryasethia/markdrop?style=social)](https://github.com/shoryasethia/markdrop/stargazers)
[![Issues](https://img.shields.io/github/issues/shoryasethia/markdrop)](https://github.com/shoryasethia/markdrop/issues)
[![Forks](https://img.shields.io/github/forks/shoryasethia/markdrop?style=social)](https://github.com/shoryasethia/markdrop/network/members)

A Python package for converting PDFs to structured Markdown and interactive HTML, with AI-powered image and table descriptions across **six major LLM providers**. Available on PyPI.

---

## Features

- [x] PDF → Markdown conversion with formatting preservation (via Docling)
- [x] Automatic image extraction using XRef IDs
- [x] Table detection using Microsoft's Table Transformer
- [x] PDF URL support
- [x] AI-powered image and table descriptions — **6 providers**: Gemini, OpenAI, Anthropic Claude, Groq, OpenRouter, LiteLLM
- [x] Interactive HTML output with downloadable Excel tables
- [x] Customisable image resolution and UI elements
- [x] Structured logging (never pollutes your app's root logger)
- [ ] Support for DOCX / PPTX input

---

## Installation

**Core install (PDF conversion + Gemini/OpenAI):**
```bash
pip install markdrop
```

**With Anthropic Claude:**
```bash
pip install "markdrop[anthropic]"
```

**With Groq:**
```bash
pip install "markdrop[groq]"
```

**With LiteLLM (routes to 100+ providers):**
```bash
pip install "markdrop[litellm]"
```

**Everything (including local HuggingFace models):**
```bash
pip install "markdrop[all]"
```

> **OpenRouter** is accessed through the `openai` package (already included in core), so no extra install is needed.

---

## Supported AI Providers

| Provider | `--ai_provider` | Default model | Vision |
|---|---|---|---|
| Google Gemini | `gemini` | `gemini-3.1-flash-lite` | ✅ |
| OpenAI | `openai` | `gpt-5.4` | ✅ |
| Anthropic Claude | `anthropic` | `claude-opus-4-6` | ✅ |
| Groq | `groq` | `meta-llama/llama-4-maverick-17b-128e-instruct` | ✅ |
| OpenRouter | `openrouter` | `google/gemini-3.1-flash-lite` (any model) | ✅ |
| LiteLLM | `litellm` | `openai/gpt-5.4` (configurable) | ✅ |

> All models are configurable — use `--model` to override for any provider, or set `model_name_override` in `ProcessorConfig`.

---

## Quick Start

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1oApTrP_kjNn0s1tpE0SIWRyGzYfflQsi?usp=sharing)
[![Watch the demo](https://img.shields.io/badge/YouTube-Demo-red?logo=youtube&logoColor=white)](https://youtu.be/2xg7W0-oiw0)

---

## CLI Usage

### 1. Convert PDF → Markdown + HTML

```bash
markdrop convert <input_path> --output_dir <dir> [--add_tables]
```

```bash
# Example
markdrop convert report.pdf --output_dir out --add_tables
# Also works with URLs:
markdrop convert https://arxiv.org/pdf/1706.03762 --output_dir out
```

### 2. Generate AI Descriptions for Images & Tables

```bash
markdrop describe <markdown_file> --ai_provider <provider> [--output_dir <dir>] [--remove_images] [--remove_tables]
```

| Provider | `--ai_provider` |
|---|---|
| Google Gemini 2.0 Flash | `gemini` |
| OpenAI GPT-4o | `openai` |
| Anthropic Claude Opus | `anthropic` |
| Groq Llama-4 Scout | `groq` |
| OpenRouter | `openrouter` |
| LiteLLM | `litellm` |

```bash
# Gemini (default)
markdrop describe doc.md --ai_provider gemini

# Anthropic Claude
markdrop describe doc.md --ai_provider anthropic --remove_images

# Groq (fastest inference)
markdrop describe doc.md --ai_provider groq

# OpenRouter (any model)
markdrop describe doc.md --ai_provider openrouter

# LiteLLM (unified gateway)
markdrop describe doc.md --ai_provider litellm
```

### 3. Set Up API Keys

```bash
markdrop setup <provider>
```

Keys are stored in `<package-root>/.env` with `0o600` permissions on POSIX systems.

```bash
markdrop setup gemini       # → GEMINI_API_KEY
markdrop setup openai       # → OPENAI_API_KEY
markdrop setup anthropic    # → ANTHROPIC_API_KEY
markdrop setup groq         # → GROQ_API_KEY
markdrop setup openrouter   # → OPENROUTER_API_KEY
markdrop setup litellm      # → LITELLM_API_KEY
```

### 4. Analyze Images in a PDF

```bash
markdrop analyze report.pdf --output_dir pdf_analysis --save_images
```

### 5. Batch Image Description Generation

```bash
markdrop generate images/ --output_dir descriptions/ --prompt "Describe in detail." \
  --llm_client gemini openai
```

Available `--llm_client` values: `qwen`, `gemini`, `openai`, `llama-vision`, `molmo`, `pixtral`

---

## Python API

### PDF Conversion

```python
from markdrop import markdrop, MarkDropConfig, add_downloadable_tables
from pathlib import Path
import logging

config = MarkDropConfig(
    image_resolution_scale=2.0,
    download_button_color='#444444',
    log_level=logging.INFO,
    log_dir='logs',
    excel_dir='markdrop-excel-tables',
)

html_path = markdrop("path/to/input.pdf", "output", config)
downloadable_html = add_downloadable_tables(html_path, config)
```

### AI Descriptions

```python
from markdrop import process_markdown, ProcessorConfig, AIProvider, setup_keys

# One-time key setup (writes to .env)
setup_keys('anthropic')

config = ProcessorConfig(
    input_path="doc.md",
    output_dir="output",
    ai_provider=AIProvider.ANTHROPIC,       # GEMINI | OPENAI | ANTHROPIC | GROQ | OPENROUTER | LITELLM
    remove_images=False,
    remove_tables=False,
    table_descriptions=True,
    image_descriptions=True,
    max_retries=3,
    retry_delay=2,
    # Override default models (all providers have matching config fields):
    anthropic_model_name="claude-sonnet-4-5",    # faster / cheaper
    anthropic_text_model_name="claude-sonnet-4-5",
)

output_path = process_markdown(config)
```

#### Using OpenRouter to access any model

```python
config = ProcessorConfig(
    input_path="doc.md",
    output_dir="output",
    ai_provider=AIProvider.OPENROUTER,
    openrouter_model_name="meta-llama/llama-4-scout",   # any model on openrouter.ai/models
    openrouter_text_model_name="anthropic/claude-sonnet-4-5",
    openrouter_site_url="https://yoursite.com",
    openrouter_site_name="My App",
)
```

#### Using LiteLLM for any 100+ provider

```python
import os
os.environ["ANTHROPIC_API_KEY"] = "..."   # set any provider's key

config = ProcessorConfig(
    input_path="doc.md",
    output_dir="output",
    ai_provider=AIProvider.LITELLM,
    litellm_model_name="anthropic/claude-opus-4-6",
    litellm_text_model_name="groq/llama-3.3-70b-versatile",
)
```

### Batch Image Description Generation

```python
from markdrop import generate_descriptions

generate_descriptions(
    input_path='images/',
    output_dir='output/',
    prompt='Give a highly detailed description of this image.',
    llm_client=['gemini', 'llama-vision'],
)
```

---

## API Reference

### `ProcessorConfig` – AI Provider Fields

| Field | Default | Notes |
|---|---|---|
| `gemini_model_name` | `gemini-2.0-flash` | Vision model |
| `gemini_text_model_name` | `gemini-2.0-flash` | Text model |
| `openai_model_name` | `gpt-4o` | Vision + text |
| `openai_text_model_name` | `gpt-4o` | |
| `anthropic_model_name` | `claude-opus-4-6` | Vision |
| `anthropic_text_model_name` | `claude-sonnet-4-5` | Text (cheaper) |
| `groq_model_name` | `meta-llama/llama-4-scout-17b-16e-instruct` | Vision |
| `groq_text_model_name` | `llama-3.3-70b-versatile` | Text |
| `openrouter_model_name` | `google/gemini-2.0-flash-001` | Any model string from openrouter.ai/models |
| `openrouter_text_model_name` | `anthropic/claude-sonnet-4-5` | |
| `litellm_model_name` | `openai/gpt-4o` | `provider/model` format |
| `litellm_text_model_name` | `openai/gpt-4o` | |

### `MarkDropConfig`

| Field | Default | Notes |
|---|---|---|
| `image_resolution_scale` | `2.0` | Scale factor for extracted images |
| `download_button_color` | `'#444444'` | HTML button colour |
| `log_level` | `logging.INFO` | |
| `log_dir` | `'logs'` | |
| `excel_dir` | `'markdrop_excel_tables'` | |

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md).

```bash
git clone https://github.com/shoryasethia/markdrop.git
cd markdrop
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -e ".[all]"
```

---

## Project Structure

```
markdrop/
├── setup.py
├── requirements.txt
├── README.md
└── markdrop/
    ├── __init__.py
    ├── main.py          ← CLI entry-point
    ├── process.py       ← PDF conversion
    ├── parse.py         ← AI description engine (all 6 providers)
    ├── helper.py        ← PDF image analysis
    ├── utils.py         ← PDF download helpers
    ├── setup_keys.py    ← Interactive API key manager
    ├── ignore_warnings.py
    ├── src/
    │   └── markdrop-logo.png
    └── models/
        ├── img_descriptions.py
        ├── model_loader.py  ← Local HF model loader
        ├── responder.py
        └── logger.py
```

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=shoryasethia/markdrop&type=Timeline)](https://star-history.com/#shoryasethia/markdrop&Timeline)

---

## License

MIT — see [LICENSE](LICENSE).

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## Support

- [Open an issue](https://github.com/shoryasethia/markdrop/issues)