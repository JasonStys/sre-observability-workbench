"""Presentation-adapter unit tests with real core/SQLite workers; real widgets are separately frozen-tested. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: Variable — line 223
# definition: __init__ — line 226
# parameter: self — line 226
# parameter: value — line 226
# definition: get — line 230
# parameter: self — line 230
# definition: set — line 234
# parameter: self — line 234
# parameter: value — line 234
# variable: callback — line 237
# definition: trace_add — line 240
# parameter: _event — line 240
# parameter: callback — line 240
# parameter: self — line 240
# definition: Widget — line 245
# definition: __init__ — line 248
# parameter: _args — line 248
# parameter: kwargs — line 248
# parameter: self — line 248
# parameter: _items — line 252
# definition: pack — line 254
# parameter: _kwargs — line 254
# parameter: self — line 254
# definition: grid — line 257
# parameter: _kwargs — line 257
# parameter: self — line 257
# definition: grid_remove — line 260
# parameter: self — line 260
# definition: columnconfigure — line 263
# parameter: _args — line 263
# parameter: _kwargs — line 263
# parameter: self — line 263
# definition: add — line 266
# parameter: _args — line 266
# parameter: _kwargs — line 266
# parameter: self — line 266
# definition: theme_use — line 269
# parameter: _args — line 269
# parameter: self — line 269
# definition: configure — line 272
# parameter: _args — line 272
# parameter: kwargs — line 272
# parameter: self — line 272
# definition: heading — line 276
# parameter: _args — line 276
# parameter: _kwargs — line 276
# parameter: self — line 276
# definition: column — line 279
# parameter: _args — line 279
# parameter: _kwargs — line 279
# parameter: self — line 279
# definition: bind — line 282
# parameter: _args — line 282
# parameter: self — line 282
# definition: yview — line 285
# parameter: _args — line 285
# parameter: self — line 285
# definition: set — line 288
# parameter: _args — line 288
# parameter: self — line 288
# definition: state — line 291
# parameter: flags — line 291
# parameter: self — line 291
# variable: flag — line 293
# definition: invoke — line 299
# parameter: self — line 299
# definition: insert — line 305
# parameter: _parent — line 305
# parameter: _position — line 305
# parameter: iid — line 305
# parameter: self — line 305
# parameter: values — line 305
# definition: delete — line 309
# parameter: items — line 309
# parameter: self — line 309
# variable: item — line 311
# variable: item — line 313
# definition: get_children — line 315
# parameter: self — line 315
# definition: selection — line 319
# parameter: self — line 319
# definition: selection_set — line 323
# parameter: identity — line 323
# parameter: self — line 323
# definition: Text — line 329
# definition: delete — line 332
# parameter: _args — line 332
# parameter: self — line 332
# definition: insert — line 336
# parameter: _position — line 336
# parameter: self — line 336
# parameter: text — line 336
# definition: Root — line 341
# definition: __init__ — line 344
# parameter: self — line 344
# definition: title — line 349
# parameter: _args — line 349
# parameter: self — line 349
# definition: geometry — line 352
# parameter: _args — line 352
# parameter: self — line 352
# definition: minsize — line 355
# parameter: _args — line 355
# parameter: self — line 355
# definition: protocol — line 358
# parameter: _event — line 358
# parameter: callback — line 358
# parameter: self — line 358
# definition: after — line 362
# parameter: _delay — line 362
# parameter: callback — line 362
# parameter: self — line 362
# definition: destroy — line 366
# parameter: self — line 366
# definition: mainloop — line 370
# parameter: self — line 370
# variable: _ — line 374
# definition: presentation — line 382
# parameter: monkeypatch — line 382
# parameter: _parent — line 387
# variable: name — line 389
# variable: messages — line 403
# parameter: _kwargs — line 405
# parameter: args — line 405
# parameter: _kwargs — line 408
# parameter: args — line 408
# definition: app — line 414
# parameter: presentation — line 414
# parameter: tmp_path — line 414
# variable: state — line 416
# variable: root — line 417
# variable: window — line 418
# definition: thread_stacks — line 428
# variable: frames — line 430
# variable: lines — line 431
# variable: thread — line 432
# variable: frame — line 433
# variable: _ — line 435
# variable: frame — line 445
# definition: test_failure_diagnostics_observe_actual_blocked_thread_without_values — line 449
# variable: entered — line 451
# variable: release — line 451
# definition: blocked — line 453
# variable: private_local — line 455
# variable: thread — line 460
# variable: diagnostic — line 464
# definition: settle — line 475
# parameter: window — line 475
# variable: deadline — line 477
# definition: test_real_controller_run_filter_detail_history_export_and_help — line 484
# parameter: app — line 485
# parameter: monkeypatch — line 485
# parameter: presentation — line 485
# parameter: tmp_path — line 485
# parameter: _kwargs — line 511
# variable: original — line 513
# variable: exported — line 515
# variable: path — line 516
# parameter: _kwargs — line 521
# definition: test_explicit_retention_confirmation_removes_only_selected_local_copy — line 527
# parameter: app — line 528
# parameter: monkeypatch — line 528
# parameter: tmp_path — line 528
# variable: exported — line 538
# variable: original — line 539
# parameter: _args — line 540
# parameter: _kwargs — line 540
# parameter: _args — line 543
# parameter: _kwargs — line 543
# variable: path — line 546
# definition: test_input_selection_cancel_busy_failure_and_literal_row_cap — line 553
# parameter: app — line 554
# parameter: monkeypatch — line 554
# parameter: tmp_path — line 554
# variable: name — line 557
# parameter: _kwargs — line 561
# parameter: _kwargs — line 566
# parameter: _kwargs — line 569
# variable: kind — line 571
# variable: value — line 575
# parameter: _kwargs — line 576
# variable: index — line 592
# definition: test_close_retains_lock_until_actual_core_transaction_finishes — line 604
# parameter: app — line 605
# parameter: monkeypatch — line 605
# parameter: tmp_path — line 605
# variable: ready — line 608
# variable: release — line 608
# variable: actual — line 609
# definition: pause — line 611
# parameter: args — line 611
# variable: reopened — line 629
# definition: test_main_native_close_and_rejected_acceptance_paths — line 636
# parameter: monkeypatch — line 637
# parameter: presentation — line 637
# parameter: tmp_path — line 637
# variable: actual — line 640
# definition: create — line 642
# parameter: root — line 642
# parameter: state — line 642
# variable: window — line 644
# variable: profile — line 649
# variable: reopened — line 651
# variable: unknown — line 675
# END CODE MAP

import sys
import threading
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from sre import desktop as module
from sre import desktop_project as project
from sre.desktop_io import Rejected
from sre.desktop_state import Workspace


class Variable:
    """Inert presentation variable; invokes the same registered GUI trace callbacks."""

    def __init__(self, value=""):
        """Keep a scalar control value and registered change callbacks."""
        self.value, self.callbacks = value, []

    def get(self):
        """Return the current presentation control value."""
        return self.value

    def set(self, value):
        """Change a control and exercise actual application rendering callbacks."""
        self.value = value
        for callback in self.callbacks:
            callback()

    def trace_add(self, _event, callback):
        """Retain the GUI's value-change handler."""
        self.callbacks.append(callback)


