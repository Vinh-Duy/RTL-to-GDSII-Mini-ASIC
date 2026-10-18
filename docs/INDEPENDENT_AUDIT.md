# Independent final engineering audit

Audit date: **17 October 2026**, Asia/Ho_Chi_Minh. Fresh execution ran at
17:40–17:42 local time. This is a new inspection and rerun of the existing working
tree, not a claim of external third-party certification.

**Verdict: the synthesis milestone is genuine and reproducible, but two reporting/
reproducibility findings remain before an unqualified “ready for GitHub” verdict.**
The project is not a completed physical-design or RTL-to-GDSII implementation.
No working RTL, scripts, constraints, tests, README or existing technical report
was edited during this audit. Only audit evidence/report files and generated run
outputs were added. No commit or push was made.

## 1. Findings requiring attention

### F1 — Medium: the documented reproduction command does not force the pinned Yosys

Location: [scripts/common.py](../scripts/common.py), lines 23–29;
[README.md](../README.md), lines 133–137.

`make setup` installs pinned YoWASP under `.venv`, but `yosys()` chooses any native
`yosys` on PATH before that installation unless `YOSYS` is explicitly set. Thus a
reader following the README on a machine with native Yosys can synthesize with a
different version and obtain different mapping/area than the published baseline.
The local Mac has no native Yosys, so this did not corrupt the measured results.
CI intentionally uses distribution tools and is already documented as a different
baseline; that is separate from the README reproduction issue.

An isolated PATH-selection probe confirmed that the native-path candidate wins
while the pinned local executable exists. The candidate was a stub used only for
selection inspection; it was never run as a synthesis engine.
[Probe evidence](evidence/independent-audit-20261017/tool-selection-reproduction.json).

**Required resolution:** make the published exact-baseline instructions explicitly
set `YOSYS="$PWD/.venv/bin/yowasp-yosys"`, or change/document selection policy.
The commands in section 7 below already supply the explicit setting. No code fix
was applied because this was an audit-only request.

### F2 — Medium: the current-status report can present stale verification as PASS

Location: [scripts/report.py](../scripts/report.py), lines 17–20.

The report compares only the two RTL hashes. It does not invalidate a recorded PASS
when known-answer vectors, testbench/oracle code, or other relevant stage inputs
change. This matters when the report is used as the status of the current checkout.

Reproduction used a completely isolated copy and a **real previously successful**
simulation summary. Only the copy's `add_zero` expected value changed from 0 to 1.
`report.py` returned exit 0 and simulation PASS; rerunning verification in that
same copy returned exit 1 at the oracle consistency assertion. No production file
was changed, and this probe contains no invented physical measurement.
[Probe evidence](evidence/independent-audit-20261017/freshness-reproduction.json).

**Required resolution:** validate stage-relevant input hashes, including verification
inputs, before presenting current PASS, or clearly report a historical/unverified
status when those inputs changed. For physical results the same principle includes
SDC/configuration. The existing documentation honestly says the report checks RTL
freshness, but that does not make it a complete current-state validation mechanism.
Today's published claims remain valid because fresh runs passed and their inputs
were independently checked during this audit.

## 2. Completed stages and fresh verification

| Stage/check | Audit status | Actual observation |
|---|---|---|
| Upstream source provenance | PASS | RTL and inherited answers match the original Git commit bytes |
| RTL elaboration | PASS | Icarus `-g2012 -Wall`; exit 0 |
| Boundary/directed/random RTL regression | PASS | 5,280 vectors |
| Exhaustive RTL simulation | PASS | 524,320 vectors; compiler and simulator exit 0 |
| Failure injection | PASS | All four intentionally faulty cases rejected |
| Runner/metrics unit tests | PASS | Six tests |
| Technology-mapped Yosys synthesis | PASS | Synthesis and model-generation exit 0 |
| Independent mapped-netlist check | PASS | Re-read mapped Verilog; `check -assert`: 0 problems |
| Exhaustive gate-level simulation | PASS | Fresh 524,320-vector run; compiler and simulator exit 0 |
| Actual waveform output | PASS | 20,350-byte RTL VCD; definitions and 303 timestamp records |
| ORFS synthesis | NOT RUN | No installed physical-flow environment |
| Floorplanning | NOT RUN | No floorplan database |
| Placement/legality | NOT RUN | No placement database or legality report |
| CTS | NOT RUN | No clock tree or CTS report |
| Global routing | NOT RUN | No routing guides/congestion report |
| Detailed routing | NOT RUN | No routed database/DRC report |
| Final STA | NOT RUN | No timing report or extracted parasitics |
| GDSII generation/read-back | NOT RUN | No GDSII artifact or viewer run |
| Physical experiments | NOT RUN | No executed samples/experimental CSV rows |
| Remote GitHub Actions | NOT RUN | No remote workflow execution established by this audit |

