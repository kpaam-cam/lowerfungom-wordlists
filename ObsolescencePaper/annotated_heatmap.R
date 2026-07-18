# Annotated, subunit-aware heatmap for the Lower Fungom distance matrix.
# Run from this directory with: Rscript annotated_heatmap.R

input <- "../Good-WestermannPaperSupplementalMaterials/analyses/kplfSubset-SCA-0.45_threshold-heatmap.matrix.dst"
png_out <- "annotated_subunit_heatmap.png"
pdf_out <- "annotated_subunit_heatmap.pdf"
heatmap_only_png <- "heatmap_only.png"
heatmap_only_pdf <- "heatmap_only.pdf"

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
# Cluster all varieties together. No subunit-level ordering is imposed;
# any subunit blocks that appear are a consequence of the full matrix.
global_hc <- hclust(as.dist(dists), method = "average")
ord <- global_hc$order
dists <- dists[ord, ord]
subunit <- subunit[ord]
labels <- rownames(dists)
n <- nrow(dists)
groups <- levels(subunit)
label_cols <- unname(group_cols[as.character(subunit)])

# Reverse the requested dark-blue block while leaving the rest of the global
# hierarchical order unchanged. The displayed heatmap order is reversed on
# both axes, so this reverses the corresponding segment in the stored order.
display_labels <- rev(labels)
block_left <- match("MCANgun3", display_labels)
block_right <- match("ABSMissong1", display_labels)
if (!is.na(block_left) && !is.na(block_right) && block_left < block_right) {
  stored_segment <- (n - block_right + 1):(n - block_left + 1)
  prefix <- if (stored_segment[1] > 1) seq_len(stored_segment[1] - 1) else integer(0)
  suffix <- if (stored_segment[length(stored_segment)] < n) {
    (stored_segment[length(stored_segment)] + 1):n
  } else integer(0)
  reordered <- c(prefix, rev(stored_segment), suffix)
  dists <- dists[reordered, reordered]
  subunit <- subunit[reordered]
  labels <- labels[reordered]
  label_cols <- label_cols[reordered]
}

# Swap the adjacent Abar and Ngun runs in the displayed order. Their members
# stay internally ordered; only the two run positions are exchanged.
display_groups <- rev(as.character(subunit))
display_indices <- rev(seq_len(n))
find_run <- function(x, value) {
  hits <- which(!is.na(x) & x == value)
  if (!length(hits)) return(integer(0))
  seq(min(hits), max(hits))
}
abar_run <- find_run(display_groups, "Abar")
ngun_run <- find_run(display_groups, "Ngun")
if (length(abar_run) > 0 && length(ngun_run) > 0 &&
    !is.na(min(abar_run)) && !is.na(min(ngun_run)) &&
    min(abar_run) < min(ngun_run)) {
  before <- if (min(abar_run) > 1) seq_len(min(abar_run) - 1) else integer(0)
  between <- if (max(abar_run) + 1 < min(ngun_run)) {
    (max(abar_run) + 1):(min(ngun_run) - 1)
  } else integer(0)
  after <- if (max(ngun_run) < n) (max(ngun_run) + 1):n else integer(0)
  new_display_indices <- c(
    before,
    ngun_run,
    between,
    abar_run,
    after
  )
  reordered <- rev(display_indices[new_display_indices])
  dists <- dists[reordered, reordered]
  subunit <- subunit[reordered]
  labels <- labels[reordered]
  label_cols <- label_cols[reordered]
}

# Swap the displayed Munken and Ngun runs, preserving each run internally.
display_groups <- rev(as.character(subunit))
display_indices <- rev(seq_len(n))
munken_run <- find_run(display_groups, "Munken")
ngun_run <- find_run(display_groups, "Ngun")
if (length(munken_run) > 0 && length(ngun_run) > 0 &&
    !is.na(min(munken_run)) && !is.na(min(ngun_run)) &&
    min(munken_run) < min(ngun_run)) {
  before <- if (min(munken_run) > 1) seq_len(min(munken_run) - 1) else integer(0)
  between <- if (max(munken_run) + 1 < min(ngun_run)) {
    (max(munken_run) + 1):(min(ngun_run) - 1)
  } else integer(0)
  after <- if (max(ngun_run) < n) (max(ngun_run) + 1):n else integer(0)
  new_display_indices <- c(before, ngun_run, between, munken_run, after)
  reordered <- rev(display_indices[new_display_indices])
  dists <- dists[reordered, reordered]
  subunit <- subunit[reordered]
  labels <- labels[reordered]
  label_cols <- label_cols[reordered]
}

