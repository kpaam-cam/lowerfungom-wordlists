# Experimenting with spectral clusters based on
# https://rpubs.com/gargeejagtap/SpectralClustering
# Idea came from work by Wieling and Nerbonne
# Started with cognate graphs, but that was a semi-random choice

## Overall the spectral experiment "failed", PAM seems like the best

library(tidyverse)
library(gridExtra)
library(ggplot2)
library(igraph)
library(ggnetwork)
library(factoextra)
library(cluster)


cogNetwork <- read.csv(
'/Users/jcgood/gitrepos/lowerfungom-wordlists/analyses/Phase3a-Fall2023/kplfSubset-0.450.55_thresholds-cognates-Network.tsv',
sep = "\t"
)

# Extract information from graph
netGraph <- graph_from_data_frame(cogNetwork, directed=FALSE)

# igraph looks for a weight attribute; so I copy it here
E(netGraph)$weight <- E(netGraph)$SharedCognateCount

# Make an adjacency matrix to put the weights in a matrix as a means of calculating a layout
netAdjacency <- as_adjacency_matrix(netGraph, attr="weight")
netDist = dist(netAdjacency)
netMat = as.matrix(netDist)


cogDists <-
  read.csv(
    '/Users/jcgood/gitrepos/lowerfungom-wordlists/analyses/Phase3a-Fall2023/kplfSubset-SCA-0.45_threshold-heatmap.matrix.dst',
    sep = "\t"
  )
rownames(cogDists) = cogDists[, 1]
cogDists = cogDists[, -1]
#netMat = as.matrix(cogDists)


options(ggrepel.max.overlaps = Inf)


# Create layout from earlier work
invAdjacency = 1/netAdjacency
invAdjacency[!is.finite(invAdjacency)] <- 0 # change accidental infinities to zero
sqrtInvAdjacency <- invAdjacency^(1/2)
sqrtInvAdjacencyMDS <- cmdscale(sqrtInvAdjacency)
invGraph <- netGraph
E(invGraph)$weight <- sqrt(1/E(netGraph)$weight)
mdsLayout <- layout_with_mds(invGraph, dist=sqrtInvAdjacency)
xFlippedMdsLayout <- mdsLayout
xFlippedMdsLayout[,2] <- -xFlippedMdsLayout[,2]


# Following directions in RPub
## Create Degree matrix
D <- matrix(0, nrow = nrow(netMat), ncol = nrow(netMat))

for (i in 1:nrow(netMat)) {
  
      # Find top 10 nearest neighbors using Euclidean distance
      index <- order(netMat[i,])[2:11]
      
      # Assign value to neighbors
      D[i,][index] <- 1 
}

# find mutual neighbors
D = D + t(D) 
D[ D == 2 ] = 1

# find degrees of vertices
degrees = colSums(D) 
n = nrow(D)

## Compute Laplacian matrix
# Since k > 2 clusters (3), we normalize the Laplacian matrix:
laplacian = ( diag(n) - diag(degrees^(-1/2)) %*% D %*% diag(degrees^(-1/2)) )

## Compute eigenvectors
eigenvectors = eigen(laplacian, symmetric = TRUE)
n = nrow(laplacian)
eigenvectors = eigenvectors$vectors[,(n - 2):(n - 1)]

# Find out which clusters are optimal
fviz_nbclust(eigenvectors, pam, method="silhouette", k.max=30) + ggtitle("")

m = 13 # pick a number
sc = kmeans(eigenvectors, m)

# get labels for the data
sc_results = cbind(rownames(netAdjacency), cluster = as.factor(sc$cluster))
layoutDF = as.data.frame(xFlippedMdsLayout)

# plot data
sc_plot = ggplot(data = layoutDF, aes(x=xFlippedMdsLayout[,1], y=xFlippedMdsLayout[,2], color=sc_results[,2], label=sc_results[,1])) + geom_point() + geom_text() + theme( legend.position="bottom" )

km <- kmeans(netDist, m) 

## Retrieve and store cluster assignments
kmeans_clusters <- km$cluster
kmeans_results <- cbind(rownames(netAdjacency), cluster = as.factor(kmeans_clusters))
kmeans_plot = ggplot(data = layoutDF, aes(x=xFlippedMdsLayout[,1], y=xFlippedMdsLayout[,2], color=kmeans_results[,2], label=kmeans_results[,1])) + geom_point() + geom_text() + theme( legend.position="bottom" )

grid.arrange(kmeans_plot, sc_plot, nrow=1)