from feat.detector import Detector
import pandas as pd
import numpy as np

# Load detector (uses default models: RetinaFace + ResMaskNet)
detector = Detector()

# Process video
results = detector.detect_video(r"C:\Users\Jeslyn\OneDrive\Desktop\capstone\Capstone-2T6\presentation_analyzer\processed_video.mp4")  # or .detect_image("frame.jpg")

# --- Extract Features ---

# 1. Facial Action Units (AU) -- muscle intensities
aus = results.get_aus()

# 2. Head Pose -- pitch, yaw, roll (in degrees)
pose = results.get_landmarks_stats()[["pose_Rx", "pose_Ry", "pose_Rz"]]

# 3. Emotion Predictions -- happy, sad, angry, etc.
emotions = results.get_emotions()


# 4. Facial Expressiveness -- variance across AUs
facial_expressiveness_score = aus.var().mean()

# 5. Smile Intensity -- AU12 (lip corner puller)
smile_intensity_mean = aus["AU12"].mean()
smile_intensity_var = aus["AU12"].var()

# 6. Eye Gaze Direction (approximate): use pose_Rx/pose_Ry as proxies
avg_gaze_pitch = pose["pose_Rx"].mean()
