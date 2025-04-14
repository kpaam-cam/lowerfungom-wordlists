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
groldists <-
  read.csv(   '/Users/jcgood/gitrepos/lowerfungom-wordlists/grollemund-wordlists/analyses/18June2024-allformsIthink/grollemund-SCA-0.45_threshold-heatmap.matrix.dst',
    sep = "\t"
  )
rownames(groldists) = groldists[, 1]
groldists = groldists[, -1]
groldistspca = prcomp(dists, scale. = TRUE)

# Reverse axes for spatial presentation
groldistspca$x[, 1] = distspca$x[, 1] * -1
groldistspca$x[, 2] = distspca$x[, 2] * -1

groldistsmds <- cmdscale(groldists, eig=T) # need eig for plotting
groldistsmds.df <- as.data.frame(groldistsmds$points)


dists <-
  read.csv(
    '/Users/jcgood/gitrepos/lowerfungom-wordlists/grollemund-wordlists/analyses/segments/segmentProfiles-Grollemund.tsv',

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
mdsgroups = as.factor(pam(groldists, n)$cluster)

# Now integrate those groups into the MDS object for plotting
distsmds.df$groups = mdsgroups[rownames(distsmds.df)]
groldistsmds.df$groups = mdsgroups[rownames(groldistsmds.df)]

# handordered to match lexical colors
matchcolors = c("#4E79C5", "#D1B541", "#521A13")

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


# Now generate the plot, no labels
ggscatter(
	distsmds.df,
	x = "V1",
	y = "V2",
	color = "groups",
	size = 2,
	repel = TRUE,
	show.legend=FALSE
	) + scale_y_reverse() + scale_x_reverse() +
	theme(legend.position = "none") +
	scale_color_manual("", labels = clusterLabels[[n-1]],
						values = matchcolors
						) +
	xlab("Dimension 1") +
	ylab("Dimension 2")

# Now generate the lex plot, no labels
ggscatter(
	groldistsmds.df,
	x = "V1",
	y = "V2",
	color = "groups",
	size = 2,
	repel = TRUE,
	show.legend=FALSE
	) + scale_y_reverse() + scale_x_reverse() +
	theme(legend.position = "none") +
	scale_color_manual("", labels = clusterLabels[[n-1]],
						values = matchcolors
						) +
	xlab("Dimension 1") +
	ylab("Dimension 2")


# Animation
library(ggpubr)
library(gganimate)
library(ggplot2)
library(dplyr)
library(av)


groldistsmds.df$frame <- "First"
distsmds.df$frame <- "Second"
combined_df <- bind_rows(groldistsmds.df, distsmds.df)

p <- ggscatter(
	combined_df,
	x = "V1",
	y = "V2",
	color = "groups",
	size = 1,
	repel = TRUE,
	label = NULL,
	show.legend = FALSE
	) +
	scale_y_reverse() + scale_x_reverse() +
	theme(legend.position = "none") +
	scale_color_manual(values = matchcolors) +
	xlab("Dimension 1") +
	ylab("Dimension 2") +
	transition_states(frame, transition_length = 2, state_length = 1) +
	ease_aes('linear')

animate(p, nframes = 1600, fps = 80, width = 2160, height = 2160, res = 400, end_pause = 100, renderer = av_renderer("/Users/jcgood/Desktop/animated_plot.mp4"))
