# AI Model Selection Guide (Antigravity)

## Objective

Use the **smallest model that reliably produces the required result**.
Only move to a stronger model when the task genuinely requires deeper
reasoning.

------------------------------------------------------------------------

## Decision Rule

  -----------------------------------------------------------------------
  If the task is...                                        Use
  -------------------------------------------------------- --------------
  Simple lookup, formatting, rewriting                     Gemini 3.5
                                                           Flash (Low)

  Normal coding, documentation, refactoring                Gemini 3.5
                                                           Flash (Medium)

  Larger coding tasks, multiple files                      Gemini 3.5
                                                           Flash (High)

  Large context, good quality, daily engineering           Gemini 3.6
                                                           Flash (Medium)

  Complex engineering with many files                      Gemini 3.6
                                                           Flash (High)

  Deep reasoning or architecture                           Gemini 3.1 Pro

  Difficult reasoning where quality matters more than      Claude Sonnet
  speed                                                    4.6 (Thinking)

  Mission-critical design/research                         Claude Opus
                                                           4.6 (Thinking)

  Local/open-weight experimentation                        GPT-OSS 120B
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# Model Guide

  -------------------------------------------------------------------------
  Model         Best For          Avoid Using For            Example
  ------------- ----------------- -------------------------- --------------
  Gemini 3.5    Grammar,          Architecture, debugging    Convert notes
  Flash (Low)   formatting,       large codebases            to Markdown
                markdown,                                    
                summaries, regex,                            
                small scripts                                

  Gemini 3.5    Small Python      Large refactors            Write a CSV
  Flash         functions, SQL,                              parser
  (Medium)      JSON fixes,                                  
                documentation                                

  Gemini 3.5    Daily coding,     Deep research              Refactor a
  Flash (High)  reviews,                                     module
                debugging, 2--5                              
                file changes                                 

  Gemini 3.6    Slightly higher   Heavy reasoning            Explain an API
  Flash (Low)   quality than 3.5                             
                for general chat                             

  Gemini 3.6    Default model for Extremely complex          Review 10
  Flash         most software     reasoning                  files and
  (Medium)      engineering                                  suggest fixes

  Gemini 3.6    Large             Simple edits               Design and
  Flash (High)  repositories,                                implement a
                long context,                                feature across
                implementation                               20 files
                planning                                     

  Gemini 3.1    Architecture,     Simple coding              Design an
  Pro           algorithms,                                  event-driven
                trade-offs                                   pipeline

  Claude Sonnet Difficult         Formatting tasks           Find subtle
  4.6           debugging,                                   concurrency
  (Thinking)    nuanced code                                 bugs
                review, reasoning                            

  Claude Opus   Highest-quality   Routine coding             Review an
  4.6           analysis,                                    entire AI
  (Thinking)    research, system                             platform
                design                                       architecture

  GPT-OSS 120B  Open-weight       Highest accuracy tasks     Generate
  (Medium)      validation,                                  boilerplate
                alternative                                  locally
                opinions, local                              
                workflows                                    
  -------------------------------------------------------------------------

------------------------------------------------------------------------

# Recommended Workflow

## 1. Routine (80% of work)

**Gemini 3.6 Flash (Medium)**

Examples: - Python coding - Refactoring - Documentation - Unit tests -
Code review - Git assistance

------------------------------------------------------------------------

## 2. Cheap Tasks

**Gemini 3.5 Flash (Low)**

Examples: - Rename variables - Rewrite README - Convert JSON - Markdown
generation - Regex - CSV cleanup

------------------------------------------------------------------------

## 3. Medium Engineering

**Gemini 3.5 Flash (High)**

Examples: - Build a class - Fix bugs - Modify several files - Small
feature implementation

------------------------------------------------------------------------

## 4. Large Engineering

**Gemini 3.6 Flash (High)**

Examples: - Repository-wide changes - Multi-module implementation -
Large refactoring - Long context discussions

------------------------------------------------------------------------

## 5. Architecture

**Gemini 3.1 Pro**

Examples: - System design - AI pipeline - Database design - Performance
strategy

------------------------------------------------------------------------

## 6. Difficult Reasoning

**Claude Sonnet 4.6 (Thinking)**

Examples: - Root cause analysis - Hard debugging - Complex algorithm
review - Security review

------------------------------------------------------------------------

## 7. Highest Quality

**Claude Opus 4.6 (Thinking)**

Use only when the answer quality matters more than cost.

Examples: - Final architecture review - Research synthesis - Critical
design decisions

------------------------------------------------------------------------

# Token Optimization

  Task                  Recommended Model
  --------------------- -------------------------
  Grammar / Rewrite     Gemini 3.5 Flash Low
  Markdown              Gemini 3.5 Flash Low
  Email                 Gemini 3.5 Flash Low
  SQL                   Gemini 3.5 Flash Medium
  Python Function       Gemini 3.5 Flash Medium
  Bug Fix               Gemini 3.5 Flash High
  Multi-file Refactor   Gemini 3.6 Flash Medium
  Large Refactor        Gemini 3.6 Flash High
  AI Architecture       Gemini 3.1 Pro
  Difficult Debugging   Claude Sonnet Thinking
  Research              Claude Opus Thinking

------------------------------------------------------------------------

# Personal Recommendation

Default to:

-   **Gemini 3.6 Flash (Medium)** for everyday engineering.
-   **Gemini 3.5 Flash (Low)** for inexpensive utility tasks.
-   **Claude Sonnet 4.6 (Thinking)** only when stuck on a difficult
    problem.
-   **Claude Opus 4.6 (Thinking)** only for rare, high-impact decisions.
-   **Gemini 3.1 Pro** for architecture and planning.

This minimizes token usage while maintaining high output quality.




Is this task modifying/designing the pipeline execution or cross-engine architecture?
 ├── YES ──> Use Claude Sonnet 4.6 (Thinking) [or Opus 4.6 for extreme cases]
 └── NO
      │
      ├── Does it require reading 5+ full Python files simultaneously?
      │    ├── YES ──> Use Gemini 3.1 Pro (High)
      │    └── NO
      │         │
      │         ├── Is it implementing a new single engine or business logic function?
      │         │    ├── YES ──> Use Gemini 3.6 Flash (High) or GPT-OSS 120B
      │         │    └── NO
      │         │         │
      │         │         └── Is it a quick bug fix, formatting, typo, or docstring patch?
      │         │              └── YES ──> Use Gemini 3.6 Flash (Low / Medium)  <-- "Kill the Mosquito"
