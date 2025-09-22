import joblib
import pandas as pd

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
        # REPLACE PATHS WHEN RUNNING FOR YOURSELF
        scaler = joblib.load(r'C:\Users\Jeslyn\OneDrive\Desktop\capstone\Capstone-2T6\Audio_Stream\tmp\emotion_scaler.pkl')
        predictor = joblib.load(r'C:\Users\Jeslyn\OneDrive\Desktop\capstone\Capstone-2T6\Audio_Stream\tmp\emotion_kmeans_model.pkl')

    elif type == 'confidence':
        # REPLACE PATHS WHEN RUNNING FOR YOURSELF
        scaler = joblib.load(r'C:\Users\Jeslyn\OneDrive\Desktop\capstone\Capstone-2T6\Audio_Stream\tmp\confidence_scaler.pkl')
        predictor = joblib.load(r'C:\Users\Jeslyn\OneDrive\Desktop\capstone\Capstone-2T6\Audio_Stream\tmp\kmeans_model.pkl')

    elif type == 'delivery':
        # REPLACE PATHS WHEN RUNNING FOR YOURSELF
        scaler = joblib.load(r'Capstone-2T6\Audio_Stream\tmp\delivery_scaler.pkl')
        predictor = joblib.load(r'Capstone-2T6\Audio_Stream\tmp\rf_model.pkl')

    return scaler, predictor

def run_model(scaler, predictor, feature_cols, cluster_labels, segments, label):
    """
    Run the model on the given features and cluster labels.

    Parameters:
        scaler (joblib.load, mandatory): Scaler model.
        predictor (joblib.load, mandatory): Predictor model.
        feature_cols (list[str], mandatory): List of feature columns.
        cluster_labels (dict, mandatory): Dictionary of cluster labels.
        segments (list[dict], mandatory): List of segments.
        label (str, mandatory): Label to use for the predicted clusters.
    
    Returns:
        pd.DataFrame: DataFrame with the predicted clusters and emotions.
    """
    df_segments = pd.DataFrame(segments)
    x_new = df_segments[feature_cols].fillna(0)
    x_new_scaled = scaler.transform(x_new)
    predicted_clusters = predictor.predict(x_new_scaled)

    df_segments["reclustered"] = predicted_clusters
    df_segments[label] = df_segments["reclustered"].map(cluster_labels)

    return(df_segments[["timestamp", "reclustered", label]])
