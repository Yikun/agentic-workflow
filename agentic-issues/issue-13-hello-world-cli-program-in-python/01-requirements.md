# Requirements Document — Hello World CLI Program

## 1. Overview

A command-line interface (CLI) program written in Python that outputs a greeting message. The program must support a default greeting and allow customization via a command-line argument.

## 2. Functional Requirements

### FR-01: Default Greeting Output
When executed without any arguments, the program SHALL output the text `Hello, World!` followed by a newline character.

### FR-02: Custom Name Argument
The program SHALL accept an optional command-line argument `--name <value>`. When provided, the program SHALL output `Hello, <value>!` where `<value>` is the string passed to the `--name` argument.

### FR-03: Help Documentation
The program SHALL provide a `--help` option that displays usage instructions, including:
- A brief description of the program's purpose
- Available options and their syntax
- Examples of usage

## 3. Non-Functional Requirements

### NFR-01: Code Quality
The source code SHALL pass all checks performed by the `ruff` linter and formatter with zero errors.

### NFR-02: Python Version Compatibility
The program SHALL be compatible with Python 3.8 or higher.

### NFR-03: Execution Environment
The program SHALL be executable via the standard Python interpreter invocation (e.g., `python hello.py`).

## 4. Assumptions

- The user has Python 3.8 or higher installed on their system.
- The user invokes the program from a terminal or command prompt.
- The `--name` argument value contains only printable ASCII characters (no input validation required for special characters or Unicode).
- The program is executed in an environment where standard output is available.

## 5. Out of Scope

- Input validation for the `--name` argument (e.g., handling empty strings, special characters, or very long names).
- Internationalization or localization support.
- Configuration file support.
- Logging or debugging output.
- Installation as a system-wide command or package distribution (e.g., via pip).
- Error handling for invalid arguments beyond the built-in `--help` functionality.
- Unit tests (to be defined separately in test case specifications).