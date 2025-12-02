import os
import json
import pandas as pd
import opensmile
from pydub import AudioSegment
import tempfile  # NEW

# Initialize OpenSMILE
smile = opensmile.Smile(
    feature_set=opensmile.FeatureSet.eGeMAPSv02,
    feature_level=opensmile.FeatureLevel.Functionals
)

def segment_audio(audio, feature_cols, segment_duration_ms=3000, step_size=1500, out_dir=None):
    """ 
    Segment audio into smaller chunks and extract features.

    Parameters:
        audio (AudioSegment): AudioSegment object to process.
        segment_duration_ms (int): Duration of each segment in ms.
        step_size (int): Hop size in ms (overlap = segment_duration_ms - step_size).
        feature_cols (list[str]): Feature columns to extract.
        out_dir (str|None): Directory to write temp WAV segments (auto-created). If None, use OS temp.

    Returns:
        list[dict]: Extracted features per segment with timestamps.
    """
    segments = []
    file_id = "segmented_audio"

    # Cross-platform temp directory for segment WAVs
    if out_dir is None:
        out_dir = os.path.join(tempfile.gettempdir(), "capstone_segments")
    os.makedirs(out_dir, exist_ok=True)

    # Segment audio
    for i in range(0, len(audio) - segment_duration_ms + 1, step_size):
        segment = audio[i:i + segment_duration_ms]
        segment_path = os.path.join(out_dir, f"{file_id}_segment_{i}.wav")
        segment.export(segment_path, format="wav")

        # Extract features
        try:
            features_df = smile.process_file(segment_path).reset_index(drop=True).round(3)
        finally:
            # Clean up the temp wav regardless of success
            try:
                os.remove(segment_path)
            except OSError:
                pass

        features = features_df.to_dict("records")[0]

        # Timestamp label
        start_sec = i // 1000
        end_sec = (i + segment_duration_ms) // 1000
        timestamp = f"{start_sec//60:02d}:{start_sec%60:02d} - {end_sec//60:02d}:{end_sec%60:02d}"

        # Build feature row
        row = {"file_id": file_id, "timestamp": timestamp}
        for col in feature_cols:
            row[col] = features.get(col)
        segments.append(row)
    
    return segments

def merge_on_timestamp(dfs, target_columns, join_col="timestamp"):
    """
    Merge DataFrames on a join column, keeping only target columns from each DF.
    """
    targets = []
    for t in target_columns:
        if t != join_col and t not in targets:
            targets.append(t)

    selected = []
    for target in targets:
        for df in dfs:
            if target in df.columns:
                selected.append(df[[join_col, target]])
                break

    if not selected:
        # Nothing found; return an empty DF with just the join column
        return pd.DataFrame(columns=[join_col] + targets)

    merged_df = selected[0]
    for other_df in selected[1:]:
        merged_df = pd.merge(merged_df, other_df, on=join_col, how="inner")
    return merged_df

def create_json_output(merged_df, target_columns, join_col="timestamp", filename="output.json", out_dir=None):
    """
    Create a JSON output from a merged DataFrame, always including the join column.
    Returns the path to the JSON file.
    """
    cols_to_keep = [join_col] + target_columns
    records = merged_df[cols_to_keep].to_dict(orient="records")
    json_str = json.dumps(records, indent=2)

    if out_dir is None:
        out_dir = os.getcwd()
    os.makedirs(out_dir, exist_ok=True)
    file_path = os.path.join(out_dir, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(json_str)
    return file_path
