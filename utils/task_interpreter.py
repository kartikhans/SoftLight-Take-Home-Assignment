import json
import re
from utils.external_api.ChatGpt import ChatGpt
from utils.external_api.Claude import Claude
from utils.external_api.Gemini import Gemini
from utils.external_api.DeepSeek import DeepSeek


class TaskInterpreter:
    def __init__(self, model: str = "chatgpt"):
        if model in ["deepseek"]:
            self.model_client = DeepSeek()
        elif model in ["gemini"]:
            self.model_client = Gemini()
        elif model in ["claude"]:
            self.model_client = Claude()
        else:
            self.model_client = ChatGpt()

    def parse_task(self, task_description, history, current_dom):
        """Use AI to break down tasks into actionable steps"""
        prompt = f"""
                    ---
                    Main Task: {task_description}
                    ---
                    Action History:
                    {json.dumps(history, indent=2) if history else "No actions taken yet."}
                    ---
                    Current Simplified DOM:
                    {current_dom}
                    ---
                    What is your next single JSON action?
                """

        try:
            content = """
                        You are an expert AI agent controlling a web browser.
                        Your goal is to accomplish a user's task.
                        
                        You will be given:
                        1.  The main task.
                        2.  A history of your previous actions.
                        3.  The current simplified DOM of the page, showing only interactive elements.
                        
                        You must decide the single next action to take.
                        Your available actions are:
                        1.  {"action": "CLICK", "element_id": <id>, "reason": "why I am clicking this"}
                        2.  {"action": "TYPE", "element_id": <id>, "text": "<text_to_type>", "reason": "why I am typing this"}
                        3.  {"action": "PRESS_KEY", "key": "<key_name>", "reason": "why I am pressing this key"} (e.g., "Enter", "Tab")
                        4.  {"action": "FINISH", "reason": "The task is fully complete"}
                        
                        RULES:
                        - Respond with *only* a single, valid JSON object.
                        - Look at the DOM and pick the best `element_id` to interact with.
                        - The `element_id` is a number (e.g., 1, 2, 3...).
                        - Do not make up IDs. Only use IDs from the current DOM.
                        - Think step-by-step to get closer to the main task.
                    """
            result = self.model_client.generate_response(prompt=prompt, content=content)

            # Clean the response
            result = re.sub(r"```json\s*|\s*```", "", result).strip()
            print(f"[LLM Decision]: {result}")

            return json.loads(result)

        except Exception as e:
            print(f"Error parsing task: {e}")
            # Return a fallback structure
            return {"action": "FINISH", "reason": f"Error occurred: {e}"}