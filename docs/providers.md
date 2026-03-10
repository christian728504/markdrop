# Providers & Models Guide

Markdrop is capable of automatically distributing tasks—like describing complex data plots, charts, equations, and tables—to a variety of modern AI providers. This document outlines exactly which models are used and how to control them.

## Supported Providers
We maintain a suite of default models, audited regularly. Current defaults (as of **March 2026**):

| Provider | `--ai_provider` argument | Default Image Model | Default Table Model |
| --- | --- | --- | --- |
| Google Gemini | `gemini` | `gemini-3.1-flash-lite` | `gemini-3.1-flash-lite` |
| OpenAI | `openai` | `gpt-5.4` | `gpt-5.4` |
| Anthropic | `anthropic` | `claude-opus-4-6` | `claude-sonnet-4-5` |
| Groq | `groq` | `meta-llama/llama-4-maverick...` | `llama-3.3-70b-versatile` |
| OpenRouter | `openrouter` | *Needs Override* | *Needs Override* |
| LiteLLM | `litellm` | *Needs Proxy Identifier* | *Needs Proxy Identifier* |

## Overriding Models on the CLI
Both `--model` and `--text-model` flags are available during a `markdrop describe` execution to force alternate generations.

### Example: Using Anthropic
Anthropic's Opus is the primary vision model, but it is expensive. If you want to use the cheaper Sonnet model for both Images and Tables:

```bash
markdrop describe file.md \
    --ai_provider anthropic \
    --model claude-sonnet-4-5 \
    --text-model claude-sonnet-4-5
```

### Example: OpenRouter
OpenRouter exposes numerous community endpoints. Pass any valid string from the [OpenRouter models index](https://openrouter.ai/models).

```bash
markdrop describe file.md \
    --ai_provider openrouter \
    --model "google/gemini-2.5-pro-vision" \
    --text-model "meta-llama/llama-4-scout"
```

### Example: LiteLLM Proxies
LiteLLM unifies over 100+ providers via a proxy-naming standard. You simply prefix the provider name.

```bash
# Assuming you previously set API environment bounds
export ANTHROPIC_API_KEY="..."

markdrop describe file.md \
    --ai_provider litellm \
    --model "anthropic/claude-opus-4-6"
```
