"""
Edge loop: capture video, run YOLO, simple fall detection, and send to server.
"""
import os
import time
from datetime import datetime

import cv2
import numpy as np
from ultralytics import YOLO

from video_source import get_capture, is_video_file
from fall_logic import PersonState, is_lying_down, detect_fall
from sender import send_fall_event

SAVE_DIR = "captured"
os.makedirs(SAVE_DIR, exist_ok=True)


def create_frame_sequence_image(frames, cols=5):
    """
    Create a composite image showing a sequence of frames in a grid.
    frames: list of frames to combine
    cols: number of columns in the grid
    """
    if not frames:
        return None
    
    # Calculate grid dimensions
    num_frames = len(frames)
    rows = (num_frames + cols - 1) // cols  # Ceiling division
    
    # Get frame dimensions
    h, w = frames[0].shape[:2]
    
    # Create composite image
    composite = np.zeros((h * rows, w * cols, 3), dtype=np.uint8)
    
    for i, frame in enumerate(frames):
        row = i // cols
        col = i % cols
        y_start = row * h
        y_end = y_start + h
        x_start = col * w
        x_end = x_start + w
        
        # Resize frame if needed and place in composite
        if frame.shape[:2] != (h, w):
            frame = cv2.resize(frame, (w, h))
        composite[y_start:y_end, x_start:x_end] = frame
        
        # Add frame number label
        cv2.putText(composite, f"T-{num_frames-i-1}", 
                   (x_start + 10, y_start + 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    return composite


def run_edge(source=0):
    cap = get_capture(source)
    model = YOLO("yolov8n.pt")
    prev_state = None
    last_fall_time = None  # Track last fall detection time for cooldown
    COOLDOWN_SECONDS = 10  # 10 seconds cooldown between fall detections
    
    # Frame buffer to store recent frames (1-2 seconds before fall)
    frame_buffer = []
    BUFFER_SECONDS = 2  # Store 2 seconds of frames before fall
    buffer_max_size = None  # Will be set based on FPS
    
    # For video files, calculate delay based on FPS
    is_file = is_video_file(source)
    if is_file:
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 30  # Default FPS if cannot detect
        delay_ms = int(1000 / fps)  # Delay in milliseconds
        buffer_max_size = int(fps * BUFFER_SECONDS)  # Store 2 seconds of frames
        print(f"Processing video file at {fps:.2f} FPS")
    else:
        delay_ms = 1  # Minimal delay for live camera
        buffer_max_size = 60  # Default: 60 frames for live camera (assuming ~30fps)

    while True:
        ret, frame = cap.read()
        if not ret:
            if is_file:
                print("Video ended. Press 'q' to exit or restart.")
                # Optionally loop the video
                # cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                # continue
            break

        # Store frame in buffer (before processing)
        frame_buffer.append(frame.copy())
        # Keep only recent frames (1-2 seconds)
        if len(frame_buffer) > buffer_max_size:
            frame_buffer.pop(0)
        
        # YOLO inference
        results = model(frame, verbose=False)[0]

        # Debug: Print detection info (first few frames only)
        if not hasattr(run_edge, '_debug_count'):
            run_edge._debug_count = 0
        if run_edge._debug_count < 5:
            print(f"Frame {run_edge._debug_count}: Detected {len(results.boxes)} objects")
            if len(results.boxes) > 0:
                for i, box in enumerate(results.boxes[:3]):  # Show first 3
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    print(f"  Object {i}: class_id={cls_id}, confidence={conf:.2f}")
            run_edge._debug_count += 1

        # Use the largest person bbox
        person_bbox = None
        max_area = 0
        person_count = 0
        for box in results.boxes:
            cls_id = int(box.cls[0])
            if cls_id != 0:  # 0 is person class in COCO dataset
                continue
            person_count += 1
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            area = (x2 - x1) * (y2 - y1)
            if area > max_area:
                max_area = area
                person_bbox = (x1, y1, x2, y2)

        # Draw all person detections
        for box in results.boxes:
            cls_id = int(box.cls[0])
            if cls_id != 0:  # 0 is person class
                continue
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            confidence = float(box.conf[0])
            
            # Draw bounding box
            color = (0, 255, 0)  # Green for normal detection
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label with confidence
            label = f"Person {confidence:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Show detection count on screen
        info_text = f"Persons detected: {person_count}"
        cv2.putText(frame, info_text, (10, frame.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        if person_bbox:
            # Calculate ratio for debugging
            x1, y1, x2, y2 = person_bbox
            w = x2 - x1
            h = y2 - y1
            ratio = w / h if h > 0 else 0
            
            curr_state = PersonState(
                is_lying=is_lying_down(person_bbox),
                bbox=person_bbox,
            )

            # Debug: Print state info (first 20 frames or when state changes)
            if not hasattr(run_edge, '_frame_count'):
                run_edge._frame_count = 0
            run_edge._frame_count += 1
            
            state_changed = prev_state is not None and prev_state.is_lying != curr_state.is_lying
            if run_edge._frame_count <= 20 or state_changed:
                prev_status = "None" if prev_state is None else ("LYING" if prev_state.is_lying else "STANDING")
                curr_status = "LYING" if curr_state.is_lying else "STANDING"
                print(f"Frame {run_edge._frame_count}: ratio={ratio:.2f}, prev={prev_status}, curr={curr_status}")

            # Highlight the largest person (used for fall detection) with different color
            status_color = (0, 0, 255) if curr_state.is_lying else (255, 0, 0)  # Red if lying, Blue if standing
            cv2.rectangle(frame, (x1, y1), (x2, y2), status_color, 3)
            status_text = "LYING" if curr_state.is_lying else "STANDING"
            cv2.putText(frame, status_text, (x1, y2 + 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
            
            # Also show ratio on screen
            ratio_text = f"Ratio: {ratio:.2f}"
            cv2.putText(frame, ratio_text, (x1, y2 + 45), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # Fall detection with cooldown
            if detect_fall(prev_state, curr_state):
                current_time = time.time()
                
                # Check if enough time has passed since last fall detection
                if last_fall_time is None or (current_time - last_fall_time) >= COOLDOWN_SECONDS:
                    print("FALL DETECTED!")
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    # Save current frame (fall detected frame)
                    filename = f"{timestamp}_fall.jpg"
                    path = os.path.join(SAVE_DIR, filename)
                    cv2.imwrite(path, frame)
                    
                    # Save frames from buffer (before fall)
                    if len(frame_buffer) > 1:
                        # Create a composite image with frames before fall
                        buffer_frames = frame_buffer[:-1]  # Exclude current frame (already saved)
                        
                        # Save individual frames before fall
                        pre_fall_dir = os.path.join(SAVE_DIR, f"{timestamp}_pre_fall")
                        os.makedirs(pre_fall_dir, exist_ok=True)
                        
                        for i, pre_frame in enumerate(buffer_frames):
                            pre_filename = f"frame_{i:03d}.jpg"
                            pre_path = os.path.join(pre_fall_dir, pre_filename)
                            cv2.imwrite(pre_path, pre_frame)
                        
                        # Create a composite image showing sequence
                        composite = create_frame_sequence_image(buffer_frames + [frame])
                        if composite is not None:
                            composite_path = os.path.join(SAVE_DIR, f"{timestamp}_sequence.jpg")
                            cv2.imwrite(composite_path, composite)
                        print(f"Saved {len(buffer_frames)} pre-fall frames + current frame")
                    
                    # Send to server
                    upload_success = send_fall_event(path, room="living_room")
                    if upload_success:
                        print(f"[성공] Fall event saved and sent to server. Cooldown: {COOLDOWN_SECONDS}s")
                    else:
                        print(f"[실패] Fall event saved locally but failed to send to server. Check server connection. Cooldown: {COOLDOWN_SECONDS}s")
                    # Draw fall alert on frame
                    cv2.putText(frame, "FALL DETECTED!", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                    
                    # Update last fall time
                    last_fall_time = current_time
                else:
                    # Still in cooldown period
                    remaining_time = COOLDOWN_SECONDS - (current_time - last_fall_time)
                    print(f"Fall detected but in cooldown. Ignoring. ({remaining_time:.1f}s remaining)")
                    # Draw cooldown message on frame
                    cv2.putText(frame, f"COOLDOWN: {remaining_time:.1f}s", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)

            prev_state = curr_state

        # Local monitoring
        cv2.imshow("Edge Fall Detection", frame)
        # Use appropriate delay: video files need FPS-based delay, live camera needs minimal delay
        key = cv2.waitKey(delay_ms) & 0xFF
        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    import sys
    
    # Command line argument: python main.py [source]
    # source can be:
    #   - 0 (default): webcam
    #   - "rtsp://..." or "http://...": IP camera stream
    #   - "path/to/video.mp4": Video file (mp4, avi, mov, etc.)
    if len(sys.argv) > 1:
        source = sys.argv[1]
        # If it's a number string, convert to int
        if source.isdigit():
            source = int(source)
    else:
        source = 0
    
    print(f"Starting with video source: {source}")
    try:
        run_edge(source)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
