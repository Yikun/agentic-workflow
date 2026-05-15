# Test Cases — Hello World CLI Program

## Functional Requirement Tests

### TC-01: Default Greeting Output
**Requirement:** FR-01  
**Preconditions:** 
- Python 3.8 or higher is installed
- `hello.py` is accessible in the working directory

**Steps:**
1. Open a terminal/command prompt
2. Navigate to the directory containing `hello.py`
3. Execute: `python hello.py`

**Expected Result:**
- The program outputs `Hello, World!` followed by a newline character
- Exit code is `0`

**Type:** Functional - Positive

---

### TC-02: Custom Name Argument — Single Word
**Requirement:** FR-02  
**Preconditions:**
- Python 3.8 or higher is installed
- `hello.py` is accessible in the working directory

**Steps:**
1. Open a terminal/command prompt
2. Navigate to the directory containing `hello.py`
3. Execute: `python hello.py --name Alice`

**Expected Result:**
- The program outputs `Hello, Alice!` followed by a newline character
- Exit code is `0`

**Type:** Functional - Positive

---

### TC-03: Custom Name Argument — Multiple Words
**Requirement:** FR-02  
**Preconditions:**
- Python 3.8 or higher is installed
- `hello.py` is accessible in the working directory

**Steps:**
1. Open a terminal/command prompt
2. Navigate to the directory containing `hello.py`
3. Execute: `python hello.py --name "Alice and Bob"`

**Expected Result:**
- The program outputs `Hello, Alice and Bob!` followed by a newline character
- Exit code is `0`

**Type:** Functional - Positive

---

### TC-04: Help Documentation Display
**Requirement:** FR-03  
**Preconditions:**
- Python 3.8 or higher is installed
- `hello.py` is accessible in the working directory

**Steps:**
1. Open a terminal/command prompt
2. Navigate to the directory containing `hello.py`
3. Execute: `python hello.py --help`

**Expected Result:**
- The program displays usage instructions containing:
  - A brief description of the program's purpose
  - Available options (`--name` and `--help`)
  - Usage examples
- Exit code is `0`

**Type:** Functional - Positive

---

### TC-05: Help Documentation Content Verification
**Requirement:** FR-03  
**Preconditions:**
- Python 3.8 or higher is installed
- `hello.py` is accessible in the working directory

**Steps:**
1. Execute: `python hello.py --help`
2. Capture the output
3. Verify the output contains:
   - Program description mentioning "greeting"
   - `--name` option with description
   - At least one usage example

**Expected Result:**
- Help output includes all required elements (description, options, examples)
- Format is human-readable and well-structured

**Type:** Functional - Positive

---

## Non-Functional Requirement Tests

### TC-06: Code Quality — Ruff Linter Check
**Requirement:** NFR-01  
**Preconditions:**
- `ruff` is installed in the environment
- `hello.py` is accessible

**Steps:**
1. Navigate to the project root directory
2. Execute: `ruff check agentic-issues/issue-13-hello-world-cli-program-in-python/src/hello.py`

**Expected Result:**
- Ruff exits with code `0` (no errors)
- No linting errors or warnings are reported

**Type:** Non-Functional - Code Quality

---

### TC-07: Code Quality — Ruff Formatter Check
**Requirement:** NFR-01  
**Preconditions:**
- `ruff` is installed in the environment
- `hello.py` is accessible

**Steps:**
1. Navigate to the project root directory
2. Execute: `ruff format --check agentic-issues/issue-13-hello-world-cli-program-in-python/src/hello.py`

**Expected Result:**
- Ruff formatter exits with code `0`
- File is already properly formatted (no changes needed)

**Type:** Non-Functional - Code Quality

---

### TC-08: Python Version Compatibility
**Requirement:** NFR-02  
**Preconditions:**
- Python 3.8 is available (or specific version to test)
- `hello.py` is accessible

