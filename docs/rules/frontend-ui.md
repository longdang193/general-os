# Frontend UI Rule

Use the repository's existing design system and semantic native controls.
Material visual changes require fresh rendered checks for affected states,
keyboard access, focus, contrast, responsive behavior, supported themes, and
reduced motion. Browser evidence supplements committed regression tests.

## Design Tool Integration

- Treat specifications, source code, tests, and the existing design system as
  authoritative for behavior and reusable implementation values.
- Use approved Figma or OpenDesign references as visual and interaction
  evidence when available; record the reference and revision without
  duplicating it.
- When multiple design sources exist, name one authority per design concern and
  resolve conflicts explicitly before implementation.
- Prefer configured native capabilities; do not install, authenticate, or
  reimplement vendor tooling without approval.
- If a design tool is unavailable, continue with the approved specification and
  existing design system, recording the missing evidence.
- Verify material UI changes through rendered inspection, accessibility checks,
  and relevant tests.
