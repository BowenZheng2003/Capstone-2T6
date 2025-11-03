import joblib
import pandas as pd
import numpy as np

def load_model(type: str):
    """
    Load pre-trained scaler and predictor models based on the specified type.

    Parameters:
        type (str, mandatory): Type of model to load. Must be one of: 'emotion', 'confidence', or 'delivery'.
    
    Returns:
        tuple: A tuple containing (scaler, predictor) where both are joblib-loaded model objects.
            - scaler: Pre-trained StandardScaler model for feature normalization
            - predictor: Pre-trained machine learning model (KMeans or RandomForest) for predictions
    """
    if type == 'emotion':
        scaler = joblib.load(r'/Users/jeslyn/Desktop/projects/Capstone-2T6/Audio_Stream/utils/weights/emotion_scaler.pkl')
        predictor = joblib.load(r'/Users/jeslyn/Desktop/projects/Capstone-2T6/Audio_Stream/utils/weights/emotion_kmeans_model.pkl')

    elif type == 'confidence':
        scaler = joblib.load(r'/Users/jeslyn/Desktop/projects/Capstone-2T6/Audio_Stream/utils/weights/confidence_scaler.pkl')
        predictor = joblib.load(r'/Users/jeslyn/Desktop/projects/Capstone-2T6/Audio_Stream/utils/weights/kmeans_model.pkl')

    elif type == 'delivery':
        scaler = joblib.load(r'/Users/jeslyn/Desktop/projects/Capstone-2T6/Audio_Stream/utils/weights/delivery_scaler.pkl')
        predictor = joblib.load(r'/Users/jeslyn/Desktop/projects/Capstone-2T6/Audio_Stream/utils/weights/rf_model.pkl')

    return scaler, predictor

def aggregate_segment_features(df_segments, base_features):
    """
    Compute mean, std, min, max for each base feature in the segments.
    
    Parameters:
        df_segments (pd.DataFrame): DataFrame with raw features per segment
        base_features (list[str]): List of base feature names
    
    Returns:
        pd.DataFrame: DataFrame with aggregated statistics
    """
    aggregated_data = []
    
    for idx, row in df_segments.iterrows():
        agg_dict = {'timestamp': row.get('timestamp', idx)}
        
        for feature in base_features:
            if feature in df_segments.columns:
                # If you have multiple values per segment, compute statistics
                # Otherwise, just use the single value for all stats
                value = row[feature]
                
                # For single values, set all stats to the same value
                # (Or if your segment_audio returns arrays, compute proper stats)
                agg_dict[f'mean_{feature}'] = value
                agg_dict[f'std_{feature}'] = 0  # No variation in single value
                agg_dict[f'min_{feature}'] = value
                agg_dict[f'max_{feature}'] = value
        
        aggregated_data.append(agg_dict)
    
    return pd.DataFrame(aggregated_data)

def run_model(scaler, predictor, feature_cols, cluster_labels, segments, label):
    """
    Run the model on the given features and cluster labels.

    Parameters:
        scaler (joblib.load, mandatory): Scaler model.
        predictor (joblib.load, mandatory): Predictor model.
        feature_cols (list[str], mandatory): List of base feature columns (without stat prefix).
        cluster_labels (list[str], mandatory): List of cluster labels (for delivery model, these are the output names).
        segments (list[dict], mandatory): List of segments.
        label (str, mandatory): Label type ('delivery', 'emotion', 'confidence').
    
    Returns:
        pd.DataFrame: DataFrame with the predicted values.
    """
    df_segments = pd.DataFrame(segments)
    
    # Check what columns we actually have
    print("Available columns:", df_segments.columns.tolist()[:10], "...")
    
    # For delivery model, we need mean, std, min, max for each feature
    if label == 'delivery':
        # Build the full feature list expected by the model
        stats = ["mean", "std", "min", "max"]
        full_feature_cols = [f"{stat}_{col}" for stat in stats for col in feature_cols]
        
        # Check if aggregated features already exist
        if not all(col in df_segments.columns for col in full_feature_cols):
            df_segments = aggregate_segment_features(df_segments, feature_cols)
        
        # Select features and fill missing values
        x_new = df_segments[full_feature_cols].fillna(0)
        
        # Transform and predict
        x_new_scaled = scaler.transform(x_new)
        predictions = predictor.predict(x_new_scaled)
        
        # For Random Forest multi-output, predictions is a 2D array
        # Each column corresponds to one of the cluster_labels
        result_df = pd.DataFrame()
        result_df['timestamp'] = df_segments['timestamp'].values
        
        # Get the index of the maximum value across the 4 dimensions (0-3)
        result_df['cluster'] = predictions.argmax(axis=1)
        result_df[label] = result_df['cluster']
        
        return result_df[["timestamp", "cluster", label]]
    
    else:
        # For clustering models (emotion, confidence)
        x_new = df_segments[feature_cols].fillna(0)
        x_new_scaled = scaler.transform(x_new)
        predicted_clusters = predictor.predict(x_new_scaled)
        
        df_segments["cluster"] = predicted_clusters
        df_segments[label] = df_segments["cluster"].map(dict(enumerate(cluster_labels)))
        
        return df_segments[["timestamp", "cluster", label]]


# # Your main code
# import Audio_Stream.utils.processing as processing
# from pydub import AudioSegment
# from Audio_Stream.utils import audio_extraction

# input_video = "/Users/jeslyn/Desktop/projects/Capstone-2T6/backend/IMG_4027 2.MOV"
# audio_file = audio_extraction.extract_mp3(input_file=input_video)
# audio = AudioSegment.from_file(audio_file)

# # Base features (without stat prefix)
# base_clarity_features = [
#     "F0semitoneFrom27.5Hz_sma3nz_amean",
#     "HNRdBACF_sma3nz_amean",
#     "jitterLocal_sma3nz_amean",
#     "shimmerLocaldB_sma3nz_amean",
#     "loudness_sma3_amean",
#     "mfcc1_sma3_amean",
#     "mfcc2_sma3_amean",
#     "mfcc3_sma3_amean"
# ]

# # Generate segments
# segments = processing.segment_audio(audio, feature_cols=base_clarity_features)

# # Debug: print first segment to see structure
# print("First segment keys:", list(segments[0].keys()) if segments else "No segments")

# scaler, predictor = load_model("delivery")
# clarity_labels = ["Focused", "Authentic", "NotAwkward", "EngagingTone"]

# result = run_model(scaler, predictor, feature_cols=base_clarity_features, 
#                    cluster_labels=clarity_labels, segments=segments, label="delivery")

# print(result)