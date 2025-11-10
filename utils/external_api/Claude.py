from anthropic import Anthropic
from utils.config import Config


class Claude:
    def __init__(self):
        self.client = Anthropic(api_key=Config.CLAUDE_API_KEY)
        self.model_name = ""
        self.get_model()

    def get_model(self):
        models = self.client.models.list(limit=1).data
        if not models:
            self.model_name = "claude-haiku-4-5-20251001"
        self.model_name = models[0].id

    def generate_response(self, prompt, content, model_name=None):
        if model_name is None:
            model_name = self.model_name

        message = self.client.messages.create(
            model=model_name,
            max_tokens=1024,
            system=content,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )

        return message.content[0].text


if __name__ == "__main__":
    s = Claude()
    prompt = "Who is the President of United States?"
    print(
        s.generate_response(
            prompt=prompt, content="You're a journalist and write it that way."
        )
    )
