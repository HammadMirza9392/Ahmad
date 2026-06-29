"""
OpenRouter Provider
Uses OpenAI-compatible API with OpenRouter base URL.
"""
from openai import OpenAI
from app.ai.base_provider import BaseProvider


class OpenRouterProvider(BaseProvider):

    def __init__(self, api_key, model_name, **kwargs):
        super().__init__(api_key, model_name, **kwargs)
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=kwargs.get('api_base_url', 'https://openrouter.ai/api/v1'),
        )

    def generate(self, messages, system_prompt=None):
        formatted = self._format_messages(messages, system_prompt)
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=formatted,
            temperature=self.temperature,
            top_p=self.top_p,
            max_tokens=self.max_tokens,
        )
        text = response.choices[0].message.content
        metadata = {
            'provider': 'openrouter',
            'model': self.model_name,
            'tokens': response.usage.total_tokens if response.usage else 0,
        }
        return text, metadata

    def generate_stream(self, messages, system_prompt=None):
        formatted = self._format_messages(messages, system_prompt)
        stream = self.client.chat.completions.create(
            model=self.model_name,
            messages=formatted,
            temperature=self.temperature,
            top_p=self.top_p,
            max_tokens=self.max_tokens,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content

    def test_connection(self):
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{'role': 'user', 'content': 'Say "Connection successful" in one sentence.'}],
                max_tokens=50,
            )
            return True, f'Connected. Response: {response.choices[0].message.content[:100]}'
        except Exception as e:
            return False, str(e)
