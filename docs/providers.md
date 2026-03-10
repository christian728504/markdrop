# Supported AI Providers & Model Configuration

Markdrop operates completely agnostic to the underlying AI model processing the document images and tables. This affords users extreme flexibility. 

When you execute `markdrop describe`, the system will search the text for image binaries and table formats, package that visual and textual data according to the SDK specifications of the selected provider, and generate semantic summaries.

---

## Default Providers (March 2026 Specifications)

To simplify operations out of the box, Markdrop enforces rigorously-tested March 2026 defaults. If you do not override manually, these are the models Markdrop relies on for its core reasoning tasks.

| Provider Flag | Network | Vision Model (Images) | Text Model (Tables) | Notes |
| --- | --- | --- | --- | --- |
| `--ai_provider gemini` | Google | `gemini-3.1-flash-lite` | `gemini-3.1-flash-lite` | Built directly on `google-genai` SDK. Currently defaults due to speed and broad availability. |
| `--ai_provider openai` | OpenAI | `gpt-5.4` | `gpt-5.4` | Standard high-accuracy reasoning default. |
| `--ai_provider anthropic` | Anthropic | `claude-opus-4-6` | `claude-sonnet-4-5` | **Crucial Split**: Opus handles complex visual reasoning across massive page layouts. Sonnet intercepts text tables, given it yields identical textual evaluations at 20% of the cost. |
| `--ai_provider groq` | Groq | `meta-llama/llama-4-maverick...` | `llama-3.3-70b-versatile` | Ultra high-speed LLama inference proxy routes. |

---

## API & CLI Model Overrides

The default models are robust but sometimes fail specific use-cases due to cost or speed limits. You can instruct Markdrop to utilize alternative models dynamically:

### Via the CLI
Use the `--model` flag to dictate the primary Vision model, and the optional `--text-model` flag to specify the tabular parser.

```bash
markdrop describe out/report.md \
    --ai_provider anthropic \
    --model claude-sonnet-4-5 \
    --text-model claude-haiku-3-5
```
*In the example above, all images are routed to Sonnet, and all tables are handled by Haiku, resulting in the cheapest possible Claude architecture.*

### Via the Python API
If constructing the `ProcessorConfig` manually:
```python
config = ProcessorConfig(
    input_path="file.md",
    output_dir="out",
    ai_provider=AIProvider.OPENAI,
    openai_model_name="o3-mini",
    openai_text_model_name="gpt-5.4-turbo"
)
```

---

## Platform Proxies (Universal Access)

Markdrop supports massive aggregate platforms routing via proxy paths.

### OpenRouter (`--ai_provider openrouter`)
OpenRouter proxies practically every LLM API worldwide over a unified OpenAI SDK spec framework. Markdrop passes specific metadata arguments behind the scenes ensuring compatibility. Because OpenRouter is a gateway, *you must specify a model override*. The default string is technically `google/gemini-3.1-flash-lite`.

```bash
# Provide the explicit OpenRouter registry model string
markdrop describe file.md \
    --ai_provider openrouter \
    --model "x-ai/grok-vision-beta"
```

### LiteLLM (`--ai_provider litellm`)
An open-source proxy router. Assuming you have configured the downstream provider keys (e.g. `export MISTRAL_API_KEY="..."`), you simply pass the `litellm` prefix combined with `[provider]/[model]`.

```python
config = ProcessorConfig(
    input_path="file.md",
    output_dir="out",
    ai_provider=AIProvider.LITELLM,
    litellm_model_name="mistral/pixtral-large-2411"
)
```

---

## Local Models

Markdrop's `generate` command supports evaluating isolated images directly against local PyTorch inferences via the `transformers` library on your GPU, minimizing cloud egress.

These local endpoints are not used for bulk Markdown enrichment, but rather programmatic benchmarking (`models/responder.py`):
1.  **Qwen** (`model_choice='qwen'`): Utilizes `qwen_vl_utils`.
2.  **LLaMA Vision** (`model_choice='llama-vision'`).
3.  **Molmo** (`model_choice='molmo'`): Half-precision inference utilizing Hugging Face configurations.
4.  **Pixtral** (`model_choice='pixtral'`).

```python
from markdrop import generate_descriptions
generate_descriptions(
    input_path='eval_dataset/',
    output_dir='local_results/',
    prompt='Identify object.',
    llm_client=['molmo'] 
)
```
