# Final engineering validation

## Follow-up recheck — 30 October 2026

`make lint test simulate` passed: Icarus lint, 14 Python tests and 5,280 RTL
vectors. The workflow YAML parses and is manual-only (`workflow_dispatch`). The
physical host remains unavailable: `make physical-preflight` and `make physical`
exit 2 before any ORFS command. The latest attempt is
`reports/physical/20261027T145432Z-66661b19`; all seven physical stages and every
physical metric are `NOT RUN`/null. `make timing` also exits 2 because there is no
successful final timing report. No `.gds`, `.odb`, `.def` or routed artifacts were
found in `reports/`; the utilization study was not run because the baseline did
not complete.

The manual GitHub Actions workflow builds the pinned ORFS source with the official
Docker build script, copies platform files into the image, checks the image revision
label and in-container revision marker, records tool versions and checks the
Nangate45 typical Liberty hash before invoking the existing flow. It uploads logs,
reports, summaries, manifests and any final GDS on both success and failure. It is
on the remote default branch but has not executed. The `gh` CLI is unavailable
here; launch it by selecting **Actions → ORFS physical baseline and utilization
sweep → Run workflow** on GitHub. No physical result is claimed.

The experiment runner now writes a manifest containing configuration and source
hashes, environment, toolchain, per-run metrics and stage status. It serializes
30%, 45% and 60% utilization points and stops after the first non-PASS run. GDS
size and SHA-256 are added only after a successful KLayout read-back. Missing via
counts and timing fields stay null. No plots are generated when there are not
enough successful measured points.

---

## Follow-up recheck — 26 October 2026

The current macOS workspace was rechecked after the 17 October audit. `make lint test`
passed (11 unit tests), `make simulate` passed 5,280 vectors, and `make report`
completed. `make physical-preflight` and `make physical` still stop before any ORFS
stage because this host has no Docker, OpenROAD, KLayout or prepared ORFS checkout.
The latest physical attempt is `reports/physical/20261026T153529Z-cee46489`; all stages remain `NOT RUN`, all
physical metrics are null, and no GDSII was generated. `make timing` correctly
returns `NOT RUN` because there is no final timing report. These results are a
fresh environment check, not a physical-design run. Reproduction commands for a
Linux host are in [ENVIRONMENT.md](ENVIRONMENT.md).

The physical runner now has a separate `make physical-preflight` target, checks
that a container contains the pinned ORFS revision, and reports synthesized and
final cell area separately when those exact-stage JSON metrics exist. Via count
remains null unless a verified source is available. No RTL or testbench behavior
was changed in this follow-up.

---

Date: 17 October 2026, Asia/Ho_Chi_Minh. **Current deliverable: synthesis-complete,
not a complete RTL-to-GDSII implementation.** Evidence snapshots are indexed by
[file hash and original run directory](evidence/index.json).

## Stage-by-stage status

| Stage or requirement | Status | Checked result |
|---|---|---|
| Workspace/environment detection | PASS | Independent existing Git repo; Intel x86_64 Mac, 8 GB RAM |
| Original RTL reuse/provenance | PASS | Byte-identical ALU; commit and SHA-256 recorded |
| Registered synchronous contract | PASS | 16 output registers; no input-register stage |
| RTL compile/elaboration | PASS | Icarus 13.0, `-g2012 -Wall` |
| Standard RTL simulation | PASS | 5,280 vectors; exit 0 and scoreboard PASS marker |
| Exhaustive RTL simulation | PASS | 524,320 vectors; exit 0 and scoreboard PASS marker |
| Waveform generation | PASS | Nonempty real simulation VCD |
| Fault-detection tests | PASS | Four intentionally incorrect cases rejected |
| Execution/metrics unit tests | PASS | Six tests including timeout and missing metrics |
| Technology-mapped synthesis | PASS | 744 library cells; 16 registers; 879.928 µm² |
| Mapped netlist validation | PASS | No remaining Yosys internal cells; all cells defined |
| Gate-level regression | PASS | 5,280 vectors on latest mapped netlist |
| Exhaustive gate-level simulation | PASS | 524,320 vectors; netlist/models match latest rerun byte for byte |
| ORFS synthesis | NOT RUN | Physical environment preflight stopped before ORFS commands |
| Floorplanning | NOT RUN | No OpenROAD environment |
| Placement and legality | NOT RUN | No placement database/report |
| CTS | NOT RUN | No clock tree or CTS report |
| Global routing | NOT RUN | No routing guides/congestion results |
| Detailed routing | NOT RUN | No routed database/violation report |
| Final STA | NOT RUN | No WNS/TNS/setup/hold/critical-path measurements |
| GDSII generation and read-back | NOT RUN | No GDSII file |
| Clock-period/utilization experiments | NOT RUN | Preflight exit 2; no experimental rows |
| Physical figures/layout screenshot | NOT RUN | No physical observations to visualize |
| Formal equivalence | NOT RUN | Ordinary gate simulation is not formal checking |
| Optional width study | NOT RUN | Deferred |
| GitHub Actions | NOT RUN | Workflow authored, not executed remotely |
| Documentation links/claims | PASS | Local links resolved; numerical claims checked against evidence |
| Prior-repository preservation | PASS | Initial and final status identical; no writes issued there |
| Git diff/whitespace | PASS | `git diff --check`; source additions reviewed |

