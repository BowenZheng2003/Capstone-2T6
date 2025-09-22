import json
from collections import defaultdict

def concatenate_streams(audio: str, video: str, text: str):
    """
    Merge three JSON "streams" (files) into a single JSON file by matching records on the "timestamp" key.

    Parameters
    ----------
    audio : str
        Path to a JSON file containing a list (array) of objects with a "timestamp" field and audio-related keys
        (e.g., "confidence", "emotion", "tone").
    video : str
        Path to a JSON file containing a list of objects with a "timestamp" field and video/body-language keys
        (e.g., "smile_intensity", "eye_contact_ratio").
    text : str
        Path to a JSON file containing a list of objects with a "timestamp" field and text/transcript keys
        (e.g., "transcription").
    
    Returns
    ----------
    None
        The merged JSON is written to "merged.json". The function does not return the merged data.

    """
    
    json_files = [audio, video, text]
    # Dictionary to merge by timestamp
    
    merged = defaultdict(dict)

    # Load each file and merge by timestamp
    for file_path in json_files:
        with open(file_path) as f:
            data = json.load(f)
            for entry in data:
                if not isinstance(entry, dict):
                    continue  # skip non-dict entries
                ts = entry.get("timestamp")
                if not ts:
                    continue  # skip entries without timestamp

                # Merge all keys except timestamp
                for k, v in entry.items():
                    if k == "timestamp":
                        continue
                    if k in merged[ts] and isinstance(v, dict):
                        merged[ts][k].update(v)
                    elif k in merged[ts] and isinstance(v, str):
                        merged[ts][k] = merged[ts][k] + " " + v
                    else:
                        merged[ts][k] = v

    # Convert merged dict back to list of dicts
    merged_list = [{"timestamp": ts, **vals} for ts, vals in merged.items()]

    # Optional: sort by start time
    def parse_ts(ts):
        start = ts.split("-")[0].strip()
        if ":" in start:
            mins, secs = start.split(":")
            return int(mins) * 60 + int(secs)
        return int(start)

    merged_list.sort(key=lambda x: parse_ts(x["timestamp"]))

    # Save merged JSON
    with open("merged.json", "w") as f:
        json.dump(merged_list, f, indent=2)

    print("✅ Merged JSON saved to 'merged.json'")

    return "merged.json"
# # test the function
# concatenate_streams(audio=r"C:\Users\Jeslyn\Downloads\audio.json",
#                     video=r"C:\Users\Jeslyn\Downloads\body_language.json",
#                     text=r"C:\Users\Jeslyn\Downloads\transcript.json")