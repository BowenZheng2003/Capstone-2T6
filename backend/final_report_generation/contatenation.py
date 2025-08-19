import json

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
    
    files = [audio, video, text]
    # Dictionary to merge by timestamp
    merged_data = {}

    # Go through each file
    for f in files:
        with open(f, "r") as infile:
            data = json.load(infile)
            for entry in data:
                ts = entry["timestamp"]
                if ts not in merged_data:
                    merged_data[ts] = {"timestamp": ts}
                # Merge the rest of the fields into the same timestamp entry
                for k, v in entry.items():
                    if k != "timestamp":
                        merged_data[ts][k] = v

    # Convert merged_data back into a list of dicts (if needed)
    final_data = list(merged_data.values())

    # Save to output file
    with open("merged.json", "w") as outfile:
        json.dump(final_data, outfile, indent=2)

# test the function
concatenate_streams(audio=r"C:\Users\Jeslyn\Downloads\audio.json",
                    video=r"C:\Users\Jeslyn\Downloads\body_language.json",
                    text=r"C:\Users\Jeslyn\Downloads\transcript.json")