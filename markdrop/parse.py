"""
markdrop/parse.py
=================
Markdown post-processor that uses AI to generate descriptions for embedded
images and tables.

Supported AI providers
-----------------------
    gemini       – Google Gemini (google-generativeai)
    openai       – OpenAI GPT-4o
    anthropic    – Anthropic Claude (claude-opus-4-6 / claude-sonnet-4-5)
    groq         – Groq (llama-4-scout-17b via OpenAI-compatible API)
    openrouter   – OpenRouter (any model via OpenAI-compatible API)
    litellm      – LiteLLM (any 100+ providers via unified interface)
"""

import os
import re
import time
import base64
import logging
import shutil
from pathlib import Path
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional

import urllib.parse

# ---------------------------------------------------------------------------
# Lazy named logger – does NOT touch the root logger or create directories at
# import time.
# ---------------------------------------------------------------------------
_logger: Optional[logging.Logger] = None


def _get_logger() -> logging.Logger:
    """Lazily initialise the markdrop.parse logger with file + stream handlers."""
    global _logger
    if _logger is not None:
        return _logger

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f'markdrop_parse_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

    _logger = logging.getLogger("markdrop.parse")
    if not _logger.handlers:
        _logger.setLevel(logging.INFO)
        fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        fh = logging.FileHandler(log_file)
        fh.setFormatter(fmt)
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        _logger.addHandler(fh)
        _logger.addHandler(sh)
    return _logger


class _LazyLogger:
    """Proxy so callers can write ``logger.info(...)`` before the logger is initialised."""
    def __getattr__(self, name):
        return getattr(_get_logger(), name)


logger = _LazyLogger()


# ---------------------------------------------------------------------------
# Provider enum
# ---------------------------------------------------------------------------

class AIProvider(Enum):
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    OPENROUTER = "openrouter"
    LITELLM = "litellm"


# ---------------------------------------------------------------------------
# Default prompts
# ---------------------------------------------------------------------------

DEFAULT_IMAGE_PROMPT = (
    "Provide a detailed, contextually rich description of this image. "
    "Include visual details, context, data, and any relevant information "
    "that would help someone understand what this image conveys without seeing it. "
    "Make it descriptive enough to serve as a replacement for the image."
)

DEFAULT_TABLE_PROMPT = (
    "Analyze this markdown table and provide a detailed description of its contents. "
    "Include key insights, patterns, and important details. Make the summary "
    "comprehensive enough to replace the original table.\n\nTable:\n"
)


# ---------------------------------------------------------------------------
# Configuration dataclass
# ---------------------------------------------------------------------------

