import os
import json
import pandas as pd
import opensmile
from pydub import AudioSegment


# Initialize OpenSMILE
smile = opensmile.Smile(
    feature_set=opensmile.FeatureSet.eGeMAPSv02,
    feature_level=opensmile.FeatureLevel.Functionals
)

def segment_audio(audio, feature_cols, segment_duration_ms=3000, step_size=1500):
    """ 
    Segment audio into smaller chunks and extract features.
    
    Parameters:
        audio (AudioSegment, mandatory): AudioSegment object to process.
        segment_duration_ms (int, optional): Duration of each segment in milliseconds.
        step_size (int, optional): Overlap amount in milliseconds.
        feature_cols (list[str], mandatory): List of feature columns to extract.
    
    Returns:
        list[dict]: List of dictionaries with the extracted features.
    """

    segments = []
    file_id = "segmented_audio"
    # audio is already an AudioSegment object, no need to load it again

    # Segment audio
    for i in range(0, len(audio) - segment_duration_ms + 1, step_size):
        segment = audio[i:i + segment_duration_ms]
        segment_path = f"/tmp/{file_id}_segment_{i}.wav"
        segment.export(segment_path, format="wav")

        # Extract features
        features_df = smile.process_file(segment_path).reset_index(drop=True).round(3)
        features = features_df.to_dict("records")[0]
        os.remove(segment_path)

        # Timestamp
        start_sec = i // 1000
        end_sec = (i + segment_duration_ms) // 1000
        timestamp = f"{start_sec//60:02d}:{start_sec%60:02d} - {end_sec//60:02d}:{end_sec%60:02d}"

        # Build feature row with all required features
        feature_row = {"file_id": file_id, "timestamp": timestamp}
        for col in feature_cols:
            feature_row[col] = features.get(col)

        segments.append(feature_row)
    
    return segments

def merge_on_timestamp(dfs, target_columns, join_col="timestamp"):
    """
    Merge DataFrames on a join column, keeping only target columns from each DF.
    
    Parameters:
        dfs (list[pd.DataFrame], mandatory): List of DataFrames to search.
        target_columns (list[str], mandatory): Columns to keep (in addition to join_col).
        join_col (str, optional): Column name to merge on. Default is 'timestamp'.
    
    Returns:
        pd.DataFrame: Merged DataFrame.
    """
    # Get rid of duplicates and skip join_col if passed by mistake
    targets = []
    for t in target_columns:
        if t == join_col:
            continue
        if t not in targets:
            targets.append(t)

    selected_dfs = []

    for target in targets:
        for df in dfs:
            if target in df.columns:
                selected_dfs.append(df[[join_col, target]])
                break  # Stop once we find the target column in a DF

    # Merge all selected DFs on join_col
    merged_df = selected_dfs[0]
    for other_df in selected_dfs[1:]:
        merged_df = pd.merge(merged_df, other_df, on=join_col, how="inner")

    return merged_df

def create_json_output(merged_df, target_columns, join_col="timestamp", filename="output.json"):
    """
    Create a JSON output from a merged DataFrame, always including the join column.
    
    Parameters:
        merged_df (pd.DataFrame, mandatory): Merged DataFrame.
        target_columns (list[str], mandatory): Columns to keep (besides join_col).
        join_col (str, optional): Column name to always include (default "timestamp").
    
    Returns:
        str: JSON string.
    """
    cols_to_keep = [join_col] + target_columns
    records = merged_df[cols_to_keep].to_dict(orient="records")
    json_str = json.dumps(records, indent=2)

    # Save JSON string to a file in the current directory
    file_path = os.path.join(os.getcwd(), filename)
    with open(file_path, "w") as f:
        f.write(json_str)

    return json_str
