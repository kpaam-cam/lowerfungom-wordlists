# Used in the Westermann paper to graphs of concept overlap across doculects for Lower Fungom

library(igraph)
library(ggnetwork)
library(RColorBrewer)

cogNetwork <- read.csv(

'/Users/jcgood/gitrepos/lowerfungom-wordlists/analyses/Phase3a-Fall2023/kplfSubset-0.450.55_thresholds-cognates-Network.tsv',

#'/Users/jcgood/gitrepos/lowerfungom-wordlists/analyses/Phase3a-Fall2023/kplfSubset-0.450.55lexstatid_thresholds-cognates-Network.tsv',

sep = "\t"

)

netGraph <- graph_from_data_frame(cogNetwork, directed=FALSE)

# igraph looks for a weight attribute; so I copy it here
E(netGraph)$weight <- E(netGraph)$SharedCognateCount

# Basic plot using shared cognates as weighting
plot(netGraph, edge.width = 1.032^(E(netGraph)$weight)/10, vertex.size=0, vertex.shape = 'none', edge.curved=.2)

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

# The PDF rendered the graph in ways that were not as visually nice as a .tiff.
png(file=paste("/Users/jcgood/Library/CloudStorage/Box-Box/Papers/WestermannVolume/Figures/", "CogNetwork" ,".png", sep=""),
	units="in", width=6, height=5, res=1000)
# Aspects of this remain magical to me
ggplot(ggnetwork(netGraph, layout=xFlippedMdsLayout), # convert igraph to ggnetwork graph
	aes(x = x, y = y, xend = xend, yend = yend)) + # Set up graph base
	geom_edges(aes(color = weight, lwd=1.03^weight), show.legend=FALSE, curvature=.15 ) + 
	geom_nodes(color = "darkblue", size = 1) + scale_colour_gradientn(colours = edgecolors) +
	geom_nodetext_repel(aes(label = name), color = "darkblue", size = 2.5, max.overlaps=Inf) +
	scale_linewidth(range = c(0, 2)) + # Default scaling makes lines too wide
	theme_blank() +
	theme(
        plot.background = element_rect(fill = "lightcyan"), 
        panel.background = element_rect(fill = "lightcyan", colour=NA)
    	)
dev.off()

# Make the Buu-specific graph
BuuNetwork <- read.csv(   '/Users/jcgood/gitrepos/lowerfungom-wordlists/analyses/Phase3a-Fall2023/kplfSubset-0.450.55_thresholds-cognateSelection-Network.tsv',
    sep = "\t"
)

BuuGraph <- graph_from_data_frame(BuuNetwork, directed=FALSE)

# Tried but failed to gray out "unused" vertices. Will need to await some kind of overhaul not using igraph, maybe
png(file=paste("/Users/jcgood/Library/CloudStorage/Box-Box/Papers/WestermannVolume/Figures/", "BuuCogNetwork" ,".png", sep=""),
	units="in", width=6, height=5, res=1000)
ggplot(ggnetwork(BuuGraph, layout=xFlippedMdsLayout), # convert igraph to ggnetwork graph
       aes(x = x, y = y, xend = xend, yend = yend)) + # Set up graph base
    geom_edges(aes(color=color, lwd=1.03^weight), curvature=.1, show.legend = FALSE ) + 
    geom_nodes(color = "gray30", size = 1) +
    geom_nodetext_repel(aes(label = name), color="gray30", size = 2.5, max.overlaps=Inf) +
    scale_linewidth(range = c(0, 1)) + # Default scaling makes lines too wide
    # the igraph to ggplot conversion caused problems for attributes. colors were read as attributes, not colors. This hack gets the colors right
    scale_color_manual(values = c("#5385BC", "transparent", "transparent", "#9970AB", "#E34D34")) +
    theme_blank()
dev.off()
    


############# OLD CODE, replaced with ggplot2 version for node readability
# with color
cols <- brewer.pal(3, "YlOrRd")
CRP = colorRampPalette(cols)
plot(netGraph, edge.width = 1.033^(E(netGraph)$weight)/10, vertex.size=0, vertex.shape = 'none', edge.curved=.2, layout=xFlippedMdsLayout, edge.color = CRP(130)[(E(netGraph)$weight)], vertex.label.cex=.5)

# Make the Buu-specific graph
BuuNetwork <- read.csv(   '/Users/jcgood/gitrepos/lowerfungom-wordlists/analyses/Phase3a-Fall2023/kplfSubset-0.450.55_thresholds-cognateSelection-Network.tsv',
    sep = "\t"
)

# For color formatting (and maybe other things in the future)
BuuNodes <- read.csv(   '/Users/jcgood/gitrepos/lowerfungom-wordlists/analyses/Phase3a-Fall2023/kplfSubset-0.450.55_thresholds-cognateSelection-Vertices.tsv',
    sep = "\t"
)

BuuGraph <- graph_from_data_frame(BuuNetwork, directed=FALSE)

plot(BuuGraph, edge.width = 1.05^(E(BuuGraph)$weight)/10, vertex.size=0, vertex.shape = 'none', edge.curved=.15, layout=xFlippedMdsLayout, vertex.label.cex=.6, vertex.label.color=BuuNodes$color)
