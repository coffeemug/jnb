# jnb

Open a Jupyter notebook as its own self-contained process, with a minimal UI.

```sh
jnb              # new scratch notebook, e.g. ~/py_notebooks/scratch-Sep-27-2026.ipynb
jnb file.ipynb   # open file.ipynb, creating it in the current directory if needed
```

- Each `jnb` runs its own server, which exits a few seconds after you close the tab.
- The kernel uses the uv project you run `jnb` from, with Jupyter layered on top
  (the project's own dependencies aren't changed). Outside a project it uses the
  scratch directory's project if it has one, and a bare environment otherwise.
- New notebooks open with the cursor in the first cell.
- No top bar, autosave every 5 seconds, one Ctrl-C shuts the server down.
- Jupyter settings come only from this repo's `jupyter/` folder, so your global
  `~/.jupyter` isn't used or modified.

## Install

Requires [uv](https://docs.astral.sh/uv/).

```sh
git clone <this repo> ~/jnb
~/jnb/install.sh      # symlinks jnb into ~/.local/bin
```

To remove it, run `~/jnb/uninstall.sh`, then delete the repo.

## Configuration

- `JNB_SCRATCH_DIR`: where plain `jnb` puts new notebooks (default `~/py_notebooks`).
  Make it a uv project (`uv init --bare`) and `uv add` packages to have them
  available in notebooks opened outside any project.
- `JNB_BIN_DIR`: where `install.sh` puts the `jnb` link (default `~/.local/bin`).

## Files

- `bin/jnb`: the command.
- `ext/jnb_watch.py`: server extension that shuts the server down when the tab
  closes and focuses the first cell of a new notebook.
- `jupyter/`: Jupyter config and UI settings used by `jnb`.
- `requirements.txt`: the Jupyter packages layered onto each environment.
