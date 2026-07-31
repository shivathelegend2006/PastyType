# PastyType

## Overview
PastyType is a graphical keyboard automation utility designed to convert clipboard text into simulated hardware-level keystrokes. It inputs text directly into the active window holding cursor focus, eliminating the need for application-specific APIs, browser extensions, or DOM manipulation.

The tool is engineered specifically to reconcile formatting disparities between Integrated Development Environments (IDEs)—which dynamically enforce auto-indentation and delimiter completion—and standard unformatted plain-text applications.

---

## Technical Requirements & Elevation

### Administrative Privileges (Windows UAC)
Because PastyType simulates hardware-level input across operating system windows, **execution with Administrator privileges is mandatory on Windows environments.** 

If the target application (e.g., Visual Studio Code, elevated terminal sessions, or security-hardened browser processes) operates with elevated permissions or under restrictive UI policies, Windows User Account Control (UAC) will silently intercept and block background keystroke injection unless PastyType is operating with equivalent administrative elevation.

---

## Installation & Deployment

PastyType can be deployed as a compiled standalone executable or run directly from source.

### Option 1: Standalone Executable (Recommended)
For end-users seeking immediate execution without configuring a local Python development environment:
1. Navigate to the **Releases** section of this repository.
2. Download the latest release archive (`PastyType-Windows.zip`).
3. Extract the archive contents to a secure local directory.
4. Right-click `PastyType.exe` and select **Run as administrator**.

### Option 2: Source Code Execution
For developers intending to inspect the typing engine, modify source code, or compile custom binaries:
1. Clone the repository:
   ```bash
   git clone [https://github.com/shivathelegend2006/PastyType.git](https://github.com/shivathelegend2006/PastyType.git)
   cd PastyType

```

2. Install the necessary runtime dependencies:
```bash
pip install -r requirements.txt

```


3. Launch an elevated terminal session (Administrator) and execute the main entry point:
```bash
python src/main.py

```



---

## Usage Protocol

Before executing automated typing sequences, review the documentation within the application interface to understand how specific typing modes interact with various text editors.

### Operating Modes

* **IDE Auto-Indent Mode (Enabled):** Recommended for intelligent code editors (e.g., Visual Studio Code, JetBrains IDEs, LeetCode, HackerRank). In this mode, PastyType strips leading whitespace from new lines and employs predictive cursor-jump logic to prevent the duplication of automatically paired delimiters (brackets, parentheses, and quotes).
* **Raw Mode (IDE Auto-Indent Disabled):** Recommended for unformatted text environments (e.g., Notepad, basic web input fields, command-line interfaces). PastyType systematically outputs every individual space, tab character, and alphanumeric symbol precisely as represented in the source text.

### Standard Execution Workflow

1. **Input Source Text:** Paste the intended text into the primary PastyType buffer.
2. **Configure Operating Mode:** Select either **IDE Auto-Indent ON** or **Raw Mode** based on the target application's behavior.
3. **Configure Transmission Interval:** Adjust the **Typing Delay** parameter. A baseline interval between `10 ms` and `20 ms` is recommended for standard execution.
4. **Apply Configuration:** Click **Save** to commit hotkey bindings and delay parameters.
5. **Establish Focus:** Click within the target application to ensure the input cursor is active and correctly positioned.
6. **Initiate Transmission:** Press the configured **Start Hotkey** (Default: `Q`) and refrain from manual keyboard or mouse input until execution concludes.
7. **Abort Execution:** To terminate an active transmission immediately, press the **Stop Hotkey** (Default: `ESC`).

---

## Troubleshooting & Diagnostic Guide

Keystroke simulation relies on precise OS cursor synchronization and timing. If anomalies occur during transmission, consult the diagnostic protocols below:

### 1. Execution Initiates But No Characters Are Rendered

* **Root Cause:** The application lacks sufficient elevation to inject input into the target process.
* **Resolution:** Terminate PastyType. Re-launch the executable or terminal session by right-clicking and selecting **Run as administrator**. Operating system security policies prevent non-elevated background processes from sending input to elevated active windows.

### 2. Character Output is Skipped, Out-of-Order, or Scrambled

* **Root Cause:** The configured typing interval is lower than the target application's render loop threshold. Web-based editors utilize JavaScript execution threads that may experience latency when processing high-frequency keystroke injection (e.g., `0 ms` delay).
* **Resolution:** Increase the **Typing Delay** parameter to `20 ms` or `30 ms`. Providing sufficient buffer time for the target application to process and render each character ensures sequential consistency.

### 3. Text Output Exhibits Excessive Horizontal Indentation or Drifting

* **Root Cause:** An incorrect typing mode is selected. When **Raw Mode** is active within an intelligent IDE, PastyType transmits physical indentation spaces while the IDE simultaneously applies automatic indentation, resulting in exponential whitespace growth.
* **Resolution:** Enable **IDE Auto-Indent Mode** within PastyType. This instructs the automation engine to strip leading whitespace and allow the target editor to manage line indentation natively.

### 4. Delimiters (Brackets, Parentheses, Quotes) Are Duplicated

* **Root Cause:** The target editor's auto-completion feature is pairing syntax delimiters automatically, but PastyType is either operating in **Raw Mode** or the transmission interval is too rapid for the arrow-key step-over logic to execute.
* **Resolution:** Verify that **IDE Auto-Indent Mode** is enabled, and increase the **Typing Delay** by `5 ms` to `10 ms` to allow cursor navigation commands to register.

### 5. Unintended Autocomplete or Predictive Text is Inserted

* **Root Cause:** Inline predictive assistants (e.g., GitHub Copilot, IntelliSense ghost-text) are intercepting newline (`Enter`) key events and automatically inserting suggested code blocks during transmission.
* **Resolution:** Temporarily disable inline AI completion or ghost-text features within the target editor prior to executing extensive automated typing sequences.


