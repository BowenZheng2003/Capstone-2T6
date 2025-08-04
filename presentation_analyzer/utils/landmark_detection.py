import cv2
import mediapipe as mp
import os
import json

mp_holistic = mp.solutions.holistic

def detect_landmarks(frame_dir, output_json_dir="landmarks/"):
    if not os.path.exists(output_json_dir):
        os.makedirs(output_json_dir)

    holistic = mp_holistic.Holistic(static_image_mode=True)

    for frame_name in sorted(os.listdir(frame_dir)):
        if not frame_name.endswith(".jpg"):
            continue

        frame_path = os.path.join(frame_dir, frame_name)
        image_bgr = cv2.imread(frame_path)
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        results = holistic.process(image_rgb)
        landmarks_dict = {}

        def extract_landmarks(landmarks, label):
            return {
                label: [
                    {
                        "x": lm.x,
                        "y": lm.y,
                        "z": lm.z if hasattr(lm, 'z') else None,
                        "visibility": lm.visibility if hasattr(lm, 'visibility') else None
                    }
                    for lm in landmarks.landmark
                ]
            }

        if results.pose_landmarks:
            landmarks_dict.update(extract_landmarks(results.pose_landmarks, "pose"))
        if results.face_landmarks:
            landmarks_dict.update(extract_landmarks(results.face_landmarks, "face"))
        if results.left_hand_landmarks:
            landmarks_dict.update(extract_landmarks(results.left_hand_landmarks, "left_hand"))
        if results.right_hand_landmarks:
            landmarks_dict.update(extract_landmarks(results.right_hand_landmarks, "right_hand"))

        json_path = os.path.join(output_json_dir, frame_name.replace(".jpg", ".json"))
        with open(json_path, 'w') as f:
            json.dump(landmarks_dict, f, indent=2)

    holistic.close()
    print(f"[✓] Landmarks saved in '{output_json_dir}'")
