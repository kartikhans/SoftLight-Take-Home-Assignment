from xai_sdk import Client
from xai_sdk.chat import user, system
from utils.config import Config

class GrokClient:
    def __init__(self):
        self.model_name = "grok-4-fast-reasoning"
        self.client = Client(
            api_key=Config.GROK_API_KEY,
            timeout=3600, # Override default timeout with longer timeout for reasoning models
        )
    def generate_response(self, prompt, content, model_name=None):
        if model_name is not None:
            self.model_name = model_name

        chat = self.client.chat.create(model=self.model_name)
        chat.append(system(content))
        chat.append(user(prompt))

        response = chat.sample()
        return response.content