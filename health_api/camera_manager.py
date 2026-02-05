import cv2
import numpy as np
from threading import Lock

from core.app_context import AppContext


class CameraManager:
    """
    High‑reliability camera abstraction for the Ingenious Irrigation OS.

    Features:
    - Auto‑initializing OpenCV VideoCapture
    - Automatic recovery if the camera disconnects
    - Synthetic fallback frames when hardware is unavailable
    - Thread‑safe capture (important for async API + background tasks)
    - Designed for Pi Camera, USB webcams, and virtual cameras
    """

    def __init__(self, ctx: AppContext, camera_index: int = 0):
        self.ctx = ctx
        self.logger = getattr(self.ctx, "logger", None)
        self.camera_index = camera_index

        self.cap = None
        self.lock = Lock()

        self._init_camera()

    # ------------------------------------------------------------
    # Logging helper
    # ------------------------------------------------------------
    def _log(self, level: str, msg: str, *args):
        if self.logger:
            getattr(self.logger, level)(msg, *args)

    # ------------------------------------------------------------
    # Camera initialization
    # ------------------------------------------------------------
    def _init_camera(self):
        """
        Attempt to initialize the camera. If unavailable, fall back to synthetic frames.
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_index)

            if not self.cap.isOpened():
                self._log(
                    "warning",
                    "Camera not available at index %s. Using synthetic frames.",
                    self.camera_index,
                )
                self.cap = None
            else:
                self._log("info", "Camera initialized at index %s", self.camera_index)

        except Exception as e:
            self._log("exception", "Camera initialization error: %s", e)
            self.cap = None

    # ------------------------------------------------------------
    # Frame capture
    # ------------------------------------------------------------
    def capture_frame(self):
        """
        Capture a frame from the camera.

        Returns:
            np.ndarray (BGR) frame
        """
        with self.lock:
            if self.cap is not None:
                try:
                    ret, frame = self.cap.read()
                    if ret and frame is not None:
                        return frame

                    # If read fails, try to reinitialize once
                    self._log("warning", "Camera read failed. Attempting reinitialization.")
                    self._init_camera()

                    if self.cap is not None:
                        ret, frame = self.cap.read()
                        if ret and frame is not None:
                            return frame

                except Exception as e:
                    self._log("exception", "Camera capture error: %s", e)

            # If we reach here, camera is unavailable
            self._log("info", "Using synthetic fallback frame.")
            return self._synthetic_frame()

    # ------------------------------------------------------------
    # Synthetic fallback frame
    # ------------------------------------------------------------
    def _synthetic_frame(self):
        """
        Generate a synthetic frame that resembles a lawn.
        This ensures the AI pipeline never breaks, even with no camera.
        """
        h, w = 480, 640
        frame = np.zeros((h, w, 3), dtype="uint8")

        # Base green
        frame[:, :] = (40, 160, 40)  # BGR

        # Add subtle texture
        cv2.rectangle(frame, (50, 100), (w - 50, h - 50), (50, 180, 50), thickness=-1)

        # Add noise for realism
        noise = np.random.randint(0, 15, (h, w, 3), dtype="uint8")
        frame = cv2.add(frame, noise)

        return frame

    # ------------------------------------------------------------
    # Release camera
    # ------------------------------------------------------------
    def release(self):
        """
        Release the camera resource cleanly.
        """
        with self.lock:
            if self.cap is not None:
                try:
                    self.cap.release()
                    self._log("info", "Camera released.")
                except Exception as e:
                    self._log("exception", "Error releasing camera: %s", e)
