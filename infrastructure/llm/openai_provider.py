from openai import OpenAI

class OpenAIProvider:
    def __init__(self, config_provider):
        self.config_provider = config_provider
        self.api_key = self.config_provider.get_secret('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key)
    def generate_completion(self, messages, model, max_tokens):
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.5,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    def is_configured(self):
        return bool(self.api_key)