# Swap the displayed Koshin and Buu runs, preserving each run internally.
display_groups <- rev(as.character(subunit))
display_indices <- rev(seq_len(n))
koshin_run <- find_run(display_groups, "Koshin")
buu_run <- find_run(display_groups, "Buu")
if (length(koshin_run) > 0 && length(buu_run) > 0 &&
    !is.na(min(koshin_run)) && !is.na(min(buu_run)) &&
    min(koshin_run) < min(buu_run)) {
  before <- if (min(koshin_run) > 1) seq_len(min(koshin_run) - 1) else integer(0)
  between <- if (max(koshin_run) + 1 < min(buu_run)) {
    (max(koshin_run) + 1):(min(buu_run) - 1)
  } else integer(0)
  after <- if (max(buu_run) < n) (max(buu_run) + 1):n else integer(0)
  new_display_indices <- c(before, buu_run, between, koshin_run, after)
  reordered <- rev(display_indices[new_display_indices])
  dists <- dists[reordered, reordered]
  subunit <- subunit[reordered]
  labels <- labels[reordered]
  label_cols <- label_cols[reordered]
}

# Move the displayed Kung run to the lower-right/end of the order.
display_groups <- rev(as.character(subunit))
display_indices <- rev(seq_len(n))
kung_run <- find_run(display_groups, "Kung")
if (length(kung_run) > 0 && max(kung_run) < n) {
  before <- if (min(kung_run) > 1) seq_len(min(kung_run) - 1) else integer(0)
  after <- (max(kung_run) + 1):n
  new_display_indices <- c(before, after, kung_run)
  reordered <- rev(display_indices[new_display_indices])
  dists <- dists[reordered, reordered]
  subunit <- subunit[reordered]
  labels <- labels[reordered]
  label_cols <- label_cols[reordered]
}

# Move the combined displayed Mumfu-Mundabli block to the lower-right/end.
display_groups <- rev(as.character(subunit))
display_indices <- rev(seq_len(n))
mumfu_run <- find_run(display_groups, "Mumfu")
mundabli_run <- find_run(display_groups, "Mundabli")
if (length(mumfu_run) > 0 && length(mundabli_run) > 0 &&
    min(mumfu_run) < min(mundabli_run)) {
  block_start <- min(mumfu_run)
  block_end <- max(mundabli_run)
  before <- if (block_start > 1) seq_len(block_start - 1) else integer(0)
  after <- if (block_end < n) (block_end + 1):n else integer(0)
  block <- block_start:block_end
  new_display_indices <- c(before, after, block)
  reordered <- rev(display_indices[new_display_indices])
  dists <- dists[reordered, reordered]
  subunit <- subunit[reordered]
  labels <- labels[reordered]
  label_cols <- label_cols[reordered]
}

# Swap the displayed Kung block with the adjacent Mumfu-Mundabli block.
display_groups <- rev(as.character(subunit))
display_indices <- rev(seq_len(n))
kung_run <- find_run(display_groups, "Kung")
mumfu_run <- find_run(display_groups, "Mumfu")
mundabli_run <- find_run(display_groups, "Mundabli")
if (length(kung_run) > 0 && length(mumfu_run) > 0 && length(mundabli_run) > 0 &&
    min(kung_run) < min(mumfu_run) &&
    max(kung_run) + 1 == min(mumfu_run)) {
  block_start <- min(mumfu_run)
  block_end <- max(mundabli_run)
  before <- if (min(kung_run) > 1) seq_len(min(kung_run) - 1) else integer(0)
  after <- if (block_end < n) (block_end + 1):n else integer(0)
  block <- block_start:block_end
  new_display_indices <- c(before, block, kung_run, after)
  reordered <- rev(display_indices[new_display_indices])
  dists <- dists[reordered, reordered]
  subunit <- subunit[reordered]
  labels <- labels[reordered]
  label_cols <- label_cols[reordered]
}

