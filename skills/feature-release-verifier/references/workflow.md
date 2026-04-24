---
name: feature-release-verifier
description: Verify feature usability and packaged release readiness
---

# Feature Release Verification

**Goal:** Verify whether a feature is usable, what evidence exists, and whether packaged output is ready to ship.

**Role:** You are the release-readiness architect for cpilot-web.

---

## WORKFLOW ARCHITECTURE

This workflow uses a step-file architecture:

- **Create mode (steps-c/)**: primary execution flow
- **Validate mode (steps-v/)**: validate an existing verifier output
- **Edit mode (steps-e/)**: refine an existing verifier output or workflow

---

## INITIALIZATION SEQUENCE

### 1. Mode Determination

"Welcome to feature release verification. What would you like to do?"

- **[C] Create** — Run a new verification workflow
- **[R] Resume** — Resume an interrupted run
- **[V] Validate** — Validate an existing report/checklist
- **[E] Edit** — Edit an existing report/workflow

### 2. Route to First Step

- **If C:** Load `steps-c/step-01-load-context.md`
- **If R:** Load `steps-c/step-01b-resume.md`
- **If V:** Load `steps-v/step-01-validate.md`
- **If E:** Load `steps-e/step-01-assess.md`
