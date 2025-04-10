# Early visualizations for Lower Fungom data

library(ggplot2)
library(ggfortify)
library(factoextra)
library(cluster)
library(ggpubr)
library(khroma)

smooth_rainbow <- color("smooth rainbow")
options(ggrepel.max.overlaps = Inf)

clusterLabels = list(
	c("Mungbam","Non-Mungbam"),
	c("Mungbam","Mufu-Mundabli","Other"),
	c("Other","Mufu-Mundabli","Mungbam", "Kung"),
	c("Other","Mufu-Mundabli", "Mashi", "Mungbam","Kung"),
	c("Ajumbu","Other", "Mufu-Mundabli", "Mashi","Mungbam","Kung"),
	c("Ajumbu","Mixed 1", "Mixed 2", "Mufu-Mundabli","Mashi","Mungbam", "Kung"),
	c("Ajumbu","Mixed 1", "Mixed 2", "Mufu-Mundabli","Mashi","Mungba", "Missong", "Kung"),
	c("Ajumbu","Fang", "Koshin", "Buu", "Mufu-Mundabli","Mashi","Mungba", "Missong", "Kung"),
	c("Ajumbu","Fang", "Koshin", "Buu", "Mufu-Mundabli","Mashi","Mixed Mungbam 1", "Mixed Mungbam 2", "Missong", "Kung"),
	c("Ajumbu","Fang", "Koshin", "Buu", "Mufu-Mundabli","Mashi","Mixed Mungbam 1", "Mixed Mungbam 2", "Munken", "Missong", "Kung"),
	c("Ajumbu","Fang", "Koshin", "Buu", "Mufu-Mundabli","Mashi","Abar", "Ngun", "Biya", "Munken", "Missong", "Kung"),
	c("Ajumbu","Fang","Koshin","Buu","Mufu","Mundabli","Mashi","Abar","Ngun","Biya", "Munken","Missong","Kung")
	)


# Use this to get the medoid clusters for visualization to show how 
# segment clustering differs from lexical clusters
lfdists <-
  read.csv(
    '/Users/jcgood/gitrepos/lowerfungom-wordlists/analyses/Phase3a-Fall2023/kplfSubset-SCA-0.45_threshold-heatmap.matrix.dst',
    sep = "\t"
  )
rownames(lfdists) = lfdists[, 1]
lfdists = lfdists[, -1]


dists <-
  read.csv(
    '/Users/jcgood/gitrepos/lowerfungom-wordlists/analyses/segments/segmentProfiles-LF.tsv',
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


phdistsmds <- cmdscale(dists, eig=T) # need eig for plotting
phdistsmds.df <- as.data.frame(phdistsmds$points)

# For lexical-based clusters
n = 13
mdsgroups = as.factor(pam(lfdists, n)$cluster)

# Now integrate those groups into the MDS object for plotting
phdistsmds.df$groups = mdsgroups[rownames(phdistsmds.df)]
 
# Hand ordered smooth_rainbow 13 colors to kind of match the schematic LF map
matchcolors = c("#62AC99", "#97211B", "#6F4C9B", "#D7AE3E", "#E69136", "#E4682E", "#B2BD4E", "#5469B9", "#4D8BC4", "#559FB0", "#62AC99", "#7FB974", "#521A13")

# Now generate the plot
ggscatter(
	phdistsmds.df,
	x = "V1",
	y = "V2",
	color = "groups",
	size = 1,
	repel = TRUE,
	label=rownames(phdistsmds.df),
	show.legend=FALSE
	) + scale_y_reverse() + scale_x_reverse() +
	theme(legend.position = "none") +
	scale_color_manual("", labels = clusterLabels[[n-1]],
						values = matchcolors
						) +
	xlab("Dimension 1") +
	ylab("Dimension 2")


