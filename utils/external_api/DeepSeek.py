from openai import OpenAI
from utils.config import Config


class DeepSeek:
    def __init__(self):
        self.client = OpenAI(
            api_key=Config.DEEPSEEK_API_KEY, base_url=Config.DEEPSEEK_BASE_URL
        )
        self.model_name = "deepseek-chat"

    def generate_response(
            self,
            prompt,
            content,
            model_name=None,
            temperature=0.7,
            write_file=False,
    ):
        if model_name is not None:
            self.model_name = model_name
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "user", "content": prompt},
                {
                    "role": "system",
                    "content": content,
                },
            ],
            temperature=temperature,
            max_tokens=3000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        if write_file:
            with open(f"DeepSeekReplies/Christmas.txt", "w") as f:
                f.write(completion.choices[0].message.content)
                f.close()
                return
        return completion.choices[0].message.content


if __name__ == "__main__":
    s = DeepSeek()
    prompt = "Cease-fire between Israel and Hamas finally decided and peace is there. Teach us about cease-fire and why is it crucial?"
    print(s.generate_response(prompt=prompt, content="You're a journalist"))