Fresh command exit codes are preserved in
[commands.json](evidence/independent-audit-20261017/commands.json).
`make physical`, `make timing` and `make experiments` each returned **2**.
Those are blocked preflight/report requests, not completed physical stages and
not evidence of a design failing placement or routing.

The four negative cases deliberately fail their simulations: corrupted expected
value, wrong ADD implementation, asynchronous reset, and additional latency.
Their rejection is the expected successful test outcome. No unexpected DUT or
synthesis failure occurred in the fresh audit runs. F2 is a reporting-integrity
failure reproduced separately from those six passing unit tests.

## 3. Actual metrics and provenance

| Measured synthesis metric | Independently confirmed value |
|---|---:|
| Mapped library instances | 744 |
| Sequential cells | 16 DFF_X1 |
| Combinational cells | 728 |
| Total mapped cell area | 879.928 µm² |
| Sequential cell area | 72.352 µm² |

Area was independently recomputed by parsing the pinned Liberty cell areas and
summing them over mapped JSON instances, rather than trusting only the published
summary. A separate Yosys read/check/stat command on the emitted Verilog reproduced
the same counts/area and reported no structural problems.

The platform is Nangate45 typical, 1.10 V / 25 °C, from ORFS commit
`7bcaf475c884e15f674e428aa04dbf92bd0426ed`. The library SHA-256 is
`8d540a4d4cf6d09d27c87ad067857a9c0c2eeb023ab7a56e058cd3113db4e9b1`.
The rerun used Yosys 0.70 (`28ba3cb92`) via YoWASP 0.70.0.0.post1259,
Python 3.10.11 and Icarus Verilog 13.0 on Intel x86_64 macOS 13.7.8.

The regenerated mapped Verilog and functional models are byte-identical to the
published evidence. The mapped netlist SHA-256 remains
`1375f6c52286e8a468fb34d743428a6105a0809d5e7afc3217fec5c36f6fab31`.
All 35 files in the existing evidence index matched their recorded hashes.

The raw exhaustive stimulus was independently inspected: **524,288 distinct binary
input/opcode combinations**, 524,320 total rows including 32 known answers, and zero
mismatches against an independently written arithmetic check. Multiplication in
that check used partial-product accumulation. This confirms the domain claim rather
than relying solely on the testbench's printed counter.

**Physical metrics are unavailable:** no core/die area, achieved utilization,
setup/hold WNS/TNS, critical-path delay, clock-buffer count, routed wirelength,
congestion or routing violations were measured. The configured 10 ns period,
30% baseline core utilization, 0.70 placement density and planned 30/45/60% sweep
are inputs/plans only. The 879.928 µm² value is mapped cell area, not die area.

## 4. GDSII location and validation

**There is no GDSII file location to report.** Repository inventory found no
`.gds`, `.oas`, `.odb`, `.def` or `.spef` artifacts before audit fixtures were created.
Generation and KLayout read-back are NOT RUN. The prepared future output path is
`reports/physical/<run-id>/results/nangate45/alu_top/base/6_final.gds`; that is a path
pattern, not an existing deliverable.

## 5. Documentation accuracy and remaining limitations

The README and technical report correctly disclose synthesis-complete status,
retain all eight operations, distinguish simulation from formal equivalence/STA,
and avoid claiming physical timing or GDS success. Their published numerical
claims match the actual evidence and fresh reruns. Local documentation links
resolved. F1 is a concrete gap in the reproduction instructions.

Additional limitations and evidence qualifications:

