import seaborn as sns
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import set_link_color_palette
import pandas as pd

# Load an example dataset from seaborn
iris = sns.load_dataset("iris")
# Remove the 'species' column to leave only numerical data for clustering
df_numeric = iris.pop("species")
# Load the full dataset again for the numeric values
df = sns.load_dataset("iris").drop("species", axis=1)

# Create the clustered heatmap
# The function automatically performs hierarchical clustering
sns.clustermap(df)

# Display the plot
plt.show()

# df: rows = edge types, columns = knowledge graphs
# index = edge types, columns = KG names

# Force dendrogram colors
set_link_colr_palette(["green", "blue"])

g = sns.clustermap(
    df,
    cmap="mako",
    row_cluster=False,      # 🚫 no left dendrogram
    col_cluster=True,       # ✅ top dendrogram
    dendrogram_ratio=(.15, .05),
    cbar_pos=(.02, .8, .03, .18),
    linewidths=0,
    figsize=(10, 6),
    tree_kws=dict(linewidths=1.5)
)

# Axis labels
g.ax_heatmap.set_xlabel("Knowledge Graph")
g.ax_heatmap.set_ylabel("Edge Type")

# Rotate KG labels if needed
plt.setp(g.ax_heatmap.get_xticklabels(), rotation=45, ha="right")

plt.show()
