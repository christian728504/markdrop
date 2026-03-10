from setuptools import setup, find_packages

setup(
    name="markdrop",
    version="0.4.0",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4",
        "docling",
        "docling_core==2.16.0",
        "openai>=1.0.0",
        "openpyxl",
        "packaging",
        "pandas",
        "Pillow",
        "protobuf",
        "python-dotenv",
        "pymupdf",
        "requests",
        "tqdm",
        "google-generativeai",
        "numpy<2.0",
    ],
    extras_require={
        # Install with: pip install markdrop[anthropic]
        "anthropic": ["anthropic>=0.40.0"],
        # Install with: pip install markdrop[groq]
        "groq": ["groq>=0.14.0"],
        # Install with: pip install markdrop[litellm]
        "litellm": ["litellm>=1.0.0"],
        # Install with: pip install markdrop[local-models]
        "local-models": [
            "torch",
            "transformers",
        ],
        # Install everything: pip install markdrop[all]
        "all": [
            "anthropic>=0.40.0",
            "groq>=0.14.0",
            "litellm>=1.0.0",
            "torch",
            "transformers",
        ],
    },
    author="Shorya Sethia",
    author_email="shoryasethia4may@gmail.com",
    description=(
        "A comprehensive PDF processing toolkit that converts PDFs to markdown with "
        "advanced AI-powered features for image and table analysis. Supports local files "
        "and URLs, preserves document structure, extracts high-quality images, detects "
        "tables using advanced ML models, and generates detailed content descriptions "
        "using multiple LLM providers including OpenAI GPT-4o, Google Gemini, "
        "Anthropic Claude, Groq, OpenRouter, and LiteLLM."
    ),
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/shoryasethia/markdrop",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Markup :: Markdown",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.10",
    keywords=(
        "pdf markdown converter ai llm table-extraction image-analysis "
        "document-processing gemini openai anthropic claude groq openrouter litellm"
    ),
    entry_points={
        "console_scripts": [
            "markdrop=markdrop.main:main",
        ],
    },
    include_package_data=True,
)