"""
app.py
======
SimLauncherApp — the main QMainWindow.

Responsibilities:
    - Build and arrange the top-level layout
    - Own the input widgets (executable picker, start/stop time fields)
    - Coordinate SimulationConfig validation, SimulationRunner lifecycle,
      and ResultsPanel updates
    - Enforce the constraint: 0 <= start < stop < 5

Class hierarchy:
    SimLauncherApp (QMainWindow)
        ├── SimulationConfig      [src.config]
        ├── SimulationRunner      [src.runner]
        └── ResultsPanel          [src.results]
"""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from src.config import SimulationConfig
from src.results import ResultsPanel
from src.runner import SimulationRunner
from src.styles import (
    APP_STYLESHEET,
    INPUT_STYLE,
    LABEL_STYLE,
    PRIMARY_BUTTON_STYLE,
    SECONDARY_BUTTON_STYLE,
    ACCENT,
    TEXT_SECONDARY,
    BORDER,
    SURFACE,
)


class SimLauncherApp(QMainWindow):
    """
    Main application window for the OpenModelica Simulation Launcher.

    Provides a GUI to:
        1. Select a compiled OpenModelica model executable.
        2. Enter start and stop time parameters.
        3. Run the simulation and view live output.
        4. Abort a running simulation.

    Constraint enforced: 0 <= start_time < stop_time < 5
    """

    WINDOW_TITLE: str = "OpenModelica Simulation Launcher"
    MIN_WIDTH: int = 780
    MIN_HEIGHT: int = 620

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._runner: Optional[SimulationRunner] = None
        self._build_ui()
        self._connect_signals()
        self._apply_styles()

    # ── UI Construction ───────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        """Construct the full window layout and all child widgets."""
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setMinimumSize(QSize(self.MIN_WIDTH, self.MIN_HEIGHT))
        self.resize(900, 680)

        # Central widget + root layout
        root_widget = QWidget()
        self.setCentralWidget(root_widget)
        root_layout = QVBoxLayout(root_widget)
        root_layout.setContentsMargins(20, 20, 20, 16)
        root_layout.setSpacing(16)

        # ── Header ────────────────────────────────────────────────────────
        root_layout.addWidget(self._build_header())

        # ── Divider ───────────────────────────────────────────────────────
        root_layout.addWidget(self._make_divider())

        # ── Input section ─────────────────────────────────────────────────
        root_layout.addWidget(self._build_input_section())

        # ── Divider ───────────────────────────────────────────────────────
        root_layout.addWidget(self._make_divider())

        # ── Results panel (expands to fill remaining space) ───────────────
        self._results_panel = ResultsPanel()
        root_layout.addWidget(self._results_panel, stretch=1)

        # ── Action buttons ────────────────────────────────────────────────
        root_layout.addWidget(self._build_action_bar())

        # ── Status bar ────────────────────────────────────────────────────
        self._status_bar = QStatusBar()
        self._status_bar.setStyleSheet(
            f"QStatusBar {{ color: {TEXT_SECONDARY}; font-size: 11px; "
            f"border-top: 1px solid {BORDER}; padding: 2px 8px; }}"
        )
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage("Ready — select an executable to begin.")

    def _build_header(self) -> QWidget:
        """Build the title + subtitle header block."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        title = QLabel("OpenModelica Simulation Launcher")
        title.setStyleSheet(
            "color: #e8e8ff; font-size: 20px; font-weight: bold; "
            "letter-spacing: 0.5px;"
        )

        subtitle = QLabel(
            "Run compiled OpenModelica model executables with custom time parameters."
        )
        subtitle.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        return container

    def _build_input_section(self) -> QWidget:
        """Build the three input fields: executable path, start time, stop time."""
        container = QWidget()
        container.setStyleSheet(f"background-color: {SURFACE}; border-radius: 6px;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        section_label = QLabel("SIMULATION PARAMETERS")
        section_label.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: 11px; "
            f"font-weight: bold; letter-spacing: 2px;"
        )
        layout.addWidget(section_label)

        # ── Field 1: Executable path ──────────────────────────────────────
        layout.addWidget(self._make_label("EXECUTABLE PATH"))
        exe_row = QHBoxLayout()
        self._exe_field = QLineEdit()
        self._exe_field.setPlaceholderText(
            "Select the compiled OpenModelica executable…"
        )
        self._exe_field.setToolTip(
            "Path to the compiled model executable "
            "(e.g. TwoConnectedTanks or TwoConnectedTanks.exe)"
        )
        self._exe_field.setStyleSheet(INPUT_STYLE)

        browse_btn = QPushButton("Browse…")
        browse_btn.setFixedWidth(90)
        browse_btn.setStyleSheet(SECONDARY_BUTTON_STYLE)
        browse_btn.setToolTip("Open file picker to choose the executable")
        browse_btn.clicked.connect(self._browse_executable)

        exe_row.addWidget(self._exe_field)
        exe_row.addWidget(browse_btn)
        layout.addLayout(exe_row)

        # ── Fields 2 & 3: Time parameters (side by side) ─────────────────
        time_row = QHBoxLayout()
        time_row.setSpacing(16)

        # Start time
        start_col = QVBoxLayout()
        start_col.setSpacing(6)
        start_col.addWidget(self._make_label("START TIME  (integer, ≥ 0)"))
        self._start_field = QLineEdit()
        self._start_field.setPlaceholderText("e.g. 0")
        self._start_field.setToolTip("Simulation start time — must be 0 or greater")
        self._start_field.setStyleSheet(INPUT_STYLE)
        start_col.addWidget(self._start_field)

        # Stop time
        stop_col = QVBoxLayout()
        stop_col.setSpacing(6)
        stop_col.addWidget(self._make_label("STOP TIME   (integer, < 5)"))
        self._stop_field = QLineEdit()
        self._stop_field.setPlaceholderText("e.g. 4")
        self._stop_field.setToolTip(
            "Simulation stop time — must be greater than start and less than 5"
        )
        self._stop_field.setStyleSheet(INPUT_STYLE)
        stop_col.addWidget(self._stop_field)

        time_row.addLayout(start_col)
        time_row.addLayout(stop_col)
        layout.addLayout(time_row)

        # Constraint hint
        hint = QLabel("⚠  Constraint:  0  ≤  start  <  stop  <  5")
        hint.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: 11px; "
            f"border: 1px solid {BORDER}; border-radius: 3px; "
            f"padding: 4px 8px;"
        )
        layout.addWidget(hint)

        return container

    def _build_action_bar(self) -> QWidget:
        """Build the Run / Abort button bar."""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        self._run_btn = QPushButton("▶  Run Simulation")
        self._run_btn.setFixedHeight(42)
        self._run_btn.setStyleSheet(PRIMARY_BUTTON_STYLE)
        self._run_btn.setToolTip("Validate inputs and start the simulation (Enter)")

        self._abort_btn = QPushButton("■  Abort")
        self._abort_btn.setFixedHeight(42)
        self._abort_btn.setFixedWidth(110)
        self._abort_btn.setEnabled(False)
        self._abort_btn.setStyleSheet(SECONDARY_BUTTON_STYLE)
        self._abort_btn.setToolTip("Terminate the running simulation")

        layout.addStretch()
        layout.addWidget(self._abort_btn)
        layout.addSpacing(8)
        layout.addWidget(self._run_btn)

        return container

    # ── Signal wiring ─────────────────────────────────────────────────────────

    def _connect_signals(self) -> None:
        """Wire all widget signals to their handler slots."""
        self._run_btn.clicked.connect(self._handle_run)
        self._abort_btn.clicked.connect(self._handle_abort)

        # Allow Enter key in time fields to trigger run
        self._start_field.returnPressed.connect(self._handle_run)
        self._stop_field.returnPressed.connect(self._handle_run)

        # Keyboard shortcut: Ctrl+R to run
        run_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        run_shortcut.activated.connect(self._handle_run)

    # ── Slot handlers ─────────────────────────────────────────────────────────

    def _browse_executable(self) -> None:
        """Open a file dialog so the user can pick the model executable."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select OpenModelica Executable",
            "",
            "All Files (*)",
        )
        if path:
            self._exe_field.setText(path)
            self._status_bar.showMessage(f"Executable selected: {path}")

    def _handle_run(self) -> None:
        """
        Validate inputs, build a SimulationConfig, and start the runner.
        Shows an error dialog if validation fails.
        """
        # Prevent double-start
        if self._runner and self._runner.isRunning():
            return

        config, error = SimulationConfig.from_inputs(
            executable_path=self._exe_field.text(),
            start_time_str=self._start_field.text(),
            stop_time_str=self._stop_field.text(),
        )

        if error:
            self._show_error("Invalid Input", error)
            return

        # config is guaranteed non-None when error is None
        if config is None:
            return

        # Disconnect previous runner signals to prevent double-firing on re-run
        if self._runner is not None:
            try:
                self._runner.simulation_started.disconnect()
                self._runner.log_line.disconnect()
                self._runner.simulation_finished.disconnect()
                self._runner.simulation_error.disconnect()
            except RuntimeError:
                pass  # already disconnected

        # Reset results panel and start simulation
        self._results_panel.clear_log()
        self._results_panel.append_line(f"Config loaded:\n{config}\n")

        self._runner = SimulationRunner(config, parent=self)
        self._runner.simulation_started.connect(self._on_simulation_started)
        self._runner.log_line.connect(self._results_panel.append_line)
        self._runner.simulation_finished.connect(self._on_simulation_finished)
        self._runner.simulation_error.connect(self._on_simulation_error)
        self._runner.start()

    def _handle_abort(self) -> None:
        """Abort the currently running simulation."""
        if self._runner:
            self._runner.abort()
            self._set_running_state(False)
            self._status_bar.showMessage("Simulation aborted.")
            self._results_panel.set_status("error")

    def closeEvent(self, event) -> None:
        """
        Handle window close gracefully.
        Aborts any running simulation and waits for the background
        thread to finish before exiting — prevents zombie threads.
        """
        if self._runner and self._runner.isRunning():
            self._runner.abort()
            self._runner.wait(3000)  # wait up to 3s
        event.accept()

    # ── Runner signal handlers ────────────────────────────────────────────────

    def _on_simulation_started(self) -> None:
        """Called when the simulation process starts."""
        self._set_running_state(True)
        self._results_panel.set_status("running")
        self._status_bar.showMessage("Simulation running…")

    def _on_simulation_finished(self, return_code: int, elapsed: float) -> None:
        """Called when the simulation process exits."""
        self._set_running_state(False)
        self._results_panel.set_elapsed(elapsed)

        if return_code == 0:
            self._results_panel.set_status("success")
            self._status_bar.showMessage(
                f"Simulation completed successfully in {elapsed:.2f}s."
            )
        else:
            self._results_panel.set_status("error")
            self._status_bar.showMessage(
                f"Simulation exited with code {return_code}."
            )

    def _on_simulation_error(self, message: str) -> None:
        """Called when a fatal error occurs in the runner."""
        self._set_running_state(False)
        self._results_panel.set_status("error")
        self._results_panel.append_line(f"\n✖  ERROR: {message}")
        self._status_bar.showMessage("Simulation failed — see output for details.")
        self._show_error("Simulation Error", message)

    # ── UI state helpers ──────────────────────────────────────────────────────

    def _set_running_state(self, is_running: bool) -> None:
        """
        Toggle the enabled/disabled state of inputs and buttons.

        Args:
            is_running : True while a simulation is in progress.
        """
        self._run_btn.setEnabled(not is_running)
        self._abort_btn.setEnabled(is_running)
        self._exe_field.setEnabled(not is_running)
        self._start_field.setEnabled(not is_running)
        self._stop_field.setEnabled(not is_running)

    def _show_error(self, title: str, message: str) -> None:
        """
        Display a modal error dialog.

        Args:
            title   : Dialog window title.
            message : Body text of the error.
        """
        dialog = QMessageBox(self)
        dialog.setWindowTitle(title)
        dialog.setText(message)
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        dialog.exec()

    # ── Utility ───────────────────────────────────────────────────────────────

    @staticmethod
    def _make_label(text: str) -> QLabel:
        """Create a consistently styled field label."""
        label = QLabel(text)
        label.setStyleSheet(LABEL_STYLE)
        return label

    @staticmethod
    def _make_divider() -> QFrame:
        """Create a horizontal divider line."""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFixedHeight(1)
        line.setStyleSheet(f"background-color: {BORDER}; border: none;")
        return line

    # ── Style ─────────────────────────────────────────────────────────────────

    def _apply_styles(self) -> None:
        """Apply the global application stylesheet."""
        self.setStyleSheet(APP_STYLESHEET)
