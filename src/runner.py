"""
runner.py
=========
SimulationRunner — executes the OpenModelica model executable
in a background QThread and communicates results back to the UI
via Qt signals (no blocking of the main thread).
"""

from __future__ import annotations

import subprocess
import time
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal

from src.config import SimulationConfig


class SimulationRunner(QThread):
    """
    Background thread that executes the compiled OpenModelica executable.

    Signals:
        simulation_started  : Emitted when the process starts.
        log_line (str)      : Emitted for each line of stdout/stderr output.
        simulation_finished : Emitted with (return_code, elapsed_seconds).
        simulation_error    : Emitted with an error message string on failure.
    """

    simulation_started: pyqtSignal = pyqtSignal()
    log_line: pyqtSignal = pyqtSignal(str)
    simulation_finished: pyqtSignal = pyqtSignal(int, float)
    simulation_error: pyqtSignal = pyqtSignal(str)

    def __init__(self, config: SimulationConfig, parent=None) -> None:
        """
        Args:
            config : Validated SimulationConfig instance.
            parent : Optional Qt parent object.
        """
        super().__init__(parent)
        self._config: SimulationConfig = config
        self._process: Optional[subprocess.Popen] = None

    def run(self) -> None:
        """
        Execute the simulation process in the background thread.
        Streams stdout/stderr line-by-line via log_line signal.
        Guaranteed to emit either simulation_finished or simulation_error.
        """
        self.simulation_started.emit()
        args = self._config.to_cli_args()
        start_ts = time.monotonic()

        self.log_line.emit(f"▶  Launching: {' '.join(args)}")
        self.log_line.emit("─" * 60)

        try:
            self._process = subprocess.Popen(
                args,                        # list — never shell=True
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,    # merge stderr into stdout
                text=True,
                bufsize=1,                   # line-buffered
            )

            if self._process.stdout is None:
                self.simulation_error.emit("Failed to open stdout pipe.")
                return

            for line in self._process.stdout:
                self.log_line.emit(line.rstrip())

            self._process.wait()
            elapsed = time.monotonic() - start_ts
            return_code = self._process.returncode

            self.log_line.emit("─" * 60)
            self.log_line.emit(
                f"✔  Process exited with code {return_code} "
                f"in {elapsed:.2f}s"
            )
            self.simulation_finished.emit(return_code, elapsed)

        except FileNotFoundError:
            self.simulation_error.emit(
                f"Executable not found at runtime:\n{self._config.executable_path}"
            )
        except PermissionError:
            self.simulation_error.emit(
                f"Permission denied when running:\n{self._config.executable_path}"
            )
        except OSError as exc:
            self.simulation_error.emit(f"OS error during simulation:\n{exc}")

    def abort(self) -> None:
        """
        Forcefully terminate the running simulation process.
        Tries SIGTERM first, escalates to SIGKILL if process survives.
        Safe to call even if no process is running.
        """
        if self._process and self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                # SIGTERM ignored — force kill
                self._process.kill()
                self.log_line.emit("⚠  Process force-killed (SIGKILL).")
                return
            self.log_line.emit("⚠  Simulation aborted by user.")