# Swap the displayed Mashi block with the adjacent Mumfu-Mundabli block.
display_groups <- rev(as.character(subunit))
display_indices <- rev(seq_len(n))
mashi_run <- find_run(display_groups, "Mashi")
mumfu_run <- find_run(display_groups, "Mumfu")
mundabli_run <- find_run(display_groups, "Mundabli")
if (length(mashi_run) > 0 && length(mumfu_run) > 0 && length(mundabli_run) > 0 &&
    min(mashi_run) < min(mumfu_run) &&
    max(mashi_run) + 1 == min(mumfu_run)) {
  block_start <- min(mumfu_run)
  block_end <- max(mundabli_run)
  before <- if (min(mashi_run) > 1) seq_len(min(mashi_run) - 1) else integer(0)
  after <- if (block_end < n) (block_end + 1):n else integer(0)
  block <- block_start:block_end
  new_display_indices <- c(before, block, mashi_run, after)
  reordered <- rev(display_indices[new_display_indices])
  dists <- dists[reordered, reordered]
  subunit <- subunit[reordered]
  labels <- labels[reordered]
  label_cols <- label_cols[reordered]
}

# Optimize only the order of the existing contiguous color blocks. Each block
# remains intact; the objective minimizes the light/dark discontinuity across
# block boundaries in the displayed heatmap.
display_indices <- rev(seq_len(n))
display_colors <- rev(label_cols)
block_starts <- c(1, which(display_colors[-1] != display_colors[-n]) + 1)
block_ends <- c(block_starts[-1] - 1, n)
block_count <- length(block_starts)
display_distance <- dists[display_indices, display_indices]
boundary_cost <- matrix(0, block_count, block_count)
for (i in seq_len(block_count)) {
  for (j in seq_len(block_count)) {
    if (i != j) {
      left_edge <- block_ends[i]
      right_edge <- block_starts[j]
      boundary_cost[i, j] <- 2 * sum(abs(
        display_distance[, left_edge] - display_distance[, right_edge]
      ))
    }
  }
}

best_cost <- Inf
best_blocks <- seq_len(block_count)
search_block_orders <- function(path, remaining, cost) {
  if (!length(remaining)) {
    if (cost < best_cost) {
      best_cost <<- cost
      best_blocks <<- path
    }
    return(invisible(NULL))
  }
  for (candidate in remaining) {
    step_cost <- if (length(path)) boundary_cost[path[length(path)], candidate] else 0
    search_block_orders(c(path, candidate), setdiff(remaining, candidate), cost + step_cost)
  }
}
search_block_orders(integer(0), seq_len(block_count), 0)

new_display_indices <- unlist(lapply(best_blocks, function(k) {
  display_indices[block_starts[k]:block_ends[k]]
}), use.names = FALSE)
reordered <- rev(new_display_indices)
dists <- dists[reordered, reordered]
subunit <- subunit[reordered]
labels <- labels[reordered]
label_cols <- label_cols[reordered]
message("Optimized color-block order: ", paste(rev(best_blocks), collapse = " "))

# Rotate the final square display 180 degrees so the Abar end is upper-left.
reordered <- rev(seq_len(n))
dists <- dists[reordered, reordered]
subunit <- subunit[reordered]
labels <- labels[reordered]
label_cols <- label_cols[reordered]

# Re-express distance as closeness: larger values are closer relationships.
closeness <- 1 - dists

# Use the observed off-diagonal range for the main linear color scale. The
# sidebar and subunit summary below remain on the original closeness scale.
linear_limits <- c(min(closeness[upper.tri(closeness)]), 1)

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

