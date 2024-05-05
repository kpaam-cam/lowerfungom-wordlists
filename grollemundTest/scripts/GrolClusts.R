library(cluster)
library(factoextra)
library(ggfortify)
library(ggplot2)
library(khroma)
library(ggpubr)
library(ggrepel)


dists <-
  read.csv(
    '/Users/jcgood/gitrepos/lowerfungom-wordlists/grollemundTest/analyses/grollemund-LS-0.55_threshold-heatmap.matrix.dst',
    sep = "\t"
  )
rownames(dists) = dists[, 1]
dists = dists[, -1]

clusterLabels = list(
  c("West","East"),
  c("Northwest","East","Southwest"),
  c("Other","Mufu-Mundabli","Mungbam", "Kung")
)


autoplot(
  pam(dists, n),
  label = TRUE,
  label.size = 3,
  label.repel = T,
  max.overlaps = Inf
) + scale_y_reverse() +
  theme_light() +
  theme(legend.spacing.x = unit(0, "points"),
        legend.text=element_text(size=rel(1.25), margin = margin(r = 18)),
        legend.title=element_text(size=rel(0)),
        legend.position = "bottom",
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank()) + 
  guides(color = guide_legend(override.aes = aes(label = "", alpha = 1), title.position = "top")) +
  scale_color_manual("", labels = clusterLabels[[n-1]], values = c(smooth_rainbow(n, range = c(0.25, 1))))