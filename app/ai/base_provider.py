"""
Base AI Provider
Abstract interface that all AI providers must implement.
"""
from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """Abstract base class for AI providers."""

    def __init__(self, api_key, model_name, **kwargs):
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = kwargs.get('temperature', 0.7)
        self.top_p = kwargs.get('top_p', 0.9)
        self.max_tokens = kwargs.get('max_tokens', 2048)
        self.timeout = kwargs.get('timeout', 30)

    @abstractmethod
    def generate(self, messages, system_prompt=None):
        """Generate a complete response. Returns (text, metadata_dict)."""
        pass

    @abstractmethod
    def generate_stream(self, messages, system_prompt=None):
        """Yield response chunks for streaming. Each chunk is a string."""
        pass

    @abstractmethod
    def test_connection(self):
        """Test if the API key and model are valid. Returns (success, message)."""
        pass

    def _format_messages(self, messages, system_prompt=None):
        """Build a standardized message list from conversation history."""
        formatted = []
        if system_prompt:
            formatted.append({'role': 'system', 'content': system_prompt})
        for msg in messages:
            formatted.append({
                'role': msg.get('role', 'user'),
                'content': msg.get('content', ''),
            })
        return formatted
