"""
HuggingFace Provider
Uses HuggingFace Inference API.
"""
import requests
from app.ai.base_provider import BaseProvider


class HuggingFaceProvider(BaseProvider):

    API_URL = 'https://api-inference.huggingface.co/models/'

    def __init__(self, api_key, model_name, **kwargs):
        super().__init__(api_key, model_name, **kwargs)
        self.headers = {'Authorization': f'Bearer {self.api_key}'}

    def generate(self, messages, system_prompt=None):
        # Build a single prompt string from messages
        prompt = self._build_prompt(messages, system_prompt)
        payload = {
            'inputs': prompt,
            'parameters': {
                'max_new_tokens': self.max_tokens,
                'temperature': self.temperature,
                'top_p': self.top_p,
                'return_full_text': False,
            },
        }
        response = requests.post(
            f'{self.API_URL}{self.model_name}',
            headers=self.headers,
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()

        text = ''
        if isinstance(data, list) and data:
            text = data[0].get('generated_text', '')
        elif isinstance(data, dict):
            text = data.get('generated_text', '')

        metadata = {'provider': 'huggingface', 'model': self.model_name}
        return text, metadata

    def generate_stream(self, messages, system_prompt=None):
        # HuggingFace Inference API has limited streaming; fall back to single response
        text, _ = self.generate(messages, system_prompt)
        # Simulate streaming by yielding word chunks
        words = text.split(' ')
        buffer = ''
        for word in words:
            buffer += word + ' '
            if len(buffer) >= 20:
                yield buffer
                buffer = ''
        if buffer:
            yield buffer

    def test_connection(self):
        try:
            payload = {
                'inputs': 'Say "Connection successful" in one sentence.',
                'parameters': {'max_new_tokens': 50},
            }
            response = requests.post(
                f'{self.API_URL}{self.model_name}',
                headers=self.headers,
                json=payload,
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
            text = data[0].get('generated_text', '') if isinstance(data, list) else str(data)
            return True, f'Connected. Response: {text[:100]}'
        except Exception as e:
            return False, str(e)

    def _build_prompt(self, messages, system_prompt=None):
        """Convert chat messages to a single prompt string."""
        parts = []
        if system_prompt:
            parts.append(f'System: {system_prompt}')
        for msg in messages:
            role = msg.get('role', 'user').capitalize()
            parts.append(f'{role}: {msg["content"]}')
        parts.append('Assistant:')
        return '\n'.join(parts)
