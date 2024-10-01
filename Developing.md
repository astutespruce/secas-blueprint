# SECAS Southeast Conservation Blueprint Explorer - Local Development

## Architecture

This uses a data processing pipeline in Python to prepare all spatial data for use in this application.

The user interface is creating using GatsbyJS as a static web application.

The API is implemented in Python and provides summary reports for pre-defined summary units and user-defined areas.

## Development

Python dependencies are managed using `uv`. First,
[install uv](https://docs.astral.sh/uv/), then:

```bash
uv venv .venv --python 3.12
<source it according to your shell, e.g., source .venv/bin/activate.fish>
uv sync --extras dev
```

To update the requirements.txt file used to build these dependencies into the API
Docker container for deployment, run:

```bash
uv pip compile pyproject.toml -o ../secas-docker/docker/api/secas-blueprint-requirements.txt
```

### Other dependencies

On MacOS, install other dependencies:

- `brew install gdal`
- `brew install pango`

For Macos M1 (Arm64), you also may need to setup a symlink for one of the libraries
to be found:

```
sudo ln -s /opt/homebrew/opt/fontconfig/lib/libfontconfig.1.dylib /usr/local/lib/fontconfig-1
```

Tilesets are created using `tippecanoe` (installed via homebrew) or
[`rastertiler-rs`](https://github.com/brendan-ward/rastertiler-rs) built from
source. See [analysis/prep/tiles/README](./analysis/prep/tiles/README.md) for more information
