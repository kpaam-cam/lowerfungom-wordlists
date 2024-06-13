# Code placeholder to keep track of how I made one plot

# Based on LF cog distances, 0-53

# 8 groupings trial and error for sensible ones

cogLabels = c("Mungbam", "Eastern contact zone", "Minor cognates", "Mashi", "Mufu-Mundabli", "Kung", "Ajumbu", "Fang")

autoplot(
    pam(dists, 8),
    label = FALSE,
) + scale_x_reverse() +theme_light() +
    theme(legend.spacing.x = unit(0, "points"),
          legend.text=element_text(size=rel(1), margin = margin(r = 6)),
          legend.title=element_text(size=rel(0)),
          legend.position = "bottom",
          panel.grid.major = element_blank(),
          panel.grid.minor = element_blank()) + guides(color = guide_legend(override.aes = aes(label = "", alpha = 1), title.position = "top")) + 
    scale_color_manual("", labels = cogLabels, values = c(smooth_rainbow(8, range = c(0.15, 1))))
    
autoplot(
    pam(dists, 8),
    label = TRUE,
    label.size = 3,
    label.repel = T
) + scale_x_reverse() +theme_light() +
    theme(legend.spacing.x = unit(0, "points"),
          legend.text=element_text(size=rel(1), margin = margin(r = 6)),
          legend.title=element_text(size=rel(0)),
          legend.position = "bottom",
          panel.grid.major = element_blank(),
          panel.grid.minor = element_blank()) + guides(color = guide_legend(override.aes = aes(label = "", alpha = 1), title.position = "top")) + 
    scale_color_manual("", labels = cogLabels, values = c(smooth_rainbow(8, range = c(0.15, 1))))