# Block-level seriation variant of annotated_heatmap.R: hierarchical clustering
# is NOT used to determine order at all (kept only to draw a reference
# dendrogram panel). Instead each language block is ordered directly
# by a minimum-cost Hamiltonian path (open TSP) over mean pairwise
# "boundary discontinuity" cost the block-order optimizer used:
#   cost(i, j) = sum_k |dist(i, k) - dist(j, k)|
# i.e. two leaves are cheap to place adjacent when they have similar
# dissimilarity profiles to everyone else, not just to each other. Brute
# force is impossible at n = 52 (52! ~= 8e67), so each path is built with a
# nearest-neighbor construction followed by 2-opt local search. Kung and
# Mashi remain contiguous and internally seriated, but are pushed to the
# lower-right as terminal blocks. The other language blocks are unconstrained.
# Run from this directory with: Rscript annotated_heatmap_block_seriation_modified.R

input <- "../Good-WestermannPaperSupplementalMaterials/analyses/kplfSubset-SCA-0.45_threshold-heatmap.matrix.dst"
png_out <- "annotated_subunit_heatmap_block_seriation_modified.png"
pdf_out <- "annotated_subunit_heatmap_block_seriation_modified.pdf"
heatmap_only_png <- "heatmap_only_block_seriation_modified.png"
heatmap_only_pdf <- "heatmap_only_block_seriation_modified.pdf"

dists <- read.delim(input, check.names = FALSE, row.names = 1)
dists <- as.matrix(dists)
storage.mode(dists) <- "numeric"

subunit_names <- c("Biya", "Munken", "Ngun", "Abar", "Missong", "Kung",
                   "Mumfu", "Mundabli", "Buu", "Koshin", "Fang", "Ajumbu", "Mashi")
subunit <- vapply(rownames(dists), function(x) {
  hit <- subunit_names[vapply(subunit_names, grepl, logical(1), x, fixed = TRUE)]
  if (length(hit) != 1) stop("Could not identify subunit for: ", x)
  hit
}, character(1))

# Match the radar-chart spoke_colors palette in SLIGcalc/scripts/r/Radars2-working.r.
group_cols <- c(
  Missong = "darkblue", Mashi = "grey30", Mumfu = "orange", Mundabli = "orange",
  Koshin = "purple4", Fang = "darkred", Buu = "darkorange3", Ajumbu = "darkgreen",
  Kung = "grey60", Abar = "darkblue", Ngun = "darkblue", Biya = "darkblue",
  Munken = "darkblue"
)

subunit <- factor(subunit, levels = subunit_names)
n <- nrow(dists)
labels0 <- rownames(dists)

# Kept only for the reference dendrogram panel; not used to order the heatmap.
global_hc <- hclust(as.dist(dists), method = "average")

# Profile-distance cost matrix: identical formula to the block optimizer's
# boundary_cost, just evaluated for every leaf pair instead of only the two
# leaves that happen to sit at a block edge.
profile_cost <- as.matrix(dist(dists, method = "manhattan"))

path_length <- function(path, cost) {
  sum(cost[cbind(path[-length(path)], path[-1])])
}

nearest_neighbor_path <- function(cost, start) {
  n <- nrow(cost)
  visited <- rep(FALSE, n)
  path <- integer(n)
  path[1] <- start
  visited[start] <- TRUE
  for (k in 2:n) {
    last <- path[k - 1]
    candidates <- which(!visited)
    next_node <- candidates[which.min(cost[last, candidates])]
    path[k] <- next_node
    visited[next_node] <- TRUE
  }
  path
}

two_opt <- function(path, cost) {
  n <- length(path)
  improved <- TRUE
  while (improved) {
    improved <- FALSE
    for (i in seq_len(n - 2)) {
      for (j in (i + 1):(n - 1)) {
        old_cost <- cost[path[i], path[i + 1]] + cost[path[j], path[j + 1]]
        new_cost <- cost[path[i], path[j]] + cost[path[i + 1], path[j + 1]]
        if (new_cost < old_cost - 1e-9) {
          path[(i + 1):j] <- rev(path[(i + 1):j])
          improved <- TRUE
        }
      }
    }
  }
  path
}

