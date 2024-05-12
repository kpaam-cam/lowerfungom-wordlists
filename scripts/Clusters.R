# This looks for clusters in languages based on lingpy cognate differences, tuned
# specifically to the Lower Fungom data

library(cluster)
library(factoextra)
library(ggfortify)
library(ggplot2)
library(khroma)
library(ggpubr)

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
	c("Ajumbu","Mixed 1", "Mixed 2", "Mufu-Mundabli","Mashi","Mungbam", "Kung"),
	c("Ajumbu","Mixed 1", "Mixed 2", "Mufu-Mundabli","Mashi","Mungba", "Missong", "Kung"),
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

# Example to get point-level silhouette scores
fviz_silhouette(pam(dists,7), label=TRUE)
	
# Some hacking for the PCA chart to get it to match the one produced by autoplot for pam, which must be embedded deep in the code making it easy to alter it for the straight PCA
# PAM uses prcomp, but we should not adjust for variance (because I don't think this is justified for the data)
distspca = prcomp(dists)

# Decided to use MDS in the end for this, but will keep this for future reference
pc1per = label_percent(.01)(summary(distspca)$importance[2])
pc2per = label_percent(.01)(summary(distspca)$importance[5])

# Finding optimal cluster number, etc.
# See below for how I hacked it to get rid of vertical cline
pdf(file=paste("/Users/jcgood/Library/CloudStorage/Box-Box/Papers/WestermannVolume/Figures/", "ClusterScores" ,".pdf", sep=""),
	width=8, height=4)
fviz_nbclust(dists, pam, method="silhouette", k.max=25) + ggtitle("")
dev.off()

# If we want to get the raw data, do this
clusterscores <- fviz_nbclust(dists, pam, method="silhouette", k.max=25) + ggtitle("")
clusterscores$data

# MDS plot for all village variation together. Hacked together since the MDS data structure confused me
# Ideas for this came from: https://corpling.hypotheses.org/3497
distsmds <- cmdscale(dists, eig=T) # need eig for plotting
distsmds.df <- as.data.frame(distsmds$points)

# Now we do a hack. The PAM for the thirteen villages, unlike clustering on the MDS,
# happens to get the 13 villages right, while clustering on the MDS doesn't quite do
# this. So, we use the groupings from PAM as a quick way to get the groupings into
# an R data object of some kind (a vector?) to colorize the MDS graph property.
# The data structure could have been produced by hand, but I still don't really
# understand R data types, and pam produced what I needed. So, it was easier.
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
						) +
	xlab("Dimension 1") +
	ylab("Dimension 2")
dev.off()


#############
fviz_nbclust <- function (x, FUNcluster = NULL, method = c("silhouette", "wss", "gap_stat"),
                          diss = NULL, k.max = 10, nboot = 100, verbose = interactive(),
                          barfill="steelblue", barcolor="steelblue", 
                          linecolor = "steelblue", print.summary = TRUE,  ...) 
  {
  set.seed(123)
  if(k.max < 2) stop("k.max must bet > = 2")
  method = match.arg(method)
  if(!inherits(x, c("data.frame", "matrix")) & !("Best.nc" %in% names(x)))
    stop("x should be an object of class matrix/data.frame or ",
         "an object created by the function NbClust() [NbClust package].")
  
  # x is an object created by the function NbClust() [NbClust package]
  if(inherits(x, "list") & "Best.nc" %in% names(x)){
      best_nc <- x$Best.nc
      if(class(best_nc) == "numeric") print(best_nc)
      else if(class(best_nc) == "matrix") 
        .viz_NbClust(x, print.summary, barfill, barcolor)
  }
  else if(is.null(FUNcluster)) stop("The argument FUNcluster is required. ",
                                    "Possible values are kmeans, pam, hcut, clara, ...")
  else if(!is.function(FUNcluster)){
    stop(
      "The argument FUNcluster should be a function. ",
      "Check if you're not overriding the specified function name somewhere."
      )
  }
  else if(method %in% c("silhouette", "wss")) {

      if (is.data.frame(x)) x <- as.matrix(x)
      if(is.null(diss)) diss <- stats::dist(x)
      
      v <- rep(0, k.max)
      if(method == "silhouette"){
        for(i in 2:k.max){
          clust <- FUNcluster(x, i, ...)
          v[i] <- .get_ave_sil_width(diss, clust$cluster)
        }
      }
      else if(method == "wss"){
        for(i in 1:k.max){
          clust <- FUNcluster(x, i, ...)
          v[i] <- .get_withinSS(diss, clust$cluster)
        }
        
      }
      
      df <- data.frame(clusters = as.factor(1:k.max), y = v, stringsAsFactors = TRUE)
      
      ylab <- "Total Within Sum of Square"
      if(method == "silhouette") ylab <- "Average silhouette width"
      
      p <- ggpubr::ggline(df, x = "clusters", y = "y", group = 1,
                          color = linecolor, ylab = ylab,
                          xlab = "Number of clusters k",
                          main = "Optimal number of clusters"
                          )
      if(method == "silhouette") 
        # The hack to get rid of the vertical line, removed the code adding it.
        p <- p 
      
      return(p) 
  }
  
  else if(method == "gap_stat"){
    extra_args <- list(...)
    gap_stat <- cluster::clusGap(x, FUNcluster, K.max = k.max,  B = nboot, 
                                 verbose = verbose, ...)
    if(!is.null(extra_args$maxSE)) maxSE <- extra_args$maxSE
    else maxSE <- list(method = "firstSEmax", SE.factor = 1)
    p <- fviz_gap_stat(gap_stat,  linecolor = linecolor, maxSE = maxSE)
    return(p) 
  }
  

}

