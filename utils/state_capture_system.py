import time
from task_interpreter import TaskInterpreter
from capture_content import CaptureContent
from state_detector import StateDetector
from screenshot_manager import ScreenshotManager
from config import Config
from constants import test_tasks


class UIStateCaptureSystem:
    def __init__(self, model: str = "chatgpt"):
        self.task_interpreter = TaskInterpreter(model)
        self.browser = CaptureContent(
            headless=False
        )  # Set to True for headless operation
        self.state_detector = StateDetector()
        self.screenshot_manager = ScreenshotManager()

    def execute_task(self, task_description, app_url=None):
        """
        Execute a task and capture UI states
        """
        print(f"\n{'=' * 50}")
        print(f"Executing task: {task_description}")
        print(f"{'=' * 50}")

        try:
            # Step 1: Interpret the task using AI
            print("1. Analyzing task...")
            task_plan = self.task_interpreter.parse_task(task_description)
            print(f"   App: {task_plan.get('app_name', 'Unknown')}")
            print(f"   Steps: {len(task_plan.get('steps', []))}")

            # Step 2: Setup task directory
            task_dir = self.screenshot_manager.setup_task_directory(task_description)
            print(f"2. Task directory: {task_dir}")

            # Step 3: Navigate to starting URL
            starting_url = app_url or task_plan.get("starting_url")
            if starting_url:
                print(f"3. Navigating to: {starting_url}")
                self.browser.navigate_to(starting_url)
            else:
                print("3. No starting URL provided")
                return None

            # Step 4: Capture initial state
            print("4. Capturing initial state...")
            initial_screenshot = self.browser.capture_screenshot()
            if initial_screenshot:
                self.screenshot_manager.save_screenshot(
                    initial_screenshot,
                    "initial_state",
                    {
                        "url": self.browser.get_current_url(),
                        "description": "Initial page state",
                    },
                )

            # Step 5: Execute each step
            steps = task_plan.get("steps", [])
            for i, step in enumerate(steps):
                print(step)
                step_num = i + 1
                action = step.get("action", "click")
                target = step.get("target_element", "")
                description = step.get("description", "")

                print(f"5.{step_num} Executing: {action} '{target}' - {description}")

                # Perform the action
                if action.lower() in ["click", "select", "choose", "press"]:
                    success = self.browser.find_and_click(target)

                    if success:
                        # Capture state after action
                        time.sleep(Config.WAIT_TIME)
                        screenshot = self.browser.capture_screenshot()

                        if screenshot and self.state_detector.has_ui_changed(
                            screenshot
                        ):
                            self.screenshot_manager.save_screenshot(
                                screenshot,
                                f"step_{step_num}_{target.replace(' ', '_')}",
                                {
                                    "url": self.browser.get_current_url(),
                                    "action": action,
                                    "target": target,
                                    "description": description,
                                    "success": True,
                                },
                            )
                            print(f"   ✓ State captured")
                        else:
                            print(f"   ⚠ No significant UI change detected")
                    else:
                        print(f"   ✗ Failed to find/click element")
                        # Still capture screenshot for debugging
                        screenshot = self.browser.capture_screenshot()
                        if screenshot:
                            self.screenshot_manager.save_screenshot(
                                screenshot,
                                f"step_{step_num}_failed_{target.replace(' ', '_')}",
                                {
                                    "url": self.browser.get_current_url(),
                                    "action": action,
                                    "target": target,
                                    "description": description,
                                    "success": False,
                                },
                            )

            # Step 6: Save task metadata
            self.screenshot_manager.save_task_metadata(task_description, starting_url)

            # Step 7: Return results
            results = self.screenshot_manager.get_captured_states()
            print(f"\nTask completed! Captured {len(results)} UI states")
            print(f"Results saved in: {task_dir}")

            return results

        except Exception as e:
            print(f"Error executing task: {e}")
            return None

    def cleanup(self):
        """Let's clean up all used resources"""
        self.browser.close_browser()
        self.state_detector.reset()
        self.screenshot_manager.reset()


def main(model: str = "chatgpt"):
    # Create system instance
    system = UIStateCaptureSystem(model=model)

    try:
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

        # Execute the task
        results = system.execute_task(task_description, app_url)

        if results:
            print(f"\n🎉 Successfully captured {len(results)} UI states!")
            print("Check the 'captured_states' folder for results.")
        else:
            print("\n❌ Task execution failed")

    except KeyboardInterrupt:
        print("\n\nExecution interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        system.cleanup()


if __name__ == "__main__":
    model = input("Which model would you like to use for Task Interpretation: ")
    main(model)
