# Python API Reference

Markdrop exposes a simple integration hierarchy for usage directly within Python workflows.

## Extracting a Document (`markdrop` function)

```python
from markdrop import markdrop, MarkDropConfig, add_downloadable_tables
import logging

config = MarkDropConfig(
    image_resolution_scale=2.0,            # Output quality of raster chunks
    download_button_color='#444444',       # Hex coloring of HTML export
    log_level=logging.INFO,                # Sets standard namespaced logger output
)

html_path = markdrop(
    input_doc_path="path/to/paper.pdf", 
    output_dir="data_dumps", 
    config=config
)

# Optional tabular augmentation 
add_downloadable_tables(html_path, config)
```

## Adding AI Semantic Text (`process_markdown`)

As of `v4.0.0`, `process_markdown` is an asynchronous coroutine. You must invoke it either via `asyncio.run()` or `await` it inside an existing context.

```python
import asyncio
from markdrop import process_markdown, ProcessorConfig, AIProvider

config = ProcessorConfig(
    input_path="data_dumps/paper.md",      # Extracted markdown generated above
    output_dir="data_dumps/ai_pass",
    
    # Model Configurations
    ai_provider=AIProvider.GEMINI,
    gemini_model_name="gemini-3.1-flash-lite", 
    
    # Processing Directives
    remove_images=False,                   # True removes raw image embeddings entirely
    table_descriptions=True,
    
    # Network robustness
    max_retries=3,
    retry_delay=2,
)

async def run_pipeline():
    processed_file_path = await process_markdown(config)
    print(f"Finished evaluating text at {processed_file_path}")

asyncio.run(run_pipeline())
```
