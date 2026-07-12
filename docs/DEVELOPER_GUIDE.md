# DEVELOPER_GUIDE.md

# TABELA Developer Guide

---

# 1. Purpose

This guide describes how to develop, maintain, and extend TABELA without introducing regressions.

It assumes familiarity with Python and the project architecture.

---

# 2. Development Principles

Follow these principles for all changes:

* One responsibility per engine.
* Keep engines independent.
* Prefer deterministic logic.
* Avoid duplicate calculations.
* Separate calculations from presentation.
* Preserve historical compatibility.

---

# 3. Project Structure

```text
TABELA/

core/
    Pipeline
    Configuration
    Utilities
    Theme Mapping

engines/
    Business Logic

data/
    Static Input Files

market_data/
    Historical Data

reports/

main.py
```

Do not place business logic in `main.py`.

---

# 4. Execution Flow

Normal execution starts from:

```text
main.py
        ↓
pipeline.py
        ↓
engines
        ↓
reports
```

The pipeline should remain the single orchestration point.

---

# 5. Engine Design

Every engine should have:

* One responsibility
* Clear inputs
* Clear outputs
* Minimal dependencies

Avoid engines that perform unrelated tasks.

---

# 6. Adding a New Engine

Recommended steps:

1. Create the engine.
2. Define its public interface.
3. Add unit tests.
4. Integrate into the pipeline.
5. Update documentation.
6. Validate downstream outputs.

Do not bypass the pipeline.

---

# 7. Modifying Existing Engines

Before changing an engine:

* Identify upstream dependencies.
* Identify downstream consumers.
* Review persisted JSON.
* Review historical compatibility.

If a schema changes, update loaders before writers.

---

# 8. Configuration

All configurable values belong in `config.py`.

Examples:

* thresholds
* weights
* limits
* directories
* feature flags

Avoid hard-coded constants inside engines.

---

# 9. Historical Data

Historical files are production data.

Rules:

* Never overwrite history.
* Never rename existing fields unnecessarily.
* Prefer additive schema changes.
* Maintain backward compatibility.

---

# 10. Error Handling

Recoverable errors:

* Missing optional files
* Empty datasets
* Unknown mappings

Fatal errors:

* Missing required inputs
* Invalid configuration
* Corrupt required data

Raise exceptions only for unrecoverable conditions.

---

# 11. Logging

Log:

* pipeline start
* engine execution
* warnings
* recoverable errors
* output locations

Do not log excessive internal calculations.

---

# 12. Performance

General guidelines:

* Read files once.
* Reuse processed data.
* Cache lookup tables.
* Avoid nested loops where practical.
* Prefer dictionaries for lookups.

---

# 13. Testing

Any significant change should be verified against:

* Valid input
* Empty input
* Missing optional data
* Invalid mappings
* Historical data compatibility

Regression testing should compare outputs with previous versions.

---

# 14. JSON Guidelines

Persist only structured information.

Allowed:

* scores
* identifiers
* rankings
* dates
* metrics

Do not persist:

* formatted reports
* ANSI colors
* generated narratives
* presentation details

---

# 15. Coding Standards

Recommended conventions:

* Descriptive function names.
* Small functions.
* Early validation.
* Explicit return values.
* Consistent naming.

Avoid:

* global mutable state
* hidden side effects
* duplicated algorithms

---

# 16. Documentation

Every new engine should update:

* ARCHITECTURE.md
* TECHNICAL_SPECIFICATION.md
* DATA_MODEL.md (if persisted data changes)

Keep documentation synchronized with implementation.

---

# 17. Safe Refactoring

Safe changes:

* Internal implementation improvements
* Performance optimizations
* Additional validation
* New reports

High-risk changes:

* Pipeline order
* JSON schema
* Theme mapping
* Composite scoring
* Historical processing

These require regression testing.

---

# 18. Backward Compatibility

Preserve compatibility whenever possible.

When introducing new fields:

* Provide defaults.
* Keep existing field names.
* Avoid changing file names.
* Avoid changing directory structure without justification.

---

# 19. Review Checklist

Before merging a change, verify:

* Code builds.
* Pipeline completes.
* Historical files load.
* Reports generate.
* No duplicate calculations introduced.
* Documentation updated.
* Existing outputs remain valid unless intentionally changed.

---

# 20. Development Priorities

Priority order:

1. Correctness
2. Historical consistency
3. Maintainability
4. Performance
5. New features

Never sacrifice correctness for performance.

---

# 21. Code Delivery Rules

For future code changes:

### Small files (≤250 lines)

* 1–2 logical changes: provide patches.
* 3 or more logical changes: replace the entire file.

### Large files (>250 lines)

* 1–2 logical changes: provide patches.
* 3 or more logical changes: replace complete functions.
* Replace an entire large file only when explicitly requested.

---

# 22. Pull Request Checklist

Every completed change should answer:

* Does it improve TABELA?
* Does it duplicate existing functionality?
* Does it preserve historical compatibility?
* Does it require documentation updates?
* Does it introduce new dependencies?
* Does it change persisted data?

If the answer to the last question is "yes", update `DATA_MODEL.md`.

---

# 23. Rebuild Considerations

When rebuilding modules:

* Implement one engine at a time.
* Validate each engine independently.
* Integrate only after passing validation.
* Preserve public interfaces where practical.
* Avoid simultaneous redesign of multiple engines.

Incremental validation is preferred over large-scale rewrites.
