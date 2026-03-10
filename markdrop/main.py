import argparse
import asyncio
import logging
import sys
import time
from pathlib import Path

from .helper import analyze_pdf_images
from .models.img_descriptions import generate_descriptions
from .parse import AIProvider, ProcessorConfig, process_markdown
from .process import MarkDropConfig, add_downloadable_tables, markdrop
from .setup_keys import setup_keys

# Human-readable provider list for CLI help text
PROVIDER_CHOICES = [p.value for p in AIProvider]


def configure_logging(log_level=logging.INFO):
    """Set up the root markdrop logger to output to console and file when running as CLI."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"markdrop_{time.strftime('%Y%m%d_%H%M%S')}.log"

    logger = logging.getLogger("markdrop")
    logger.setLevel(log_level)

    fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    fh = logging.FileHandler(log_file)
    fh.setFormatter(fmt)
    
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    
    logger.addHandler(fh)
    logger.addHandler(sh)


def main():
    configure_logging()

    parser = argparse.ArgumentParser(
        description="MarkDrop: A comprehensive PDF processing toolkit.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ------------------------------------------------------------------ convert
    convert_parser = subparsers.add_parser(
        "convert",
        help="Convert PDF to markdown and HTML.",
    )
    convert_parser.add_argument("input_path", type=str, help="Path or URL to the input PDF file")
    convert_parser.add_argument(
        "--output_dir", type=str, default="output", help="Directory to save output files"
    )
    convert_parser.add_argument(
        "--add_tables", action="store_true", help="Add downloadable tables to the HTML output"
    )

    # ------------------------------------------------------------------ describe
    describe_parser = subparsers.add_parser(
        "describe",
        help="Generate AI descriptions for images and tables in a markdown file.",
    )
    describe_parser.add_argument("input_path", type=str, help="Path to the markdown file")
    describe_parser.add_argument(
        "--output_dir", type=str, default="output", help="Directory to save the processed file"
    )
    describe_parser.add_argument(
        "--ai_provider",
        type=str,
        choices=PROVIDER_CHOICES,
        default="gemini",
        help=(
            "AI provider to use for descriptions.\n"
            "  gemini      – Google Gemini 2.0 Flash\n"
            "  openai      – OpenAI GPT-4o\n"
            "  anthropic   – Anthropic Claude (claude-opus-4-6)\n"
            "  groq        – Groq Llama-4 Scout (fast inference)\n"
            "  openrouter  – OpenRouter (route to any model)\n"
            "  litellm     – LiteLLM (100+ providers, unified API)"
        ),
    )
    describe_parser.add_argument(
        "--remove_images", action="store_true", help="Replace images with their descriptions"
    )
    describe_parser.add_argument(
        "--remove_tables", action="store_true", help="Replace tables with their summaries"
    )
    describe_parser.add_argument(
        "--model",
        type=str,
        default="",
        help=(
            "Override the vision/primary model for the chosen provider.\n"
            "Examples:\n"
            "  --model gemini-3.1-pro-preview    (for --ai_provider gemini)\n"
            "  --model gpt-5.4-pro               (for --ai_provider openai)\n"
            "  --model claude-opus-4-6           (for --ai_provider anthropic)\n"
            "  --model mistral/mistral-large     (for --ai_provider openrouter)\n"
            "  --model anthropic/claude-opus-4-6 (for --ai_provider litellm)"
        ),
    )
    describe_parser.add_argument(
        "--text-model",
        dest="text_model",
        type=str,
        default="",
        help="Override the text-only model (used for table descriptions). Same format as --model.",
    )

    # ------------------------------------------------------------------ analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analyze images in a PDF file")
    analyze_parser.add_argument("input_path", type=str, help="Path or URL to the PDF file")
    analyze_parser.add_argument(
        "--output_dir",
        type=str,
        default="output/analysis",
        help="Directory to save analysis results",
    )
    analyze_parser.add_argument("--save_images", action="store_true", help="Save extracted images")

    # ------------------------------------------------------------------ setup
    setup_parser = subparsers.add_parser("setup", help="Set up API keys for AI providers")
    setup_parser.add_argument(
        "provider",
        type=str,
        choices=["gemini", "openai", "anthropic", "groq", "openrouter", "litellm"],
        help="The AI provider to configure",
    )

    # ------------------------------------------------------------------ generate
    generate_parser = subparsers.add_parser("generate", help="Generate descriptions for images")
    generate_parser.add_argument(
        "input_path", type=str, help="Path to an image file or a directory of images"
    )
    generate_parser.add_argument(
        "--output_dir",
        type=str,
        default="output/descriptions",
        help="Directory to save the descriptions CSV",
    )
    generate_parser.add_argument(
        "--prompt",
        type=str,
        default="Describe the image in detail.",
        help="Prompt for the AI model",
    )
    generate_parser.add_argument(
        "--llm_client", nargs="+", default=["gemini"], help="List of LLM clients to use"
    )

    # ------------------------------------------------------------------ dispatch
    args = parser.parse_args()

    if args.command == "convert":
        config = MarkDropConfig()
        output_dir = Path(args.output_dir)
        html_path = markdrop(args.input_path, str(output_dir), config)
        if args.add_tables:
            add_downloadable_tables(html_path, config)
        print(f"Conversion complete. Output saved in {output_dir}")

    elif args.command == "describe":
        config = ProcessorConfig(
            input_path=str(Path(args.input_path)),
            output_dir=str(Path(args.output_dir)),
            ai_provider=AIProvider(args.ai_provider),
            remove_images=args.remove_images,
            remove_tables=args.remove_tables,
            model_name_override=args.model,
            text_model_name_override=args.text_model,
        )
        asyncio.run(process_markdown(config))
        print(f"Description generation complete. Output saved in {args.output_dir}")

    elif args.command == "analyze":
        analyze_pdf_images(
            args.input_path, args.output_dir, verbose=True, save_images=args.save_images
        )
        print(f"Analysis complete. Results saved in {args.output_dir}")

    elif args.command == "setup":
        setup_keys(args.provider)

    elif args.command == "generate":
        generate_descriptions(
            input_path=args.input_path,
            output_dir=args.output_dir,
            prompt=args.prompt,
            llm_client=args.llm_client,
        )
        print(f"Image description generation complete. Output saved in {args.output_dir}")


if __name__ == "__main__":
    main()
