# This takes a matrix of distances of selected cognates in the dataset (across concepts)
# and loads it for clustering analyses

library(ggfortify)
library(factoextra)
library(cluster)

dists <-
  read.csv(

#'/Users/jcgood/gitrepos/lowerfungom-wordlists/analyses/Phase3a-Fall2023/kplfSubset-chisq.tsv',
         #'/Users/jcgood/gitrepos/lowerfungom-wordlists/analyses/Phase3a-Fall2023/kplfSubset-scaid053-wghtdcogdistances.tsv',

'/Users/jcgood/gitrepos/lowerfungom-wordlists/analyses/Phase3a-Fall2023/kplfSubset-scaid053-cogdistances.tsv',

 #'/Users/jcgood/gitrepos/lowerfungom-wordlists/grollemund-wordlists/analyses/grollemund-chisq.tsv',

#'/Users/jcgood/gitrepos/lowerfungom-wordlists/grollemund-wordlists/analyses/grollemund-scaid20400-cogdistances.tsv',

#'/Users/jcgood/gitrepos/lowerfungom-wordlists/grollemund-wordlists/analyses/grollemund-scaid40400-cogdistances.tsv',

#'/Users/jcgood/gitrepos/lowerfungom-wordlists/grollemund-wordlists/analyses/grollemund-scaid100500-wghtdcogdistances.tsv',

   sep = "\t"

  )
rownames(dists) = dists[, 1]
dists = dists[, -1]
distspca = prcomp(dists, scale. = TRUE)

# Reverse axes for spatial presentation
#distspca$x[, 1] = distspca$x[, 1] * -1
#distspca$x[, 2] = distspca$x[, 2] * -1

options(ggrepel.max.overlaps = Inf)

fviz_pca_ind(
  distspca,
  col.ind = "cos2",
  gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"),
  repel = TRUE
) + scale_x_reverse()


autoplot(
    pam(dists, n),
    label = TRUE,
    label.size = 3,
    label.repel = T
) +
    theme_light() +
    theme(legend.spacing.x = unit(0, "points"),
          legend.text=element_text(size=rel(1.25), margin = margin(r = 18)),
          legend.title=element_text(size=rel(0)),
          legend.position = "bottom",
          panel.grid.major = element_blank(),
          panel.grid.minor = element_blank()) +
    guides(color = guide_legend(override.aes = aes(label = "", alpha = 1), title.position = "top")) +
    scale_color_manual("", labels = clusterLabels[[n-1]], values = c(smooth_rainbow(n, range = c(0.25, 1)))) + coord_flip() + scale_x_reverse()