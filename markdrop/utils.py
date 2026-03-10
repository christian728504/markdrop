import ipaddress
import logging
import os
import urllib.parse
from contextlib import suppress

import requests
from tqdm import tqdm

logger = logging.getLogger("markdrop.utils")


def is_safe_url(url: str) -> bool:
    """SSRF Protection: Ensure URL is HTTP/HTTPS and resolves to a public IP."""
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False

        import socket

        ip = socket.gethostbyname(parsed.hostname)
        ip_obj = ipaddress.ip_address(ip)
        return not (ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_multicast)
    except Exception:
        return False


from typing import Optional

def download_pdf(url: str, download_dir: str | os.PathLike) -> Optional[str]:
    """Download PDF from a URL with progress bar, timeout, and size limit."""
    MAX_PDF_BYTES = 200 * 1024 * 1024  # 200 MB hard cap
    DOWNLOAD_TIMEOUT = 30  # seconds

    if not is_safe_url(url):
        raise ValueError(f"Download aborted: Unsafe or invalid URL (SSRF block): {url}")

    file_path = None
    try:
        response = requests.get(url, stream=True, timeout=DOWNLOAD_TIMEOUT)
        response.raise_for_status()

        # Get filename from URL
        filename = url.split("/")[-1]
        if not filename.endswith(".pdf"):
            filename += ".pdf"

        file_path = os.path.join(download_dir, filename)
        os.makedirs(download_dir, exist_ok=True)
        total_size = int(response.headers.get("content-length", 0))

        downloaded = 0
        with (
            open(file_path, "wb") as f,
            tqdm(
                desc=f"Downloading {filename}",
                total=total_size,
                unit="iB",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar,
        ):
            for data in response.iter_content(chunk_size=1024):
                downloaded += len(data)
                if downloaded > MAX_PDF_BYTES:
                    raise ValueError(
                        f"Download aborted: exceeded {MAX_PDF_BYTES // (1024 * 1024)} MB size limit"
                    )
                f.write(data)
                bar.update(len(data))

        logger.info(f"Successfully downloaded PDF to {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error downloading PDF from {url}: {e}")
        if file_path and os.path.exists(file_path):
            with suppress(OSError):
                os.remove(file_path)
        raise


def cleanup_download_dir(download_dir: str | os.PathLike, verbose: bool = False) -> None:
    """Clean up downloaded PDF files"""
    try:
        for filename in os.listdir(download_dir):
            file_path = os.path.join(download_dir, filename)
            os.remove(file_path)
            if verbose:
                logger.info(f"Removed temporary file: {file_path}")
        os.rmdir(download_dir)
        if verbose:
            logger.info(f"Removed temporary directory: {download_dir}")
    except Exception as e:
        logger.error(f"Error cleaning up download directory: {e}")
