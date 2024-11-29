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
uv pip install -e [dev].
```

To check for outdated dependencies and upgrade them:

```bash
uv pip list --outdated

# install latest version
uv pip install -U <packages>
```

To update the requirements.txt file used to build these dependencies into the API
Docker container for deployment, run:

```bash
uv pip compile -U pyproject.toml -o ../secas-docker/docker/api/secas-blueprint-requirements.txt
```

### Other dependencies

On MacOS, install other dependencies:

- `brew install gdal`
- `brew install pango`

For Macos M1 (Arm64), you also may need to setup symlinks for some of the libraries
to be found:

```bash
sudo ln -s /opt/homebrew/opt/glib/lib/libgobject-2.0.0.dylib /usr/local/lib/gobject-2.0
sudo ln -s /opt/homebrew/opt/pango/lib/libpango-1.0.dylib /usr/local/lib/pango-1.0
sudo ln -s /opt/homebrew/opt/harfbuzz/lib/libharfbuzz.dylib /usr/local/lib/harfbuzz
sudo ln -s /opt/homebrew/opt/fontconfig/lib/libfontconfig.1.dylib /usr/local/lib/fontconfig-1
sudo ln -s /opt/homebrew/opt/pango/lib/libpangoft2-1.0.dylib /usr/local/lib/pangoft2-1.0
```

Tilesets are created using `tippecanoe` (installed via homebrew) or
[`rastertiler-rs`](https://github.com/brendan-ward/rastertiler-rs) built from
source. See [analysis/prep/tiles/README](./analysis/prep/tiles/README.md) for more information
