# Detected environment and execution options

## Current recheck — 30 October 2026

The Mac still has no Docker, OpenROAD, KLayout or pinned ORFS checkout. The latest
`make physical` attempt is `reports/physical/20261027T145432Z-66661b19`; it stopped
before the first ORFS command, with all stages `NOT RUN`. No physical artifacts or
timing measurements exist. The workflow in
[physical-baseline.yml](../.github/workflows/physical-baseline.yml) has been pushed,
but has not been run. The local workspace has no `gh` executable, so launch it from
GitHub Actions.

Launch it from GitHub **Actions → ORFS physical baseline and utilization sweep → Run workflow**.
It runs the physical preflight, baseline, final timing, and then the utilization
study only if the baseline and timing commands succeed. Artifacts are retained for
30 days, including stage logs/reports, manifests, metrics and any generated GDS.

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

From a copy of this project on that Linux machine, build the official ORFS Docker
image from the pinned revision. ORFS records dependent source revisions in its
submodules, so initialize them after checking out the project pin:

```bash
mkdir -p .tools
# A full clone/build can be large: review resources before running.
git clone https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts.git .tools/OpenROAD-flow-scripts
git -C .tools/OpenROAD-flow-scripts checkout 7bcaf475c884e15f674e428aa04dbf92bd0426ed
git -C .tools/OpenROAD-flow-scripts submodule update --init --recursive
cd .tools/OpenROAD-flow-scripts
./build_openroad.sh --threads 2 --copy-platforms
cd ../..
# Mark the just-built image with the checked-out ORFS source revision.
export ORFS_REVISION="$(git -C .tools/OpenROAD-flow-scripts rev-parse HEAD)"
test "$ORFS_REVISION" = 7bcaf475c884e15f674e428aa04dbf92bd0426ed
docker build --pull=false --build-arg ORFS_REVISION="$ORFS_REVISION" \
  --tag alu-orfs:pinned - <<'DOCKERFILE'
FROM openroad/orfs:latest
ARG ORFS_REVISION
RUN printf '%s\n' "$ORFS_REVISION" > /OpenROAD-flow-scripts/.orfs-revision
LABEL org.openroad-flow-scripts.revision="$ORFS_REVISION"
DOCKERFILE
# Use the immutable local image ID; the runner checks its recorded revision.
export ORFS_IMAGE="$(docker image inspect alu-orfs:pinned --format '{{.Id}}')"
make physical-preflight
make physical
make timing
```

`--copy-platforms` is required here because ORFS excludes platform files from
the default Docker build context; without it the Nangate45 design inputs are not
inside the image. This uses the official `build_openroad.sh` option documented in
the [ORFS Docker build instructions](https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts/blob/master/docs/user/BuildWithDocker.md).
The wrapper records the checked-out ORFS revision. The runner checks that marker,
the pinned Nangate45 Liberty hash, and actual Yosys, OpenROAD and KLayout versions.
It invokes official `synth`, `floorplan`, `place`, `cts`,
`grt`, `route`, and `finish` targets in order. It does not replace upstream stages.
All generated artifacts use a new project-local `WORK_HOME`. A stage needs both
exit code zero and its expected nonempty artifact. GDS must additionally pass a
KLayout read-back check. Inspect the CTS report to confirm a clock tree was actually
constructed and final reports for timing/routing violations; completed commands
alone are not a sign-off verdict.

## Existing prebuilt-image option

Do not install Docker Desktop automatically on this host. Docker supports the
current and two preceding macOS major versions; this macOS 13 installation is
outside that window. Review the official [Mac requirements and installation steps](https://docs.docker.com/desktop/setup/install/mac-install/)
before any OS/application change. On a supported Mac, select the **Intel** installer,
install/start Docker Desktop explicitly, and check `docker info`. Installing it or
upgrading macOS requires a separate decision. A Linux machine with Docker Engine
avoids changing this Mac.

The runner requires the `.orfs-revision` marker added by the pinned source-build
steps above. The unmodified upstream prebuilt image does not expose its source
revision inside the container and cannot pass this project's preflight on its own.
Review its platform and image provenance before using it:

```bash
docker buildx imagetools inspect openroad/orfs:latest
# Review advertised platforms and download/storage requirements first.
# Pull a linux/amd64 image only after this review.
docker pull --platform linux/amd64 openroad/orfs:latest
docker image inspect openroad/orfs:latest --format '{{.Os}}/{{.Architecture}} {{json .RepoDigests}}'
```

No image has been built or verified on this Mac. The local source-build route above
is preferred because it ties the official image build to the pinned checkout.

Intel can run linux/amd64 through Linux virtualization without instruction-set
emulation. On an Apple Silicon host, this baseline would require an amd64 emulator
and can be slower; verify an actual arm64 tool image before switching architectures.
Do not compare experiments across tool/image changes as one controlled sweep.

The supported `POST_CTS_TCL` hook writes `report_cts` counts in the CTS process.
The runner requires positive roots, inserted buffers, subnets and sinks before
labeling CTS PASS. A copied-through database or skipped tree cannot satisfy this check.
