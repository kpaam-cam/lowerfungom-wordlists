library(igraph)

cogNetwork <- read.csv(
'/Users/jcgood/gitrepos/lowerfungom-wordlists/analyses/Phase3a-Fall2023/kplfSubset-0.450.55_thresholds-cognates-Network.tsv',
sep = "\t"
)

netGraph <- graph_from_data_frame(cogNetwork, directed=FALSE)

# igraph looks for a weight attribute; so I copy it here
E(netGraph)$weight <- E(netGraph)$SharedCognateCount

# Basic plot using shared cognates as weighting
plot(netGraph, edge.width = 1.032^(E(netGraph)$weight)/10, vertex.size=0, vertex.shape = 'none', edge.curved=.2)

# Make an adjacency matrix
netAdjacency <- as_adjacency_matrix(netGraph, attr="weight")

# Create inverted adjacency for distance measures for things like MDS
invAdjacency = 1/netAdjacency
invAdjacency[!is.finite(invAdjacency)] <- 0 # change accidental infinities to zero

# I played around with transformations that seem to make the data more intelligble
# Square root helped by "compressing" distances
sqrtInvAdjacency <- invAdjacency^(1/2)

# Making an MDS
sqrtInvAdjacencyMDS <- cmdscale(sqrtInvAdjacency)
plot(sqrtInvAdjacencyMDS)
text(x=sqrtInvAdjacencyMDS[,1], y=sqrtInvAdjacencyMDS[,2], labels = row.names(sqrtInvAdjacencyMDS), cex=.7)

# Make a new graph with the inverse weights
invGraph <- netGraph
E(invGraph)$weight <- sqrt(1/E(netGraph)$weight)
