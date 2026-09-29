"""Jupyter server extension loaded by `jnb`:

- shut the server down as soon as its notebook tab is closed, so each `jnb`
  run is one self-contained process;
- on a brand-new notebook (a single empty cell), put the cursor in that cell;
- open the browser straight at the notebook, not the file browser.
"""

import os
import time

from jupyter_server.utils import url_escape, url_path_join
from tornado.ioloop import PeriodicCallback
from tornado.web import OutputTransform

GRACE = 3  # seconds with no tab connected before exiting (survives a page reload)
STARTUP = 120  # exit if no tab ever connects

FOCUS_SCRIPT = b"""<script>
(async () => {
  const until = async (f, ms = 20000) => {
    const t = Date.now(); let v;
    while (!(v = f()) && Date.now() - t < ms) await new Promise(r => setTimeout(r, 50));
    return v;
  };
  const app = await until(() => window.jupyterapp);
  const panel = await until(() => app?.shell.currentWidget?.content?.widgets && app.shell.currentWidget);
  if (!panel) return;
  await panel.context.ready;
  await panel.revealed;
  const nb = panel.content;
  if (nb.widgets.length !== 1 || nb.widgets[0].model.sharedModel.getSource() !== "") return;
  await until(() => nb.widgets[0].editor);
  const focus = () => {
    nb.activeCellIndex = 0;
    nb.mode = "edit";
    nb.widgets[0].editor.focus();
  };
  focus();
  // opened straight from the OS, the page can be ready before the browser
  // window is active, and activating the window takes focus off the cell
  if (!document.hasFocus()) window.addEventListener("focus", () => setTimeout(focus), {once: true});
})();
</script>"""


class _InjectFocusScript(OutputTransform):
    def __init__(self, request):
        self._active = request.path.startswith("/notebooks/")

    def transform_first_chunk(self, status_code, headers, chunk, finishing):
        if self._active and finishing and b"</body>" in chunk:
            chunk = chunk.replace(b"</body>", FOCUS_SCRIPT + b"</body>", 1)
            if "Content-Length" in headers:
                headers["Content-Length"] = str(len(chunk))
        return status_code, headers, chunk


def _jupyter_server_extension_points():
    return [{"module": "jnb_watch"}]


def _load_jupyter_server_extension(serverapp):
    serverapp.web_app.transforms.append(_InjectFocusScript)

    # with use_redirect_file off, Jupyter opens default_url and ignores the file
    # it was given, so make the notebook itself the default url
    if serverapp.file_to_run:
        rel = os.path.relpath(os.path.abspath(serverapp.file_to_run), serverapp.root_dir)
        serverapp.default_url = url_path_join(
            serverapp.base_url, "notebooks", url_escape(url_path_join(*rel.split(os.sep)))
        )

    started = time.monotonic()
    last_connected = None

    def check():
        nonlocal last_connected
        now = time.monotonic()
        if any(k["connections"] for k in serverapp.kernel_manager.list_kernels()):
            last_connected = now
            return
        if last_connected is None and now - started < STARTUP:
            return
        if last_connected is None or now - last_connected > GRACE:
            serverapp.log.info("jnb: notebook tab closed; shutting down.")
            pc.stop()
            serverapp.stop()

    pc = PeriodicCallback(check, 500)
    pc.start()