**Steps:**
1. Verify Python version: `python --version` (should be 3.8 or higher)
2. Execute: `python hello.py`
3. Execute: `python hello.py --name Test`

**Expected Result:**
- Program runs successfully without syntax errors
- Uses only Python 3.8+ compatible features
- Outputs correct greetings

**Type:** Non-Functional - Compatibility

---

### TC-09: Execution via Standard Python Interpreter
**Requirement:** NFR-03  
**Preconditions:**
- Python 3.8 or higher is installed
- `hello.py` is accessible

**Steps:**
1. Open a terminal/command prompt
2. Execute: `python hello.py` (using standard invocation)

**Expected Result:**
- Program executes successfully
- Standard output contains the greeting message
- No errors are raised

**Type:** Non-Functional - Execution

---

### TC-10: Exit Code Verification
**Requirement:** NFR-03  
**Preconditions:**
- Python 3.8 or higher is installed
- `hello.py` is accessible

**Steps:**
1. Execute: `python hello.py; echo $?` (Unix/Linux/macOS)
   OR execute: `python hello.py; echo $LASTEXITCODE` (Windows PowerShell)
2. Execute: `python hello.py --name Test; echo $?`

**Expected Result:**
- Both commands return exit code `0`
- Program indicates successful execution

**Type:** Non-Functional - Execution

---

## Edge Case Tests

### TC-11: Empty String as Name Value
**Requirement:** FR-02  
**Preconditions:**
- Python 3.8 or higher is installed
- `hello.py` is accessible

**Steps:**
1. Execute: `python hello.py --name ""`

**Expected Result:**
- Program outputs `Hello, !` followed by a newline character
- No crash or error occurs
- Exit code is `0`

**Type:** Edge Case

---

### TC-12: Name with Special Characters
**Requirement:** FR-02  
**Preconditions:**
- Python 3.8 or higher is installed
- `hello.py` is accessible

**Steps:**
1. Execute: `python hello.py --name "User@123!#$%"`
2. Execute: `python hello.py --name "O'Brien"`
3. Execute: `python hello.py --name "Test-User_123"`

**Expected Result:**
- Program outputs `Hello, User@123!#$%!` (with newline)
- Program outputs `Hello, O'Brien!` (with newline)
- Program outputs `Hello, Test-User_123!` (with newline)
- No crashes or errors occur

**Type:** Edge Case

---

### TC-13: Very Long Name Value
**Requirement:** FR-02  
**Preconditions:**
- Python 3.8 or higher is installed
- `hello.py` is accessible

