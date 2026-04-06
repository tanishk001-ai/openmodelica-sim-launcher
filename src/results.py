"""
results.py
==========
ResultsPanel — a QWidget that displays simulation output logs,
status indicators, and elapsed time. Kept as its own class so the
main window stays clean (separation of concerns).
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QTextCharFormat, QFont
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.styles import (
    LOG_BACKGROUND,
    LOG_TEXT_COLOR,
    LOG_SUCCESS_COLOR,
    LOG_ERROR_COLOR,
    LOG_INFO_COLOR,
    PANEL_STYLE,
)


class StatusBadge(QLabel):
    """
    Small colored label used to indicate simulation state.
    States: idle | running | success | error
    """

    _COLORS: dict[str, tuple[str, str]] = {
        "idle":    ("#3a3a4a", "#aaaacc"),
        "running": ("#1a3a5c", "#4fc3f7"),
        "success": ("#1a3a1a", "#69f0ae"),
        "error":   ("#3a1a1a", "#ff5252"),
    }

    def __init__(self, parent=None) -> None:
        super().__init__("● IDLE", parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(28)
        self.set_state("idle")

    def set_state(self, state: str) -> None:
        """
        Update badge appearance for the given state.

        Args:
            state : One of 'idle', 'running', 'success', 'error'.
        """
        bg, fg = self._COLORS.get(state, self._COLORS["idle"])
        label_map = {
            "idle":    "● IDLE",
            "running": "● RUNNING",
            "success": "✔ SUCCESS",
            "error":   "✖ ERROR",
        }
        self.setText(label_map.get(state, "● IDLE"))
        self.setStyleSheet(
            f"background-color: {bg}; color: {fg}; "
            f"border-radius: 4px; padding: 2px 10px; "
            f"font-size: 11px; font-weight: bold; letter-spacing: 1px;"
        )


class ResultsPanel(QWidget):
    """
    Displays simulation log output and status information.

    Provides:
        - Status badge (idle / running / success / error)
        - Elapsed time display
        - Scrollable plain-text log area
        - Clear log button
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        """Construct and arrange all child widgets."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # ── Header row ────────────────────────────────────────────────────
        header = QHBoxLayout()

        output_label = QLabel("SIMULATION OUTPUT")
        output_label.setStyleSheet(
            "color: #7c7caa; font-size: 11px; "
            "font-weight: bold; letter-spacing: 2px;"
        )

        self._status_badge = StatusBadge()

        self._time_label = QLabel("—")
        self._time_label.setStyleSheet("color: #7c7caa; font-size: 11px;")
        self._time_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        clear_btn = QPushButton("Clear")
        clear_btn.setFixedWidth(60)
        clear_btn.setFixedHeight(24)
        clear_btn.setStyleSheet(
            "QPushButton { background: #2a2a3a; color: #7c7caa; "
            "border: 1px solid #3a3a5a; border-radius: 3px; font-size: 11px; }"
            "QPushButton:hover { background: #3a3a5a; color: #ccccff; }"
        )
        clear_btn.clicked.connect(self.clear_log)

        header.addWidget(output_label)
        header.addStretch()
        header.addWidget(self._status_badge)
        header.addSpacing(12)
        header.addWidget(self._time_label)
        header.addSpacing(8)
        header.addWidget(clear_btn)

        # ── Log area ──────────────────────────────────────────────────────
        self._log = QPlainTextEdit()
        self._log.setReadOnly(True)
        self._log.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self._log.setFont(QFont("Courier New", 10))
        self._log.setStyleSheet(
            f"QPlainTextEdit {{"
            f"  background-color: {LOG_BACKGROUND};"
            f"  color: {LOG_TEXT_COLOR};"
            f"  border: 1px solid #2a2a3a;"
            f"  border-radius: 4px;"
            f"  padding: 8px;"
            f"}}"
        )
        self._log.setPlaceholderText(
            "Simulation output will appear here once you click Run…"
        )

        layout.addLayout(header)
        layout.addWidget(self._log)
        self.setStyleSheet(PANEL_STYLE)

    # ── Public API ────────────────────────────────────────────────────────────

    def append_line(self, line: str) -> None:
        """
        Append a single line to the log area.
        Color-codes lines containing known keywords.

        Args:
            line : The text line to append.
        """
        self._log.appendPlainText(line)
        # Auto-scroll to bottom
        scrollbar = self._log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def set_status(self, state: str) -> None:
        """
        Update the status badge.

        Args:
            state : 'idle' | 'running' | 'success' | 'error'
        """
        self._status_badge.set_state(state)

    def set_elapsed(self, seconds: float) -> None:
        """
        Display the elapsed simulation time.

        Args:
            seconds : Total elapsed time in seconds.
        """
        self._time_label.setText(f"⏱ {seconds:.2f}s")

    def clear_log(self) -> None:
        """Clear all log content and reset status to idle."""
        self._log.clear()
        self._status_badge.set_state("idle")
        self._time_label.setText("—")
