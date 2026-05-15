# Implementation Decisions

This document records key decisions made during the implementation of the Hello World CLI Program.

## Decision 1: Function Separation

**Context:** The architecture document specifies components (CLI Entry Point, Argument Parser, Greeting Generator, Output Handler) but recommends a single-module approach.

**Decision:** Implemented as separate functions (`create_parser`, `generate_greeting`, `main`) within a single file.

**Rationale:**
- Maintains separation of concerns for testability and clarity
- Each function has a single responsibility
- Allows `generate_greeting` to be tested independently
- `create_parser` returns the parser for potential testing of argument handling

**Alternative Considered:** Inline all logic in `main()` - rejected due to reduced testability and clarity.

---

## Decision 2: Explicit Return Type for main()

**Context:** Python functions can omit return type annotations.

**Decision:** Added explicit `-> int` return type annotation for `main()`.

**Rationale:**
- Documents the expected return value (exit code)
- Aligns with type checking best practices
- Improves code clarity for future maintainers

---

## Decision 3: Using print() Instead of sys.stdout.write()

**Context:** Architecture document mentions `sys.stdout` for output.

**Decision:** Used `print()` function instead of `sys.stdout.write()`.

**Rationale:**
- `print()` automatically appends the newline character as required
- More idiomatic Python
- Simpler and more readable
- Meets the output contract specification

**Trade-off:** Slightly less explicit about output destination, but acceptable for this use case.

---

## Decision 4: ArgumentParser Epilog for Examples

**Context:** FR-03 requires examples in help documentation.

**Decision:** Used `RawDescriptionHelpFormatter` with an `epilog` containing formatted examples.

**Rationale:**
- Preserves the formatting of the examples section
- Clear, readable help output
- Aligns with user expectations for CLI documentation

---

## Decision 5: Explicit sys.exit() Call

**Context:** `main()` returns an exit code, but the script could run without explicit exit handling.

**Decision:** Used `sys.exit(main())` in the `if __name__ == "__main__"` block.

**Rationale:**
- Ensures the exit code is propagated to the shell
- Follows Python CLI best practices
- Allows the function to be tested without exiting the test process

---

## Decision 6: No Shebang Portability Concern

**Context:** Cross-platform compatibility.

**Decision:** Used `#!/usr/bin/env python3` shebang.

**Rationale:**
- Works on most Unix-like systems
- Uses `env` to find Python in PATH
- Windows ignores shebang, invoking via `python hello.py` works correctly

---

## Decision 7: Default Value in argparse

**Context:** FR-01 requires "World" as default greeting target.

**Decision:** Set `default="World"` in `parser.add_argument()`.

**Rationale:**
- Keeps default logic in the argument parser
- Single source of truth for the default value
- Simpler than checking `None` in `generate_greeting`

---

## Summary

All decisions align with the architecture document while ensuring clean, maintainable code that passes linting checks and meets all functional requirements.