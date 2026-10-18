# Reviewed local execution evidence

These are compact snapshots from actual commands on 17 October 2026.
`index.json` maps each snapshot to its original ignored run directory and records
SHA-256 values. Large tools, the full Liberty file and repeated raw runs are not
versioned. The synthesis snapshot includes the mapped netlist, statistics and
Liberty-derived functional models so the reported implementation can be inspected.
The platform license and original library notice are preserved alongside them.

The exhaustive gate run used a mapped netlist and models byte-identical to the
later synthesis rerun. Summaries record their absolute original paths and content
hashes; those historical paths do not need to exist on another machine.
The `.ys` snapshots are historical command evidence, not portable entry points;
use `make synth` to generate paths appropriate to your checkout.

`checks` contains harness checks; an expected nonzero physical-preflight exit is a
PASS of error handling, not a successful physical stage. The physical summary
says NOT RUN, and its metrics are null. Unit-test fixture values are not experiments.

This directory is not silently refreshed by `make report`. Review new outputs and
update numerical portfolio claims together when a new milestone is achieved.
