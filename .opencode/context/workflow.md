# Anchored SDD Workflow

This is the project lifecycle. The agent MUST read this file at the start of
every request, identify the current stage (from `openspec status`, the
`tasks.md` checkboxes and the active vs archived changes), and execute the
stage the user's intent maps to. One stage per request; stop and report
afterwards.

## Intent routing

| What the user says                             | Stage   | Tool                                        |
| ---------------------------------------------- | ------- | ------------------------------------------- |
| "add this artifact" / describes a new feature  | 1       | `/opsx-propose <name> <spec prompt>`        |
| "ambiguity X resolves to Y" / spec-level change of mechanism Z | 2 / 6.B | `/opsx-update <change> <revision prompt>` |
| "implement"                                    | 5       | `/opsx-apply` — next pending task group by default; granular scope allowed (see stage 5) |
| "review the implementation, X is missing"      | 6.B → 5 | `/opsx-update`, then `/opsx-apply` again    |
| "verify"                                       | 7.B     | `/opsx-verify`                              |
| "archive"                                      | 8       | `/opsx-archive`                             |
| "audit"                                        | 9       | skill `spec-audit`                          |
| drifts found                                   | 9       | regularize: `/opsx-propose` → apply → archive |
| "change mechanism Z" (no artifact named, info provided as file or description) | decision tree below | A / B / new change |

### Decision tree for "change mechanism Z"

When the user asks to change a mechanism without naming an artifact, the
agent locates where the mechanism lives today and picks the path:

1. **Locate** the mechanism:
   - Active changes: `openspec list` + read the `proposal.md` and
     `tasks.md` of each active change.
   - Living specs: search `openspec/specs/**/spec.md`.
   - Archived history: search `openspec/changes/archive/`.

2. **Decide** by state:

   | Found in                        | Path                                                                   |
   | ------------------------------- | ---------------------------------------------------------------------- |
   | An active change (not archived) | **A**: `/opsx-update <change> <revision>` → re-apply affected tasks    |
   | A living spec (archived)        | **B**: `/opsx-propose` a new change with a `MODIFIED` delta → validate → user commit → apply → archive |
   | Nowhere                         | `/opsx-propose` a new change: the user's information becomes new requirements (new capability or `ADDED` requirement) |
   | Implemented but not archived, and the request changes the change's **intent** (not a refinement) | Say so and propose **B** (or a fresh `/opsx-new`), instead of patching with A |

3. **Execute** that single stage, using the user's information (file,
   description, whatever provided) as the input of the revision, then stop
   and report.

Never assume when the state is ambiguous (e.g. two active changes touch the
same mechanism): ask the user before writing anything.


## Stages

1. **Create the change in the specification:**

   ```
   /opsx-propose <change-name> <description>
   ```

   Creates the change and generates all artifacts in one step
   (proposal.md → specs/<capability>/spec.md → design.md → tasks.md).
   CLI steps the agent runs:
   `openspec new change` → `openspec status --change <name> --json` →
   `openspec instructions <artifact> --change <name> --json` per artifact,
   inspecting the reference codebase (`/home/ale/mapfre/personal/django_ig`)
   before drafting. Delta spec format: `## Purpose` for new capabilities;
   `## ADDED/MODIFIED/REMOVED Requirements`; `### Requirement:` with
   MUST/SHALL; scenarios as `#### Scenario:` with WHEN/THEN bullets
   (exactly 4 hashtags); every requirement needs at least one scenario.

2. **List ambiguities that need a business decision:**

   After step 1, list the real ambiguities that need a business decision and
   resolve them one by one with the user. Each resolution is applied with
   `/opsx-update <change> <revision prompt>`, which revises the artifacts and
   propagates the change in both directions for coherence (a change in specs
   may require revising the proposal and vice versa). It shows every revision
   before writing and never edits code. (`/opsx-continue` creates artifacts
   that do not exist yet; it does not revise existing ones.)

3. **Verify the specification format:**

   ```
   openspec validate <change-name>
   ```

4. **Commit (planning).** The user commits; the agent announces the gate.

5. **Implementation:**

   ```
   /opsx-apply
   ```

   **Execution granularity** (state is the `tasks.md` checkbox list):

   - "implement" → the next pending task **group** (the `## N.` sections in
     `tasks.md`), then stop and report.
   - "implement group N" → that group only.
   - "implement task N.M" / "implement up to N.M" → that task / every task up
     to and including N.M.
   - "implement everything" → all remaining groups without stopping.

   The smallest implementation unit is a single task; never split a task.
   Per `config.yaml` operations guidance, run pytest and ruff after each
   task.

6. **Manual validation.**

   6.B. Optional: if the implementation revealed that the plan was wrong or
   incomplete, `/opsx-update <change> <what to change>` first, then
   `/opsx-apply` again to carry the revised plan into code.

7. **Commit (implementation).** The user commits; the agent announces the gate.

   7.B. `/opsx-verify` — check the implementation matches the artifacts
   before archiving.

8. **Archive the change and turn the delta into the living spec:**

   ```
   /opsx-archive
   ```

   Merges the delta into `openspec/specs/<capability>/spec.md` (the anchor).

9. **Run the spec-audit skill:**

   ```
   spec-audit → reports drifts
   ```

   Then regularize each drift:
   `/opsx-propose <prompt describing the drift fixes>` → `/opsx-apply` →
   `/opsx-archive` — the living specs end up describing reality again.

## Conduct rules

- Never `git commit` / `git push` — commits belong to the user. When a
  commit gate is reached, say so and stop.
- The spec is the source of truth: every observable behavior change lands as
  an OpenSpec change; behavior not described in `openspec/specs/` is a
  defect.
- All artifacts, specs, commits and documentation in English.
- Reference implementation for grounding requirements:
  `/home/ale/mapfre/personal/django_ig` (apps organized by domain:
  `accounts`, `social`, `posts`, `api`, `web`; Clean Architecture layers
  views → use_cases → services → models).
