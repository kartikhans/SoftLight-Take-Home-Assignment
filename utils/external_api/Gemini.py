from google import genai
from google.genai import types
from utils.config import Config


class Gemini:
    def __init__(self):
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.model_name = "gemini-2.5-flash"

    def generate_response(self, prompt, content, model_name=None):
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=content),
        )
        return response.text


if __name__ == "__main__":
    s = Gemini()
    prompt = "Who is the President of United States?"
    print(s.generate_response(prompt=prompt, content="Answer it like a Journalist"))