# Getting Started with Markdrop

Markdrop is a high-performance Python toolkit explicitly designed to bridge the gap between complex PDF research documents and modern, AI-powered markup. It extracts text alongside preserving formatting and tabular structures, while asynchronously enriching the content using 6 prominent Multi-Modal Language Models.

## Core Installation

Markdrop requires Python 3.10+. The core package comes with built-in support for OpenAI and Gemini APIs.

```bash
pip install markdrop
```

### Provider Extensions
If you prefer models from other architectures, use the package extensions:

```bash
# To unlock Anthropic Claude Support
pip install "markdrop[anthropic]"   

# To unlock Groq's high-speed Llama models
pip install "markdrop[groq]"

# To unlock LiteLLM routing (access 100+ different providers)
pip install "markdrop[litellm]"

# To install everything in one go
pip install "markdrop[all]"
```
> **OpenRouter** is supported out-of-the-box (since it proxies through the `openai` Python SDK).

## First Steps

### 1. Configure your API Keys
Markdrop securely stores keys in your local environment. Run the interactive setup command for whichever provider you plan to use:

```bash
markdrop setup gemini
# Enter mapping string...
```

### 2. Extract a PDF
Use the `convert` command to ingest a local PDF (or an HTTPS link). By default, this outputs a raw `.md` file with image links, and a web-friendly `.html` file.

```bash
markdrop convert https://arxiv.org/pdf/1706.03762 --output_dir my_research
```

### 3. Asynchronous AI Enrichment
Transform the document's structure into deep semantic text using Vision models. This replaces isolated images or complex ASCII tables with contextual AI descriptions.

```bash
# Uses Gemini 2.0 Flash to replace image blobs with text interpretations
markdrop describe my_research/1706.03762.md --ai_provider gemini --remove_images
```

Read more in the [CLI Reference](cli_reference.md) or the [API Reference](api_reference.md).