class Widget:
    """Minimal inert ttk presentation adapter; no core, storage or analysis output is mocked."""

    def __init__(self, *_args, **kwargs):
        """Retain properties, rows and command closures."""
        self.options, self.rows, self.selected = kwargs, {}, ()
        self.flags = set()
        self.tk = SimpleNamespace(call=lambda *_items: None)

    def pack(self, **_kwargs):
        """Accept presentation layout."""

    def grid(self, **_kwargs):
        """Accept presentation grid coordinates."""

    def grid_remove(self):
        """Accept operation-specific hidden controls."""

    def columnconfigure(self, *_args, **_kwargs):
        """Accept resize weights."""

    def add(self, *_args, **_kwargs):
        """Accept notebook/paned-window children."""

    def theme_use(self, *_args):
        """Accept native style selection."""

    def configure(self, *_args, **kwargs):
        """Retain updated widget options."""
        self.options.update(kwargs)

    def heading(self, *_args, **_kwargs):
        """Accept a literal table heading."""

    def column(self, *_args, **_kwargs):
        """Accept table sizing."""

    def bind(self, *_args):
        """Accept event registration; tests invoke actual handlers explicitly."""

    def yview(self, *_args):
        """Accept scroll requests."""

    def set(self, *_args):
        """Accept scrollbar position updates."""

    def state(self, flags):
        """Preserve disabled controls so a simulated click cannot bypass a busy guard."""
        for flag in flags:
            if flag.startswith("!"):
                self.flags.discard(flag[1:])
            else:
                self.flags.add(flag)

    def invoke(self):
        """Invoke the actual registered command unless the control is disabled."""
        if "disabled" not in self.flags:
            return self.options["command"]()
        return None

    def insert(self, _parent, _position, *, iid, values):
        """Retain exact rows inserted by real project rendering."""
        self.rows[iid] = values

    def delete(self, *items):
        """Remove rows and their selections like a real treeview."""
        for item in items:
            self.rows.pop(item, None)
        self.selected = tuple(item for item in self.selected if item in self.rows)

    def get_children(self):
        """Return displayed row identities."""
        return tuple(self.rows)

    def selection(self):
        """Return the current selected row identity."""
        return self.selected

    def selection_set(self, identity):
        """Select one existing row like a real single-selection control."""
        assert identity in self.rows
        self.selected = (identity,)


