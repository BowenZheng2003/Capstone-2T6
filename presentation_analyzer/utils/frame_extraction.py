import cv2
import os

def extract_frames(
    video_path,
    output_dir="frames/",
    frame_interval_ms=1000,
    resize_dim=(640, 480)
):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    interval = int(fps * (frame_interval_ms / 1000))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    current_frame = 0
    saved_frame_idx = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if current_frame % interval == 0:
            if resize_dim:
                frame = cv2.resize(frame, resize_dim)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_filename = os.path.join(output_dir, f"frame_{saved_frame_idx:04d}.jpg")
            cv2.imwrite(frame_filename, cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR))
            saved_frame_idx += 1

        current_frame += 1

    cap.release()
    print(f"[✓] Extracted {saved_frame_idx} frames to '{output_dir}'")
