---
name: frontend-validator
description: >
  Triggered when building or testing the static web UI. Uses browser
  subagent to screenshot each screen and verify against UX spec.
---

# Frontend Validator Skill

## Triggers
- "web UI"
- "frontend screen"
- "Agent Check Screen"
- "Progress Screen"
- "Bootstrap installer"

## Instructions

1. Open `frontend/index.html` in browser subagent.
2. Navigate each screen (0-5).
3. Capture screenshot artifact for each screen.
4. Assert no console errors.
5. Test at 375px, 768px, 1280px viewports.
6. Verify screen flow: Bootstrap → Detect → Flash → Progress → WiFi → Success.