class Text(Widget):
    """Retain literal detail output without interpreting markup or executing event fields."""

    def delete(self, *_args):
        """Clear existing literal detail text."""
        self.text = ""

    def insert(self, _position, text):
        """Retain the exact rendered detail text."""
        self.text = text


class Root:
    """Deterministic presentation event queue; actual Tk mainloops are independently exercised by frozen acceptance."""

    def __init__(self):
        """Create a fresh owned presentation root."""
        self.callbacks, self.destroyed = [], False
        self.on_loop = None

    def title(self, *_args):
        """Accept window title."""

    def geometry(self, *_args):
        """Accept initial geometry."""

    def minsize(self, *_args):
        """Accept minimum geometry."""

    def protocol(self, _event, callback):
        """Keep the application's native close callback."""
        self.close_callback = callback

    def after(self, _delay, callback):
        """Queue the actual lifecycle callback without a platform display server."""
        self.callbacks.append(callback)

    def destroy(self):
        """Mark only this owned root as closed."""
        self.destroyed = True

    def mainloop(self):
        """Run the requested test lifecycle using real application callbacks."""
        if self.on_loop:
            self.on_loop()
        for _ in range(200):
            if self.destroyed:
                return
            self.callbacks.pop(0)()
        raise AssertionError("presentation lifecycle did not close")


@pytest.fixture
def presentation(monkeypatch):
    """Replace only OS presentation surfaces; real worker, core, SQLite and export code remain active."""
    monkeypatch.setattr(module.tk, "StringVar", Variable)
    monkeypatch.setattr(module.tk, "BooleanVar", Variable)
    monkeypatch.setattr(module.tk, "Tk", Root)
    monkeypatch.setattr(module.tk, "Toplevel", lambda _parent: Root())
    monkeypatch.setattr(module.tk, "Text", Text)
    for name in (
        "Frame",
        "Label",
        "Notebook",
        "Combobox",
        "Entry",
        "Button",
        "Checkbutton",
        "Panedwindow",
        "Treeview",
        "Scrollbar",
        "Style",
    ):
        monkeypatch.setattr(module.ttk, name, Widget)
    messages = []
    monkeypatch.setattr(
        module.messagebox, "showinfo", lambda *args, **_kwargs: messages.append(args)
    )
    monkeypatch.setattr(
        module.messagebox, "showerror", lambda *args, **_kwargs: messages.append(args)
    )
    return messages


@pytest.fixture
def app(tmp_path, presentation):
    """Build the actual workbench controller against an isolated real durable workspace."""
    state = Workspace(tmp_path / "profile", project.PRODUCT, project.ROOT)
    root = Root()
    window = module.Workbench(root, state)
    try:
        yield window
    finally:
        if window.worker_thread:
            window.worker_thread.join(10)
            assert not window.worker_thread.is_alive(), thread_stacks()
        state.close()


