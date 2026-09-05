# TODO

## In Progress

## Done
- [x] Vendor the ten official Roboflow skills (roboflow/computer-vision-skills
  @ 5816914) into `.CLAUDE/skill/`, add root `.mcp.json` (Roboflow MCP
  server), `docs/ROBOFLOW_SETUP.md`, `requirements-roboflow.txt`, and the
  Roboflow tools (`roboflow_check.py`, `roboflow_upload.py`,
  `roboflow_eval.py` → Gate-4 standard results); case-study addendum for
  Tile_Sorting's new conveyor-footage tool.
- [x] Turn claude_MV into the machine-vision baseline/template repo — CLAUDE.md
  with the four gates (data understanding, compute survey,
  deployment-target-first, standard results), docs (MV workflow, Tile_Sorting
  case study, deployment-target guide, results standard), tools
  (compute_survey.py, standard_results.py), model-folder template, `.CLAUDE/`
  rules library carried over from Tile_Sorting.

## Not Started
- [ ] Exercise the template on the next new MV project and fold back anything
  that turned out awkward in practice.
- [ ] Add a `.tflite` export recipe alongside ONNX in the model-folder template
  once a project actually needs it (MCU-class target).
- [ ] Evaluate the planned pip→`uv` migration for this template's setup steps.