@dataclass
class ProcessorConfig:
    input_path: str
    output_dir: str
    ai_provider: AIProvider
    remove_images: bool = False
    remove_tables: bool = False
    table_descriptions: bool = True
    image_descriptions: bool = True
    max_retries: int = 3
    retry_delay: int = 2

    # ----------------------------------------------------------------
    # Generic override: set either of these to force a specific model
    # for the selected provider (takes precedence over provider-specific
    # model fields below). Useful for the --model CLI flag.
    # ----------------------------------------------------------------
    model_name_override: str = ""        # vision / primary model
    text_model_name_override: str = ""   # text-only model

    # --- Gemini ---
    # gemini-3.1-flash-lite: launched March 3 2026, cost-efficient, low-latency
    # gemini-3.1-pro-preview: Feb 2026 flagship (complex reasoning)
    gemini_model_name: str = "gemini-3.1-flash-lite"
    gemini_text_model_name: str = "gemini-3.1-flash-lite"

    # --- OpenAI ---
    # gpt-5.4: current flagship as of March 2026 (vision + reasoning)
    # gpt-5-mini: cost-optimised variant
    openai_model_name: str = "gpt-5.4"
    openai_text_model_name: str = "gpt-5.4"

    # --- Anthropic ---
    # claude-opus-4-6: Feb 2026 flagship (complex reasoning, agentic)
    # claude-sonnet-4-6: Feb 17 2026, default on claude.ai (speed + quality)
    anthropic_model_name: str = "claude-opus-4-6"
    anthropic_text_model_name: str = "claude-sonnet-4-6"

    # --- Groq ---
    # llama-4-maverick: optimised for multilingual + multimodal (2026)
    # llama-4-scout: alternative vision model
    groq_model_name: str = "meta-llama/llama-4-maverick-17b-128e-instruct"
    groq_text_model_name: str = "meta-llama/llama-4-maverick-17b-128e-instruct"

    # --- OpenRouter (any model on https://openrouter.ai/models) ---
    openrouter_model_name: str = "google/gemini-3.1-flash-lite"
    openrouter_text_model_name: str = "anthropic/claude-sonnet-4-6"
    openrouter_site_url: str = ""
    openrouter_site_name: str = "markdrop"

    # --- LiteLLM (provider/model format) ---
    litellm_model_name: str = "openai/gpt-5.4"
    litellm_text_model_name: str = "openai/gpt-5.4"

    image_prompt: str = field(default_factory=lambda: DEFAULT_IMAGE_PROMPT)
    table_prompt: str = field(default_factory=lambda: DEFAULT_TABLE_PROMPT)

    # ------------------------------------------------------------------
    # Helpers to resolve the effective model name for the active provider
    # ------------------------------------------------------------------
    def effective_model(self) -> str:
        """Return the vision model to use, respecting --model override."""
        if self.model_name_override:
            return self.model_name_override
        return {
            AIProvider.GEMINI: self.gemini_model_name,
            AIProvider.OPENAI: self.openai_model_name,
            AIProvider.ANTHROPIC: self.anthropic_model_name,
            AIProvider.GROQ: self.groq_model_name,
            AIProvider.OPENROUTER: self.openrouter_model_name,
            AIProvider.LITELLM: self.litellm_model_name,
        }.get(self.ai_provider, "")

    def effective_text_model(self) -> str:
        """Return the text model to use, respecting --text-model override."""
        if self.text_model_name_override:
            return self.text_model_name_override
        return {
            AIProvider.GEMINI: self.gemini_text_model_name,
            AIProvider.OPENAI: self.openai_text_model_name,
            AIProvider.ANTHROPIC: self.anthropic_text_model_name,
            AIProvider.GROQ: self.groq_text_model_name,
            AIProvider.OPENROUTER: self.openrouter_text_model_name,
            AIProvider.LITELLM: self.litellm_text_model_name,
        }.get(self.ai_provider, "")


# ---------------------------------------------------------------------------
# AI Processor
# ---------------------------------------------------------------------------

