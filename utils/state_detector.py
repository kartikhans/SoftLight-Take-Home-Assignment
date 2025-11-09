import cv2
import numpy as np
from PIL import Image
import io
from skimage.metrics import structural_similarity as ssim
from config import Config


class StateDetector:
    def __init__(self):
        self.previous_state = None
        self.threshold = Config.SIMILARITY_THRESHOLD

    def has_ui_changed(self, current_screenshot):
        """
        Detect if UI state has significantly changed using structural similarity
        """
        if self.previous_state is None:
            self.previous_state = current_screenshot
            return True

        try:
            # Convert screenshots to numpy arrays
            current_img = np.array(Image.open(io.BytesIO(current_screenshot)))
            prev_img = np.array(Image.open(io.BytesIO(self.previous_state)))

            # Resize to same dimensions if needed
            if current_img.shape != prev_img.shape:
                prev_img = cv2.resize(
                    prev_img, (current_img.shape[1], current_img.shape[0])
                )

            # Convert to grayscale
            current_gray = cv2.cvtColor(current_img, cv2.COLOR_RGB2GRAY)
            prev_gray = cv2.cvtColor(prev_img, cv2.COLOR_RGB2GRAY)

            # Calculate structural similarity
            similarity_score, _ = ssim(current_gray, prev_gray, full=True)

            self.previous_state = current_screenshot
            return similarity_score < (1 - self.threshold)

        except Exception as e:
            print(f"Error in UI change detection: {e}")
            # If comparison fails, assume change occurred
            self.previous_state = current_screenshot
            return True

    def reset(self):
        self.previous_state = None
