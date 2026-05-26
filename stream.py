import math
import time

from .config import ARM_LINES, POSE_THRESHOLD, SERVO_MAX_ANGLE
from .pose_math import arm_is_flexed, angle_degrees, get_keypoints


def generate_frames(*, engine, hw, input_width: int, input_height: int):
    import cv2
    from PIL import Image
    from . import pose_engine

    prev_time = time.time()

    while True:
        ret, frame = hw.cap.read()

        if not ret:
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb)

        image_width, image_height = pil_image.size
        scale_x = image_width / input_width
        scale_y = image_height / input_height

        poses, _inference_time = engine.DetectPosesInImage(pil_image)

        for pose in poses:
            for label in pose.keypoints:
                kp = pose.keypoints[label]
                new_point = pose_engine.Point(kp.point[0] * scale_x, kp.point[1] * scale_y)
                pose.keypoints[label] = pose_engine.Keypoint(new_point, kp.score)

        left_flexed = False
        right_flexed = False
        left_angle = None
        right_angle = None

        shoulder_angle = None
        elbow_angle_val = None
        wrist_angle_val = None

        for pose in poses:
            if pose.score < POSE_THRESHOLD:
                continue

            points = get_keypoints(pose)

            for name, point in points.items():
                cv2.circle(frame, point, 5, (0, 255, 0), -1)
                cv2.putText(
                    frame,
                    name,
                    (point[0] + 5, point[1] - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (0, 255, 0),
                    1,
                )

            for a, b in ARM_LINES:
                if a in points and b in points:
                    cv2.line(frame, points[a], points[b], (255, 0, 0), 2)

            if "right shoulder" in points and "right elbow" in points and "right wrist" in points:
                shoulder = points["right shoulder"]
                elbow = points["right elbow"]
                wrist = points["right wrist"]

                vec_x = elbow[0] - shoulder[0]
                vec_y = elbow[1] - shoulder[1]
                mag_vec = math.sqrt(vec_x**2 + vec_y**2)
                if mag_vec > 0:
                    cos_angle = vec_y / mag_vec
                    angle_rad = math.acos(max(-1.0, min(1.0, cos_angle)))
                    shoulder_angle = math.degrees(angle_rad)
                    shoulder_servo = (shoulder_angle / 180.0) * SERVO_MAX_ANGLE
                else:
                    shoulder_servo = 0.0

                elbow_angle_val = angle_degrees(shoulder, elbow, wrist)
                elbow_servo = (elbow_angle_val / 180.0) * SERVO_MAX_ANGLE

                wrist_vec_x = wrist[0] - elbow[0]
                wrist_vec_y = wrist[1] - elbow[1]
                wrist_angle_rad = math.atan2(wrist_vec_y, wrist_vec_x)
                wrist_angle_deg = math.degrees(wrist_angle_rad)
                if wrist_angle_deg < 0:
                    wrist_angle_deg += 360
                wrist_angle_val = wrist_angle_deg
                wrist_servo = (wrist_angle_deg / 360.0) * SERVO_MAX_ANGLE

                hw.set_servos(shoulder=shoulder_servo, elbow=elbow_servo, wrist=wrist_servo)

            left_flexed, left_angle = arm_is_flexed(points, "left")
            right_flexed, right_angle = arm_is_flexed(points, "right")

        if left_flexed or right_flexed:
            hw.led.on()
        else:
            hw.led.off()

        status_y = 30

        if shoulder_angle is not None:
            cv2.putText(
                frame,
                f"Shoulder angle: {shoulder_angle:.1f}",
                (10, status_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2,
            )
            status_y += 25

        if elbow_angle_val is not None:
            cv2.putText(
                frame,
                f"Elbow angle: {elbow_angle_val:.1f}",
                (10, status_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2,
            )
            status_y += 25

        if wrist_angle_val is not None:
            cv2.putText(
                frame,
                f"Wrist angle: {wrist_angle_val:.1f}",
                (10, status_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2,
            )
            status_y += 25

        if left_angle is not None:
            cv2.putText(
                frame,
                f"Left arm angle: {left_angle:.1f} {'FLEXED' if left_flexed else ''}",
                (10, status_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2,
            )
            status_y += 25

        if right_angle is not None:
            cv2.putText(
                frame,
                f"Right arm angle: {right_angle:.1f} {'FLEXED' if right_flexed else ''}",
                (10, status_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2,
            )
            status_y += 25

        fps = 1.0 / max(time.time() - prev_time, 1e-6)
        prev_time = time.time()

        cv2.putText(
            frame,
            f"FPS: {fps:.1f}",
            (10, status_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2,
        )

        ok, buffer = cv2.imencode(".jpg", frame)
        if not ok:
            continue

        jpg = buffer.tobytes()
        yield b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + jpg + b"\r\n"

