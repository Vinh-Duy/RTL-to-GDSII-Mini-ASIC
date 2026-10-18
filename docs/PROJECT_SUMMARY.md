# Project summary for an undergraduate portfolio

## A. English summary (129 words)

I developed a reproducible standard-cell implementation workflow around my previously verified eight-bit ALU. I preserved all eight operations, including division, and added a registered output interface with a defined synchronous reset contract. Using Icarus Verilog, I checked every binary operand and opcode combination at both RTL and mapped gate level, alongside reset and latency tests. I synthesized the design with Yosys and the Nangate45 typical library, obtaining 744 cells, including sixteen registers, and 879.928 square micrometres of mapped cell area. I also prepared official OpenROAD flow configuration and experiment automation with isolated outputs, timeouts and metric provenance. Physical implementation remains unexecuted because the local Mac lacks OpenROAD and Docker. The current project demonstrates verified synthesis and careful engineering evidence, with placement, routing and timing analysis as the next milestone.

## B. Four completed technical achievements

1. Preserved the original eight-operation ALU exactly and added a synchronous
   registered wrapper with an explicit observable capture contract.
2. Passed exhaustive known-input RTL and mapped-gate simulation, each with
   524,320 vectors, and rejected four deliberately injected verification faults.
3. Executed Nangate45 technology mapping with 744 cells, 16 registers and
   879.928 µm² mapped area; checked netlist cell types and library provenance.
4. Implemented isolated execution/evidence capture and tested timeout, failure
   propagation and missing-metric handling; prepared official ORFS integration.

## C. Extension of the earlier project

The earlier repository asks whether the combinational ALU behaves correctly.
This project adds synchronous interface behavior and demonstrates how the same
function maps to real standard-cell types. It prepares the physical constraints
and experimental framework needed to study placement, clocking and routing.
Those physical stages are future execution work, not completed achievements.

## D. Actual results

- RTL: 5,280-vector regression PASS; 524,320-vector exhaustive suite PASS.
- Gate level: 524,320-vector exhaustive functional suite PASS.
- Mapping: 744 total cells = 728 combinational + 16 DFF_X1 cells.
- Mapped area: 879.928 µm², of which 72.352 µm² is sequential-cell area.
- Physical results: **NOT RUN**. No core/die area, setup/hold slack, routed
  wirelength, congestion, GDSII or power number is available.
- Remote GitHub Actions execution: **NOT RUN**.

## E. Two-line CV description

Implemented and exhaustively verified a registered eight-operation 8-bit ALU at RTL and mapped gate level; synthesized 744 Nangate45 cells with 879.928 µm² mapped area using Yosys.
Prepared a reproducible OpenROAD physical-design workflow with constrained IO timing and isolated experiment logging; placement, routing and STA remain pending environment setup.

## F–G. Five interview questions and answers

**1. What does synthesis do, and why is a standard-cell library necessary?**
Synthesis elaborates RTL and lowers arithmetic/control into Boolean logic and
registers, optimizes it, and maps it to available cells. The library defines cell
functions, area and timing characteristics. I verified a Nangate45 mapping rather
than merely counting generic RTL operators. Yosys/ABC performed the mapping.

**2. What is the difference between placement and routing, and between cell,
core and die area?**
Placement assigns cells to legal physical positions. Routing connects their pins
with wires and vias. Mapped cell area sums individual library cell areas. Core
area includes whitespace and room for placement/power infrastructure; die area
also includes surrounding margins. I measured cell area only. I have not yet
executed placement or routing for this design.

**3. What is a critical path, and how does clock period affect timing closure?**
The critical path has the least relevant slack under the timing constraints.
A shorter target period usually reduces the setup time budget and can cause
optimization, buffering or larger cells. Routing adds parasitic delay. My ALU has
input-to-register arithmetic paths, so external input delays also consume the
budget. I configured a provisional 10 ns target, but did not measure its slack
or establish a maximum frequency.

**4. How do you know the wrapper and synthesized design are correct?**
I compare results after each rising edge with an integer oracle, verify output
stability before capture, and exercise synchronous reset and back-to-back inputs.
Both RTL and functional gate simulation covered the full binary arithmetic domain.
Four injected faults confirmed that the harness fails on incorrect behavior.
This is strong finite-domain simulation evidence, not formal equivalence or
proof of timing behavior, metastability handling or analog correctness.

**5. Why would a GDSII file not be enough for tapeout?**
GDSII stores layout geometry; readability does not prove manufacturing correctness.
A real tapeout needs a foundry-qualified process and checks such as DRC/LVS,
antenna, multi-corner timing, extraction validation, power integrity and integration
review. This educational project has not generated GDSII and claims none of those
sign-off outcomes.

## H. Limitations

The present deliverable is synthesis-complete. Physical-flow integration lacks
an execution-capable OpenROAD/Linux environment on the local Mac. No physical
experiments, final timing, formal equivalence or power analysis ran. A future
portfolio revision should replace these pending statements only with checked
outputs from actual execution. See [LIMITATIONS.md](LIMITATIONS.md).
