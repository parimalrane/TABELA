# Aider User Guide for TABELA

## Start Aider

Open PowerShell in the TABELA folder:

```powershell
cd C:\TABELA
```

Start Aider:

```powershell
$env:OLLAMA_API_BASE="http://127.0.0.1:11434"
aider --model ollama/qwen2.5-coder:14b --map-tokens 0
```

---

## Basic Workflow

### 1. Clear previous context

```
/drop
```

### 2. Add only the files needed

Example:

```
/add main.py
```

or

```
/add engines/short_engine.py
/add engines/short_scoring_engine.py
```

Never add the entire project.

---

### 3. Ask one focused question

Examples:

```
Explain this file.
```

```
Review this code for bugs only.
```

```
Explain the execution flow.
```

```
Find performance bottlenecks.
```

```
Suggest refactoring opportunities.
```

---

## Useful Commands

Clear current context:

```
/drop
```

Show files currently loaded:

```
/ls
```

Add a file:

```
/add filename.py
```

Remove a file:

```
/drop filename.py
```

Undo last Aider edit:

```
/undo
```

Exit:

```
/exit
```

---

## Recommended Workflow

Work on one module at a time.

Example:

```
/drop
/add engines/rotation_engine.py
```

Complete that task before moving to another module.

Then:

```
/drop
/add engines/snapshot_engine.py
```

---

## Good Prompts

```
Explain this file.
```

```
Explain the architecture.
```

```
Review for bugs only.
```

```
Review for edge cases.
```

```
Find dead code.
```

```
Find duplicated logic.
```

```
Explain how this function works.
```

```
Suggest unit tests.
```

---

## Avoid

❌ Loading many unrelated files.

❌ Asking multiple questions at once.

❌ Working on multiple modules simultaneously.

---

## TABELA Best Practice

Typical session:

```
/drop
/add main.py

Explain this file.
```

```
/drop
/add engines/long_scoring_engine.py

Review for bugs only.
```

```
/drop
/add engines/short_engine.py
/add engines/short_scoring_engine.py

Explain the complete execution flow.
```

---

## Current Configuration

Model

```
qwen2.5-coder:14b
```

Startup

```powershell
$env:OLLAMA_API_BASE="http://127.0.0.1:11434"
aider --model ollama/qwen2.5-coder:14b --map-tokens 0
```

---

## Notes

- Use only the files required for the current task.
- Keep sessions focused.
- Commit code frequently using Git.
- Use Aider as a coding assistant, not as a replacement for code review.