#' @rdname fviz_nbclust
#' @param gap_stat an object of class "clusGap" returned by the function
#'   clusGap() [in cluster package]
#' @param maxSE a list containing the parameters (method and SE.factor) for
#'   determining the location of the maximum of the gap statistic (Read the
#'   documentation ?cluster::maxSE). Allowed values for maxSE$method include: 
#'   \itemize{ \item "globalmax": simply corresponds to the global maximum,
#'   i.e., is which.max(gap) \item "firstmax": gives the location of the first
#'   local maximum \item "Tibs2001SEmax": uses the criterion, Tibshirani et al
#'   (2001) proposed: "the smallest k such that gap(k) >= gap(k+1) - s_{k+1}". 
#'   It's also possible to use "the smallest k such that gap(k) >= gap(k+1) -
#'   SE.factor*s_{k+1}" where SE.factor is a numeric value which can be 1
#'   (default), 2, 3, etc. \item "firstSEmax": location of the first f() value
#'   which is not larger than the first local maximum minus SE.factor * SE.f[],
#'   i.e, within an "f S.E." range of that maximum. \item
#'   see ?cluster::maxSE for more options }
#'   
#'   
#' @export
fviz_gap_stat <- function(gap_stat,  linecolor = "steelblue",
                          maxSE = list(method = "firstSEmax", SE.factor = 1)){
  if(!inherits(gap_stat, "clusGap"))
    stop("Only an object of class clusGap is allowed. (cluster package)")
  if(is.list(maxSE)){
    if(is.null(maxSE$method)) maxSE$method = "firstmax"
    if(is.null(maxSE$SE.factor)) maxSE$SE.factor = 1
  }
  else stop("The argument maxSE must be a list containing the parameters method and SE.factor")
  
  # first local max
  gap <- gap_stat$Tab[, "gap"]
  se <- gap_stat$Tab[, "SE.sim"]
  decr <- diff(gap) <= 0
  k <- .maxSE(gap, se, method = maxSE$method, SE.factor = maxSE$SE.factor)
  
  #k <- length(gap)
  #k = if (any(decr)) which.max(decr) else k

  df <- as.data.frame(gap_stat$Tab, stringsAsFactors = TRUE)
  df$clusters <- as.factor(1:nrow(df))
  df$ymin <- gap-se
  df$ymax <- gap + se
  p <- ggpubr::ggline(df, x = "clusters", y = "gap", group = 1, color = linecolor)+
    ggplot2::geom_errorbar(aes_string(ymin="ymin", ymax="ymax"), width=.2, color = linecolor)+
    geom_vline(xintercept = k, linetype=2, color = linecolor)+
    labs(y = "Gap statistic (k)", x = "Number of clusters k",
         title = "Optimal number of clusters")
  p
}




