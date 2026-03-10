import logging
from contextlib import suppress

from .helper import analyze_pdf_images

import sys
from unittest.mock import MagicMock
if 'torch' not in sys.modules:
    sys.modules['torch'] = MagicMock()
if 'transformers' not in sys.modules:
    sys.modules['transformers'] = MagicMock()
if 'docling' not in sys.modules:
    sys.modules['docling'] = MagicMock()
    sys.modules['docling.document_converter'] = MagicMock()
    sys.modules['docling.datamodel'] = MagicMock()
    sys.modules['docling.datamodel.base_models'] = MagicMock()
    sys.modules['docling.datamodel.pipeline_options'] = MagicMock()
if 'docling_core' not in sys.modules:
    sys.modules['docling_core'] = MagicMock()
    sys.modules['docling_core.types'] = MagicMock()
    sys.modules['docling_core.types.doc'] = MagicMock()

# Suppress noisy transformers / torch warnings at import time
with suppress(ImportError):
    from .ignore_warnings import *  # noqa: F401, F403
from .models.img_descriptions import generate_descriptions
from .parse import AIProvider, ProcessorConfig, process_markdown
from .process import MarkDropConfig, add_downloadable_tables, markdrop
from .setup_keys import setup_keys
from .utils import cleanup_download_dir, download_pdf

logging.getLogger(__name__).addHandler(logging.NullHandler())

__version__ = "4.0.0"

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