**Steps:**
1. Generate a long string (e.g., 1000 characters): 
   - Linux/macOS: `python hello.py --name "$(python -c 'print("A"*1000)')"`
   - Windows: `python hello.py --name "AAAA...AAA"` (1000 A's)
2. Verify program handles the input

**Expected Result:**
- Program outputs `Hello, <1000 A's>!` followed by a newline
- No buffer overflow or memory error occurs
- Exit code is `0`

**Type:** Edge Case

---

### TC-14: Invalid Argument Handling
**Requirement:** FR-02, FR-03  
**Preconditions:**
- Python 3.8 or higher is installed
- `hello.py` is accessible

**Steps:**
1. Execute: `python hello.py --invalid-option`
2. Observe the program behavior

**Expected Result:**
- Program displays an error message indicating unrecognized argument
- Program displays usage information
- Exit code is non-zero (typically `2` for argparse errors)

**Type:** Edge Case - Negative

---

### TC-15: Missing Value After --name
**Requirement:** FR-02  
**Preconditions:**
- Python 3.8 or higher is installed
- `hello.py` is accessible

**Steps:**
1. Execute: `python hello.py --name` (without providing a value)

**Expected Result:**
- Program displays an error message indicating argument requires a value
- Exit code is non-zero (typically `2` for argparse errors)

**Type:** Edge Case - Negative

---

### TC-16: Multiple --name Arguments
**Requirement:** FR-02  
**Preconditions:**
- Python 3.8 or higher is installed
- `hello.py` is accessible

**Steps:**
1. Execute: `python hello.py --name Alice --name Bob`

**Expected Result:**
- Program uses the last provided value (`Bob`)
- Outputs `Hello, Bob!` followed by a newline
- Exit code is `0`

**Type:** Edge Case

---

### TC-17: Name with Unicode Characters
**Requirement:** FR-02  
**Preconditions:**
- Python 3.8 or higher is installed
- `hello.py` is accessible
- Terminal supports UTF-8 encoding

**Steps:**
1. Execute: `python hello.py --name "日本語"`
2. Execute: `python hello.py --name "Émilie"`
3. Execute: `python hello.py --name "Привет"`

**Expected Result:**
- Program outputs `Hello, 日本語!` (with newline)
- Program outputs `Hello, Émilie!` (with newline)
- Program outputs `Hello, Привет!` (with newline)
- No encoding errors occur

**Type:** Edge Case

---

### TC-18: Name with Newline or Tab Characters
**Requirement:** FR-02  
**Preconditions:**
- Python 3.8 or higher is installed
- `hello.py` is accessible

**Steps:**
1. Execute: `python hello.py --name "Alice"$'\n'"Bob"` (bash escape for newline)
2. Execute: `python hello.py --name "Alice"$'\t'"Bob"` (bash escape for tab)

**Expected Result:**
- Program accepts the input without crashing
- Output contains the literal newline/tab characters in the name
- Exit code is `0`

**Type:** Edge Case

---

### TC-19: Numeric Name Value
**Requirement:** FR-02  
**Preconditions:**
- Python 3.8 or higher is installed
- `hello.py` is accessible

**Steps:**
1. Execute: `python hello.py --name 12345`
2. Execute: `python hello.py --name "42"`

**Expected Result:**
- Program outputs `Hello, 12345!` (with newline)
- Program outputs `Hello, 42!` (with newline)
- Numbers are treated as string input
- Exit code is `0`

**Type:** Edge Case

---

## Test Summary

| TC ID | Requirement | Type | Priority |
|-------|-------------|------|----------|
| TC-01 | FR-01 | Functional - Positive | High |
| TC-02 | FR-02 | Functional - Positive | High |
| TC-03 | FR-02 | Functional - Positive | Medium |
| TC-04 | FR-03 | Functional - Positive | High |
| TC-05 | FR-03 | Functional - Positive | Medium |
| TC-06 | NFR-01 | Non-Functional - Code Quality | High |
| TC-07 | NFR-01 | Non-Functional - Code Quality | High |
| TC-08 | NFR-02 | Non-Functional - Compatibility | Medium |
| TC-09 | NFR-03 | Non-Functional - Execution | High |
| TC-10 | NFR-03 | Non-Functional - Execution | Medium |
| TC-11 | FR-02 | Edge Case | Medium |
| TC-12 | FR-02 | Edge Case | Medium |
| TC-13 | FR-02 | Edge Case | Low |
| TC-14 | FR-02, FR-03 | Edge Case - Negative | Medium |
| TC-15 | FR-02 | Edge Case - Negative | Medium |
| TC-16 | FR-02 | Edge Case | Low |
| TC-17 | FR-02 | Edge Case | Medium |
| TC-18 | FR-02 | Edge Case | Low |
| TC-19 | FR-02 | Edge Case | Low |

---

## Coverage Matrix

| Requirement | Test Cases |
|-------------|------------|
| FR-01 | TC-01 |
| FR-02 | TC-02, TC-03, TC-11, TC-12, TC-13, TC-14, TC-15, TC-16, TC-17, TC-18, TC-19 |
| FR-03 | TC-04, TC-05, TC-14 |
| NFR-01 | TC-06, TC-07 |
| NFR-02 | TC-08 |
| NFR-03 | TC-09, TC-10 |

All functional and non-functional requirements are covered by at least one test case.