draw_main <- function(main_title = "Lower Fungom closeness heatmap (axes reversed)",
                      show_side_label = TRUE, compact = FALSE) {
  par(mar = c(10.0, 8.5, if (compact) 1.2 else 4.5,
              if (compact) 0.2 else 1.2), xpd = NA)
  # Put a small physical gap between the fixed color blocks.  The heatmap
  # cells themselves remain square; only the spacing between blocks changes.
  display_indices <- rev(seq_len(n))
  display_labels <- labels[display_indices]
  display_cols <- label_cols[display_indices]
  gap <- 0
  cell_x <- seq_len(n) + c(0, cumsum(display_cols[-1] != display_cols[-n])) * gap
  # Reflect the x geometry; reversing the vector itself would move gaps to
  # the wrong rows because the spacing is nonuniform at block boundaries.
  cell_y <- max(cell_x) + 1 - cell_x
  cell_half <- 0.51  # eliminate rasterization seams between adjacent cells
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
  # A single visible frame around the full map; the block outlines below are
  # drawn afterward so their dotted white edges remain legible over it.
  frame_col <- "grey55"
  rect(min(cell_x) - .5, min(cell_y) - .5,
       max(cell_x) + .5, max(cell_y) + .5,
       border = frame_col, lwd = 1.5, lty = 1)
  usr <- par("usr")
  text(cell_x, min(cell_y) - 0.95, labels = display_labels, srt = 90,
       adj = c(1, 0.5), xpd = NA, col = display_cols, cex = 0.62)
  # From left to right: labels, color strip, whitespace, heatmap.
  text(-0.05, cell_y, labels = display_labels, adj = c(1, 0.5),
       xpd = NA, col = display_cols, cex = 0.62)
  if (show_side_label) {
    mtext("Closeness (1 - distance)", side = 4, line = 0.2, cex = 0.8)
  }
  for (i in seq_len(n)) {
    # Separate the annotation strips from the heatmap with visible gaps.
    rect(cell_x[i] - .5, .10, cell_x[i] + .5, .35,
         col = display_cols[i], border = NA)
    rect(.10, cell_y[i] - .5, .35, cell_y[i] + .5,
         col = display_cols[i], border = NA)
  }

  # Outline contiguous runs that share the same label color in the global
  # hierarchical ordering. This intentionally merges adjacent subunits that
  # use the same radar-chart color. Singletons are left unboxed.
  run_key <- display_cols
  run_start <- c(1, which(run_key[-1] != run_key[-n]) + 1)
  run_end <- c(run_start[-1] - 1, n)
  draw_alternating_edge <- function(x1, y1, x2, y2) {
    edge_length <- sqrt((x2 - x1)^2 + (y2 - y1)^2)
    ux <- (x2 - x1) / edge_length
    uy <- (y2 - y1) / edge_length
    # Adjacent short segments: alternating colors without blank gaps.
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
  line_extension <- 0
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
       main = "Global average-linkage hierarchical clustering")
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

# Trim the standalone outputs to their actual content bounds after rendering.
# The composite figure is intentionally left at its full layout size.
crop_heatmap_only <- function() {
  magick <- Sys.which("magick")
  if (nzchar(magick)) {
    trimmed_png <- file.path(tempdir(), "heatmap_only_trimmed.png")
    status <- system2(magick, c(heatmap_only_png, "-trim", "+repage", trimmed_png))
    if (identical(status, 0L)) file.copy(trimmed_png, heatmap_only_png, overwrite = TRUE)
  }

  pdfcrop <- Sys.which("pdfcrop")
  if (nzchar(pdfcrop)) {
    cropped_pdf <- file.path(tempdir(), "heatmap_only_cropped.pdf")
    status <- system2(pdfcrop, c(heatmap_only_pdf, cropped_pdf))
    if (identical(status, 0L)) file.copy(cropped_pdf, heatmap_only_pdf, overwrite = TRUE)
  }
}

crop_heatmap_only()
message("Wrote ", png_out, " and ", pdf_out)
message("Wrote ", heatmap_only_png, " and ", heatmap_only_pdf)
