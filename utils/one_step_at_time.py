import os
import re
import time
from playwright.sync_api import sync_playwright
from task_interpreter import TaskInterpreter
from state_detector import StateDetector
from utils.constants import test_tasks


class OneStepAtTime:
    def __init__(self, model):
        self.task_interpreter = TaskInterpreter(model)
        self.state_detector = StateDetector()

    def decide_next_action(self, task: str, history: list, current_dom: str) -> dict:
        result = self.task_interpreter.parse_task(task, history, current_dom)
        return result

    def run_agent(self, task: str, start_url: str, max_steps: int = 15):
        sanitized_task = re.sub(r'[^a-zA-Z0-9_-]', '_', task.lower())[:50]
        screenshot_dir = f"screenshots/{sanitized_task}"
        action_history = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=500)
            page = browser.new_page()
            page.goto(start_url)

            try:
                for i in range(max_steps):
                    print(f"\n--- Step {i+1} ---")

                    # Give the page a moment to settle
                    time.sleep(1)

                    dom_string = self.state_detector.get_simplified_dom_string(page)

                    screenshot_path = os.path.join(screenshot_dir, f"{i+1:02d}_state.png")
                    self.state_detector.capture_screenshot(page, screenshot_path)

                    if not dom_string:
                        print("DOM string is empty, cannot proceed.")
                        break

                    llm_decision = self.task_interpreter.parse_task(
                        task_description=task,
                        history=action_history,
                        current_dom=dom_string
                    )

                    action_history.append(llm_decision)
                    action_type = llm_decision.get("action")

                    if action_type == "CLICK":
                        element_id = llm_decision.get("element_id")
                        print(f"[Action]: Clicking element {element_id}")
                        self.state_detector.click_element(page, str(element_id))

                    elif action_type == "TYPE":
                        element_id = llm_decision.get("element_id")
                        text = llm_decision.get("text")
                        print(f"[Action]: Typing '{text}' into element {element_id}")
                        self.state_detector.type_in_element(page, str(element_id), text)

                    elif action_type == "PRESS_KEY":
                        key = llm_decision.get("key")
                        print(f"[Action]: Pressing key '{key}'")
                        self.state_detector.press_key(page, key)

                    elif action_type == "FINISH":
                        print("[Action]: Task finished.")
                        screenshot_path = os.path.join(screenshot_dir, f"{i+2:02d}_final_state.png")
                        self.state_detector.capture_screenshot(page, screenshot_path)
                        break
                    else:
                        print(f"Unknown action: {action_type}")
                        break

                print("\n--- Loop finished ---")

            except Exception as e:
                print(f"An error occurred: {e}")
            finally:
                print("Closing browser.")
                browser.close()

if __name__ == "__main__":
    model = input("Which model would you like to use for Task Interpretation: ")
    k = OneStepAtTime(model)

    example_tasks = test_tasks

    print("UI State Capture System")
    print("Available example tasks:")

    for i, task in enumerate(example_tasks, 1):
        print(f"{i}. {task.get('description')}")

    # Let user choose the task
    choice = input(
        f"\nChoose task (1-{len(example_tasks)}) or enter custom task: "
    ).strip()

    if choice.isdigit() and 1 <= int(choice) <= len(example_tasks):
        task = example_tasks[int(choice) - 1]
        task_description = task.get("description")
        app_url = task.get("url")
    else:
        task_description = choice
        app_url = input(
            "Enter app URL (or press Enter for auto-detection): "
        ).strip()
        if not app_url:
            app_url = None

    if not os.environ.get("OPENAI_API_KEY"):
        print("="*50)
        print("ERROR: OPENAI_API_KEY environment variable not set.")
        print("Please set your API key before running.")
        print("="*50)
    else:
        print("\n\n--- Starting Task ---")
        k.run_agent(task=task_description, start_url=app_url)