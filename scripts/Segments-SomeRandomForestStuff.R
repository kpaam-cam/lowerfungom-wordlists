library(ggplot2)
library(plyr)

segdists = 
as.data.frame(read.csv(
					#"/Users/jcgood/gitrepos/tls/analyses/segments/normedSegmentCounts-TLS.tsv", 
					#"/Users/jcgood/gitrepos/lowerfungom-wordlists/analyses/segments/normedSegmentCounts-LF.tsv",
					"/Users/jcgood/gitrepos/lowerfungom-wordlists/analyses/segments/normedSegmentCounts-LF-ASCIIChars.tsv",
					#"/Users/jcgood/gitrepos/lowerfungom-wordlists/grollemund-wordlists/analyses/normedSegmentCounts-Grollemund.tsv",
				sep="\t", header=TRUE, row.names=1))

docsegdists = t(segdists) # transpose the data frame

# Change LF doculect names to variety names as factor
docsegdists <- transform(docsegdists, Varieties = factor(sub("^.{3}(.*?)(\\d+)$", "\\1", rownames(docsegdists))))

docsegrf = randomForest(formula = docsegdists$Varieties ~ ., data = docsegdists, ntree=10000)

varImpPlot(docsegrf)