seriated_path <- function(cost) {
  # Multi-start: try every leaf as the nearest-neighbor construction's starting
  # point, refine each with 2-opt, keep the cheapest resulting path.
  best_path <- NULL
  best_len <- Inf
  for (start in seq_len(nrow(cost))) {
    candidate <- two_opt(nearest_neighbor_path(cost, start), cost)
    candidate_len <- path_length(candidate, cost)
    if (candidate_len < best_len) {
      best_len <- candidate_len
      best_path <- candidate
    }
  }
  list(path = best_path, length = best_len)
}

# Build and seriate every language block internally.
block_indices <- lapply(subunit_names, function(block_name) {
  which(as.character(subunit) == block_name)
})
block_paths <- lapply(seq_along(block_indices), function(i) {
  indices <- block_indices[[i]]
  result <- seriated_path(profile_cost[indices, indices, drop = FALSE])
  message(subunit_names[i], " internal seriation path cost: ", round(result$length, 1))
  indices[result$path]
})

# Compare blocks using mean pairwise profile distance. This is the direct
# aggregate analogue of the blue-block principle: a block's global placement
# reflects all of its varieties, not just its boundary variety.
block_cost <- matrix(0, length(block_indices), length(block_indices))
for (i in seq_along(block_indices)) {
  for (j in seq_along(block_indices)) {
    if (i != j) {
      block_cost[i, j] <- mean(profile_cost[block_indices[[i]], block_indices[[j]]])
    }
  }
}
# Keep Kung and Mashi as terminal blocks. The stored order is reversed for
# display, so Kung first and Mashi second puts Mashi just inside Kung at the
# lower-right. All remaining language blocks are ordered freely.
protected_names <- c("Kung", "Mashi")
protected_ids <- match(protected_names, subunit_names)
free_ids <- setdiff(seq_along(block_indices), protected_ids)
free_result <- seriated_path(block_cost[free_ids, free_ids, drop = FALSE])
message("Unconstrained language-block path cost: ", round(free_result$length, 1))

block_order <- c(protected_ids, free_ids[free_result$path])
ord <- unlist(block_paths[block_order], use.names = FALSE)
dists <- dists[ord, ord]
subunit <- subunit[ord]
labels <- labels0[ord]
label_cols <- unname(group_cols[as.character(subunit)])

# Re-express distance as closeness: larger values are closer relationships.
closeness <- 1 - dists
linear_limits <- c(min(closeness[upper.tri(closeness)]), 1)

groups <- levels(subunit)
group_mean <- matrix(NA_real_, length(groups), length(groups), dimnames = list(groups, groups))
for (i in seq_along(groups)) {
  for (j in seq_along(groups)) {
    xi <- which(subunit == groups[i])
    xj <- which(subunit == groups[j])
    vals <- closeness[xi, xj]
    if (i == j) vals <- vals[upper.tri(vals)]
    group_mean[i, j] <- mean(vals)
  }
}

heat_cols <- colorRampPalette(c("#173F5F", "#20639B", "#3CAEA3", "#F6D55C", "#ED553B"))(201)
color_limits <- c(0, 1)

