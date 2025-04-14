import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram

# Load the dataset
df = pd.read_csv('../analyses/segments/segmentProfiles-LF.tsv', sep='\t', index_col=0)

# Convert distances to similarities by subtracting all values from 1
df_similarity = 1 - df

# Compute the linkage matrix
linkage_matrix = linkage(df_similarity, method='average')

# Create a dendrogram to get the order of the rows and columns
dendro = dendrogram(linkage_matrix, no_plot=True)
order = dendro['leaves']

# Reorder the dataframe
df_reordered = df_similarity.iloc[order, order]

# Create a heatmap with rainbow color scale
plt.figure(figsize=(20, 15))
sns.heatmap(df_reordered, cmap='rainbow')
plt.title('Reordered Heatmap of segmentProfiles-TLS.tsv (Similarities)')
plt.savefig('../analyses/segments/SegmentHeatmap.pdf', format='pdf')
#plt.show()

