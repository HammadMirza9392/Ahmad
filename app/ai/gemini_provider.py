"""
Google Gemini Provider
"""
import google.generativeai as genai
from app.ai.base_provider import BaseProvider


class GeminiProvider(BaseProvider):

    def __init__(self, api_key, model_name, **kwargs):
        super().__init__(api_key, model_name, **kwargs)
        genai.configure(api_key=self.api_key)
        self.generation_config = genai.types.GenerationConfig(
            temperature=self.temperature,
            top_p=self.top_p,
            max_output_tokens=self.max_tokens,
        )

    def generate(self, messages, system_prompt=None):
        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_prompt,
        )
        # Convert messages to Gemini format
        history = []
        last_content = ''
        for msg in messages:
            role = 'model' if msg['role'] == 'assistant' else 'user'
            if msg == messages[-1]:
                last_content = msg['content']
            else:
                history.append({'role': role, 'parts': [msg['content']]})

        chat = model.start_chat(history=history)
        response = chat.send_message(last_content, generation_config=self.generation_config)
        metadata = {
            'provider': 'gemini',
            'model': self.model_name,
        }
        return response.text, metadata

    def generate_stream(self, messages, system_prompt=None):
        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_prompt,
        )
        history = []
        last_content = ''
        for msg in messages:
            role = 'model' if msg['role'] == 'assistant' else 'user'
            if msg == messages[-1]:
                last_content = msg['content']
            else:
                history.append({'role': role, 'parts': [msg['content']]})

        chat = model.start_chat(history=history)
        response = chat.send_message(last_content, generation_config=self.generation_config, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text

    def test_connection(self):
        try:
            model = genai.GenerativeModel(model_name=self.model_name)
            response = model.generate_content('Say "Connection successful" in one sentence.')
            return True, f'Connected. Response: {response.text[:100]}'
        except Exception as e:
            return False, str(e)
