from .config import (
    CAMERA_INDEX,
    CLAW_MAX_ANGLE,
    FRAME_HEIGHT,
    FRAME_WIDTH,
    LED_GPIO_PIN,
    REST_ANGLE,
    SERVO_CHANNELS,
    SERVO_CLAW,
    SERVO_ELBOW,
    SERVO_I2C_ADDRESS,
    SERVO_MAX_ANGLE,
    SERVO_MIN_ANGLE,
    SERVO_PULSE_MAX_US,
    SERVO_PULSE_MIN_US,
    SERVO_SHOULDER,
    SERVO_WRIST,
)


class Hardware:
    def __init__(self) -> None:
        import cv2
        from adafruit_servokit import ServoKit
        from gpiozero import LED

        self.led = LED(LED_GPIO_PIN)

        self.kit = ServoKit(channels=SERVO_CHANNELS, address=SERVO_I2C_ADDRESS)
        self.kit.servo[SERVO_SHOULDER].set_pulse_width_range(SERVO_PULSE_MIN_US, SERVO_PULSE_MAX_US)
        self.kit.servo[SERVO_ELBOW].set_pulse_width_range(SERVO_PULSE_MIN_US, SERVO_PULSE_MAX_US)
        self.kit.servo[SERVO_WRIST].set_pulse_width_range(SERVO_PULSE_MIN_US, SERVO_PULSE_MAX_US)
        self.kit.servo[SERVO_CLAW].set_pulse_width_range(SERVO_PULSE_MIN_US, SERVO_PULSE_MAX_US)
        self.kit.servo[SERVO_SHOULDER].angle = REST_ANGLE
        self.kit.servo[SERVO_ELBOW].angle = REST_ANGLE
        self.kit.servo[SERVO_WRIST].angle = REST_ANGLE
        self.kit.servo[SERVO_CLAW].angle = REST_ANGLE

        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

        if not self.cap.isOpened():
            raise RuntimeError("Could not open camera. Try CAMERA_INDEX = 1.")

    def set_servos(self, *, shoulder: float, elbow: float, wrist: float) -> None:
        self.kit.servo[SERVO_SHOULDER].angle = max(SERVO_MIN_ANGLE, min(SERVO_MAX_ANGLE, shoulder))
        self.kit.servo[SERVO_ELBOW].angle = max(SERVO_MIN_ANGLE, min(SERVO_MAX_ANGLE, elbow))
        self.kit.servo[SERVO_WRIST].angle = max(SERVO_MIN_ANGLE, min(SERVO_MAX_ANGLE, wrist))

    def set_claw(self, angle: float) -> None:
        self.kit.servo[SERVO_CLAW].angle = max(SERVO_MIN_ANGLE, min(CLAW_MAX_ANGLE, angle))

    def close(self) -> None:
        try:
            if getattr(self, "cap", None) is not None:
                self.cap.release()
        finally:
            if getattr(self, "led", None) is not None:
                self.led.off()
                self.led.close()

