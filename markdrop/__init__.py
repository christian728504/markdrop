from pathlib import Path
from .process import markdrop, MarkDropConfig, add_downloadable_tables
from .parse import process_markdown, ProcessorConfig, AIProvider

from .utils import cleanup_download_dir, download_pdf
from .models.img_descriptions import generate_descriptions
from .setup_keys import setup_keys
from .helper import analyze_pdf_images

# Suppress noisy transformers / torch warnings at import time
from .ignore_warnings import *  # noqa: F401, F403

__version__ = "0.4.0"

__all__ = [
    # Main processing functions
    "markdrop",
    "process_markdown",
    "add_downloadable_tables",
    # Configuration classes
    "MarkDropConfig",
    "ProcessorConfig",
    # AI provider enum
    "AIProvider",
    # Utility functions
    "generate_descriptions",
    "setup_keys",
    "analyze_pdf_images",
    "download_pdf",
    "cleanup_download_dir",
    # Version
    "__version__",
]