# Agent Rules

## 0. Mandatory startup workflow

For EVERY request, before doing anything else:

1. Read `.opencode/context/workflow.md`.
2. Identify the current lifecycle stage from `openspec status`, the
   `tasks.md` checkboxes, and which changes are active vs archived.
3. Route the user's intent to a stage using the routing table in that file
   and execute that stage.
4. Execute ONE stage per request, then stop with a brief report and wait for
   the next instruction.

This rule applies EVEN IF the user says "continue", "fix this", "small
change" or anything similar: identify the stage first.

## 1. Spec is the source of truth

Every observable behavior change MUST land as an OpenSpec change
(proposal + deltas) or be regularized as such. Behavior not described in
`openspec/specs/` is a defect, even if the code works. Never edit code to
introduce behavior that no change describes.

## 2. Commits belong to the user

NEVER run `git commit`, `git push`, `git add` or any other git write
operation. When the workflow reaches a commit gate (after
`openspec validate`, after implementation), announce it and stop.

## 3. Language

All artifacts, specs, commits, documentation and code in English.

## 4. Reference implementation

The reference app lives at `/home/ale/mapfre/personal/django_ig`. Ground
requirements and designs in its real code (apps by domain: `accounts`,
`social`, `posts`, `api`, `web`; Clean Architecture layers:
views → use_cases → services → models). Never invent requirements the
reference app does not have without flagging the deviation.
