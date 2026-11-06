# Tasks

## 1. Spec regularization

- [ ] 1.1 social: add "Feed with follows but no posts" scenario to Followed-users feed (F1)
- [ ] 1.2 social: add "Profile grid without posts" scenario to User profile page (F2)
- [ ] 1.3 social: name suggestions panel chrome and add "No suggestions available" scenario (F3)
- [ ] 1.4 posts + social: document non-HTMX GET honoring `?page=` with full page at that window (F4)
- [ ] 1.5 web-ui: state first-media-only rendering in card anatomy and profile structure (F6)

## 2. Test fixes

- [ ] 2.1 Assert empty-feed icon in the empty state test (F5)
- [ ] 2.2 Add scenario docstrings to the 4 supplementary tests (F8)

## 3. Config

- [ ] 3.1 Fix `seed_data` → `seed_demo_data` in openspec/config.yaml (F7)

## 4. Quality gates

- [ ] 4.1 Full pytest suite passes, coverage >= 80%
- [ ] 4.2 ruff and mypy clean

## Workflow follow-up

- Commit implementation (super-commit at the gate)
- Verify the change
- Archive the change