class AIProcessor:
    def __init__(self, config: ProcessorConfig):
        if not isinstance(config.ai_provider, AIProvider):
            raise TypeError(
                f"config.ai_provider must be an AIProvider enum member, "
                f"got {type(config.ai_provider)}"
            )
        self.config = config
        self._setup_ai_clients()

    # ------------------------------------------------------------------
    # Client initialisation
    # ------------------------------------------------------------------

    def _setup_ai_clients(self):
        """Lazily import and initialise only the required provider client."""
        from dotenv import load_dotenv
        load_dotenv()

        p = self.config.ai_provider

        if p == AIProvider.GEMINI:
            import google.generativeai as genai  # type: ignore
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found – run: markdrop setup gemini")
            genai.configure(api_key=api_key)
            # Use effective_model() so --model CLI flag is respected
            self.image_model = genai.GenerativeModel(self.config.effective_model())
            self.text_model = genai.GenerativeModel(self.config.effective_text_model())

        elif p == AIProvider.OPENAI:
            from openai import OpenAI  # type: ignore
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found – run: markdrop setup openai")
            self.client = OpenAI(api_key=api_key)

        elif p == AIProvider.ANTHROPIC:
            import anthropic  # type: ignore
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found – run: markdrop setup anthropic")
            self.client = anthropic.Anthropic(api_key=api_key)

        elif p == AIProvider.GROQ:
            from openai import OpenAI  # type: ignore
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not found – run: markdrop setup groq")
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1",
            )

        elif p == AIProvider.OPENROUTER:
            from openai import OpenAI  # type: ignore
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY not found – run: markdrop setup openrouter")
            extra_headers = {}
            if self.config.openrouter_site_url:
                extra_headers["HTTP-Referer"] = self.config.openrouter_site_url
            if self.config.openrouter_site_name:
                extra_headers["X-Title"] = self.config.openrouter_site_name
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
                default_headers=extra_headers,
            )

        elif p == AIProvider.LITELLM:
            import litellm  # type: ignore
            self._litellm = litellm

        else:
            raise ValueError(f"Unknown AI provider: {p}")

    # ------------------------------------------------------------------
    # Image processing helpers (one per provider)
    # ------------------------------------------------------------------

    def _encode_image_b64(self, image_path: str) -> str:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _image_media_type(self, image_path: str) -> str:
        ext = Path(image_path).suffix.lower().lstrip(".")
        mapping = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
                   "gif": "image/gif", "webp": "image/webp", "tiff": "image/tiff",
                   "bmp": "image/bmp"}
        return mapping.get(ext, "image/jpeg")

    def process_image(self, image_path: str) -> str:
        """Generate a text description for the image at *image_path*."""
        start = time.time()
        logger.info(f"Processing image [{self.config.ai_provider.value}]: {image_path}")

        p = self.config.ai_provider

        if p == AIProvider.GEMINI:
            def _call():
                from PIL import Image  # type: ignore
                img = Image.open(image_path)
                return self.image_model.generate_content([self.config.image_prompt, img]).text
        elif p == AIProvider.OPENAI:
            def _call():
                b64 = self._encode_image_b64(image_path)
                media = self._image_media_type(image_path)
                resp = self.client.chat.completions.create(
                    model=self.config.effective_model(),
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": self.config.image_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:{media};base64,{b64}"}},
                    ]}],
                    max_tokens=500,
                )
                return resp.choices[0].message.content
        elif p == AIProvider.ANTHROPIC:
            def _call():
                b64 = self._encode_image_b64(image_path)
                media = self._image_media_type(image_path)
                resp = self.client.messages.create(
                    model=self.config.effective_model(),
                    max_tokens=500,
                    messages=[{"role": "user", "content": [
                        {"type": "image", "source": {
                            "type": "base64",
                            "media_type": media,
                            "data": b64,
                        }},
                        {"type": "text", "text": self.config.image_prompt},
                    ]}],
                )
                return resp.content[0].text
        elif p == AIProvider.GROQ:
            def _call():
                b64 = self._encode_image_b64(image_path)
                media = self._image_media_type(image_path)
                resp = self.client.chat.completions.create(
                    model=self.config.effective_model(),
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": self.config.image_prompt},
                        {"type": "image_url",
                         "image_url": {"url": f"data:{media};base64,{b64}"}},
                    ]}],
                    max_tokens=500,
                )
                return resp.choices[0].message.content
        elif p == AIProvider.OPENROUTER:
            def _call():
                b64 = self._encode_image_b64(image_path)
                media = self._image_media_type(image_path)
                resp = self.client.chat.completions.create(
                    model=self.config.effective_model(),
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": self.config.image_prompt},
                        {"type": "image_url",
                         "image_url": {"url": f"data:{media};base64,{b64}"}},
                    ]}],
                    max_tokens=500,
                )
                return resp.choices[0].message.content
        elif p == AIProvider.LITELLM:
            def _call():
                b64 = self._encode_image_b64(image_path)
                media = self._image_media_type(image_path)
                resp = self._litellm.completion(
                    model=self.config.effective_model(),
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": self.config.image_prompt},
                        {"type": "image_url",
                         "image_url": {"url": f"data:{media};base64,{b64}"}},
                    ]}],
                    max_tokens=500,
                )
                return resp.choices[0].message.content
        else:
            return f"[Unsupported provider: {p}]"

        try:
            description = self._process_with_retry(_call)
            logger.info(f"Image processed in {time.time()-start:.2f}s")
            return description
        except Exception as e:
            logger.error(f"Failed to process image {image_path}: {e}")
            return f"[Image processing failed: {image_path}]"

    # ------------------------------------------------------------------
    # Table processing (text-only)
    # ------------------------------------------------------------------

    def process_table(self, table_content: str) -> str:
        """Generate a text summary for the markdown *table_content*."""
        start = time.time()
        full_prompt = self.config.table_prompt + table_content
        p = self.config.ai_provider

        if p == AIProvider.GEMINI:
            def _call():
                return self.text_model.generate_content(full_prompt).text
        elif p in (AIProvider.OPENAI, AIProvider.GROQ, AIProvider.OPENROUTER):
            def _call():
                resp = self.client.chat.completions.create(
                    model=self.config.effective_text_model(),
                    messages=[{"role": "user", "content": full_prompt}],
                    max_tokens=500,
                )
                return resp.choices[0].message.content
        elif p == AIProvider.ANTHROPIC:
            def _call():
                resp = self.client.messages.create(
                    model=self.config.effective_text_model(),
                    max_tokens=500,
                    messages=[{"role": "user", "content": full_prompt}],
                )
                return resp.content[0].text
        elif p == AIProvider.LITELLM:
            def _call():
                resp = self._litellm.completion(
                    model=self.config.litellm_text_model_name,
                    messages=[{"role": "user", "content": full_prompt}],
                    max_tokens=500,
                )
                return resp.choices[0].message.content
        else:
            return "[Unsupported provider]"

        try:
            summary = self._process_with_retry(_call)
            logger.info(f"Table processed in {time.time()-start:.2f}s")
            return summary
        except Exception as e:
            logger.error(f"Failed to process table: {e}")
            return "[Table processing failed]"

    # ------------------------------------------------------------------
    # Retry wrapper
    # ------------------------------------------------------------------

    def _process_with_retry(self, func, *args, **kwargs):
        for attempt in range(self.config.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}/{self.config.max_retries} failed: {e}")
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay)
                else:
                    raise


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def process_markdown(config: ProcessorConfig) -> Path:
    """Process a markdown file – generate image/table descriptions via AI."""
    start = time.time()
    logger.info(f"Starting markdown processing [{config.ai_provider.value}]")

    input_path = Path(config.input_path)
    output_dir = Path(config.output_dir)

    ai_processor = AIProcessor(config)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    backup_path = create_backup(input_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    processed_path = output_dir / f"{input_path.stem}_processed{input_path.suffix}"
    shutil.copy2(backup_path, processed_path)

    with open(processed_path, "r", encoding="utf-8") as f:
        content = f.read()

    # ---- images ----
    if config.image_descriptions:
        img_pattern = r"!\[([^\]]*)\]\(([^)]+)\)"
        img_count = len(re.findall(img_pattern, content))
        logger.info(f"Found {img_count} images")

        def replace_image(match):
            alt_text, image_path = match.groups()
            decoded = urllib.parse.unquote(image_path)
            # Security: block path traversal
            try:
                root = input_path.parent.resolve()
                full = (root / decoded).resolve()
                if not str(full).startswith(str(root)):
                    logger.warning(f"Blocked path traversal attempt: {image_path}")
                    return "[Image skipped: path outside document directory]"
            except Exception:
                logger.warning(f"Could not resolve image path: {image_path}")
                return "[Image skipped: invalid path]"

            if full.exists():
                desc = ai_processor.process_image(str(full))
                if config.remove_images:
                    return f"\n\n**Image Description:** {desc}\n\n"
                return f"![{alt_text}]({image_path})\n\n**Image Description:** {desc}\n\n"
            logger.warning(f"Image not found: {image_path}")
            return f"[Image not found: {image_path}]"

        content = re.sub(img_pattern, replace_image, content)
    else:
        img_count = 0

    # ---- tables ----
    if config.table_descriptions:
        table_pattern = r"(\|[^\n]+\|\n\|[-:\|\s]+\|\n(?:\|[^\n]+\|\n)+)"
        table_count = len(re.findall(table_pattern, content))
        logger.info(f"Found {table_count} tables")

        def replace_table(match):
            table_content = match.group(1)
            summary = ai_processor.process_table(table_content)
            if config.remove_tables:
                return f"\n\n**Table Summary:** {summary}\n\n"
            return f"{table_content}\n\n**Table Summary:** {summary}\n\n"

        content = re.sub(table_pattern, replace_table, content)
    else:
        table_count = 0

    with open(processed_path, "w", encoding="utf-8") as f:
        f.write(content)

    elapsed = time.time() - start
    logger.info(
        f"Processing complete in {elapsed:.2f}s – "
        f"{img_count} images, {table_count} tables → {processed_path}"
    )
    return processed_path


def create_backup(file_path: Path) -> Path:
    """Create a timestamped backup so reruns never silently overwrite backups."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = file_path.parent / f"{file_path.stem}_original_{timestamp}{file_path.suffix}"
    shutil.copy2(file_path, backup_path)
    logger.info(f"Backup created: {backup_path}")
    return backup_path