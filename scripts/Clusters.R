library(cluster)
library(factoextra)
library(ggfortify)
library(ggplot2)
library(khroma)

dists <-
  read.csv(
    '/Users/jcgood/gitrepos/lowerfungom-wordlists/analyses/Phase3a-Fall2023/kplfSubset-SCA-0.45_threshold-heatmap.matrix.dst',
    sep = "\t"
  )
rownames(dists) = dists[, 1]
dists = dists[, -1]
distspca = prcomp(dists, scale. = TRUE)

# Reverse axes for spatial presentation
distspca$x[, 1] = distspca$x[, 1] * -1
distspca$x[, 2] = distspca$x[, 2] * -1

options(ggrepel.max.overlaps = Inf)

smooth_rainbow <- color("smooth rainbow")

clusterLabels = list(
	c("Mungbam","Non-Mungbam"),
	c("Mungbam","Mufu-Mundabli","Other"),
	c("Other","Mufu-Mundabli","Mungbam", "Kung"),
	c("Other","Mufu-Mundabli", "Mashi", "Mungbam","Kung"),
	c("Ajumbu","Other", "Mufu-Mundabli", "Mashi","Mungbam","Kung"),
	c("Ajumbu","Mixed1", "Mixed2", "Mufu-Mundabli","Mashi","Mungbam", "Kung"),
	c("Ajumbu","Mixed1", "Mixed2", "Mufu-Mundabli","Mashi","Mungbaic", "Missong", "Kung"),
	c("Ajumbu","Fang", "Koshin", "Buu", "Mufu-Mundabli","Mashi","Mungbaic", "Missong", "Kung"),
	c("Ajumbu","Fang", "Koshin", "Buu", "Mufu-Mundabli","Mashi","Mixed Mungbam 1", "Mixed Mungbam 2", "Missong", "Kung"),
	c("Ajumbu","Fang", "Koshin", "Buu", "Mufu-Mundabli","Mashi","Mixed Mungbam 1", "Mixed Mungbam 2", "Munken", "Missong", "Kung"),
	c("Ajumbu","Fang", "Koshin", "Buu", "Mufu-Mundabli","Mashi","Abar", "Ngun", "Biya", "Munken", "Missong", "Kung"),
	c("Ajumbu","Fang","Koshin","Buu","Mufu","Mundabli","Mashi","Abar","Ngun","Biya", "Munken","Missong","Kung")
	)

for( n in 2:13 ) {
	print(paste("Generating plot for", n, "clusters"))
	pdf(file=paste("/Users/jcgood/Library/CloudStorage/Box-Box/Papers/WestermannVolume/Figures/Clusters/", n ,".pdf", sep=""),
		width=10, height=8)
	print(autoplot(
		pam(dists, n),
		label = TRUE,
		label.size = 3,
		label.repel = T
		) + scale_y_reverse() + scale_x_reverse() +
		theme_light() +
		theme(legend.spacing.x = unit(0, "points"), legend.text=element_text(size=rel(1.05)), legend.title=element_text(size=rel(1.35))) +
		guides(color = guide_legend(override.aes = aes(label = "", alpha = 1))) +
		scale_color_manual(paste(" Clusters (n = ", n, ")", sep=""), labels = clusterLabels[[n-1]], values = c(smooth_rainbow(n, range = c(0.25, 1)))))
	dev.off()
	}