draw_main <- function(main_title = "Lower Fungom closeness heatmap (block seriation, Kung/Mashi terminal)",
                      show_side_label = TRUE, compact = FALSE) {
  par(mar = c(10.0, 8.5, if (compact) 1.2 else 4.5,
              if (compact) 0.2 else 1.2), xpd = NA)
  display_indices <- rev(seq_len(n))
  display_labels <- labels[display_indices]
  display_cols <- label_cols[display_indices]
  cell_x <- seq_len(n)
  cell_y <- max(cell_x) + 1 - cell_x
  cell_half <- 0.51
  plot(NA, xlim = c(-1, max(cell_x) + .5), ylim = c(-1, max(cell_y) + .5),
       asp = 1, axes = FALSE, xlab = "", ylab = "",
       bg = "white",
       main = main_title)
  for (i in seq_len(n)) {
    for (j in seq_len(n)) {
      value <- closeness[display_indices[i], display_indices[j]]
      scaled_value <- (value - linear_limits[1]) /
        (linear_limits[2] - linear_limits[1])
      color_index <- max(1, min(length(heat_cols),
                                floor(scaled_value * (length(heat_cols) - 1)) + 1))
      rect(cell_x[i] - cell_half, cell_y[j] - cell_half,
           cell_x[i] + cell_half, cell_y[j] + cell_half,
           col = heat_cols[color_index], border = NA)
    }
  }
  frame_col <- "grey55"
  rect(min(cell_x) - .5, min(cell_y) - .5,
       max(cell_x) + .5, max(cell_y) + .5,
       border = frame_col, lwd = 1.5, lty = 1)
  text(cell_x, min(cell_y) - 0.95, labels = display_labels, srt = 90,
       adj = c(1, 0.5), xpd = NA, col = display_cols, cex = 0.62)
  text(-0.05, cell_y, labels = display_labels, adj = c(1, 0.5),
       xpd = NA, col = display_cols, cex = 0.62)
  if (show_side_label) {
    mtext("Closeness (1 - distance)", side = 4, line = 0.2, cex = 0.8)
  }
  for (i in seq_len(n)) {
    rect(cell_x[i] - .5, .10, cell_x[i] + .5, .35,
         col = display_cols[i], border = NA)
    rect(.10, cell_y[i] - .5, .35, cell_y[i] + .5,
         col = display_cols[i], border = NA)
  }

  # Outline contiguous runs that share the same label color. Unlike the
  # block-based scripts, nothing forces same-color leaves to stay together
  # here -- any runs that appear are purely a consequence of the full-leaf
  # TSP-style seriation.
  run_key <- display_cols
  run_start <- c(1, which(run_key[-1] != run_key[-n]) + 1)
  run_end <- c(run_start[-1] - 1, n)
  draw_alternating_edge <- function(x1, y1, x2, y2) {
    edge_length <- sqrt((x2 - x1)^2 + (y2 - y1)^2)
    ux <- (x2 - x1) / edge_length
    uy <- (y2 - y1) / edge_length
    step <- 0.30
    dash <- 0.30
    starts <- seq(0, edge_length, by = step)
    for (k in seq_along(starts)) {
      a <- starts[k]
      b <- min(a + dash, edge_length)
      segments(x1 + ux * a, y1 + uy * a,
               x1 + ux * b, y1 + uy * b,
               col = if (k %% 2) "white" else frame_col,
               lwd = 1.25)
    }
  }
  for (i in seq_along(run_start)) {
    if (run_end[i] - run_start[i] + 1 >= 2) {
      x_start <- cell_x[run_start[i]]
      x_end <- cell_x[run_end[i]]
      y_top <- cell_y[run_start[i]]
      y_bottom <- cell_y[run_end[i]]
      x_left <- x_start - .5
      x_right <- x_end + .5
      y_bottom_edge <- min(y_top, y_bottom) - .5
      y_top_edge <- max(y_top, y_bottom) + .5
      draw_alternating_edge(x_left, y_top_edge, x_right, y_top_edge)
      draw_alternating_edge(x_right, y_top_edge, x_right, y_bottom_edge)
      draw_alternating_edge(x_right, y_bottom_edge, x_left, y_bottom_edge)
      draw_alternating_edge(x_left, y_bottom_edge, x_left, y_top_edge)
    }
  }
}

draw_color_scale <- function() {
  par(mar = c(10.0, 0.9, 1.2, 0.2), xpd = NA)
  par(bg = "white", fg = "black")
  scale_values <- seq(linear_limits[1], linear_limits[2], length.out = 201)
  scale_pad <- diff(linear_limits) * 0.08
  plot(NA, xlim = c(-.1, 1),
       ylim = c(linear_limits[1] - scale_pad, linear_limits[2] + scale_pad),
       axes = FALSE, xlab = "", ylab = "", bg = "white")
  for (i in seq_len(length(scale_values) - 1)) {
    rect(-.03, scale_values[i], .55, scale_values[i + 1],
         col = heat_cols[i], border = NA)
  }
  measure_limits <- linear_limits
  tick_values <- seq(linear_limits[1], linear_limits[2], length.out = 5)
  tick_labels <- format(seq(linear_limits[1], linear_limits[2], length.out = 5),
                        trim = TRUE, digits = 2, nsmall = 2)
  measure_x <- -.03
  segments(measure_x, measure_limits[1], measure_x, measure_limits[2], lwd = 1)
  for (i in seq_along(tick_values)) {
    segments(measure_x, tick_values[i], measure_x + .08, tick_values[i], lwd = 1)
    text(measure_x - .04, tick_values[i], tick_labels[i], adj = c(1, 0.5),
         xpd = NA, cex = 0.75)
  }
  text(.28, linear_limits[2] + 0.032 * diff(linear_limits),
       labels = "Similarity", xpd = NA, cex = 0.8)
}

