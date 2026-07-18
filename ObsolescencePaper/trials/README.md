# Heatmap trials

These are exploratory heatmap-seriation variants retained for comparison. The
paper candidate is kept at the project root:

- `annotated_heatmap_two_scale_bridge_seriation_flipped.R`
- `heatmap_only_two_scale_bridge_seriation_flipped.png`
- `heatmap_only_two_scale_bridge_seriation_flipped.pdf`

## Organization

- `scripts/` contains alternative ordering heuristics, including full-leaf,
  block, bridge-aware, spectral, and constrained two-scale variants.
- `figures/` contains the corresponding annotated and heatmap-only outputs.

The selected version uses a two-scale, boundary-aware seriation and reverses
the final display order so the Mungbam-like region appears in the upper-left.
