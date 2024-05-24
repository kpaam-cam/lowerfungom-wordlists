# Test code for working with a binary cognate matrix. Worked well with PAM.
# More or less the same as the LingPy matrix, which isn't surprising.
# Kind of messy
# Can also use with spectral, but results weird, like before
# See: https://rpubs.com/gargeejagtap/SpectralClustering
# This was a code "dump", and I don't fully remember what I was doing


binCogs = read.table('/Users/jcgood/gitrepos/lowerfungom-wordlists/analyses/Phase3a-Fall2023/kplfSubset-scaid-binMatrix.tsv', sep="\t", header = TRUE, fill=TRUE)

binRows = binCogs[, 1]
binCogs = binCogs[,-1]
rownames(binCogs) = rows

binMat = as.matrix(dist(binCogs))
binPam = pam(binMat, 7)

binPam_results <- cbind(binRows, cluster = as.factor(binPam$cluster))

pam_plot = ggplot(data = layoutDF, aes(x=xFlippedMdsLayout[,1], y=xFlippedMdsLayout[,2], color=binPam_results[,2], label=binPam_results[,1])) + geom_point() + geom_text() + theme( legend.position="bottom" )

###########################################
### ??? Why is this here? ###
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