from __future__ import annotations

import math

from .config import ARM_FLEXION_THRESHOLD_DEG, KEYPOINT_THRESHOLD


def keypoint_name(label) -> str:
    text = str(label).lower()
    text = text.replace("keypointtype.", "")
    text = text.replace("_", " ")
    return text.strip()


def angle_degrees(a, b, c) -> float:
    ax, ay = a
    bx, by = b
    cx, cy = c

    ba_x = ax - bx
    ba_y = ay - by

    bc_x = cx - bx
    bc_y = cy - by

    dot = ba_x * bc_x + ba_y * bc_y

    mag_ba = math.sqrt(ba_x**2 + ba_y**2)
    mag_bc = math.sqrt(bc_x**2 + bc_y**2)

    if mag_ba == 0 or mag_bc == 0:
        return 0.0

    cos_angle = dot / (mag_ba * mag_bc)
    cos_angle = max(-1.0, min(1.0, cos_angle))

    return math.degrees(math.acos(cos_angle))


def get_keypoints(pose) -> dict[str, tuple[int, int]]:
    points: dict[str, tuple[int, int]] = {}

    for label, keypoint in pose.keypoints.items():
        if keypoint.score < KEYPOINT_THRESHOLD:
            continue

        name = keypoint_name(label)
        x = int(keypoint.point[0])
        y = int(keypoint.point[1])

        points[name] = (x, y)

    return points


def hand_distance(points: dict[str, tuple[int, int]]) -> float | None:
    if "left wrist" not in points or "right wrist" not in points:
        return None
    lw = points["left wrist"]
    rw = points["right wrist"]
    return math.sqrt((lw[0] - rw[0]) ** 2 + (lw[1] - rw[1]) ** 2)


def arm_is_flexed(points: dict[str, tuple[int, int]], side: str) -> tuple[bool, float | None]:
    shoulder = f"{side} shoulder"
    elbow = f"{side} elbow"
    wrist = f"{side} wrist"

    if shoulder not in points or elbow not in points or wrist not in points:
        return False, None

    angle = angle_degrees(points[shoulder], points[elbow], points[wrist])
    return angle < ARM_FLEXION_THRESHOLD_DEG, angle

