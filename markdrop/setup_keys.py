"""setup_keys.py – Interactive API key manager for markdrop providers."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Keys managed per provider
_PROVIDER_KEYS = {
    "gemini": "GEMINI_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "groq": "GROQ_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "litellm": "LITELLM_API_KEY",  # used when litellm is configured with a proxy
}


def setup_keys(provider: str) -> bool:
    """Interactive function to set up API keys and save them in <package-root>/.env."""

    provider = provider.lower()
    if provider not in _PROVIDER_KEYS:
        print(f"Unknown provider '{provider}'. Valid options: {', '.join(_PROVIDER_KEYS)}")
        return False

    key_name = _PROVIDER_KEYS[provider]

    # Dynamically determine the package's root directory
    package_dir = Path(__file__).resolve().parent.parent
    env_file = package_dir / ".env"
    package_dir.mkdir(parents=True, exist_ok=True)

    # Load existing keys
    existing_keys: dict = {}
    if env_file.exists():
        try:
            load_dotenv(env_file)
            for k in _PROVIDER_KEYS.values():
                val = os.getenv(k)
                if val:
                    existing_keys[k] = val
        except Exception as e:
            print(f"Warning: could not read existing .env – {e}")

    print(f"\nMarkdrop Setup — {provider.capitalize()} API Key")
    print("=" * 44)

    if key_name in existing_keys:
        # Mask: show only first 4 chars
        masked = existing_keys[key_name][:4] + "****"
        print(f"Current key: {masked}")
        change = input("Modify existing key? [y/N]: ").strip().lower()
        if change in ("y", "yes"):
            new_val = input(f"Enter new {key_name}: ").strip()
            if new_val:
                existing_keys[key_name] = new_val
            else:
                print("No value entered – keeping existing key.")
        else:
            print("Keeping existing key.")
    else:
        new_val = input(f"Enter {key_name}: ").strip()
        if new_val:
            existing_keys[key_name] = new_val
        else:
            print("No value entered. Setup skipped.")
            return False

    # Write all keys (standard .env format: no surrounding quotes)
    try:
        with open(env_file, "w") as f:
            for k, v in existing_keys.items():
                f.write(f"{k}={v}\n")
        # Restrict permissions on POSIX systems
        try:
            os.chmod(env_file, 0o600)
        except (AttributeError, NotImplementedError):
            pass  # Windows – permissions handled separately
        print(f"Configuration saved to {env_file}.")
    except Exception as e:
        print(f"Error saving keys: {e}")
        return False

    # Reload so the current process picks up the new value
    try:
        load_dotenv(env_file, override=True)
    except Exception as e:
        print(f"Warning: could not reload .env – {e}")

    return True
