import pytest
from markdrop.parse import ProcessorConfig, AIProvider

def test_processor_config_defaults():
    """Test standard defaults and effective model resolution for config."""
    config = ProcessorConfig(
        input_path="test.md",
        output_dir="out",
        ai_provider=AIProvider.ANTHROPIC
    )
    
    # Should resolve to the Anthropic defaults since no override is provided
    assert config.effective_model() == "claude-opus-4-6"
    assert config.effective_text_model() == "claude-sonnet-4-6"

def test_processor_config_overrides():
    """Test that overrides suppress defaults."""
    config = ProcessorConfig(
        input_path="test.md",
        output_dir="out",
        ai_provider=AIProvider.ANTHROPIC,
        model_name_override="custom-vision-model",
        text_model_name_override="custom-text-model"
    )
    
    assert config.effective_model() == "custom-vision-model"
    assert config.effective_text_model() == "custom-text-model"
