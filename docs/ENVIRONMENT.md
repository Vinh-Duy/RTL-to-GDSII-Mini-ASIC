# Detected environment and execution options

Audit date: 17 October 2026 (Asia/Ho_Chi_Minh). This is the independent
`RTL_to_GDSII_Mini_ASIC` workspace, already initialized with an origin remote and
initial commit `9987e0e3301a8fc74fe35f688eb07a225efb6363`. No commit or push was made.

## Actual host

- macOS 13.7.8, build 22H730; `uname -m`: `x86_64`.
- MacBookPro14,1; Intel Core i5, 2.3 GHz, two physical cores; 8 GB RAM.
- Initial filesystem check: 233 GiB capacity, approximately 43 GiB available.
- Homebrew executable: `/usr/local/bin/brew`; no Homebrew installation was changed.
- Python 3.10.11; Icarus Verilog 13.0 and `vvp` already available.
- Docker CLI and `/Applications/Docker.app`: absent. Consequently Docker daemon and
  image compatibility tests could not run. No image has been downloaded.
- Native Yosys, Verilator, OpenROAD, standalone OpenSTA and KLayout: absent from PATH.
- `sysctl hw.memsize` was denied in the execution sandbox; `system_profiler` supplied
  RAM and CPU details. Device identifiers are intentionally excluded from repository evidence.
- Default sandbox network DNS failed. Narrowly approved downloads retrieved the open-source
  Python packages and pinned upstream library/reference files into this workspace.

## Project-local installed synthesis environment

`make setup` creates `.venv`, installs the exact versions in
[requirements-tools.txt](../requirements-tools.txt), and verifies the SHA-256 of
the Nangate45 typical Liberty file. Installed packages:

- YoWASP Yosys 0.70.0.0.post1259; tool reports Yosys 0.70, revision `28ba3cb92`.
- yowasp-runtime 1.96, wasmtime 47.0.1, click 8.5.0, platformdirs 4.12.4.
- Nangate45 library from ORFS `7bcaf475c884e15f674e428aa04dbf92bd0426ed`.
- Typical characterization: 1.10 V, 25 °C; time ns; capacitance fF.

YoWASP runs real Yosys/ABC compiled to WebAssembly. It is not a replacement
synthesis algorithm. Wasmtime uses this Intel host; no ARM-to-x86 container
emulation is involved. Initial compilation takes much longer than cached runs.
The runner confines YoWASP mounts/cache/temp files to the project. An initial
unrestricted mount-discovery probe stalled; it was stopped and replaced with
explicit project mounts. This does not establish native OpenROAD availability.

The Python wheels downloaded roughly 27 MB; the Liberty file is about 6.4 MiB.
Large PDKs, a full toolchain build and container images were not downloaded.

## Why physical implementation is blocked

No installed OpenROAD executable, ORFS checkout, KLayout or Docker daemon is
available. `make physical` was attempted and returns exit 2 with `NOT RUN` for
all ORFS stages. This is an environment preflight failure, not a routed design
failure. Native macOS compilation was not attempted: it would require additional
system dependencies and substantial build resources. A compatible Linux host is
the most direct continuation route.

## Linux continuation: official pinned checkout

These commands are **instructions, not executed results**. Use a Linux x86_64
machine with adequate RAM/storage, preferably at least 16 GB RAM and 30 GB free
for tool installation/build headroom. This is a conservative planning budget,
not measured memory consumption of this ALU. Check `df -h` and `free -h` before
large downloads. Use the official [prebuilt installation guide](https://openroad-flow-scripts.readthedocs.io/en/latest/user/BuildWithPrebuilt.html)
or the pinned repository's build instructions for the required Yosys, OpenROAD,
KLayout and auxiliary dependencies. The current ORFS flow requires more than an
arbitrary distribution's old Yosys package.

From a copy of this project on that Linux machine:

```bash
mkdir -p .tools
# A full clone/build can be large: review resources before running.
git clone https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts.git .tools/OpenROAD-flow-scripts
git -C .tools/OpenROAD-flow-scripts checkout 7bcaf475c884e15f674e428aa04dbf92bd0426ed
# Follow this checkout's official setup/build or prebuilt instructions.
# Do not run dependency-installation scripts as root without reviewing their effects.
source .tools/OpenROAD-flow-scripts/env.sh
export ORFS_ROOT="$PWD/.tools/OpenROAD-flow-scripts"
yosys -V
openroad -version
klayout -v
make physical
make timing
make experiments STUDY=utilization
```

The runner checks the checkout revision and tracked-file cleanliness, and records
actual tool versions. It invokes official `synth`, `floorplan`, `place`, `cts`,
`grt`, `route`, and `finish` targets in order. It does not replace upstream stages.
All generated artifacts use a new project-local `WORK_HOME`. A stage needs both
exit code zero and its expected nonempty artifact. GDS must additionally pass a
KLayout read-back check. Inspect the CTS report to confirm a clock tree was actually
constructed and final reports for timing/routing violations; completed commands
alone are not a sign-off verdict.

## Docker continuation

Do not install Docker Desktop automatically on this host. Docker supports the
current and two preceding macOS major versions; this macOS 13 installation is
outside that window. Review the official [Mac requirements and installation steps](https://docs.docker.com/desktop/setup/install/mac-install/)
before any OS/application change. On a supported Mac, select the **Intel** installer,
install/start Docker Desktop explicitly, and check `docker info`. Installing it or
upgrading macOS requires a separate decision. A Linux machine with Docker Engine
avoids changing this Mac.

On a suitable Docker host, inspect the official image **before pulling**:

```bash
docker buildx imagetools inspect openroad/orfs:latest
# Review advertised platforms and download/storage requirements first.
# Pull a linux/amd64 image only after this review.
docker pull --platform linux/amd64 openroad/orfs:latest
docker image inspect openroad/orfs:latest --format '{{.Os}}/{{.Architecture}} {{json .RepoDigests}}'
# Assign the immutable openroad/orfs@sha256:... reference returned above:
export ORFS_IMAGE='openroad/orfs@sha256:REPLACE_WITH_INSPECTED_DIGEST'
make physical
```

The example digest is deliberately not a fabricated identifier. The runner rejects
mutable tags, missing local images, and non-linux/amd64 images; it does not pull.
It sources the image's ORFS environment before invoking commands. Image-based runs
record their digest and tool versions and form a **separate baseline** if their ORFS
revision differs from the pinned source checkout. Record the contained ORFS revision
where available before comparing experiments. No image has been verified here.

Intel can run linux/amd64 through Linux virtualization without instruction-set
emulation. On an Apple Silicon host, this baseline would require an amd64 emulator
and can be slower; verify an actual arm64 tool image before switching architectures.
Do not compare experiments across tool/image changes as one controlled sweep.

The supported `POST_CTS_TCL` hook writes `report_cts` counts in the CTS process.
The runner requires positive roots, inserted buffers, subnets and sinks before
labeling CTS PASS. A copied-through database or skipped tree cannot satisfy this check.
