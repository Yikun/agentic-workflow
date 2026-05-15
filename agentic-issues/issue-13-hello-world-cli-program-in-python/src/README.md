# Hello World CLI Program

A simple command-line interface program written in Python that outputs a greeting message.

## Installation

**Requirements:**
- Python 3.8 or higher

**Install:**
```bash
# No installation required. Clone or download the source file.
git clone <repository-url>
cd <repository-directory>/src

# Or download the single file directly
curl -O <url-to-hello.py>
```

No additional dependencies are required. The program uses only Python standard library modules.

## Upgrade

**If using git:**
```bash
git pull origin main
# No dependency changes, so no further action needed
```

**If downloaded directly:**
- Download the latest version of `hello.py` and replace the existing file.

Since this is a single-file program with no dependencies, there are no package management steps required for upgrades.

## Uninstall

```bash
# Remove the program file
rm hello.py

# Remove the entire project directory if cloned
rm -rf <repository-directory>

# No configuration files are created by this program.
# No output directories are written by this program.
```

This program does not:
- Create any configuration files
- Write any output files to disk
- Install system-wide packages

Therefore, uninstallation is simply removing the `hello.py` file.

## Quick Start

```bash
# Default greeting
python hello.py
# Output: Hello, World!

# Custom greeting
python hello.py --name Alice
# Output: Hello, Alice!

# View help
python hello.py --help
```

## Configuration

This program does not use any configuration files. All options are provided via command-line arguments.

## CLI Reference

```
python hello.py [OPTIONS]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--name <value>` | String | `World` | Custom name for the greeting message |
| `--help` | Flag | N/A | Display usage information and exit |

**Usage Examples:**

```bash
# Output default greeting
python hello.py
# Output: Hello, World!

# Output custom greeting
python hello.py --name Alice
# Output: Hello, Alice!

# Use quotes for names with spaces
python hello.py --name "Alice and Bob"
# Output: Hello, Alice and Bob!

# Display help
python hello.py --help
```

## Output Files

This program does not write any files to disk.

**Output:**
- **Standard Output (stdout):** The greeting message followed by a newline character.
- **Exit Code:** `0` on success.

| Scenario | stdout Output | Exit Code |
|----------|---------------|-----------|
| No arguments | `Hello, World!\n` | 0 |
| `--name Alice` | `Hello, Alice!\n` | 0 |
| `--help` | Usage instructions | 0 |

No files are created, modified, or deleted by this program.