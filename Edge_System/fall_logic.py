"""
Simple fall logic based on bounding box aspect ratio.
"""
from dataclasses import dataclass


@dataclass
class PersonState:
    is_lying: bool
    bbox: tuple  # (x1, y1, x2, y2)


def is_lying_down(bbox, ratio_threshold=1.3):
    """
    bbox: (x1, y1, x2, y2)
    ratio = width / height
    If ratio exceeds threshold, treat as lying down.
    """
    x1, y1, x2, y2 = bbox
    w = x2 - x1
    h = y2 - y1
    if h == 0:
        return False
    ratio = w / h
    return ratio > ratio_threshold


def detect_fall(prev_state: "PersonState | None", curr_state: PersonState):
    """
    Detect fall when previous frame was standing and current is lying.
    """
    if prev_state is None:
        return False
    return (not prev_state.is_lying) and curr_state.is_lying
