# Registered 8-bit ALU specification

## Provenance

The combinational `alu_8bit` module is copied **without modification** from
[Vinh-Duy/RTL-Verification-Core-ALU](https://github.com/Vinh-Duy/RTL-Verification-Core-ALU),
commit `1621da9b2d9d395698cc23a3dfc3ecf2e66e905d`, using the local sibling
`Verification_Adder`. The source matched the committed file. Its 32 literal
known-answer vectors were also copied. Exact hashes and file paths are in
[evidence/source-provenance.json](evidence/source-provenance.json).
The existing repository's unrelated uncommitted documentation changes were preserved.

No operations were removed or rewritten for synthesis. The wrapper, synchronous
interface tests, synthesis scripts, SDC, ORFS configuration and experiment runner
are new work in this independent project. No complete processor or bus was added.

## Ports and operation semantics

`clk` and `rst_n` are one-bit inputs. `a` and `b` are unsigned 8-bit inputs;
`opcode` is three bits. `result` is an unsigned 16-bit registered output.
For integer A and B in [0,255]:

| Opcode | Operation | Captured value |
|---|---|---|
| 000 | ADD | A + B, including the ninth carry bit |
| 001 | SUB | (A − B) modulo 65536 |
| 010 | MUL | Full A × B product |
| 011 | DIV | floor(A/B), or 0 when B=0 |
| 100 | AND | Zero-extended bitwise A AND B |
| 101 | OR | Zero-extended bitwise A OR B |
| 110 | XOR | Zero-extended bitwise A XOR B |
| 111 | SHL | A × 2^(B mod 8), retained in 16 bits |

Examples: 255+255=510; 0−1=65535; 255×255=65025; 255/2=127;
255/0=0; 255 shifted by B=255 gives 32640 because only B[2:0] is used.
ADD can overflow eight bits, but never this 16-bit output. There is no flag output.

## Clock, reset and observable latency

There are **no input registers** and one bank of sixteen output flip-flops.
At rising edge k, when `rst_n=1`, `result` captures the ALU function of inputs
present at that edge. The observable output becomes valid after the nonblocking
assignment delta cycle in RTL (and clock-to-Q delay in real hardware).
Inputs driven after edge k are captured at edge k+1. Throughput is one transaction
per cycle; there is one output-register boundary, not two pipeline cycles.

Reset is **synchronous, active low**. At a rising edge with `rst_n=0`, result is
zero regardless of other inputs. Asserting or releasing reset between edges must
not immediately change result. Result is not specified before the first resetting
edge. There are no initial values in the synthesizable state.

The exhaustive mathematical domain contains all 524,288 known binary combinations.
The copied core retains its four-state RTL behavior, including the zero fallback
for an X/Z opcode, but this project does not claim exhaustive four-state or
metastability verification. Gate mapping need not preserve simulation-only X/Z
fallback behavior. Gate validation uses binary inputs only.

## Timing contract and assumptions

The testbench's 10 ns period and 1 ns sample offset are scheduling devices for
zero-delay functional simulation. They are not evidence that the hardware meets
100 MHz. For physical implementation, `constraints/timing.sdc` declares a separate,
provisional 10 ns `core_clk`, with fixed 1.0 ns maximum and 0.1 ns minimum IO delays,
0.10 ns setup uncertainty, 0.05 ns hold uncertainty, 0.05 ns input/clock transitions,
and 5 fF output loads. These are illustrative external-interface assumptions, not
board measurements. The Liberty units were checked.

`rst_n` is constrained as synchronous data. No false path or case analysis hides
its timing. The main arithmetic paths are **input-to-register** paths; there is
no internal register-to-register ALU pipeline. Consequently any future timing
claim must include the IO budgets. Changing the target clock while keeping these
budgets fixed changes the time available for combinational logic.

Standalone `make synth` is structural technology mapping. It does **not** read
this SDC, impose the 10 ns target on ABC, or perform STA. The official ORFS path
consumes the SDC and repeats synthesis using its own supported recipes. Its future
cell counts need not match the standalone baseline.

## Correctness criteria

A binary transaction must match the integer oracle after its capture edge and
must not change the preceding registered output before that edge. Back-to-back
transactions require no idle cycles. Reset assertion, hold and release must obey
the synchronous contract. Unknown outputs, missing vectors, malformed files,
wrong counts, uncovered opcodes or mismatches cause `$fatal` and a failing process
exit. An independent watchdog bounds the simulator; the Python runner also has a timeout.
