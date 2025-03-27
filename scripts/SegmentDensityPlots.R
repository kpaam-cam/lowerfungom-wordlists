segdists = 
as.data.frame(read.csv(
					#"/Users/jcgood/gitrepos/tls/analyses/normedSegmentCounts-TLS.tsv", 
					#"/Users/jcgood/gitrepos/lowerfungom-wordlists/analyses/normedSegmentCounts-LF.tsv",
					"/Users/jcgood/gitrepos/lowerfungom-wordlists/grollemund-wordlists/analyses/normedSegmentCounts-Grollemund.tsv",
				sep="\t", header=TRUE, row.names=1))

for (i in 1:nrow(segdists)) {
    row_data <- as.numeric(segdists[i, ])
    dens <- density(row_data)
    plot(dens, main = paste("Density Plot for", rownames(segdists)[i]), xlab = "Values", ylab = "Density")
}