# Creates the lexical network graphs used in the paper

library(igraph)
library(ggnetwork)
library(RColorBrewer)

cogNetwork <- read.csv(
	'../analyses/kplfSubset-0.45_thresholds-cognates-Network.tsv',
	sep = "\t"
	)

netGraph <- graph_from_data_frame(cogNetwork, directed=FALSE)

# igraph looks for a weight attribute; so I copy it here
E(netGraph)$weight <- E(netGraph)$SharedCognateCount

# Basic plot using shared cognates as weighting
plot(netGraph, edge.width = 1.032^(E(netGraph)$weight)/10, vertex.size=0, vertex.shape = 'none', edge.curved=.2)

# Make an adjacency matrix to put the weights in a matrix as a means of calculating a layout
netAdjacency <- as_adjacency_matrix(netGraph, attr="weight", sparse=FALSE)

# Create inverted adjacency for distance measures for things like MDS
invAdjacency = 1/netAdjacency
invAdjacency[!is.finite(invAdjacency)] <- 0 # change accidental infinities to zero

# Distance metric that yields an interpretable layout
sqrtInvAdjacency <- invAdjacency^(1/2)

# Making an MDS
sqrtInvAdjacencyMDS <- cmdscale(sqrtInvAdjacency)
plot(sqrtInvAdjacencyMDS)
text(x=sqrtInvAdjacencyMDS[,1], y=sqrtInvAdjacencyMDS[,2], labels = row.names(sqrtInvAdjacencyMDS), cex=.7)

# Make a new graph with the inverse weights
invGraph <- netGraph
E(invGraph)$weight <- sqrt(1/E(netGraph)$weight)

# Adjust the layout, edge weighting, etc
mdsLayout <- layout_with_mds(invGraph, dist=sqrtInvAdjacency)
plot(netGraph, edge.width = 1.032^(E(netGraph)$weight)/10, vertex.size=0, vertex.shape = 'none', edge.curved=.2, layout=mdsLayout)

# Flip to match east-west/north-south geogrpahy
xFlippedMdsLayout <- mdsLayout
xFlippedMdsLayout[,2] <- -xFlippedMdsLayout[,2]
plot(netGraph, edge.width = 1.032^(E(netGraph)$weight)/10, vertex.size=0, vertex.shape = 'none', edge.curved=.2, layout=xFlippedMdsLayout)

# set color scale boundaries (determined via trial and error)
edgecolors = c("#FFA50088", "#CC7722FF")

# The PDF rendered the graph in ways that were not as visually nice as a .png
png(file=paste("../figures/", "CogNetwork" ,".png", sep=""),
	units="in", width=6, height=5, res=1000)

# The workhorse plot
ggplot(ggnetwork(netGraph, layout=xFlippedMdsLayout), # convert igraph to ggnetwork graph
	aes(x = x, y = y, xend = xend, yend = yend)) + # Set up graph base
	geom_edges(aes(color = weight, lwd=1.03^weight), show.legend=FALSE, curvature=.15 ) + 
	geom_nodes(color = "darkblue", size = 1) + scale_colour_gradientn(colours = edgecolors) +
	geom_nodetext_repel(aes(label = name), color = "darkblue", size = 2.5, max.overlaps=Inf, segment.alpha = 0.6) +
	scale_linewidth(range = c(0, 2)) + # Default scaling makes lines too wide
	theme_blank() +
	theme(
        plot.background = element_rect(fill = "lightcyan"), 
        panel.background = element_rect(fill = "lightcyan", colour=NA)
    	)

dev.off()

# Make the Buu-specific graph
BuuNetwork <- read.csv(   '../analyses/kplfSubset-0.45_thresholds-cognateSelection-Network.tsv',
    sep = "\t"
	)

BuuGraph <- graph_from_data_frame(BuuNetwork, directed=FALSE)

# Mark vertices as "relevant" if they have at least one connection with weight > 0.01.
# Vertices whose connections are only 0.01 are treated as non-relevant/background.
thr <- 0.01
V(BuuGraph)$relevant <- sapply(V(BuuGraph), function(v) {
  e <- incident(BuuGraph, v, mode = "all")
  if (length(e) == 0) return(FALSE)
  any(E(BuuGraph)[e]$weight > thr)
})

# Tried but failed to gray out "unused" vertices. Will need to await some kind of overhaul not using igraph, maybe
png(file=paste("../figures/", "BuuCogNetwork" ,".png", sep=""),
	units="in", width=6, height=5, res=1000)

# Convert igraph to ggnetwork graph, carrying vertex attributes (including 'relevant')
gBuu <- ggnetwork(BuuGraph, layout=xFlippedMdsLayout)

ggplot(gBuu,
       aes(x = x, y = y, xend = xend, yend = yend)) + # Set up graph base

    # Background (non-relevant) vertices drawn first so they render underneath
    geom_nodes(data = subset(gBuu, relevant == FALSE),
               color = "grey75", size = 1.2, shape = 16, stroke = 0) +

    geom_edges(aes(color=color, lwd=1.03^weight), curvature=.1, alpha=.8, show.legend = FALSE ) +

    # Relevant vertices drawn on top
    geom_nodes(data = subset(gBuu, relevant == TRUE),
               color = "gray30", size = 1) +

    # Label only relevant vertices (keeps background nodes from visually competing)
    geom_nodetext_repel(data = subset(gBuu, relevant == TRUE),
                        aes(label = name), color="gray30", size = 2.5, max.overlaps=Inf) +

    scale_linewidth(range = c(0, 1)) + # Default scaling makes lines too wide
    # the igraph to ggplot conversion caused problems for attributes. colors were read as attributes, not colors. This hack gets the colors right
    scale_color_manual(values = c("#5385BC", "transparent", "transparent", "#9970AB", "#E34D34")) +
    theme_blank()

dev.off()
