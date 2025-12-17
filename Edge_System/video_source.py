"""
Video capture helper.
Opens a USB webcam (0), RTSP stream, HTTP stream, or video file.
"""
import cv2
import os


def get_capture(source=0):
    """
    source:
      0 → webcam
      'rtsp://...' → RTSP IP camera
      'http://...' → HTTP stream (e.g., IP Webcam app)
      'path/to/video.mp4' → Video file (mp4, avi, mov, etc.)
    
    Returns:
        cv2.VideoCapture object
    """
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video source: {source}")
    return cap


def is_video_file(source):
    """Check if source is a video file path."""
    return isinstance(source, str) and os.path.isfile(source)
