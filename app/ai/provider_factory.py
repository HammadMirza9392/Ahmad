"""
AI Provider Factory
Dynamically instantiates the correct provider based on admin configuration.
Handles primary/backup failover.
"""
from app.models.ai_settings import AIProvider
from app.utils.encryption import decrypt_value

from app.ai.gemini_provider import GeminiProvider
from app.ai.groq_provider import GroqProvider
from app.ai.openrouter_provider import OpenRouterProvider
from app.ai.huggingface_provider import HuggingFaceProvider
from app.ai.deepseek_provider import DeepSeekProvider

# Registry maps provider_type to its implementation class
PROVIDER_REGISTRY = {
    'gemini': GeminiProvider,
    'groq': GroqProvider,
    'openrouter': OpenRouterProvider,
    'huggingface': HuggingFaceProvider,
    'deepseek': DeepSeekProvider,
}


def get_provider(provider_record=None):
    """Instantiate an AI provider from a database record.
    If no record given, loads the primary active provider.
    Falls back to backup provider if primary fails to instantiate.
    """
    if provider_record is None:
        provider_record = AIProvider.query.filter_by(is_primary=True, is_active=True).first()

    if not provider_record:
        # Try backup
        provider_record = AIProvider.query.filter_by(is_backup=True, is_active=True).first()

    if not provider_record:
        raise RuntimeError('No active AI provider configured. Go to Admin → AI Settings.')

    return _build_provider(provider_record)


def get_backup_provider():
    """Get the backup provider (for failover)."""
    record = AIProvider.query.filter_by(is_backup=True, is_active=True).first()
    if not record:
        return None
    return _build_provider(record)


def _build_provider(record):
    """Construct a provider instance from its database configuration."""
    cls = PROVIDER_REGISTRY.get(record.provider_type)
    if not cls:
        # For custom providers, try OpenRouter-compatible format
        cls = OpenRouterProvider

    api_key = decrypt_value(record.api_key_encrypted)
    if not api_key:
        raise RuntimeError(f'API key for {record.name} is missing or could not be decrypted.')

    return cls(
        api_key=api_key,
        model_name=record.model_name,
        temperature=record.temperature,
        top_p=record.top_p,
        max_tokens=record.max_tokens,
        timeout=record.timeout,
        api_base_url=record.api_base_url,
    )


def get_all_provider_types():
    """Return list of available provider types for the admin dropdown."""
    return [
        ('gemini', 'Google Gemini'),
        ('groq', 'Groq'),
        ('openrouter', 'OpenRouter'),
        ('huggingface', 'HuggingFace'),
        ('deepseek', 'DeepSeek'),
        ('custom', 'Custom Provider'),
    ]