draw_sidebar <- function() {
  mean_dist <- rowMeans(closeness)
  par(mar = c(5.5, 0.8, 4.5, 3.0), xpd = NA)
  plot(mean_dist, n:1, pch = 21, bg = group_cols[as.character(subunit)],
       col = "white", cex = 0.8, axes = FALSE, xlab = "", ylab = "",
       ylim = c(.5, n + .5), main = "")
  axis(1, cex.axis = 0.7)
  abline(v = mean(mean_dist), lty = 2, col = "grey35")
  mtext("Mean closeness", side = 1, line = 2.6, cex = 0.72)
}

draw_group_summary <- function() {
  par(mar = c(4.5, 5.5, 3.0, 3.0), xpd = NA)
  image(seq_along(groups), seq_along(groups), t(group_mean[length(groups):1, ]),
        col = heat_cols, zlim = color_limits, asp = 1, axes = FALSE,
        xlab = "", ylab = "", main = "Average closeness between subunits")
  axis(1, at = seq_along(groups), labels = groups, las = 2, cex.axis = 0.7)
  axis(2, at = rev(seq_along(groups)), labels = groups, las = 2, cex.axis = 0.7)
  for (i in seq_along(groups)) {
    rect(i - .5, length(groups) - i + .5, i + .5, length(groups) - i + 1.5,
         border = group_cols[groups[i]], lwd = 2)
  }
  legend("topright", legend = c("0", "1"), fill = heat_cols[c(1, 201)],
         title = "Closeness", horiz = TRUE, bty = "n", cex = 0.7, inset = c(0, -0.28))
}

draw_dendrogram <- function() {
  par(mar = c(0.8, 5.5, 2.8, 1.2), xpd = NA)
  plot(rev(as.dendrogram(global_hc)), leaflab = "none", axes = FALSE,
       xlab = "", ylab = "",
       main = "Global average-linkage hierarchical clustering (reference only,\nnot used for this heatmap's order)")
}

make_figure <- function(device, file) {
  if (device == "png") {
    png(file, width = 13, height = 17.2, units = "in", res = 160, bg = "white")
  } else {
    pdf(file, width = 13, height = 17.2)
  }
  par(bg = "white", fg = "black")
  layout(matrix(c(1, 2, 3, 0, 4, 4), nrow = 3, byrow = TRUE),
         widths = c(8.8, 1.7), heights = c(8.2, 2.8, 6.2))
  draw_main()
  draw_sidebar()
  draw_dendrogram()
  draw_group_summary()
  dev.off()
}

make_figure("png", png_out)
make_figure("pdf", pdf_out)

make_heatmap_only <- function(device, file) {
  if (device == "png") {
    png(file, width = 9.5, height = 8.2, units = "in", res = 180, bg = "white")
  } else {
    pdf(file, width = 9.5, height = 8.2)
  }
  par(bg = "white", fg = "black")
  layout(matrix(c(1, 2), nrow = 1), widths = c(8.4, 0.9))
  par(bg = "white", fg = "black")
  draw_main(main_title = "", show_side_label = FALSE, compact = TRUE)
  draw_color_scale()
  dev.off()
}

make_heatmap_only("png", heatmap_only_png)
make_heatmap_only("pdf", heatmap_only_pdf)

crop_heatmap_only <- function() {
  magick <- Sys.which("magick")
  if (nzchar(magick)) {
    trimmed_png <- file.path(tempdir(), "heatmap_only_block_seriation_modified_trimmed.png")
    status <- system2(magick, c(heatmap_only_png, "-trim", "+repage", trimmed_png))
    if (identical(status, 0L)) file.copy(trimmed_png, heatmap_only_png, overwrite = TRUE)
  }
  pdfcrop <- Sys.which("pdfcrop")
  if (nzchar(pdfcrop)) {
    cropped_pdf <- file.path(tempdir(), "heatmap_only_block_seriation_modified_cropped.pdf")
    status <- system2(pdfcrop, c(heatmap_only_pdf, cropped_pdf))
    if (identical(status, 0L)) file.copy(cropped_pdf, heatmap_only_pdf, overwrite = TRUE)
  }
}

crop_heatmap_only()
message("Wrote ", png_out, " and ", pdf_out)
message("Wrote ", heatmap_only_png, " and ", heatmap_only_pdf)