def thread_stacks():
    """Bound failure diagnostics to static frame identity; never include arguments, locals or evidence bytes."""
    frames = sys._current_frames()
    lines = []
    for thread in threading.enumerate()[:16]:
        frame = frames.get(thread.ident)
        lines.append("thread=" + thread.name[:80])
        for _ in range(24):
            if frame is None:
                break
            lines.append(
                Path(frame.f_code.co_filename).name
                + ":"
                + str(frame.f_lineno)
                + ":"
                + frame.f_code.co_name
            )
            frame = frame.f_back
    return "\n".join(lines)[:8192]


def test_failure_diagnostics_observe_actual_blocked_thread_without_values():
    """An owned inert thread proves failure diagnostics retain its frame but not raw local data."""
    entered, release = threading.Event(), threading.Event()

    def blocked():
        """Wait only for this test's explicit cleanup; do not acquire files, sockets or external state."""
        private_local = "synthetic-sentinel-must-not-enter-diagnostics"
        assert private_local
        entered.set()
        release.wait(2)

    thread = threading.Thread(target=blocked, name="owned-diagnostic-control")
    thread.start()
    try:
        assert entered.wait(1)
        diagnostic = thread_stacks()
        assert len(diagnostic) <= 8192
        assert "owned-diagnostic-control" in diagnostic
        assert "test_desktop_gui.py" in diagnostic
        assert "synthetic-sentinel" not in diagnostic
    finally:
        release.set()
        thread.join(2)
        assert not thread.is_alive()


def settle(window):
    """Observe completion of one actual owned analysis; no retries or invented report values."""
    deadline = time.monotonic() + 10
    while window.busy and time.monotonic() < deadline:
        window.poll()
        time.sleep(0.005)
    assert not window.busy, thread_stacks()


def test_real_controller_run_filter_detail_history_export_and_help(
    app, tmp_path, monkeypatch, presentation
):
    """Real core results drive controls, literal filters, exact private exports and history reopening."""
    app.export()
    assert "completed" in app.status.get()
    app.run_button.invoke()
    assert not app.busy and app.state.history() == []
    app.authorized.set(True)
    app.run_button.invoke()
    settle(app)
    assert app.selected_run == 1 and len(app.state.history()) == 1
    assert len(app.table.get_children()) > 0
    app.table.selection_set("0")
    app.inspect()
    assert "{" in app.details.text
    app.review_selected()
    if project.REVIEW_MODE is not None:
        assert app.mode.get() == project.REVIEW_MODE and app.authorized.get() is False
    app.search.set("not-a-supported-record-never-present")
    assert app.table.get_children() == ()
    app.inspect()
    app.search.set("")
    app.history_table.selection_set("1")
    app.open_button.invoke()
    assert "without re-running" in app.status.get()
    monkeypatch.setattr(
        module.filedialog, "askdirectory", lambda **_kwargs: str(tmp_path)
    )
    original = app.state.files(1)
    app.export_button.invoke()
    exported = next(tmp_path.glob(project.PRODUCT + "-run-*"))
    assert {path.name: path.read_bytes() for path in exported.iterdir()} == original
    app.help()
    assert "plaintext" in presentation[-1][1]
    app.licenses()
    monkeypatch.setattr(
        module.filedialog, "askdirectory", lambda **_kwargs: str(tmp_path / "missing")
    )
    app.export()
    assert "unavailable" in app.status.get()


def test_explicit_retention_confirmation_removes_only_selected_local_copy(
    app, tmp_path, monkeypatch
):
    """Cancellation preserves data; confirmation deletes one exact DB bundle without touching a prior export."""
    app.remove_history()
    assert "Select" in app.status.get()
    app.review_selected()
    app.authorized.set(True)
    app.run_button.invoke()
    settle(app)
    app.history_table.selection_set("1")
    exported = app.state.export(1, tmp_path, project.PRODUCT)
    original = app.state.files(1)
    monkeypatch.setattr(module.messagebox, "askyesno", lambda *_args, **_kwargs: False)
    app.remove_button.invoke()
    assert app.state.files(1) == original
    monkeypatch.setattr(module.messagebox, "askyesno", lambda *_args, **_kwargs: True)
    app.remove_button.invoke()
    assert app.state.history() == [] and app.selected_run == 0
    assert {path.name: path.read_bytes() for path in exported.iterdir()} == original
    app.busy = True
    app.remove_history()
    assert "Wait" in app.status.get()
    app.busy = False