- No OpenROAD, Docker, KLayout, native Yosys, standalone OpenSTA or Verilator is on
  the audited PATH. Physical integration and its metric-schema compatibility have
  not been validated by an actual ORFS run. No claim that every prepared metric
  key works is established here.
- Standalone synthesis does not consume the physical SDC. No 100 MHz capability,
  timing closure or maximum operating frequency is established.
- Gate simulation is zero-delay and binary-input only. No formal equivalence,
  SDF simulation, power analysis, DRC/LVS or multi-corner sign-off ran.
- ABC warns about multi-output library cells; the mapped netlist does not use
  those full-adder cells and passes gate verification. Generated cell/netlist
  models lack explicit time-unit declarations, producing Icarus warnings; no
  delays are modeled in those modules.
- The saved main synthesis stdout log ends in the ABC portion rather than showing
  the later check/stat footer. This weakens log-only traceability but does not
  invalidate the checked outputs: the rerun returns 0, emits matching artifacts,
  and the independent netlist-check log explicitly reports 0 problems and area.
- All implementation additions remain uncommitted/untracked except the modified
  tracked README, as before the audit. They must be deliberately included when
  the owner eventually publishes. No automatic staging/commit/push occurred.
- Prior repositories' working-tree statuses still match their original snapshots.
  All 79 pre-existing audited source/document/evidence files kept their hashes.

## 6. Publication verdict

**I would not issue an unconditional “ready for GitHub” verdict yet.** Resolve F1
and F2, then recheck their reproductions. The verified synthesis milestone is
technically credible and suitable for an undergraduate portfolio once those
reproducibility/reporting issues are addressed and the synthesis-only disclosure
is retained. Completing physical design is not a prerequisite for publishing an
honestly labeled intermediate milestone; it is a prerequisite for claiming a
completed RTL-to-GDSII/physical-design project.

To claim the full project, separately obtain the compatible Linux/ORFS environment,
run all physical stages, inspect timing and violations, validate the GDS, and run
the promised controlled experiments. Remote CI remains an additional unverified
workflow; do not display a passing-CI claim before it actually runs.

## 7. Exact reproduction commands

On this workspace, with its existing Python and Icarus installations:

```bash
cd /Users/vinhduy/Desktop/RTL_to_GDSII_Mini_ASIC
make setup
export YOSYS="$PWD/.venv/bin/yowasp-yosys"
make lint test simulate validate exhaustive
make synth gate-exhaustive
make report
```

`make setup` is needed for a fresh checkout and requires network access; this audit
reused the installed pinned environment and did not reinstall it. The explicit
`YOSYS` assignment fixes executable selection for reproducing the published numbers.
The optional `make gate` repeats the shorter 5,280-vector gate regression.

The following commands were also checked and currently fail clearly with exit 2:

```bash
make physical
make timing
make experiments
```

They become meaningful physical execution commands only after following
[ENVIRONMENT.md](ENVIRONMENT.md) to prepare a compatible Linux/ORFS installation.
Then `make experiments STUDY=utilization` runs the proposed utilization sweep;
clock values must first be selected from real baseline timing before running
`make experiments STUDY=clock`. No physical reproduction success is asserted here.

## Audit evidence

- [New command exit codes](evidence/independent-audit-20261017/commands.json)
- [Independent source/hash/area/artifact inspection](evidence/independent-audit-20261017/independent-evidence-check.json)
- [Vector-domain and byte-identical reproduction checks](evidence/independent-audit-20261017/vector-and-reproduction-check.json)
- [Independent mapped-netlist structural/statistics log](evidence/independent-audit-20261017/mapped_netlist_check.log)
- [Fresh gate scoreboard output](evidence/independent-audit-20261017/gate-simulation.log)
- [Original-file preservation and final stage inventory](evidence/independent-audit-20261017/final-audit-checks.json)
- [Audit snapshot SHA-256 manifest](evidence/independent-audit-20261017/sha256.json)

Raw audit files are under
`reports/audit/independent-20261017T104041Z-9ee2bcd4/`. The freshness and PATH probes
are explicitly labeled isolated audit fixtures, not ALU experiment measurements.
