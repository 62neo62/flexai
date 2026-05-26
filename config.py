from __future__ import annotations

from pathlib import Path


def _default_model_path() -> str:
    # Prefer project-posenet's vendored models, since this repo doesn't include them.
    root = Path(__file__).resolve().parents[1]
    candidate = (
        root
        / "cnnproj"
        / "project-posenet"
        / "models"
        / "mobilenet"
        / "posenet_mobilenet_v1_075_353_481_quant_decoder_edgetpu.tflite"
    )
    return str(candidate)


MODEL_PATH = _default_model_path()

CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

KEYPOINT_THRESHOLD = 0.25
POSE_THRESHOLD = 0.20
ARM_FLEXION_THRESHOLD_DEG = 80

SERVO_SHOULDER = 0
SERVO_ELBOW = 1
SERVO_WRIST = 2
REST_ANGLE = 0

SERVO_I2C_ADDRESS = 0x40
SERVO_CHANNELS = 16
SERVO_MIN_ANGLE = 0
SERVO_MAX_ANGLE = 170
SERVO_PULSE_MIN_US = 500
SERVO_PULSE_MAX_US = 2500

LED_GPIO_PIN = 14

ARM_LINES = [
    ("right shoulder", "right elbow"),
    ("right elbow", "right wrist"),
]

