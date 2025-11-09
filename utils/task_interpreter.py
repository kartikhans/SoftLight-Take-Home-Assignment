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

    def parse_task(self, task_description):
        """Use AI to break down tasks into actionable steps"""
        prompt = f"""
        Analyze this user task and break it down into specific UI interaction steps.
        Task: "{task_description}"
        
        Return a JSON response with this structure:
        {{
            "app_name": "name of the web application",
            "starting_url": "appropriate starting URL or null if not specific",
            "steps": [
                {{
                    "step_number": number,
                    "action": "specific action to perform",
                    "target_element": "what UI element_id to look for",
                    "description": "what should happen in this step"
                }}
            ]
        }}
        
        Be very specific about the UI elements and actions.
        """

        try:
            # content = """You are a web automation expert. Break down tasks into clear UI interaction steps.
            # You must decide the action to take.
            #     Your available actions are:
            #     1.  {"action": ["CLICK", "SELECT", "CHOOSE", "PRESS"], "element_id": <id>, "reason": "why I am clicking this"}
            #     2.  {"action": "TYPE", "element_id": <id>, "text": "<text_to_type>", "reason": "why I am typing this"}
            #     3.  {"action": "FINISH", "reason": "The task is complete"}"""
            content = """You are a web automation expert. Break down tasks into clear UI interaction steps.
            You must decide the action to take.
                Your available actions are:
                1.  {"action": ["CLICK", "SELECT", "CHOOSE", "PRESS"]}
                2.  {"action": "TYPE"}
                """
            result = self.model_client.generate_response(prompt=prompt, content=content)

            # Clean the response
            result = re.sub(r"```json\s*|\s*```", "", result).strip()

            return json.loads(result)

        except Exception as e:
            print(f"Error parsing task: {e}")
            # Return a fallback structure
            return {
                "app_name": "web_app",
                "starting_url": None,
                "steps": [
                    {
                        "step_number": 1,
                        "action": "navigate",
                        "target_element": "main page",
                        "description": "Start from the main page",
                    }
                ],
            }
