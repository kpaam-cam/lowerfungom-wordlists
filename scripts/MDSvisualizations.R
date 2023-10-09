library(ggfortify)
library(factoextra)
library(cluster)

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

fviz_pca_ind(
  distspca,
  col.ind = "cos2",
  gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"),
  repel = TRUE
) + scale_x_reverse()


autoplot(
  pam(dists, 7),
  frame = TRUE,
  frame.type = 'norm',
  label = TRUE,
  label.size = 3,
  label.repel = T
) + scale_y_reverse() + scale_x_reverse()
