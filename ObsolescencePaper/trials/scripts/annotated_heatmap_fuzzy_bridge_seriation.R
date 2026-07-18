# Fuzzy bridge-aware full-leaf seriation variant of annotated_heatmap.R:
# hierarchical clustering
# is NOT used to determine order at all (kept only to draw a reference
# dendrogram panel). Instead every one of the 52 leaves is placed directly
# by a minimum-cost Hamiltonian path (open TSP), augmented with a soft
# two-sided bridge reward and soft community cohesion inferred from the data.
# "boundary discontinuity" cost the block-order optimizer used:
#   cost(i, j) = sum_k |dist(i, k) - dist(j, k)|
# i.e. two leaves are cheap to place adjacent when they have similar
# dissimilarity profiles to everyone else, not just to each other. Brute
# force is impossible at n = 52 (52! ~= 8e67), so the path is built with a
# nearest-neighbor construction followed by 2-opt and insertion local search.
# No variety is named or constrained as a bridge or as a block.
# Run from this directory with: Rscript annotated_heatmap_fuzzy_bridge_seriation.R

input <- "../Good-WestermannPaperSupplementalMaterials/analyses/kplfSubset-SCA-0.45_threshold-heatmap.matrix.dst"
png_out <- "annotated_subunit_heatmap_fuzzy_bridge_seriation.png"
pdf_out <- "annotated_subunit_heatmap_fuzzy_bridge_seriation.pdf"
heatmap_only_png <- "heatmap_only_fuzzy_bridge_seriation.png"
heatmap_only_pdf <- "heatmap_only_fuzzy_bridge_seriation.pdf"

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
  for (round in seq_len(2)) {
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

# Infer broad communities only as a soft description of the matrix. They do
# not impose contiguity or determine the order directly. Memberships are
# based on each item's mean similarity to each inferred community.
community_count <- 3L
community <- cutree(global_hc, k = community_count)
community_sizes <- tabulate(community, nbins = community_count)
similarity <- 1 - dists
community_affinity <- sapply(seq_len(community_count), function(k) {
  rowMeans(similarity[, community == k, drop = FALSE])
})
membership_temperature <- 0.06
membership <- t(apply(community_affinity, 1, function(x) {
  weights <- exp((x - max(x)) / membership_temperature)
  weights / sum(weights)
}))
confidence <- apply(membership, 1, max)
edge_scale <- median(profile_cost[upper.tri(profile_cost)])
edge_cost <- profile_cost / edge_scale
bridge_weight <- 0.35
cohesion_weight <- 0.18

bridge_score <- function(left, middle, right) {
  left_community <- which.max(membership[left, ])
  right_community <- which.max(membership[right, ])
  if (left_community == right_community) return(0)
  left_affinity <- community_affinity[middle, left_community]
  right_affinity <- community_affinity[middle, right_community]
  size_weight <- log1p(community_sizes[left_community]) *
    log1p(community_sizes[right_community])
  mixedness <- 1 - confidence[middle]
  min(left_affinity, right_affinity) * size_weight * mixedness
}

cohesion_score <- function(left, right) {
  shared_membership <- sum(membership[left, ] * membership[right, ])
  shared_membership * log1p(max(community_sizes))
}

path_objective <- function(path) {
  edge_part <- sum(edge_cost[cbind(path[-length(path)], path[-1])])
  cohesion_part <- sum(vapply(seq_len(length(path) - 1), function(i) {
    cohesion_score(path[i], path[i + 1])
  }, numeric(1)))
  bridge_part <- if (length(path) < 3) 0 else sum(vapply(seq_len(length(path) - 2),
    function(i) bridge_score(path[i], path[i + 1], path[i + 2]), numeric(1)))
  edge_part - cohesion_weight * cohesion_part - bridge_weight * bridge_part
}

bridge_local_search <- function(path) {
  improved <- TRUE
  while (improved) {
    improved <- FALSE
    best_path <- path
    best_value <- path_objective(path)

    # 2-opt reversals.
    for (i in seq_len(n - 2)) {
      for (j in (i + 1):(n - 1)) {
        candidate <- path
        candidate[(i + 1):j] <- rev(candidate[(i + 1):j])
        value <- path_objective(candidate)
        if (value < best_value - 1e-9) {
          best_path <- candidate
          best_value <- value
        }
      }
    }

    # Insertion moves let a bridge variety move between two large communities.
    for (i in seq(1, n, by = 2)) {
      remainder <- path[-i]
      for (j in seq(1, n - 1, by = 2)) {
        candidate <- append(remainder, path[i], after = j)
        value <- path_objective(candidate)
        if (value < best_value - 1e-9) {
          best_path <- candidate
          best_value <- value
        }
      }
    }

    if (best_value < path_objective(path) - 1e-9) path <- best_path
  }
  path
}

message("Inferred community sizes: ", paste(community_sizes, collapse = ", "))
message("Fuzzy membership temperature: ", membership_temperature)
best_path <- NULL
best_value <- Inf
starts <- unique(round(seq(1, n, length.out = 4)))
for (start in starts) {
  candidate <- bridge_local_search(nearest_neighbor_path(profile_cost, start))
  candidate_value <- path_objective(candidate)
  if (candidate_value < best_value) {
    best_value <- candidate_value
    best_path <- candidate
  }
}
message("Fuzzy bridge-aware path objective: ", round(best_value, 2))

ord <- best_path
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

draw_main <- function(main_title = "Lower Fungom closeness heatmap (full TSP-style seriation, no hclust)",
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
    trimmed_png <- file.path(tempdir(), "heatmap_only_fuzzy_bridge_seriation_trimmed.png")
    status <- system2(magick, c(heatmap_only_png, "-trim", "+repage", trimmed_png))
    if (identical(status, 0L)) file.copy(trimmed_png, heatmap_only_png, overwrite = TRUE)
  }
  pdfcrop <- Sys.which("pdfcrop")
  if (nzchar(pdfcrop)) {
    cropped_pdf <- file.path(tempdir(), "heatmap_only_fuzzy_bridge_seriation_cropped.pdf")
    status <- system2(pdfcrop, c(heatmap_only_pdf, cropped_pdf))
    if (identical(status, 0L)) file.copy(cropped_pdf, heatmap_only_pdf, overwrite = TRUE)
  }
}

crop_heatmap_only()
message("Wrote ", png_out, " and ", pdf_out)
message("Wrote ", heatmap_only_png, " and ", heatmap_only_pdf)
