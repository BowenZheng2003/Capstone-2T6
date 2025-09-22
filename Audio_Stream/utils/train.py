from pydub import AudioSegment
import os
import opensmile
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import joblib
from sklearn.cluster import KMeans


data_folder = 'C:/Users/Jeslyn/OneDrive/Desktop/capstone/Capstone-2T6/Audio_Stream/tmp/Segmented Interview Information-20250809T205338Z-1-001/Segmented Interview Information/'

feature_cols = [
    "F0semitoneFrom27.5Hz_sma3nz_stddevNorm",
    "loudness_sma3_amean",
    "HNRdBACF_sma3nz_amean",
    "jitterLocal_sma3nz_amean",
    "shimmerLocaldB_sma3nz_amean",
    "F0semitoneFrom27.5Hz_sma3nz_amean"        #
]

# Collect data from all CSVs
all_dfs = []

for filename in os.listdir(data_folder):
    print("FSDHJLKJSDFHJKLF", filename)
    if filename.endswith("_all_features.csv"):
        file_path = os.path.join(data_folder, filename)
        try:
            df = pd.read_csv(file_path)
            if all(col in df.columns for col in feature_cols):
                all_dfs.append(df[["file_id", "timestamp"] + feature_cols])
            else:
                print(f"Skipping {filename} — missing required features.")
        except Exception as e:
            print(f"Failed to load {filename}: {e}")

# Combine all DataFrames
if not all_dfs:
    raise ValueError("No valid feature CSVs found in the folder.")

combined_df = pd.concat(all_dfs, ignore_index=True)

# Prepare data
X = combined_df[feature_cols].fillna(0)  # Fill any missing values just in case

# Standardize the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Run K-Means clustering
kmeans = KMeans(n_clusters=5, random_state=42)
cluster_labels = kmeans.fit_predict(X_scaled)

# Assign clusters to DataFrame
combined_df["cluster"] = cluster_labels

# (Optional) Inspect cluster centers to interpret meaning
cluster_centers = scaler.inverse_transform(kmeans.cluster_centers_)
cluster_summary = pd.DataFrame(cluster_centers, columns=feature_cols)
cluster_summary.index.name = "cluster"
print(cluster_summary)

from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # This is needed for 3D plotting

# Reduce to 3 components for 3D plotting
X_pca_3d = PCA(n_components=3).fit_transform(X_scaled)

# 3D Scatter plot
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

scatter = ax.scatter(
    X_pca_3d[:, 0],
    X_pca_3d[:, 1],
    X_pca_3d[:, 2],
    c=cluster_labels,
    cmap='viridis',
    s=50,
    alpha=0.7,
    edgecolor='k'
)

ax.set_title("K-Means Clusters Visualized in 3D PCA Space")
ax.set_xlabel("PCA Component 1")
ax.set_ylabel("PCA Component 2")
ax.set_zlabel("PCA Component 3")

# Add color legend
legend = fig.colorbar(scatter, ax=ax, pad=0.1)
legend.set_label("Cluster")

plt.tight_layout()
plt.show()


import joblib

# # Save DataFrame with cluster labels
# combined_df["confidence_label"] = combined_df["cluster"].map(cluster_labels)
# combined_df.to_csv("C:/Users/Jeslyn/OneDrive/Desktop/capstone/Capstone-2T6/Audio_Stream/tmp/confidence_segments.csv", index=False)

# Save the trained scaler
joblib.dump(scaler, "C:/Users/Jeslyn/OneDrive/Desktop/capstone/Capstone-2T6/Audio_Stream/tmp/confidence_scaler.pkl")

# Save the trained KMeans model
joblib.dump(kmeans, "C:/Users/Jeslyn/OneDrive/Desktop/capstone/Capstone-2T6/Audio_Stream/tmp/kmeans_model.pkl")

# Optional: save cluster center summary
cluster_summary.to_csv("C:/Users/Jeslyn/OneDrive/Desktop/capstone/Capstone-2T6/Audio_Stream/tmp/kmeans_cluster_summary.csv")