def test_input_selection_cancel_busy_failure_and_literal_row_cap(
    app, tmp_path, monkeypatch
):
    """Operator mistakes do not silently run a prepared fixture, overwrite results or defeat close semantics."""
    name = project.FIELDS[0][0]
    monkeypatch.setattr(
        module.filedialog,
        "askopenfilename",
        lambda **_kwargs: str(tmp_path / "authorized.json"),
    )
    monkeypatch.setattr(
        module.filedialog,
        "askopenfilenames",
        lambda **_kwargs: ("one.json", "two.json"),
    )
    monkeypatch.setattr(
        module.filedialog, "askdirectory", lambda **_kwargs: str(tmp_path)
    )
    for kind in ("file", "files", "directory"):
        app.authorized.set(True)
        app.choose(name, kind)
        assert app.authorized.get() is False
    value = app.values[name].get()
    monkeypatch.setattr(module.filedialog, "askopenfilename", lambda **_kwargs: "")
    app.choose(name, "file")
    assert app.values[name].get() == value
    app.busy = True
    app.choose(name, "file")
    app.load_prepared()
    app.open_history()
    app.run()
    assert app.state.history() == []
    app.busy = False
    app.load_prepared()
    app.mode.set("unsupported-operation")
    app.authorized.set(True)
    app.run()
    settle(app)
    assert "rejected" in app.status.get().lower() and app.state.history() == []
    app.current = {"bounded": [{"event": str(index)} for index in range(5001)]}
    app.view.set("bounded")
    app.render()
    assert len(app.table.get_children()) == 5000
    app.search.set('"5000"')
    assert len(app.table.get_children()) == 1
    app.exit()
    app.run()
    app.poll()
    assert app.root.destroyed and app.state.lock == -1


def test_close_retains_lock_until_actual_core_transaction_finishes(
    app, tmp_path, monkeypatch
):
    """An in-flight real analysis is drained rather than abandoned, force-killed or exposed to a second owner."""
    ready, release = threading.Event(), threading.Event()
    actual = project.analyze

    def pause(*args):
        """Control only scheduling; completion still invokes the actual project core and durable output."""
        ready.set()
        assert release.wait(5)
        return actual(*args)

    monkeypatch.setattr(project, "analyze", pause)
    app.authorized.set(True)
    app.run_button.invoke()
    assert ready.wait(3)
    app.exit()
    app.poll()
    assert not app.root.destroyed and app.busy
    with pytest.raises((Rejected, OSError)):
        Workspace(app.state.path, project.PRODUCT, project.ROOT)
    release.set()
    settle(app)
    assert app.root.destroyed and app.state.lock == -1
    reopened = Workspace(app.state.path, project.PRODUCT, project.ROOT)
    try:
        assert len(reopened.history()) == 1
    finally:
        reopened.close()


def test_main_native_close_and_rejected_acceptance_paths(
    tmp_path, presentation, monkeypatch
):
    """Normal startup never auto-analyzes; test flags cannot enter existing real-profile state or claim partial success."""
    actual = module.Workbench

    def create(root, state):
        """Use actual controls/controller; request the normal close callback at the start of the event loop."""
        window = actual(root, state)
        root.on_loop = window.exit
        return window

    monkeypatch.setattr(module, "Workbench", create)
    profile = tmp_path / "normal"
    assert module.main(["--profile", str(profile)]) == 0
    reopened = Workspace(profile, project.PRODUCT, project.ROOT)
    assert reopened.history() == []
    reopened.close()
    with pytest.raises(SystemExit):
        module.main(["--acceptance-output", str(tmp_path / "output")])
    with pytest.raises(SystemExit):
        module.main(["--acceptance-reopen"])
    assert (
        module.main(
            ["--profile", str(profile), "--acceptance-output", str(tmp_path / "output")]
        )
        == 2
    )
    assert (
        module.main(
            [
                "--profile",
                str(tmp_path / "synthetic"),
                "--acceptance-output",
                str(tmp_path / "new-output"),
            ]
        )
        == 2
    )
    unknown = tmp_path / "unknown"
    unknown.mkdir()
    (unknown / "keep").write_bytes(b"unchanged")
    assert module.main(["--profile", str(unknown)]) == 2
    assert (unknown / "keep").read_bytes() == b"unchanged"
    assert presentation and "No saved evidence was reset" in presentation[-1][1]
