from openai import OpenAI
from utils.config import Config


class ChatGpt:
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model_name = "gpt-3.5-turbo"

    def generate_response(
            self,
            content,
            prompt,
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
            with open(f"ChatGptReplies/xyz.txt", "w") as f:
                f.write(completion.choices[0].message.content)
                f.close()
                return
        return completion.choices[0].message.content


if __name__ == "__main__":
    s = ChatGpt()
    prompt = "Cease-fire between Israel and Hamas finally decided and peace is there. Teach us about cease-fire and why is it crucial? Elaborate it"
    # print(s.generate_response(model_name="gpt-4o", content=SYSTEM_ROLE.get("JOURNALIST")))