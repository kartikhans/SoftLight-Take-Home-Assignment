from utils.config import Config
from perplexity import Perplexity

class Perplex:
    def __init__(self):
        self.client = Perplexity(api_key=Config.PERPLEXITY_API_KEY)
        self.model_name = "sonar-pro"

    def generate_response(self, prompt, content, model_name=None):
        if model_name is not None:
            self.model_name = model_name
        messages = [
            {
                "role": "system",
                "content": content,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
        )

        return response.choices[0].message.content


if __name__ == "__main__":
    s = Perplex()
    prompt = "Who is the President of the United Statues?"
    content = "You're a journalist"
    print(s.generate_response(prompt, content))
