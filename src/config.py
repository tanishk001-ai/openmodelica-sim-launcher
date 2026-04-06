"""
config.py — SimulationConfig dataclass + validation.
Validation order: 1. start time  2. stop time  3. executable
"""
from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional

TIME_MIN: float = 0.0
TIME_MAX: float = 5.0

@dataclass
class SimulationConfig:
    """Validated simulation parameters."""
    executable_path: str
    start_time: int
    stop_time: int

    @classmethod
    def from_inputs(cls, executable_path: str, start_time_str: str, stop_time_str: str) -> tuple[Optional["SimulationConfig"], Optional[str]]:
        """Validate inputs. Returns (config, None) or (None, error_message)."""
        try:
            start_time = int(start_time_str.strip())
        except ValueError:
            return None, "Start time must be a whole number (integer)."
        if start_time < TIME_MIN:
            return None, f"Start time must be >= {int(TIME_MIN)}. Got: {start_time}"

        try:
            stop_time = int(stop_time_str.strip())
        except ValueError:
            return None, "Stop time must be a whole number (integer)."
        if stop_time >= TIME_MAX:
            return None, f"Stop time must be < {int(TIME_MAX)}. Got: {stop_time}"
        if stop_time <= start_time:
            return None, f"Stop time ({stop_time}) must be greater than start time ({start_time})."

        exe_path = executable_path.strip()
        if not exe_path:
            return None, "Please select an executable file."
        if not os.path.isfile(exe_path):
            return None, f"Executable not found:\n{exe_path}"
        if not os.access(exe_path, os.X_OK):
            return None, f"File is not executable:\n{exe_path}\nTry: chmod +x <file>"

        return cls(executable_path=exe_path, start_time=start_time, stop_time=stop_time), None

    def to_cli_args(self) -> list[str]:
        """Returns [exe_path, '-override=startTime=X,stopTime=Y']"""
        return [self.executable_path, f"-override=startTime={self.start_time},stopTime={self.stop_time}"]

    def __str__(self) -> str:
        return f"Executable : {self.executable_path}\nStart Time : {self.start_time}\nStop Time  : {self.stop_time}"
