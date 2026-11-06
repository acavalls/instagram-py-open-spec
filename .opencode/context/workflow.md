# Anchored SDD Workflow

This is the project lifecycle. The agent MUST read this file at the start of
every request, identify the current stage (from `openspec status`, the
`tasks.md` checkboxes and the active vs archived changes), and route the
user's intent through the pipeline table below.

The lifecycle is a PIPELINE with exactly two human decision points:

- **PAUSE-1 (manual validation)**: after implementation. Question:
  "¿Te parece correcta la implementación? SI/NO".
- **PAUSE-2 (post-audit)**: only if the audit found drift. Question:
  "¿Cerramos el ciclo o corregimos el drift?".

Everything else runs automatically, including the commits at the agreed
gates via the super-commit procedure (see Conduct rules). A request that
starts a cycle executes every automatic phase end-to-end and stops only at
PAUSE-1, PAUSE-2, or an error.

## Intent routing

| What the user says | Action |
| --- | --- |
| Describes a new feature / "propon X" / "haz X" (no active cycle) | **Phase A** (propose → auto-decide ambiguities → validate → commit(plan) → apply → quality gates → commit(impl)) → **PAUSE-1** |
| "SI" (or equivalent approval at PAUSE-1) | **Phase B** (verify → archive → commit(archive)) → **Phase C** (audit) → close or **PAUSE-2** |
| "NO <explanation>" (rejection at PAUSE-1) | Decide from the explanation: `/opsx-update <change> <revision>` (artifacts wrong) or `/opsx-apply` (re-implementation) → quality gates → new commits (never amend) → **PAUSE-1** again |
| "cerramos" (post-audit, no drift or accepted drift) | Close the cycle with a final report |
| "corregimos" (post-audit, drift found) | Regularization mini-pipeline: `/opsx-propose` → apply → verify → archive → commit → audit again, until `IN SYNC` |
| "verify" / "archive" / "audit" / "implement[ group N]" | Direct re-entry into that stage (mid-cycle corrections) |
| "ambiguity X resolves to Y" / spec-level change of mechanism Z | `/opsx-update <change> <revision prompt>` |
| "review the implementation, X is missing" | `/opsx-update`, then `/opsx-apply` again, then quality gates and continue the pipeline |
| "change mechanism Z" (no artifact named) | Decision tree below |

### Decision tree for "change mechanism Z"

When the user asks to change a mechanism without naming an artifact, the
agent locates where the mechanism lives today and picks the path:

1. **Locate** the mechanism:
   - Active changes: `openspec list` + read the `proposal.md` and
     `tasks.md` of each active change.
   - Living specs: search `openspec/specs/**/spec.md`.
   - Archived history: search `openspec/changes/archive/`.

2. **Decide** by state:

   | Found in | Path |
   | --- | --- |
   | An active change (not archived) | **A**: `/opsx-update <change> <revision>` → re-apply affected tasks |
   | A living spec (archived) | **B**: `/opsx-propose` a new change with a `MODIFIED` delta → full pipeline |
   | Nowhere | `/opsx-propose` a new change: the user's information becomes new requirements |
   | Implemented but not archived, and the request changes the change's **intent** (not a refinement) | Say so and propose **B** (or a fresh change), instead of patching with A |

3. **Execute** that single stage, using the user's information (file,
   description, whatever provided) as the input of the revision, then stop
   and report.

Never assume when the state is ambiguous (e.g. two active changes touch the
same mechanism): ask the user before writing anything.

## Phases

### Phase A — plan and implement (automatic)

1. **Propose** (`/opsx-propose <change-name> <description>`):
   `openspec new change` → `openspec status --change <name> --json` →
   `openspec instructions <artifact> --change <name> --json` per artifact,
   inspecting the reference codebase (`/home/ale/mapfre/personal/django_ig`)
   before drafting. Delta spec format: `## Purpose` for new capabilities;
   `## ADDED/MODIFIED/REMOVED Requirements`; `### Requirement:` with
   MUST/SHALL; scenarios as `#### Scenario:` with WHEN/THEN bullets
   (exactly 4 hashtags); every requirement needs at least one scenario.

2. **Ambiguities — auto-resolved, never delegated to the user.** The agent
   resolves every business decision itself, choosing the reasonable
   alternative (parity with the reference app is the default tie-breaker),
   and documents each decision in `design.md` (or `proposal.md`) as
   "Decision: ... (agent-decided, flagged for review)". The decisions are
   listed in the report so the user can overturn any of them later with
   `/opsx-update`. Do not pause for ambiguity questions.

3. **Validate**: `openspec validate <change-name>`.

4. **Commit gate (planning)** — super-commit (see Conduct rules), then push.

5. **Implementation** (`/opsx-apply`, all remaining task groups without
   stopping). The smallest implementation unit is a single task; never split
   a task. Per `config.yaml` operations guidance, run pytest and ruff after
   each task. Finish with the full quality gates: pytest (all pass),
   coverage >= 80%, ruff, mypy.

6. **Commit gate (implementation)** — super-commit, then push.

7. **PAUSE-1**: report what was implemented (artifacts, tests, gates) and
   ask: "¿Te parece correcta la implementación? SI/NO". Suggest the manual
   browser checks when they exist, but do not require them.

### Phase B — verify and archive (automatic, after "SI")

8. **Verify** (`/opsx-verify`): completeness, requirement mapping, scenario
   coverage, design adherence. CRITICAL issues loop back to
   `/opsx-update` + `/opsx-apply` + new commits before archiving.

9. **Archive** (`/opsx-archive`): sync the delta into the living spec, move
   the change to `openspec/changes/archive/YYYY-MM-DD-<name>/`.

10. **Commit gate (archive)** — super-commit, then push. Audit (Phase C)
    must run on a clean tree because it uses `git log` as evidence.

### Phase C — audit and close (automatic, with PAUSE-2 on drift)

11. **Audit** (skill `spec-audit`).

    - `IN SYNC` → close the cycle with a final report. Done.
    - Drift found → **PAUSE-2**: report the findings and ask
      "¿Cerramos el ciclo o corregimos el drift?".
      - "corregimos" → regularization mini-pipeline (propose → apply →
        verify → archive → super-commit) → audit again, repeat until
        `IN SYNC`.
      - "cerramos" → close with the findings documented for a future cycle.

## Super-commit procedure (used at every commit gate)

1. Inspect the full repo state: `git status --short`, `git diff --stat`,
   `git log --oneline -10`.
2. Group changes by intent (feat/fix/refactor/test/chore/docs/config);
   never mix unrelated changes in one commit.
3. Check for secrets or suspicious files (.env, credentials, keys); if any
   appear, stop and ask before committing.
4. `git add <files>` per group, commit each group with a semantic message
   following the repo style, then `git push`.
5. Never amend, never force push, never skip hooks. If the grouping is
   genuinely ambiguous, stop and ask.

## Conduct rules

- Commits and pushes run automatically at the agreed gates only
  (planning, implementation, archive, regularization), via the
  super-commit procedure. Any git write outside those gates requires an
  explicit user request.
- The spec is the source of truth: every observable behavior change lands as
  an OpenSpec change; behavior not described in `openspec/specs/` is a
  defect.
- All artifacts, specs, commits and documentation in English.
- Reference implementation for grounding requirements:
  `/home/ale/mapfre/personal/django_ig` (apps organized by domain:
  `accounts`, `social`, `posts`, `api`, `web`; Clean Architecture layers
  views → use_cases → services → models).
