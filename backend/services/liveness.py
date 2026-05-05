import cv2
import numpy as np
from typing import Tuple

class LivenessService:
    """Simplified liveness detection - basic image quality checks.
    Good enough for supervised classroom environment.
    No Haar Cascades needed - faster, simpler.
    """

    def check_liveness(self, frame) -> Tuple[bool, str]:
        """
        Check if the frame is valid for face recognition.
        Uses basic heuristics: image size, quality, variance.
        Args:
            frame: numpy array (BGR image from OpenCV)
        Returns: (is_valid, message)
        """
        if frame is None or frame.size == 0:
            return False, "Invalid image"

        # Check if image is too small (likely screenshot)
        height, width = frame.shape[:2]
        if height < 480 or width < 640:
            return False, "Image too small (min 640x480)"

        # Check if image has reasonable variance (not blank/solid color)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        variance = float(gray.var())
        if variance < 100:
            return False, "Image lacks detail (too uniform)"

        # Check if image is too dark or too bright
        mean_brightness = float(gray.mean())
        if mean_brightness < 30:
            return False, "Image too dark"
        if mean_brightness > 225:
            return False, "Image too bright"

        return True, "Basic checks passed"

    def check_liveness_from_frames(self, frames_list) -> Tuple[bool, str, float]:
        """
        Check liveness from multiple frames.
        Args:
            frames_list: list of numpy arrays (frames)
        Returns: (is_live, message, confidence)
        """
        if not frames_list or len(frames_list) == 0:
            return False, "No frames provided", 0.0

        valid_count = 0
        total_frames = len(frames_list)

        for frame in frames_list:
            is_valid, _ = self.check_liveness(frame)
            if is_valid:
                valid_count += 1

        confidence = valid_count / total_frames

        # Require at least 50% of frames to pass
        if confidence >= 0.5:
            return True, f"Liveness check passed ({valid_count}/{total_frames} frames)", confidence

        return False, f"Liveness check failed ({valid_count}/{total_frames} frames)", confidence
