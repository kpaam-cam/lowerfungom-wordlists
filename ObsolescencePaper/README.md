# Obsolescence paper visualizations

This folder contains a first annotated visualization of the Lower Fungom
subunit distance matrix.

Run from this directory:

```sh
Rscript annotated_heatmap.R
```

The script reads the existing `.dst` matrix in the sibling repository's
`Good-WestermannPaperSupplementalMaterials/analyses/` directory and writes both
`annotated_subunit_heatmap.png` and `annotated_subunit_heatmap.pdf` here.

The main heatmap uses the original variety ordering, grouped into the 13
subunits represented in the labels. All varieties are ordered together by
average-linkage hierarchical clustering on the full distance matrix; no
subunit-level ordering is imposed. Subunit colors remain as row and column
annotations, allowing any blocks to emerge naturally. Values are plotted as
`1 - distance`, so
warmer colors indicate closer relationships and cooler colors indicate more
distant relationships. Colored row and column annotation strips mark subunit
identity. The right sidebar shows each variety's mean closeness, and the
lower panels show the global hierarchical clustering tree and average
closeness between subunits.
