import pytest
import argparse
from unittest.mock import patch, MagicMock
from markdrop.main import main
from markdrop.parse import AIProvider

# Mock out any delayed litellm or heavy imports during CLI init
import sys
sys.modules['litellm'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()
sys.modules['openai'] = MagicMock()
sys.modules['anthropic'] = MagicMock()

@patch('markdrop.main.process_markdown')
def test_describe_cli_overrides(mock_process, monkeypatch):
    """Test that the CLI configures ProcessorConfig correctly with model overrides."""
    import sys
    test_args = [
        "markdrop", "describe", "dummy.md", 
        "--ai_provider", "openai",
        "--model", "gpt-5.4-experimental",
        "--text-model", "gpt-5-mini"
    ]
    monkeypatch.setattr(sys, 'argv', test_args)
    
    main()
    
    # Process markdown should have been called once
    mock_process.assert_called_once()
    
    # Extract the ProcessorConfig it was called with
    config = mock_process.call_args[0][0]
    
    assert config.input_path == "dummy.md"
    assert config.ai_provider == AIProvider.OPENAI
    assert config.model_name_override == "gpt-5.4-experimental"
    assert config.text_model_name_override == "gpt-5-mini"
    
    # Verify the effective model resolution works
    assert config.effective_model() == "gpt-5.4-experimental"
    assert config.effective_text_model() == "gpt-5-mini"
