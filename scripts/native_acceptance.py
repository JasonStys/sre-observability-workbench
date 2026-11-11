"""Exercise the same real frozen Tk controls/core on an explicit synthetic profile; no arbitrary scripts. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: capture — line 92
# parameter: target — line 92
# parameter: window — line 92
# variable: load — line 98
# variable: gdi — line 99
# variable: user — line 99
# variable: pointer — line 100
# variable: arguments — line 101
# variable: library — line 101
# variable: name — line 101
# variable: result — line 101
# variable: function — line 127
# variable: handle — line 130
# variable: rectangle — line 131
# variable: height — line 134
# variable: width — line 134
# variable: source — line 137
# variable: destination — line 138
# variable: bitmap — line 139
# variable: previous — line 140
# variable: pixels — line 145
# variable: header — line 146
# variable: raw — line 164
# variable: scanlines — line 165
# variable: row — line 166
# variable: column — line 168
# variable: offset — line 169
# definition: chunk — line 172
# parameter: data — line 172
# parameter: name — line 172
# definition: exercise — line 194
# parameter: output — line 194
# parameter: reopen — line 194
# parameter: window — line 194
# variable: deadline — line 197
# variable: receipt — line 198
# definition: finish — line 218
# parameter: error — line 218
# variable: data — line 225
# variable: name — line 225
# variable: row — line 227
# definition: checked — line 234
# parameter: callback — line 234
# definition: wait — line 243
# parameter: callback — line 243
# definition: drilled — line 253
# variable: files — line 255
# variable: evidence — line 256
# variable: report — line 256
# definition: assessed — line 279
# variable: report — line 281
# definition: journeys — line 298
# variable: report — line 300
# variable: row — line 304
# definition: compared — line 319
# variable: report — line 321
# variable: row — line 322
# variable: parent — line 330
# variable: exported — line 334
# variable: path — line 336
# definition: rejected — line 343
# definition: layout — line 352
# variable: original — line 354
# variable: button — line 377
# variable: name — line 377
# variable: button — line 387
# definition: begin — line 405
# END CODE MAP

from __future__ import annotations

import ctypes
import hashlib
import json
import os
import struct
import sys
import time
import zlib
from pathlib import Path
from typing import TYPE_CHECKING, Any

from sre import desktop_project as project
from sre.desktop_io import json_value

if TYPE_CHECKING:
    from sre.desktop import Workbench


def capture(window: Workbench, target: Path) -> None:
    """Capture only this owned synthetic Tk window via PrintWindow, never the user's whole desktop."""
    if sys.platform != "win32":
        raise OSError("native screenshot acceptance targets Windows")
    from ctypes import wintypes

    load = ctypes.WinDLL
    user, gdi = load("user32", use_last_error=True), load("gdi32", use_last_error=True)
    pointer = ctypes.c_void_p
    for library, name, arguments, result in [
        (user, "GetAncestor", [pointer, ctypes.c_uint], pointer),
        (user, "GetWindowDC", [pointer], pointer),
        (gdi, "CreateCompatibleDC", [pointer], pointer),
        (gdi, "CreateCompatibleBitmap", [pointer, ctypes.c_int, ctypes.c_int], pointer),
        (gdi, "SelectObject", [pointer, pointer], pointer),
        (gdi, "DeleteObject", [pointer], ctypes.c_int),
        (gdi, "DeleteDC", [pointer], ctypes.c_int),
        (user, "ReleaseDC", [pointer, pointer], ctypes.c_int),
        (user, "PrintWindow", [pointer, pointer, ctypes.c_uint], ctypes.c_int),
        (user, "GetWindowRect", [pointer, ctypes.POINTER(wintypes.RECT)], ctypes.c_int),
        (
            gdi,
            "GetDIBits",
            [
                pointer,
                pointer,
                ctypes.c_uint,
                ctypes.c_uint,
                pointer,
                pointer,
                ctypes.c_uint,
            ],
            ctypes.c_int,
        ),
    ]:
        function = getattr(library, name)
        function.argtypes, function.restype = arguments, result
    window.root.update_idletasks()
    handle = user.GetAncestor(window.root.winfo_id(), 2)
    rectangle = wintypes.RECT()
    if not user.GetWindowRect(handle, ctypes.byref(rectangle)):
        raise OSError("owned window bounds unavailable")
    width, height = rectangle.right - rectangle.left, rectangle.bottom - rectangle.top
    if not 1 <= width <= 4096 or not 1 <= height <= 4096:
        raise OSError("owned screenshot outside bounded dimensions")
    source = user.GetWindowDC(handle)
    destination = gdi.CreateCompatibleDC(source)
    bitmap = gdi.CreateCompatibleBitmap(source, width, height)
    previous = gdi.SelectObject(destination, bitmap)
    try:
        if not user.PrintWindow(handle, destination, 2):
            raise OSError("owned window rendering unavailable")
        gdi.SelectObject(destination, previous)
        pixels = ctypes.create_string_buffer(width * height * 4)
        header = ctypes.create_string_buffer(
            struct.pack(
                "<IiiHHIIiiII",
                40,
                width,
                -height,
                1,
                32,
                0,
                width * height * 4,
                0,
                0,
                0,
                0,
            )
        )
        if gdi.GetDIBits(source, bitmap, 0, height, pixels, header, 0) != height:
            raise OSError("owned screenshot pixels incomplete")
        raw = pixels.raw
        scanlines = bytearray()
        for row in range(height):
            scanlines.append(0)
            for column in range(width):
                offset = (row * width + column) * 4
                scanlines.extend((raw[offset + 2], raw[offset + 1], raw[offset]))

        def chunk(name: bytes, data: bytes) -> bytes:
            """Encode a bounded standard PNG chunk with its actual CRC."""
            return (
                struct.pack(">I", len(data))
                + name
                + data
                + struct.pack(">I", zlib.crc32(name + data))
            )

        target.write_bytes(
            b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(scanlines)))
            + chunk(b"IEND", b"")
        )
    finally:
        gdi.SelectObject(destination, previous)
        gdi.DeleteObject(bitmap)
        gdi.DeleteDC(destination)
        user.ReleaseDC(handle, source)


