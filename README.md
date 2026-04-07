# OpenModelica Simulation Launcher

![Python](https://img.shields.io/badge/Python-3.6%2B-blue?logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/PyQt6-6.4%2B-green?logo=qt&logoColor=white)
![OpenModelica](https://img.shields.io/badge/OpenModelica-Compatible-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)
![PEP8](https://img.shields.io/badge/Code%20Style-PEP8-blue)

A desktop GUI application built with **Python + PyQt6** that launches compiled
[OpenModelica](https://openmodelica.org/) model executables with configurable
simulation time parameters.

Submitted as a screening task for the **FOSSEE Summer Fellowship 2026**
under the **OpenModelica** project track.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Compiling the OpenModelica Model](#compiling-the-openmodelica-model)
- [Running the Application](#running-the-application)
- [Usage Guide](#usage-guide)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)
- [Design Decisions](#design-decisions)

---

## Overview

This application solves a two-part task:

1. **Part 1 — Model Compilation**: Compile the `TwoConnectedTanks` Modelica
   model using OpenModelica into a standalone executable.
2. **Part 2 — GUI Launcher**: Build a Python desktop app that selects and runs
   that executable with user-supplied `startTime` and `stopTime` parameters,
   streaming the simulation output live.

The constraint enforced by the application: `0 ≤ startTime < stopTime < 5`.

---

## Architecture

The application follows a clean **OOP design** with four distinct classes,
each with a single responsibility:

```
SimLauncherApp  (QMainWindow)      ← main window, layout, input fields
├── SimulationConfig               ← dataclass: validates & holds inputs
├── SimulationRunner  (QThread)    ← runs subprocess, emits Qt signals
└── ResultsPanel  (QWidget)        ← displays live log output + status
```

**Why this structure?**

| Class | Responsibility |
|---|---|
| `SimulationConfig` | All validation logic, zero Qt dependency — fully unit-testable |
| `SimulationRunner` | Background thread, never blocks the UI |
| `ResultsPanel` | Self-contained output widget, reusable |
| `SimLauncherApp` | Orchestrates the others, owns no business logic |

This separation means each class can be modified, tested, or replaced
independently.

---

## Features

- **Executable browser** — file picker dialog for selecting the compiled model
- **Time parameter inputs** — integer fields for start and stop time
- **Input validation** — enforces `0 ≤ start < stop < 5` with clear error messages
- **Live output streaming** — stdout/stderr streamed line-by-line as simulation runs
- **Status indicator** — IDLE / RUNNING / SUCCESS / ERROR badge
- **Elapsed time display** — shows how long the simulation took
- **Abort button** — terminates a running simulation at any time
- **Keyboard shortcut** — `Ctrl+R` to run, `Enter` in time fields to trigger run
- **Non-blocking UI** — simulation runs in a `QThread`, UI stays responsive
- **Unit tests** — full coverage of validation logic

---

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.6+ | Tested on 3.10, 3.11 |
| PyQt6 | 6.4+ | GUI framework |
| OpenModelica | 1.21+ | Required to compile the model (Linux/Windows) |

> **macOS users**: PyQt6 app development works on macOS. However, OpenModelica
> model compilation must be done on Linux or Windows. The compiled executable
> and its dependent files are included in the `model/` directory of this repo
> for convenience.

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/tanishk001-ai/openmodelica-sim-launcher.git
cd openmodelica-sim-launcher

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate       # Linux/macOS
venv\Scripts\activate          # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Compiling the OpenModelica Model

> Skip this section if you are using the pre-compiled executable
> from the `model/` directory.

### On Linux (Ubuntu/Debian)

```bash
# Install OpenModelica
sudo apt-get update
sudo apt-get install -y openmodelica

# Verify installation
omc --version

# Load and compile TwoConnectedTanks via OMEdit:
# 1. Launch OMEdit
# 2. File > Open Model/Library File(s) > select package.mo
# 3. In Libraries browser, right-click TwoConnectedTanks > Simulate
# 4. Find the compiled executable at:
#    /tmp/OpenModelica/<username>/OMEdit/NonInteractingTanks.TwoConnectedTanks/
# 5. Copy TwoConnectedTanks (executable) + TwoConnectedTanks_init.xml to model/
```

### On Windows

```
1. Download OpenModelica from https://openmodelica.org/download/download-windows
2. Open OMEdit > File > Open > select package.mo
3. Simulate the TwoConnectedTanks model
4. Find the .exe at:
   C:\Users\<username>\AppData\Local\Temp\OpenModelica\OMEdit\
5. Copy TwoConnectedTanks.exe + TwoConnectedTanks_init.xml to model\
```

### Verify the executable works

```bash
# Linux
./NonInteractingTanks.TwoConnectedTanks -override=startTime=0,stopTime=4

# Windows
model\TwoConnectedTanks.exe -override=startTime=0,stopTime=4
```

Expected output: `LOG_SUCCESS | info | The simulation finished successfully.`

---

## Running the Application

```bash
python main.py
```

---

## Usage Guide

1. **Select executable** — Click `Browse…` and navigate to the compiled
   `TwoConnectedTanks` executable (or any compiled OpenModelica model).

2. **Set start time** — Enter an integer ≥ 0. Example: `0`

3. **Set stop time** — Enter an integer that is:
   - Greater than start time
   - Less than 5
   Example: `4`

4. **Run** — Click `▶ Run Simulation` (or press `Ctrl+R`).
   The output panel shows live simulation logs and a status badge.

5. **Abort** — Click `■ Abort` at any time to terminate the process.

**Constraint reminder**: `0 ≤ startTime < stopTime < 5`

---

## Running Tests

The test suite covers all validation logic in `SimulationConfig` —
independently of any Qt widgets.

```bash
# Run all tests with verbose output
python -m pytest tests/ -v

# Run with coverage report
pip install pytest-cov
python -m pytest tests/ -v --cov=src --cov-report=term-missing
```

---

## Project Structure

```
openmodelica-sim-launcher/
│
├── main.py                  ← Entry point
│
├── src/
│   ├── __init__.py
│   ├── app.py               ← SimLauncherApp (QMainWindow)
│   ├── config.py            ← SimulationConfig (dataclass + validation)
│   ├── runner.py            ← SimulationRunner (QThread)
│   ├── results.py           ← ResultsPanel (QWidget)
│   └── styles.py            ← Stylesheet + colour constants
│
├── tests/
│   ├── __init__.py
│   └── test_config.py       ← Unit tests for validation logic
│
├── model/                   ← Compiled OpenModelica executable + deps
│   ├── TwoConnectedTanks    ← (Linux) or TwoConnectedTanks.exe (Windows)
│   └── TwoConnectedTanks_init.xml
│
├── docs/
│   └── screenshot.png       ← Application screenshot
│
├── requirements.txt
└── README.md
```

---

## Design Decisions

**Why PyQt6 over Tkinter?**
PyQt6 provides native OS theming, a proper signal/slot system, and
`QThread` — which allows the simulation subprocess to run without freezing
the UI. Tkinter has no clean equivalent.

**Why a QThread for the runner?**
Running `subprocess.Popen` on the main thread would freeze the entire UI
until the simulation completes. `SimulationRunner(QThread)` runs the process
in the background and emits `log_line` signals that update the UI safely from
the main thread.

**Why keep SimulationConfig separate from the UI?**
Validation logic should not live inside a widget. Keeping it in a standalone
dataclass means it can be unit-tested without launching Qt, and re-used by
any future interface (CLI, web API, etc.).

**Why centralise styles in styles.py?**
A single file of colour tokens means the entire visual theme can be changed
in one place — no hunting through widget constructors for hex values.

---

## License

MIT — see [LICENSE](LICENSE) for details.
