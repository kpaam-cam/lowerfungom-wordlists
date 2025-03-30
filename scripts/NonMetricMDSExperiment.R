# see https://uw.pressbooks.pub/appliedmultivariatestatistics/chapter/nmds/

require(vegan, tidyverse)


dists <-
read.csv(
'/Users/jcgood/gitrepos/lowerfungom-wordlists/grollemund-wordlists/analyses/grollemund-SCA-0.45_threshold-heatmap.matrix.dst',
sep = "\t"
	)

rownames(dists) = dists[, 1]

dists = dists[, -1]

z <- metaMDS(comm = dists,
	autotransform = FALSE,
	distance = "bray",
	engine = "monoMDS",
	k = 3,
	weakties = TRUE,
	model = "global",
	maxit = 300,
	try = 40,
	trymax = 100)

z.points <- data.frame(z$points)

p <- ggplot(data = z.points, aes(x = MDS1, y = MDS2)) +
	theme_bw() +
	theme(axis.title = element_blank(),
	axis.ticks = element_blank(),
	axis.text = element_blank())

p + geom_point() + geom_text(label = rownames(dists))

z$stress