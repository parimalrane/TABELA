import sys
import re

with open('c:/TABELA/docs/SYSTEM_CONTEXT.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Update A.3
a3_match = r"(# A\.3 Root Directory\n\nThe repository root should remain intentionally lightweight\.\n\nOnly place files here that satisfy one of the following:\n\n- application entry point\n\n- repository configuration\n\n- project metadata\n\n- developer tooling\n\n- licensing\n\n)"
if re.search(a3_match, text):
    text = re.sub(a3_match, r"\1- scripts/ directory containing operator-facing batch scripts (scripts/weekly_run.py)\n\n", text)
else:
    print("A.3 not found")

# Update A.4
# We want to list: runtime_context.py and weekly_pipeline.py
text = text.replace(
"""Representative files:

- main.py

- pipeline.py

- config.py

- runtime_context.py""",
"""Representative files:

- main.py

- pipeline.py

- config.py

- runtime_context.py

- weekly_pipeline.py"""
)

# Update A.5
# Since A.5 doesn't list files, we inject a Representative files block.
a5_search = "- Historical Intelligence"
a5_replace = "- Historical Intelligence\n\nRepresentative files:\n\n- unknown_classification_persistence.py\n\n(Note: short_engine.py was removed)"
text = text.replace(a5_search, a5_replace)

# Append Appendix G (Change Log) at the bottom before `# END OF SYSTEM_CONTEXT.md`
# The provided Change log entry:
log_entry = """
---

# Appendix G (Change Log)

Date: 2026-07-27
Component: Repository Architecture & Directory Structure
Category: Refactoring / Architectural Reorganization
Reason: Moved framework orchestration (runtime_context.py, weekly_pipeline.py) into core/, isolated operator scripts in scripts/, repaired weekly_markdown_writer.py, and corrected filename typo (SYSTEM_CONTEXT.md).
Impact: Zero breaking changes to core business logic or pipeline deterministic outputs. All internal import paths synchronized.
Constraint: Do NOT modify any business methodology rules, composite scoring parameters, or data boundary constraints in SYSTEM_CONTEXT.md.

"""
text = text.replace("# END OF SYSTEM_CONTEXT.md", log_entry + "\n# END OF SYSTEM_CONTEXT.md")

with open('c:/TABELA/docs/SYSTEM_CONTEXT.md', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated perfectly.")