# Get the average silhouette width
# ++++++++++++++++++++++++++
# Cluster package required
# d: dist object
# cluster: cluster number of observation
.get_ave_sil_width <- function(d, cluster){
  if (!requireNamespace("cluster", quietly = TRUE)) {
    stop("cluster package needed for this function to work. Please install it.")
  }
  ss <- cluster::silhouette(cluster, d)
  mean(ss[, 3])
}

# Get total within sum of square
# +++++++++++++++++++++++++++++
# d: dist object
# cluster: cluster number of observation
.get_withinSS <- function(d, cluster){
  d <- stats::as.dist(d)
  cn <- max(cluster)
  clusterf <- as.factor(cluster)
  clusterl <- levels(clusterf)
  cnn <- length(clusterl)
  
  if (cn != cnn) {
    warning("cluster renumbered because maximum != number of clusters")
    for (i in 1:cnn) cluster[clusterf == clusterl[i]] <- i
    cn <- cnn
  }
  cwn <- cn
  # Compute total within sum of square
  dmat <- as.matrix(d)
  within.cluster.ss <- 0
  for (i in 1:cn) {
    cluster.size <- sum(cluster == i)
    di <- as.dist(dmat[cluster == i, cluster == i])
    within.cluster.ss <- within.cluster.ss + sum(di^2)/cluster.size
  }
  within.cluster.ss
}





# Visualization of the output returned by the function
# NbClust()
# x : an object generated by the function NbClust()
.viz_NbClust <- function(x, print.summary = TRUE,
                         barfill = "steelblue", barcolor = "steelblue")
  {
     best_nc <- x$Best.nc
    if(class(best_nc) == "numeric") print(best_nc)
     else if(class(best_nc) == "matrix"){
    best_nc <- as.data.frame(t(best_nc), stringsAsFactors = TRUE)
    best_nc$Number_clusters <- as.factor(best_nc$Number_clusters)
    
    # Summary
    if(print.summary){
      ss <- summary(best_nc$Number_clusters)
      cat ("Among all indices: \n===================\n")
      for(i in 1 :length(ss)){
        cat("*", ss[i], "proposed ", names(ss)[i], "as the best number of clusters\n" )
      }
      cat("\nConclusion\n=========================\n")
      cat("* According to the majority rule, the best number of clusters is ",
          names(which.max(ss)),  ".\n\n")
    }
    df <- data.frame(Number_clusters = names(ss), freq = ss, stringsAsFactors = TRUE )
    p <- ggpubr::ggbarplot(df,  x = "Number_clusters", y = "freq", fill = barfill, color = barcolor)+
      labs(x = "Number of clusters k", y = "Frequency among all indices",
           title = paste0("Optimal number of clusters - k = ", names(which.max(ss)) ))
    
    return(p)
  }
}


#  Determines the location of the maximum of f see ?cluster::maxSE
# +++++++++++++++++++++++++++++++++++++++++++
# f: numeric vector containing the gap statistic
# SE.f : standard error of the gap statistic
# method : character string indicating how the "optimal" number of clusters, k, 
  # is computed from the gap statistics (and their standard deviations), 
  # or more generally how the location k^ of the maximum of f[k] should be determined.
# SE.factor:  Determining the optimal number of clusters, Tibshirani et al. proposed the "1 S.E."-rule.
.maxSE <- function (f, SE.f, method = c("firstSEmax", "Tibs2001SEmax", 
                                        "globalSEmax", "firstmax", "globalmax"), SE.factor = 1) 
{
  method <- match.arg(method)
  stopifnot((K <- length(f)) >= 1, K == length(SE.f), SE.f >= 
              0, SE.factor >= 0)
  fSE <- SE.factor * SE.f
  switch(method, firstmax = {
    decr <- diff(f) <= 0
    if (any(decr)) which.max(decr) else K
  }, globalmax = {
    which.max(f)
  }, Tibs2001SEmax = {
    g.s <- f - fSE
    if (any(mp <- f[-K] >= g.s[-1])) which.max(mp) else K
  }, firstSEmax = {
    decr <- diff(f) <= 0
    nc <- if (any(decr)) which.max(decr) else K
    if (any(mp <- f[seq_len(nc - 1)] >= f[nc] - fSE[nc])) which(mp)[1] else nc
  }, globalSEmax = {
    nc <- which.max(f)
    if (any(mp <- f[seq_len(nc - 1)] >= f[nc] - fSE[nc])) which(mp)[1] else nc
  })
}