library(cluster)
library(factoextra)
library(ggfortify)
library(ggplot2)
library(khroma)
library(scales)

dists <-
  read.csv(
    '/Users/jcgood/gitrepos/lowerfungom-wordlists/analyses/Phase3a-Fall2023/kplfSubset-SCA-0.45_threshold-heatmap.matrix.dst',
    sep = "\t"
  )
rownames(dists) = dists[, 1]
dists = dists[, -1]


options(ggrepel.max.overlaps = Inf)

smooth_rainbow <- color("smooth rainbow")

clusterLabels = list(
	c("Mungbam","Non-Mungbam"),
	c("Mungbam","Mufu-Mundabli","Other"),
	c("Other","Mufu-Mundabli","Mungbam", "Kung"),
	c("Other","Mufu-Mundabli", "Mashi", "Mungbam","Kung"),
	c("Ajumbu","Other", "Mufu-Mundabli", "Mashi","Mungbam","Kung"),
	c("Ajumbu","Mixed1", "Mixed2", "Mufu-Mundabli","Mashi","Mungbam", "Kung"),
	c("Ajumbu","Mixed1", "Mixed2", "Mufu-Mundabli","Mashi","Mungba", "Missong", "Kung"),
	c("Ajumbu","Fang", "Koshin", "Buu", "Mufu-Mundabli","Mashi","Mungba", "Missong", "Kung"),
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
		theme(legend.spacing.x = unit(0, "points"),
			legend.text=element_text(size=rel(1.25), margin = margin(r = 18)),
			legend.title=element_text(size=rel(0)),
			legend.position = "bottom",
			panel.grid.major = element_blank(),
			panel.grid.minor = element_blank()) +
		guides(color = guide_legend(override.aes = aes(label = "", alpha = 1), title.position = "top")) +
		scale_color_manual("", labels = clusterLabels[[n-1]], values = c(smooth_rainbow(n, range = c(0.25, 1)))))
	dev.off()
	}
	
	
# Some hacking for the PCA chart to get it to match the one produced by autoplot for pam, which must be embedded deep in the code making it easy to alter it for the straight PCA
# PAM uses prcomp, but we should not adjust for variance (because I don't think this is justified for the data)
distspca = prcomp(dists)

# Decided to use MDS in the end for this, but will keep this for future reference
pc1per = label_percent(.01)(summary(distspca)$importance[2])
pc2per = label_percent(.01)(summary(distspca)$importance[5])

fviz_pca_ind(
    distspca,
    col.ind = "cos2",
    gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"),
    repel = TRUE, title = NULL
	) + scale_y_reverse() +
		scale_x_reverse() +
		ggtitle("") +
		xlab(paste("PC1 (", pc1per , ")", sep="")) +
		ylab(paste("PC2 (", pc2per, ")", sep="")) +
		theme_classic()


# MDS plot for all village variation together. Hacked together since the MDS data structure confused me
# Ideas for this came from: https://corpling.hypotheses.org/3497
distsmds <- cmdscale(dists, eig=T) # need eig for plotting
distsmds.df <- as.data.frame(distsmds$points)

# Now we do a hack. The PAM for the thirteen villages, unlike clustering on the MDS,
# happens to get the 13 villages right, while clustering on the MDS doesn't quite do
# this. So, we use the groupings from PAM as a quick way to get the groupings into
# an R data object of some kind (a vector?) to colorize the MDS graph propery
mdsgroups = as.factor(pam(dists, 13)$cluster)

# Now integrate those groups into the MDS object for plotting
distsmds.df$groups <- mdsgroups

# Now generate the plot
pdf(file=paste("/Users/jcgood/Library/CloudStorage/Box-Box/Papers/WestermannVolume/Figures/", "MDS" ,".pdf", sep=""),
	width=8, height=4)
ggscatter(
	distsmds.df,
	x = "V1",
	y = "V2",
	color = "groups",
	size = 1,
	repel = TRUE,
	label=rownames(distsmds.df),
	show.legend=FALSE
	) + scale_y_reverse() +
	theme(legend.position = "none") +
	scale_color_manual("", labels = clusterLabels[[n-1]],
						values = c(smooth_rainbow(n, range = c(0.25, 1)))
						)
dev.off()