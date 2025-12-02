# Audio_Stream/utils/model.py
from __future__ import annotations
import os
from pathlib import Path
import joblib
import pandas as pd
import numpy as np

# Base dir where THIS file lives: .../Audio_Stream/utils
_THIS_DIR = Path(__file__).resolve().parent
# Default weights dir: .../Audio_Stream/utils/weights
_DEFAULT_WEIGHTS_DIR = _THIS_DIR

def _weights_dir() -> Path:
    """
    Resolve weights directory. Priority:
    1) WEIGHTS_DIR env var (absolute or relative)
    2) default: <repo>/Audio_Stream/utils/weights
    """
    override = os.getenv("WEIGHTS_DIR")
    if override:
        p = Path(override).expanduser().resolve()
        if not p.exists():
            raise FileNotFoundError(f"WEIGHTS_DIR points to a non-existent path: {p}")
        return p
    return _DEFAULT_WEIGHTS_DIR

def _load_weight(filename: str):
    wd = _weights_dir()
    path = wd / filename
    if not path.exists():
        # Show where we looked and what we expected
        tried = f"Missing weight file: {path}\nLooked in: {wd}\n"
        raise FileNotFoundError(tried + "Tip: place your .pkl files there or set WEIGHTS_DIR.")
    return joblib.load(path)

def load_model(type: str):
    """
    Load pre-trained scaler and predictor models based on the specified type.
    type ∈ {'emotion', 'confidence', 'delivery'}.

    Returns
    -------
    (scaler, predictor): joblib-loaded objects
    """
    # Map logical names → filenames (adjust names here to match your repo)
    if type == 'emotion':
        scaler     = _load_weight("emotion_scaler.pkl")
        predictor  = _load_weight("emotion_kmeans_model.pkl")

    elif type == 'confidence':
        scaler     = _load_weight("confidence_scaler.pkl")
        predictor  = _load_weight("kmeans_model.pkl")            # <-- confirm filename

    elif type == 'delivery':
        scaler     = _load_weight("delivery_scaler.pkl")
        predictor  = _load_weight("rf_model.pkl")                # <-- confirm filename

    else:
        raise ValueError(f"Unknown model type: {type!r}. Use 'emotion' | 'confidence' | 'delivery'.")

    return scaler, predictor


def aggregate_segment_features(df_segments: pd.DataFrame, base_features: list[str]) -> pd.DataFrame:
    """
    Compute mean, std, min, max for each base feature in the segments (single-value fallback).
    """
    aggregated_data = []
    for idx, row in df_segments.iterrows():
        agg = {'timestamp': row.get('timestamp', idx)}
        for feature in base_features:
            if feature in df_segments.columns:
                value = row[feature]
                agg[f'mean_{feature}'] = value
                agg[f'std_{feature}']  = 0
                agg[f'min_{feature}']  = value
                agg[f'max_{feature}']  = value
        aggregated_data.append(agg)
    return pd.DataFrame(aggregated_data)

def run_model(scaler, predictor, feature_cols, cluster_labels, segments, label: str) -> pd.DataFrame:
    """
    Run scaler + predictor on segments.
    label: 'delivery' → expects aggregated stats; others use raw columns with KMeans-like predictor.
    """
    df_segments = pd.DataFrame(segments)
    print("Available columns:", df_segments.columns.tolist()[:10], "...")

    if label == 'delivery':
        stats = ["mean", "std", "min", "max"]
        full_cols = [f"{s}_{c}" for s in stats for c in feature_cols]

        if not all(c in df_segments.columns for c in full_cols):
            df_segments = aggregate_segment_features(df_segments, feature_cols)

        X = df_segments[full_cols].fillna(0)
        Xs = scaler.transform(X)
        y = predictor.predict(Xs)

        # If RandomForestClassifier multi-output predicts class per label (shape (n_samples, n_labels)),
        # convert accordingly; if it's a single class per row, y may be 1D.
        out = pd.DataFrame({'timestamp': df_segments['timestamp'].values})
        if hasattr(y, 'ndim') and y.ndim == 2 and y.shape[1] > 1:
            # Map each column to a provided cluster label if you want named outputs
            for i, name in enumerate(cluster_labels):
                out[name] = y[:, i]
            # And keep a single 'cluster' as an aggregate if needed
            out['cluster'] = np.argmax(y, axis=1)
            out[label] = out['cluster']
            keep = ['timestamp', 'cluster', label] + cluster_labels
            return out[keep]
        else:
            out['cluster'] = y if y.ndim == 1 else y.argmax(axis=1)
            out[label] = out['cluster']
            return out[['timestamp', 'cluster', label]]

    else:
        X = df_segments[feature_cols].fillna(0)
        Xs = scaler.transform(X)
        y = predictor.predict(Xs)
        df_segments['cluster'] = y
        df_segments[label] = df_segments['cluster'].map(dict(enumerate(cluster_labels)))
        return df_segments[['timestamp', 'cluster', label]]
