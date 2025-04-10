# Early visualizations for Lower Fungom data

library(ggplot2)
library(ggfortify)
library(factoextra)
library(cluster)
library(ggpubr)
library(khroma)

smooth_rainbow <- color("smooth rainbow")

# Dummy for now
clusterLabels = list(
	c("West","East"),
	c("Northwest","Southwest","East"),
	c("Northwest","Great Lakes","East", "Southwest")
	)


# Use this to get the medoid clusters for visualization to show how 
# segment clustering differs from lexical clusters
tlsdists <-
  read.csv(
    '/Users/jcgood/gitrepos/tls/analyses/tls-SCA-0.45_threshold-heatmap.matrix.dst',

    sep = "\t"
  )
rownames(tlsdists) = tlsdists[, 1]
tlsdists = tlsdists[, -1]


dists <-
  read.csv(
    #'/Users/jcgood/gitrepos/lowerfungom-wordlists/analyses/segments/segmentProfiles-LF.tsv',
    #'/Users/jcgood/gitrepos/lowerfungom-wordlists/grollemund-wordlists/analyses/segments/segmentProfiles-Grollemund.tsv',
    '/Users/jcgood/gitrepos/tls/analyses/segments/segmentProfiles-TLS.tsv',
    sep = "\t"
  )
rownames(dists) = dists[, 1]
dists = dists[, -1]
distspca = prcomp(dists, scale. = TRUE)

# Reverse axes for spatial presentation
distspca$x[, 1] = distspca$x[, 1] * -1
distspca$x[, 2] = distspca$x[, 2] * -1

options(ggrepel.max.overlaps = Inf)

fviz_pca_ind(
  distspca,
  col.ind = "cos2",
  gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"),
  repel = TRUE
) + scale_x_reverse()

# autoplot(
#   pam(dists, 7),
#   frame = TRUE,
#   frame.type = 'norm',
#   label = TRUE,
#   label.size = 3,
#   label.repel = T
# ) + scale_y_reverse() + scale_x_reverse()


distsmds <- cmdscale(dists, eig=T) # need eig for plotting
distsmds.df <- as.data.frame(distsmds$points)

# For lexical-based clusters
n = 3
mdsgroups = as.factor(pam(tlsdists, n)$cluster)

# Now integrate those groups into the MDS object for plotting
distsmds.df$groups = mdsgroups[rownames(distsmds.df)]

# handordered to match lexical colors
matchcolors = c("#521A13","#4E79C5", "#D1B541")

# Now generate the plot
ggscatter(
	distsmds.df,
	x = "V1",
	y = "V2",
	color = "groups",
	size = 1,
	repel = TRUE,
	label=rownames(distsmds.df),
	show.legend=FALSE
	) + scale_y_reverse() + scale_x_reverse() +
	theme(legend.position = "none") +
	scale_color_manual("", labels = clusterLabels[[n-1]],
						values = matchcolors
						) +
	xlab("Dimension 1") +
	ylab("Dimension 2")