def exercise(window: Workbench, output: Path, reopen: bool) -> None:
    """Drive the actual project widgets, real core and private state with independent domain oracles."""
    output.mkdir(mode=0o700)
    deadline = time.monotonic() + 55
    receipt: dict[str, Any] = {
        "schema": 1,
        "product": project.PRODUCT,
        "version": project.VERSION,
        **window.identity,
        "pid": os.getpid(),
        "parent_pid": os.getppid(),
        "synthetic": True,
        "reopen": reopen,
        "passed": False,
        "steps": [],
    }

    (output / "acceptance.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
    )

    receipt["tcl_version"] = window.root.tk.call("info", "patchlevel")
    receipt["tk_version"] = window.root.tk.call("package", "require", "Tk")

    def finish(error: bool = False) -> None:
        """Record only synthetic aggregate/hash evidence and request the ordinary graceful exit."""
        receipt["passed"] = not error
        window.acceptance_result = not error
        receipt["bundles"] = {
            str(row["id"]): {
                name: hashlib.sha256(data).hexdigest()
                for name, data in window.state.files(row["id"]).items()
            }
            for row in window.state.history()
        }
        (output / "acceptance.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )
        window.exit()

    def checked(callback: Any) -> None:
        """A failed oracle remains a failed receipt; original data is not replaced by a sample or reset."""
        try:
            callback()
        except Exception:
            receipt["failure"] = "native acceptance assertion or operation failed"
            receipt["failure_stage"] = callback.__name__
            finish(True)

    def wait(callback: Any) -> None:
        """Wait for this owned real operation without retries, collector access or forced shutdown."""
        if time.monotonic() > deadline:
            receipt["failure"] = "owned operation deadline exceeded"
            finish(True)
        elif window.busy:
            window.root.after(60, lambda: wait(callback))
        else:
            checked(callback)

    def drilled() -> None:
        """Require real finite faults and all actual gateway/worker chains, rather than trusting a rendered banner."""
        files = window.state.files(1)
        report, evidence = (
            json_value(files["assessment.json"]),
            json_value(files["drill.json"]),
        )
        assert (
            report["availability"]["requests"] == 40
            and report["availability"]["bad"] == 4
        )
        assert evidence["service_spans"] == 120 and evidence["service_logs"] == 80
        assert evidence["correlated_attempts"] == 40 and evidence["evidence_gaps"] == []
        window.table.selection_set("0")
        window.inspect()
        layout()
        capture(window, output / "fault-recovery-budget.png")
        receipt["steps"].append(
            "real-owned-loopback-faults-120-sdk-spans-40-verified-chains"
        )
        window.prepared.set(project.SCENARIOS[1])
        window.load_prepared()
        window.authorized.set(True)
        window.run_button.invoke()
        wait(assessed)

    def assessed() -> None:
        """Independently authored checkout evidence has two slow successes and no HTTP failures."""
        report = json_value(window.state.files(2)["assessment.json"])
        assert report["availability"]["bad"] == 0 and report["latency"]["bad"] == 2
        assert (
            report["percentiles"]["p95_us"] == 80000
            and report["quality"] == "COMPLETE_ASSERTED"
        )
        window.view.set("Actual request attempts")
        window.search.set('"duration_us": 80000')
        window.render()
        assert len(window.table.get_children()) == 2
        receipt["steps"].append("real-custom-evidence-slow-success-filter")
        window.prepared.set(project.SCENARIOS[2])
        window.load_prepared()
        window.authorized.set(True)
        window.run_button.invoke()
        wait(journeys)

    def journeys() -> None:
        """Disjoint service journeys retain their own owner/denominators and explicitly flag objective loosening."""
        report = json_value(window.state.files(3)["journeys.json"])
        assert report["stream_count"] == 2 and report["total_input_events"] == 40
        assert len(report["review_queue"]) == 2
        assert all(
            "objective_loosened" in row["reasons"] for row in report["review_queue"]
        )
        window.view.set("Owner review queue")
        window.search.set("")
        window.render()
        window.table.selection_set("0")
        window.inspect()
        capture(window, output / "journey-owner-review.png")
        receipt["steps"].append("real-independent-journey-owner-review")
        window.prepared.set(project.SCENARIOS[3])
        window.load_prepared()
        window.authorized.set(True)
        window.run_button.invoke()
        wait(compared)

    def compared() -> None:
        """The same records improve only under a looser latency objective; exact export preserves that caveat."""
        report = json_value(window.state.files(4)["journeys.json"])
        row = report["streams"][0]
        assert (
            row["baseline"]["latency"]["bad"] == 2
            and row["candidate"]["latency"]["bad"] == 0
        )
        assert row["loosened_thresholds"] == ["latency_us"]
        from unittest.mock import patch

        parent = output / "private-export"
        parent.mkdir()
        with patch("tkinter.filedialog.askdirectory", return_value=str(parent)):
            window.export_button.invoke()
        exported = next(parent.iterdir())
        assert {
            path.name: path.read_bytes() for path in exported.iterdir()
        } == window.state.files(4)
        window.values["target_ppm"].set("NaN")
        window.authorized.set(True)
        window.run_button.invoke()
        wait(rejected)

    def rejected() -> None:
        """Malformed objective units must not be coerced or replace a prior saved analysis."""
        assert (
            len(window.state.history()) == 4
            and "rejected" in window.status.get().lower()
        )
        receipt["steps"].append("exact-export-and-malformed-objective-retains-evidence")
        finish()

    def layout() -> None:
        """Real minimum-width layout keeps every lifecycle control fully visible even with long status text."""
        original = window.status.get()
        window.root.geometry("980x700")
        window.status.set(
            original
            + " Synthetic long-message layout check: existing evidence remains available and Exit waits for the owned operation."
        )
        window.root.update()
        receipt["layout"] = {
            "root": [window.root.winfo_width(), window.root.winfo_height()],
            "status": [
                window.status_label.winfo_width(),
                window.status_label.winfo_height(),
                window.status_label.winfo_reqheight(),
                int(window.status_label.cget("wraplength")),
            ],
            "buttons": {
                name: [
                    button.winfo_width(),
                    button.winfo_reqwidth(),
                    button.winfo_rootx() - window.root.winfo_rootx(),
                    button.winfo_rooty() - window.root.winfo_rooty(),
                    button.winfo_height(),
                ]
                for name, button in window.footer_buttons.items()
            },
        }
        assert (
            int(window.status_label.cget("wraplength"))
            <= window.status_label.winfo_width()
        )
        assert (
            window.status_label.winfo_height() >= window.status_label.winfo_reqheight()
        )
        for button in window.footer_buttons.values():
            assert button.winfo_width() >= button.winfo_reqwidth()
            assert button.winfo_rootx() >= window.root.winfo_rootx()
            assert (
                button.winfo_rootx() + button.winfo_width()
                <= window.root.winfo_rootx() + window.root.winfo_width()
            )
            assert (
                button.winfo_rooty() + button.winfo_height()
                <= window.root.winfo_rooty() + window.root.winfo_height()
            )
        window.status.set(original)
        window.root.geometry("1260x860")
        window.root.update()
        receipt["steps"].append(
            "real-minimum-width-long-status-all-lifecycle-controls-visible"
        )

    def begin() -> None:
        """Exercise the same real permission/Run/history controls, never a separate fixed-report demo."""
        if reopen:
            assert len(window.state.history()) == 4
            window.history_table.selection_set("1")
            window.open_button.invoke()
            assert len(window.current["Real service spans"]) == 120
            window.history_table.selection_set("3")
            window.open_button.invoke()
            assert len(window.current["Owner review queue"]) == 2
            receipt["steps"].append("actual-process-reopen-four-exact-bundles")
            finish()
            return
        assert window.state.history() == []
        window.run_button.invoke()
        assert not window.busy and window.state.history() == []
        window.authorized.set(True)
        window.run_button.invoke()
        wait(drilled)

    checked(begin)
