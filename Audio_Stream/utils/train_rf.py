import pandas as pd
import numpy as np
import glob
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import cross_val_score, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import make_scorer, mean_absolute_error, r2_score
import joblib

# === Step 1: Load feature files ===
import os, glob
import pandas as pd
from sklearn.preprocessing import StandardScaler

features_folder = r'C:\Users\Jeslyn\OneDrive\Desktop\capstone\Capstone-2T6\Audio_Stream\tmp\Segmented Interview Information-20250809T205338Z-1-001\Segmented Interview Information'
feature_files = glob.glob(os.path.join(features_folder, "*_all_features.csv"))

clarity_features = [
    "F0semitoneFrom27.5Hz_sma3nz_amean",
    "HNRdBACF_sma3nz_amean",
    "jitterLocal_sma3nz_amean",
    "shimmerLocaldB_sma3nz_amean",
    "loudness_sma3_amean",
    "mfcc1_sma3_amean", "mfcc2_sma3_amean", "mfcc3_sma3_amean"
]

agg_data = []
skipped_missing_cols = []
skipped_no_rows = []
for file in feature_files:
    try:
        df = pd.read_csv(file)
    except Exception as e:
        print("Failed to read", file, ":", e)
        continue

    # robust participant extraction
    fname = os.path.basename(file)
    participant = fname.split("_")[0].lower().strip()

    if not set(clarity_features).issubset(df.columns):
        skipped_missing_cols.append((fname, list(set(clarity_features) - set(df.columns))))
        continue

    subset = df[clarity_features].dropna()
    if subset.shape[0] == 0:
        skipped_no_rows.append(fname)
        continue

    agg_mean = subset.mean()
    agg_std = subset.std()
    agg_min = subset.min()
    agg_max = subset.max()

    agg_vector = pd.concat([agg_mean, agg_std, agg_min, agg_max])
    agg_vector.index = [f"{stat}_{col}" for stat in ["mean", "std", "min", "max"] for col in clarity_features]
    agg_vector = agg_vector.rename_axis("feature").reset_index(drop=True)
    # simpler to keep participant as a column
    agg_vector = pd.Series(agg_vector.values, index=[f"{stat}_{col}" for stat in ["mean", "std", "min", "max"] for col in clarity_features])
    agg_vector["Participant"] = participant
    agg_data.append(agg_vector)

print("Processed files:", len(agg_data))
print("Skipped (missing cols):", len(skipped_missing_cols))
print("Skipped (no rows after dropna):", len(skipped_no_rows))

if len(agg_data) == 0:
    raise SystemExit("No aggregated feature rows. Check skipped files above.")

agg_features_df = pd.DataFrame(agg_data)

# Load scores
score_path = r"C:\Users\Jeslyn\OneDrive\Desktop\capstone\Capstone-2T6\Audio_Stream\tmp\turker_scores_full_interview.csv"
scores_df = pd.read_csv(score_path)
scores_df["Participant"] = scores_df["Participant"].astype(str).str.lower().str.strip()

# examine Worker values
print("Worker value counts:\n", scores_df["Worker"].value_counts())

# Keep only AGGR rows (ensure exact match)
scores_df_aggr = scores_df[scores_df["Worker"].str.strip().str.upper() == "AGGR"]
print("AGGR rows:", len(scores_df_aggr))

clarity_labels = ["Focused", "Authentic", "NotAwkward", "EngagingTone"]
scores_df_aggr = scores_df_aggr[["Participant"] + clarity_labels]

merged = pd.merge(agg_features_df, scores_df_aggr, on="Participant", how="inner")
print("Merged shape:", merged.shape)
if merged.shape[0] == 0:
    # show which participants don't match
    feat_participants = set(agg_features_df["Participant"].unique())
    score_participants = set(scores_df_aggr["Participant"].unique())
    print("Participants in features not in scores (first 20):", list(feat_participants - score_participants)[:20])
    print("Participants in scores not in features (first 20):", list(score_participants - feat_participants)[:20])
    raise SystemExit("Merge produced 0 rows — fix participant naming or data.")

X = merged.drop(columns=["Participant"] + clarity_labels)
y = merged[clarity_labels]

# ensure numeric columns only
X = X.apply(pd.to_numeric, errors='coerce')

# handle NaNs (options: drop rows, or impute)
nan_rows = X.isna().any(axis=1).sum()
print("Rows with NaNs in features:", nan_rows)
# option A: drop incomplete rows
if nan_rows > 0:
    X = X.dropna()
    y = y.loc[X.index]
    print("After dropping NaNs, X shape:", X.shape)

if X.shape[0] == 0:
    raise SystemExit("No samples left after cleaning. Cannot fit scaler.")

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print("X_scaled shape:", X_scaled.shape)


rf = RandomForestRegressor(n_estimators=100, random_state=42)
multi_rf = MultiOutputRegressor(rf)

kf = KFold(n_splits=5, shuffle=True, random_state=42)
r2_scores, mae_scores = [], []

for train_idx, test_idx in kf.split(X_scaled):
    X_train, X_test = X_scaled[train_idx], X_scaled[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    multi_rf.fit(X_train, y_train)
    y_pred = multi_rf.predict(X_test)

    r2_scores.append(r2_score(y_test, y_pred, multioutput='raw_values'))
    mae_scores.append(mean_absolute_error(y_test, y_pred, multioutput='raw_values'))

# === Step 6: Report Results ===
r2_scores = np.array(r2_scores)
mae_scores = np.array(mae_scores)

print("✅ Multi-Output Random Forest Clarity Prediction (Updated - 4 Labels)")
for i, label in enumerate(clarity_labels):
    print(f"\n🎯 {label}")
    print(f"  Mean R²:  {np.mean(r2_scores[:, i]):.3f}")
    print(f"  Mean MAE: {np.mean(mae_scores[:, i]):.3f}")

# Save the trained scaler
joblib.dump(scaler, "C:/Users/Jeslyn/OneDrive/Desktop/capstone/Capstone-2T6/Audio_Stream/tmp/delivery_scaler.pkl")

# Save the trained KMeans model
joblib.dump(multi_rf, "C:/Users/Jeslyn/OneDrive/Desktop/capstone/Capstone-2T6/Audio_Stream/tmp/rf_model.pkl")