No physical stage is labeled PASS merely because its configuration exists. The
`checks` evidence labels the **test of the missing-dependency behavior** PASS;
the physical stages themselves remain NOT RUN.

## Measured evidence

- [RTL regression summary](evidence/rtl-regression/summary.json) and
  [simulation log](evidence/rtl-regression/simulation.log).
- [Exhaustive RTL summary](evidence/rtl-exhaustive/summary.json),
  [simulation log](evidence/rtl-exhaustive/simulation.log) and
  [actual limited-duration VCD](evidence/rtl-exhaustive/waveform.vcd).
- [Mapped statistics](evidence/synthesis/stat.json),
  [synthesis log](evidence/synthesis/synthesis.log),
  [mapped netlist](evidence/synthesis/alu_top_mapped.v),
  [functional library models](evidence/synthesis/nangate45_functional.v) and
  [synthesis provenance](evidence/synthesis/summary.json).
- [Exhaustive gate summary](evidence/gate-exhaustive/summary.json) and
  [scoreboard output](evidence/gate-exhaustive/simulation.log).
- [Fault injection results](evidence/fault-injection/summary.json),
  [runner tests](evidence/checks/runner_tests.log), and
  [physical preflight result](evidence/physical/summary.json).

The synthesis rerun generated exactly the same mapped Verilog and cell models
used by the exhaustive gate test:

```text
Mapped netlist SHA-256:
1375f6c52286e8a468fb34d743428a6105a0809d5e7afc3217fec5c36f6fab31
Functional model SHA-256:
71194efaf6f599655bf8b1a47b86e0dc1fc5a4a5c36f111c9fb71f09f75345ed
```

The 524,320 count includes 524,288 unique binary arithmetic cases plus 32
inherited known-answer cases. Reset/capture checks are additional behavior checks,
not additional unique arithmetic combinations. No percentages imply coverage of
unknown inputs, analog effects, timing corners or physical verification.

## Failures investigated and resolved

1. The first testbench compile failed because a generated format string had a
   literal newline. The string was fixed and both RTL suites rerun successfully.
2. A YoWASP version probe stalled during default filesystem mount discovery.
   It was terminated; project-only mounts/cache/temp paths now run successfully.
3. The first mapped-netlist validator rejected `$scopeinfo`, a Yosys debug metadata
   cell. The flow now removes it before counting/validating physical cells.
4. Initial Liberty-to-Verilog conversion failed on missing clock-gating functions.
   `-ignore_miss_func` permits unused incomplete cells. All actually instantiated
   cells elaborate, and exhaustive functional gate simulation passes.

Initial logs remain in the ignored raw run directories; none is represented as
a successful final run. The final synthesis and simulation summaries record real
exit statuses and checked outputs.

## Remaining warnings and blockers

- ABC notes two multi-output library cells (for example FA_X1). The mapped design
  does not instantiate FA_X1; cell models elaborate and binary behavior passes.
- Icarus warns that generated gate/library modules lack explicit time units. Those
  models contain no delays; this is zero-delay functional simulation, not an SDF run.
- `make physical`, `make timing` and `make experiments` return nonzero because the
  physical environment/results are absent. No corresponding engineering measurements
  or plots are reported.
- Full integration of the prepared ORFS/Docker runner and its final metric schema
  awaits actual execution. The CTS hook requires positive reported tree counts,
  so a skipped clock tree cannot be silently marked successful.

## Commands executed

The audit used `uname -m`, `sw_vers`, `df -h`, executable discovery,
`system_profiler`, Python/Icarus version checks, Git status/revision checks, and
read-only source/specification inspection. Project-local installation used
`python3 -m venv .venv` and pinned YoWASP packages; `curl` retrieved pinned Liberty,
license and official flow-reference files. No system package installation occurred.

Engineering commands included:

```bash
python3 scripts/simulate.py
python3 scripts/simulate.py --exhaustive
python3 scripts/simulate.py --corrupt-expected  # expected failure
python3 scripts/validate.py                   # four faults correctly rejected
make lint test
make exhaustive
make synth
make gate-exhaustive
make gate
make physical                               # NOT RUN, missing prerequisites
make timing                                 # NOT RUN, no final timing evidence
make experiments                            # NOT RUN, no rows fabricated
make report
python3 -m compileall -q scripts tests
git diff --check
git status --short
```

The equivalent Python gate-exhaustive entry point was also executed through the
Makefile; command arguments, timestamps and durations are in the individual
summaries. Shell wrappers passed `bash -n`. Current tool/version/platform information
is in [ENVIRONMENT.md](ENVIRONMENT.md); complete reproduction is in the README.

## Publication assessment

The repository can be published as a clearly labeled **synthesis-complete
intermediate portfolio project**. It is not ready to be presented as completed
physical implementation or a finished RTL-to-GDSII flow. Run remote CI and the
remaining physical stages before upgrading those claims. A project-wide license
has not been selected on the owner's behalf; third-party platform notices are
preserved with the generated model evidence. No commit, push or remote repository
creation was performed.
