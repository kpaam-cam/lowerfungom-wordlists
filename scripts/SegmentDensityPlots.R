library(ggplot2)
library(plyr)

segdists = 
as.data.frame(read.csv(
					"/Users/jcgood/gitrepos/tls/analyses/segments/normedSegmentCounts-TLS.tsv", 
					#"/Users/jcgood/gitrepos/lowerfungom-wordlists/analyses/segments/normedSegmentCounts-LF.tsv",
					#"/Users/jcgood/gitrepos/lowerfungom-wordlists/analyses/segments/normedSegmentCounts-LF-ASCIIChars.tsv",
					#"/Users/jcgood/gitrepos/lowerfungom-wordlists/grollemund-wordlists/analyses/segments/normedSegmentCounts-Grollemund.tsv",
				sep="\t", header=TRUE, row.names=1))

for (i in 1:nrow(segdists)) {
  row_data <- as.numeric(segdists[i, ])
  dens <- density(row_data)
  dens_df <- data.frame(x = dens$x, y = dens$y)
  
  # Create the plot
  p <- ggplot(dens_df, aes(x = x, y = y)) +
    geom_line() +
    geom_ribbon(aes(ymin = 0, ymax = y), fill = "lightblue", alpha = 0.2) +
    ggtitle(paste("Density Plot for", rownames(segdists)[i])) +
    xlab("Values") +
    ylab("Density") +
    theme_minimal()
  
  # Save the plot to a PDF file with the path "/analyses/"
  ggsave(filename = paste0(
  	#"/Users/jcgood/gitrepos/lowerfungom-wordlists/analyses/segments/dists/",
  	#"/Users/jcgood/gitrepos/tls/analyses/segments/dists/",
  	"/Users/jcgood/gitrepos/lowerfungom-wordlists/grollemund-wordlists/analyses/segments/dists/",
  	rownames(segdists)[i], ".pdf"),
  	plot = p)

	}
	
	
#### Bonus code to overlay plots (k/g example)
ggplot() +
    geom_area(data = kdens_df, aes(x = x, y = y, fill = group), alpha = 0.3) +
    geom_area(data = gdens_df, aes(x = x, y = y, fill = group), alpha = 0.3) +
    scale_fill_manual(values = c("#F8766D", "#619CFF"), labels = c("[k]", "[g]")) +
    labs(title = "Density Distributions", x = "Value", y = "Density", fill = "Distribution") +
    theme_minimal() + theme(panel.grid = element_blank(), plot.background = element_rect(fill = "white"))