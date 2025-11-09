import os
import json
from datetime import datetime


class ScreenshotManager:
    def __init__(self, base_dir="captured_states"):
        self.base_dir = base_dir
        self.current_task_dir = None
        self.captured_states = []

    def setup_task_directory(self, task_name):
        """Create directory for current task"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_task_name = "".join(
            c for c in task_name if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()
        safe_task_name = safe_task_name.replace(" ", "_")[:50]

        self.current_task_dir = os.path.join(
            self.base_dir, f"{timestamp}_{safe_task_name}"
        )
        os.makedirs(self.current_task_dir, exist_ok=True)

        return self.current_task_dir

    def save_screenshot(self, screenshot_data, step_name, metadata=None):
        """Save screenshot and return file path"""
        if not self.current_task_dir:
            raise Exception(
                "Task directory not set up. Call setup_task_directory first."
            )

        filename = f"{len(self.captured_states)}_{step_name}.png"
        filepath = os.path.join(self.current_task_dir, filename)

        # Save the screenshot
        with open(filepath, "wb") as f:
            f.write(screenshot_data)

        # Store metadata
        state_info = {
            "step": len(self.captured_states),
            "name": step_name,
            "filepath": filepath,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        self.captured_states.append(state_info)

        return filepath

    def save_task_metadata(self, task_description, app_url):
        """Save task metadata as JSON"""
        if not self.current_task_dir:
            return

        metadata = {
            "task_description": task_description,
            "app_url": app_url,
            "captured_at": datetime.now().isoformat(),
            "states": self.captured_states,
        }

        metadata_path = os.path.join(self.current_task_dir, "metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

    def get_captured_states(self):
        return self.captured_states

    def reset(self):
        self.captured_states = []
        self.current_task_dir = None
