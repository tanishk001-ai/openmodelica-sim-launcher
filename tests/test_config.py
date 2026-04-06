"""
tests/test_config.py
====================
Unit tests for SimulationConfig validation logic.

Run with:
    python -m pytest tests/ -v
"""

import os
import stat
import tempfile
import unittest

from src.config import SimulationConfig


class TestSimulationConfigValidation(unittest.TestCase):
    """Tests for SimulationConfig.from_inputs() validation."""

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _make_executable(self) -> str:
        """Create a temporary executable file and return its path."""
        fd, path = tempfile.mkstemp()
        os.close(fd)
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
        return path

    # ── Executable path validation ────────────────────────────────────────────

    def test_empty_executable_path_returns_error(self) -> None:
        config, error = SimulationConfig.from_inputs("", "0", "4")
        self.assertIsNone(config)
        self.assertIsNotNone(error)

    def test_nonexistent_executable_returns_error(self) -> None:
        config, error = SimulationConfig.from_inputs(
            "/nonexistent/path/model", "0", "4"
        )
        self.assertIsNone(config)
        self.assertIsNotNone(error)

    def test_valid_executable_and_times_returns_config(self) -> None:
        path = self._make_executable()
        try:
            config, error = SimulationConfig.from_inputs(path, "0", "4")
            self.assertIsNotNone(config)
            self.assertIsNone(error)
            self.assertEqual(config.start_time, 0)
            self.assertEqual(config.stop_time, 4)
        finally:
            os.unlink(path)

    # ── Start time validation ─────────────────────────────────────────────────

    def test_non_integer_start_time_returns_error(self) -> None:
        path = self._make_executable()
        try:
            config, error = SimulationConfig.from_inputs(path, "abc", "4")
            self.assertIsNone(config)
            self.assertIsNotNone(error)
        finally:
            os.unlink(path)

    def test_negative_start_time_returns_error(self) -> None:
        path = self._make_executable()
        try:
            config, error = SimulationConfig.from_inputs(path, "-1", "4")
            self.assertIsNone(config)
            self.assertIsNotNone(error)
        finally:
            os.unlink(path)

    def test_start_time_zero_is_valid(self) -> None:
        path = self._make_executable()
        try:
            config, error = SimulationConfig.from_inputs(path, "0", "4")
            self.assertIsNotNone(config)
            self.assertIsNone(error)
        finally:
            os.unlink(path)

    # ── Stop time validation ──────────────────────────────────────────────────

    def test_stop_time_equal_to_5_returns_error(self) -> None:
        path = self._make_executable()
        try:
            config, error = SimulationConfig.from_inputs(path, "0", "5")
            self.assertIsNone(config)
            self.assertIsNotNone(error)
        finally:
            os.unlink(path)

    def test_stop_time_greater_than_5_returns_error(self) -> None:
        path = self._make_executable()
        try:
            config, error = SimulationConfig.from_inputs(path, "0", "10")
            self.assertIsNone(config)
            self.assertIsNotNone(error)
        finally:
            os.unlink(path)

    def test_stop_time_less_than_or_equal_to_start_returns_error(self) -> None:
        path = self._make_executable()
        try:
            # Equal
            config, error = SimulationConfig.from_inputs(path, "2", "2")
            self.assertIsNone(config)
            self.assertIsNotNone(error)
            # Less than
            config, error = SimulationConfig.from_inputs(path, "3", "1")
            self.assertIsNone(config)
            self.assertIsNotNone(error)
        finally:
            os.unlink(path)

    def test_non_integer_stop_time_returns_error(self) -> None:
        path = self._make_executable()
        try:
            config, error = SimulationConfig.from_inputs(path, "0", "3.5")
            self.assertIsNone(config)
            self.assertIsNotNone(error)
        finally:
            os.unlink(path)

    # ── CLI args ──────────────────────────────────────────────────────────────

    def test_to_cli_args_format(self) -> None:
        path = self._make_executable()
        try:
            config, _ = SimulationConfig.from_inputs(path, "0", "4")
            args = config.to_cli_args()
            self.assertEqual(args[0], path)
            self.assertIn("startTime=0", args[1])
            self.assertIn("stopTime=4", args[1])
            self.assertTrue(args[1].startswith("-override="))
        finally:
            os.unlink(path)

    # ── Boundary: all valid combinations ─────────────────────────────────────

    def test_all_valid_time_combinations(self) -> None:
        path = self._make_executable()
        try:
            valid_pairs = [(0, 1), (0, 4), (1, 2), (1, 4), (2, 3), (3, 4)]
            for start, stop in valid_pairs:
                with self.subTest(start=start, stop=stop):
                    config, error = SimulationConfig.from_inputs(
                        path, str(start), str(stop)
                    )
                    self.assertIsNotNone(config, msg=error)
                    self.assertIsNone(error)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
