# RTL-to-GDSII Mini ASIC — technical report

**Measured scope, 17 October 2026: synthesis-complete.** RTL and mapped-netlist
functional verification passed. Physical implementation and timing analysis are
NOT RUN because the required environment is absent. All numerical results below
come from local execution; the project title describes the intended full flow.

**Follow-up, 30 October 2026:** the local lint, 14 runner/parser tests and 5,280-vector
RTL regression passed again. The physical preflight still stops before ORFS starts;
there are no new placement, timing, routing or GDS results. A manual hosted workflow
is on the default branch but has not been run. The current task
therefore remains a synthesis-complete checkpoint.

## 1. Introduction

This independent undergraduate project takes a previously verified combinational
8-bit ALU into registered standard-cell synthesis. It implements a small,
inspectable verification and execution harness and prepares the official OpenROAD
Flow Scripts (ORFS) integration needed to continue toward physical layout.
The evidence boundary is explicit: no GDSII has been generated.

## 2. Motivation

RTL defines logical behavior, whereas physical implementation must also satisfy
library, timing, placement and routing constraints. The project develops that
connection using a small design whose entire binary arithmetic domain can still
be simulated. Reproducible evidence is more useful here than an unnecessarily
large processor or an unsupported timing claim.

## 3. Relationship to Previous RTL Project

