# This makes a network of cognates across concepts to see how cognates bundle and
# distribute. It's still quite experimental.
library(igraph)
library(ggnetwork)
library(RColorBrewer)

cogNetwork <- read.csv(

#'/Users/jcgood/gitrepos/lowerfungom-wordlists/analyses/Phase3a-Fall2023/kplfSubset-cognetwork.tsv',

'/Users/jcgood/gitrepos/lowerfungom-wordlists/grollemund-wordlists/analyses/grollemund-cognetwork.tsv',


sep = "\t"

)

netGraph <- graph_from_data_frame(cogNetwork, directed=FALSE)

# igraph looks for a weight attribute; so I copy it here
E(netGraph)$weight <- E(netGraph)$Weight

# Basic plot using shared cognates as weighting
plot(netGraph, edge.width =E(netGraph)$weight, vertex.size=0, vertex.shape = 'none', edge.curved=.2)

# Make an adjacency matrix to put the weights in a matrix as a means of calculating a layout
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

# Experiment with layouts
mdsLayout <- layout_with_mds(invGraph, dist=sqrtInvAdjacency)
plot(netGraph, edge.width = 1.032^(E(netGraph)$weight)/10, vertex.size=0, vertex.shape = 'none', edge.curved=.2, layout=mdsLayout)

xFlippedMdsLayout <- mdsLayout
xFlippedMdsLayout[,2] <- -xFlippedMdsLayout[,2]
plot(netGraph, edge.width = 1.032^(E(netGraph)$weight)/10, vertex.size=0, vertex.shape = 'none', edge.curved=.2, layout=xFlippedMdsLayout)

# color scale (trial and error)
edgecolors = c("#FFA50088", "#CC7722FF")

# Aspects of this remain magical to me
# curvature had to be 0 for this or there was an obscure R error
ggplot(ggnetwork(netGraph, layout=xFlippedMdsLayout), # convert igraph to ggnetwork graph
	aes(x = x, y = y, xend = xend, yend = yend)) + # Set up graph base
	geom_edges(aes(color = weight, lwd=1.03^weight), show.legend=FALSE, curvature=0 ) + 
	geom_nodes(color = "darkblue", size = 1) + scale_colour_gradientn(colours = edgecolors) +
	geom_nodetext_repel(aes(label = name), color = "darkblue", size = 2.5, max.overlaps=Inf) +
	scale_linewidth(range = c(0, 2)) + # Default scaling makes lines too wide
	theme_blank() +
	theme(
        plot.background = element_rect(fill = "lightcyan"), 
        panel.background = element_rect(fill = "lightcyan", colour=NA)
    	)
