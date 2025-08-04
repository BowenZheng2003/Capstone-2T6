import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
df = pd.read_csv('output/pyfeat_results.csv')

# Emotion columns based on py-feat output
emotion_columns = ['anger', 'disgust', 'fear', 'happiness', 'sadness', 'surprise', 'neutral']

# Check if all emotion columns exist
missing = [col for col in emotion_columns if col not in df.columns]
if missing:
    raise ValueError(f"Missing emotion columns: {missing}")

# Plot emotion intensities over time
plt.figure(figsize=(12, 6))
for emotion in emotion_columns:
    plt.plot(df[emotion], label=emotion)

plt.title('Emotions Over Time')
plt.xlabel('Frame')
plt.ylabel('Emotion Intensity')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
