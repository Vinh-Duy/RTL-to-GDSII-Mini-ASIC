# Limitations and truthful claim boundaries

The project is **synthesis-complete**, with exhaustive binary RTL and functional
gate-level validation. It is **not yet a completed RTL-to-GDSII implementation**.

- OpenROAD, ORFS, KLayout and Docker are unavailable on the audited Mac. The
  physical runner's attempted preflight returned NOT RUN. There are no measured
  core/die areas, placed cells, clock tree, routing congestion, routing violations,
  post-route parasitics, setup/hold results or GDSII file.
- The 10 ns target is an input assumption. It is not achieved timing, measured
  maximum frequency, or a synthesis timing result. Standalone ABC mapping does
  not consume the SDC. There is no meaningful WNS/TNS value to quote yet.
- 879.928 µm² is the sum of mapped standard-cell areas in the Nangate45 typical
  library. It excludes whitespace, power grid, routing, future clock buffers,
  filler/tap cells and IO pads. It is neither die area nor a manufacturing estimate.
- No clock-period or utilization experiment executed. No experimental CSV rows,
  physical plots, layout images or comparative conclusions are fabricated.
- Gate simulation uses zero-delay functional models derived from Liberty and an
  independently calculated integer oracle. It validates known-input behavior and
  the tested reset/latency contract, not timing, analog behavior or formal equivalence.
  No SDF annotation, formal equivalence or exhaustive four-state verification ran.
- The ORFS runner and metric reader are prepared against inspected upstream sources
  but lack a full integration run. Unknown metric keys remain null. CTS requires
  a report confirming actual clock-tree construction; a stage output alone is not
  sufficient. Routing completion does not imply zero violations.
- A future GDS read-back check would establish readability and hierarchy only.
  Foundry-qualified DRC/LVS, antenna checking, multi-corner STA, extraction validation,
  power integrity, EM/IR, scan/DFT, packaging and sign-off are not established.
  Nangate45 is an educational/reference platform, not a commercial foundry PDK.
- No power result is claimed. A future tool-generated estimate would need explicit
  activity, corner, parasitic and methodology qualification before being reported.
- The GitHub Actions workflow is authored but **NOT RUN** remotely. Distribution
  packages in CI are version-logged rather than claimed identical to local YoWASP.
- The optional 16-bit width study was not implemented; all results concern the
  unchanged eight-operation 8-bit core with sixteen output registers.

Publish this as an honest intermediate project if desired. The portfolio must
retain the prominent synthesis-complete status until the missing stages actually
execute and their outputs are checked. No tapeout, silicon or frequency claim is justified.