The source is [RTL-Verification-Core-ALU](https://github.com/Vinh-Duy/RTL-Verification-Core-ALU)
at `1621da9b2d9d395698cc23a3dfc3ecf2e66e905d`. Only the synthesizable ALU and
32 known-answer vectors were reused, byte for byte. The original repository was
read but not edited. The existing EDA routing project is also unchanged.

The new work adds an output-register interface, clock/reset verification,
Nangate45 mapping, post-synthesis functional checks, physical-flow configuration,
and controlled-experiment infrastructure. Yosys/ABC perform synthesis; OpenROAD
would perform placement/routing. This project does not claim to invent those engines.

## 4. Design Specification

The unsigned inputs are A[7:0], B[7:0] and opcode[2:0]; result is 16 bits. Opcodes
0–7 select ADD, SUB, MUL, DIV, AND, OR, XOR, SHL. SUB wraps modulo 65536, MUL keeps
the full product, DIV returns zero for zero divisor, and SHL uses B[2:0].
See [the full specification](DESIGN_SPECIFICATION.md) for exact examples and widths.

## 5. Registered ALU Architecture

The ALU remains combinational and drives sixteen positive-edge output registers.
There are no input registers. A rising edge captures the current input function,
or zero if synchronous active-low reset is asserted. The design accepts a new
transaction each cycle. It contains one output-register boundary, not a two-stage
pipeline. Main arithmetic timing paths are input-to-register paths.

## 6. Functional Verification

Python's integer oracle is checked against the 32 inherited literal answers.
The standard suite then adds 12×12 boundary pairs for each opcode (1,152 cases)
and 4,096 reproducibly generated random cases, seed 2026: **5,280 vectors**.
The exhaustive suite includes every 256×256×8 binary combination plus the 32
known answers: **524,320 vectors**. Both executed successfully.

The SystemVerilog scoreboard rejects unknown/mismatched outputs and verifies
that changing inputs at the falling edge cannot change the registered result
before the next rising edge. It tests back-to-back transactions, a nonzero result
before reset, synchronous assertion, reset hold, reset release and correct capture.
Four targeted injected faults were rejected: a corrupted expected value, ADD
replaced by XOR, asynchronous reset, and an extra pipeline stage. These negative
tests demonstrate that success is not merely the simulator reaching `$finish`.
An actual VCD is retained, with detailed dumping limited to the first 100 vectors.

The mapped gate netlist also passed **524,320 vectors**, using the same mathematical
specification and Liberty-derived functional cell models. Gate simulation is
zero-delay and is not formal equivalence, SDF simulation, STA or physical verification.

## 7. Technology-Mapped Synthesis

Yosys 0.70 (`28ba3cb92`), delivered as YoWASP 0.70.0.0.post1259, executed real
`synth`, `dfflibmap` and ABC library mapping. Arithmetic division was retained.
The netlist has only library cells after removing Yosys's debug `$scopeinfo` object.
The script checks design connectivity, cell types and exactly sixteen registers.

| Local mapped result | Value |
|---|---:|
| Total standard cells | 744 |
| Sequential cells | 16 DFF_X1 |
| Combinational cells | 728 |
| Mapped cell area | 879.928 µm² |
| Sequential cell area | 72.352 µm² |

These figures describe standalone, non-timing-driven synthesis. This script does
not read SDC; therefore these numbers do not establish a 10 ns implementation.
ORFS will resynthesize using its own recipes, and its results may differ.

ABC reported two multi-output library cells (example FA_X1). No FA_X1 is present
in this mapped netlist; the final netlist elaborates and passes the functional
checks. Library diagnostic messages about unused sequential/clock-gating cells
are mapping/model-import context, not evidence that the design lacks registers.
Model generation initially failed on a missing function in CLKGATETST_X1; allowing
unneeded missing-function library entries resolved it. Used-cell elaboration was
then verified. No DUT operation changed to work around these issues.

## 8. Standard-Cell Platform

The sole baseline is Nangate45, with the typical Liberty file from ORFS commit
`7bcaf475c884e15f674e428aa04dbf92bd0426ed`. It is characterized at 1.10 V and 25 °C,
using ns and fF units. The downloaded file's SHA-256 is
`8d540a4d4cf6d09d27c87ad067857a9c0c2eeb023ab7a56e058cd3113db4e9b1`.
The download script also retrieves the platform license. No proprietary PDK is used.

A Liberty library supplies cell Boolean/sequential functions, area and electrical
timing models. Physical flow additionally requires LEF geometry, GDS cell views,
routing layers/rules and extraction data. Downloading only Liberty does not
constitute a complete installed physical platform.

## 9. Floorplanning

**NOT RUN.** The prepared baseline requests 30% core utilization, square aspect
ratio and 5 µm core margin. ORFS would construct the core/die bounds, rows, pins
and power distribution. Core area includes cell placement whitespace; die area
also includes surrounding margins. Neither is the mapped cell-area sum. There
is no measured floorplan dimension to report.

## 10. Placement

**NOT RUN.** Placement locates standard cells in legal rows and optimizes wire
estimates/timing. Global placement proposes positions; detailed placement legalizes
and refines them. The configured density target is 0.70. No cell-position data,
legality result or measured utilization is available.

## 11. Clock Tree Synthesis

**NOT RUN.** CTS distributes the clock to register sinks using buffers and routing
while controlling skew and latency. The sixteen-register design has a clock, but
that alone does not prove CTS will insert a tree. An actual CTS log and clock-buffer
metrics must be inspected before reporting implementation success or buffer counts.

## 12. Global Routing

**NOT RUN.** Global routing assigns coarse routes/guides and estimates resource
usage. Congestion compares routing demand with available capacity in regions and
layers. No congestion data or global-route completion result exists for this design.

## 13. Detailed Routing

**NOT RUN.** Detailed routing realizes specific tracks and vias and reports routing
rule violations. Completion and zero violations are separate claims. There are
no measured wirelength, violation count or routed net database results yet.

## 14. Timing Analysis

**NOT RUN.** The proposed SDC uses a 10 ns clock and explicit IO budgets, transitions,
loads and clock uncertainty. Synchronous reset is constrained as data, not excluded.

Setup slack is the required latest arrival minus actual data arrival. Negative
setup slack means data arrives too late. Hold slack measures whether the earliest
data arrival remains late enough after the relevant capture edge; negative hold
slack means data changes too early. WNS conventionally reports the most negative
setup slack, or zero when there is no negative setup slack. TNS sums negative
endpoint slacks as defined by the timing tool; it is not a sum over every path.

A critical path has the least relevant timing slack under the specified constraints.
Placement and routing introduce wire capacitance/resistance and change buffering,
so their delays differ from a purely logical view. In this output-only registered
architecture, the IO assumptions materially affect the arithmetic timing budget.
Clock minus slack must not be mislabeled as isolated combinational delay. A complete
expanded STA path report is needed to separate input delay, data delay, clock
latency, uncertainty and setup time.

Meeting a chosen constraint would show feasibility at that target/corner/assumptions;
it would not prove the maximum attainable frequency. No WNS, TNS, critical-path
delay, setup/hold count or maximum frequency is currently reported.

## 15. GDSII Generation

**NOT RUN.** ORFS `finish` is configured to generate the final stream layout and
reports. The prepared checker uses KLayout to require one nonempty `alu_top`
top cell and records database units and bounding box. No GDS file exists now.
Even successful read-back would prove readability rather than manufacturing readiness.

## 16. Experimental Methodology

The runner allocates fresh output directories, records content hashes and tool
versions, checks exit codes, bounds each stage, retains failures, and collects
raw metric JSON with provenance. No stale result directory is reused.

The planned utilization sweep requests 30%, 45% and 60% while retaining RTL,
platform, target clock, IO assumptions and placement density. Clock-period values
will be selected only after a measured baseline timing report is available. The
optional width study was deferred to keep attention on the essential 8-bit flow.
Higher utilization need not monotonically worsen timing: area, wirelength,
placement decisions, congestion and repair interact. A few samples cannot justify
broad causal claims. Repeat runs or seed/thread controls would strengthen inference.

## 17. Results

| Stage/check | Status | Actual evidence |
|---|---|---|
| Environment audit and source provenance | PASS | Host audit, unchanged source hashes |
| RTL elaboration | PASS | Icarus `-g2012 -Wall` |
| Standard RTL regression | PASS | 5,280 vectors |
| Exhaustive RTL simulation | PASS | 524,320 vectors |
| Testbench fault detection | PASS | Four injected faults rejected |
| Execution, parser and workflow-selection unit tests | PASS | 14 tests on 27 October |
| Nangate45 mapping | PASS | 744 cells; 879.928 µm² |
| Exhaustive functional gate simulation | PASS | 524,320 vectors |
| ORFS synthesis through finish | NOT RUN | Missing physical toolchain |
| Final STA and timing closure | NOT RUN | No timing report |
| Physical experiments and figures | NOT RUN | No executed physical samples |
| GDS generation/read-back | NOT RUN | No GDS output |
| Formal equivalence | NOT RUN | No formal engine run |
| GitHub Actions execution | NOT RUN | Workflow authored locally only |

Detailed per-stage status and evidence pointers are in
[FINAL_VALIDATION.md](FINAL_VALIDATION.md) and [evidence/](evidence/).

## 18. Discussion

The existing arithmetic core synthesizes without dropping expensive operations.
The divider is retained in the Boolean implementation, but this experiment does
not isolate its area or delay contribution, so no percentage is attributed to it.
The wrapper's state maps to sixteen DFFs as expected. Exhaustive gate simulation
supports functional preservation over the known-input arithmetic domain.

The strongest current finding is a verified mapping and reproducible checkpoint.
A clock target, a working configuration file or a successful netlist is insufficient
to support claims about a placed/routed chip. Distinguishing these evidence levels
is itself central to defensible engineering work.

## 19. Limitations

See [LIMITATIONS.md](LIMITATIONS.md). Physical placement/routing, STA, GDS, DRC/LVS,
formal equivalence, power analysis, multi-corner sign-off and remote CI execution
remain unverified. There are no layout screenshots or physical experimental figures.
The Mac's missing physical toolchain, rather than an observed divider/resource
failure in OpenROAD, is the present blocker.

## 20. Future Improvements

Run the prepared baseline on compatible Linux; inspect constraints and all stage
reports; check actual CTS and placement legality; record post-route timing and
routing violations; validate GDS read-back. Then execute the utilization and
baseline-informed clock sweeps and reproduce figures from their measured data.
Formal equivalence, a separately verified width variant, and qualified power
analysis are optional follow-ups after the essential physical flow succeeds.

## 21. Reproduction Instructions

From this repository with Python 3.10+ and Icarus installed:

```bash
make setup
make lint test simulate validate exhaustive
make synth gate-exhaustive
make report
```

Setup installs project-local pinned tools and downloads the checksum-verified
library; it needs network access. Subsequent P0 runs are local. Raw reports and
waveforms are retained under unique subdirectories. For OpenROAD use the exact
Linux/Docker continuation in [ENVIRONMENT.md](ENVIRONMENT.md), then:

```bash
make physical
make timing
make experiments STUDY=utilization
# After setting clock_periods_ns based on measured baseline:
make experiments STUDY=clock
python3 scripts/analyze_results.py reports/experiments/<run-id>/summary.json
```

The analysis command requires the optional plotting requirements. It refuses to
invent plots from absent data. No `make` target commits, pushes, publishes or
deletes source/experimental evidence.
