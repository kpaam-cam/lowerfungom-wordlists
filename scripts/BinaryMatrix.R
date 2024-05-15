# Test code for working with a binary cognate matrix. Worked well with PAM.
# More or less the same as the LingPy matrix, which isn't surprising.
# Kind of messy
# Can also use with spectral, but results weird, like before


binCogs = read.table('/Users/jcgood/gitrepos/lowerfungom-wordlists/analyses/Phase3a-Fall2023/kplfSubset-scaid-binMatrix.tsv', sep="\t", header = TRUE, fill=TRUE)

binRows = binCogs[, 1]
binCogs = binCogs[,-1]
rownames(binCogs) = rows

binMat = as.matrix(dist(binCogs))

binPam = pam(binMat, 7)

binPam_results <- cbind(binRows, cluster = as.factor(binPam$cluster))

print(autoplot(
		pam(dists, 14),
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
		guides(color = guide_legend(override.aes = aes(label = "", alpha = 1), title.position = "top")))