# Claude Log

## 2026-09-05 — Roboflow skills, MCP config, setup requirements, and tools
- The previous template PR (#1) was merged into main; restarted the working
  branch from origin/main per convention.
- Vendored all ten skills from roboflow/computer-vision-skills (upstream
  commit 5816914, plugin v0.1.1, Apache-2.0 — license copied alongside) into
  the existing `.CLAUDE/skill/` library, with
  `.CLAUDE/skill/ROBOFLOW_SKILLS_README.md` recording provenance, the three
  activation routes (plugin install / npx skills add / manual copy to
  `.claude/skills/`), and the re-sync procedure. These are newer than
  Tile_Sorting's copies (all nine differed; `roboflow-batch-processing` is
  new upstream).
- Added root `.mcp.json` (official hosted Roboflow MCP server, OAuth default
  with ROBOFLOW_API_KEY fallback) so projects created from the template get
  live Roboflow tools automatically.
- Wrote `docs/ROBOFLOW_SETUP.md` (account/keys via gitignored `.env`, MCP,
  skills, deps, tools, and where Roboflow fits each workflow phase) and
  `requirements-roboflow.txt` (roboflow, python-dotenv, requests).
- Added tools, generalized from Tile_Sorting's development/ scripts:
  `tools/roboflow_check.py` (setup verifier incl. live API-key check),
  `tools/roboflow_upload.py` (folder-per-class uploader, labeled or
  unlabeled, failure counting preserved), `tools/roboflow_eval.py`
  (serverless-API evaluation of a hosted classification model that writes
  the Gate-4 standard results via standard_results.py, honest-numbers rule
  documented). Added a matching Roboflow Integration section to CLAUDE.md.
- Checked Tile_Sorting for new work since the 2026-08-27 snapshot: one new
  commit ("pick and place hardware working") adds
  `development/process_conveyor_video.py` plus pick-and-place docs — no new
  skills. Its calibrated-thresholds-fail-on-new-footage lesson is recorded
  as case-study addendum §11; the script itself is clip/project-specific
  (hardcoded belt HSV, camera_node imports) so it was documented, not
  ported.

## 2026-08-27 — Bootstrap claude_MV as the machine-vision baseline/template repo
- Read the entire Tile_Sorting repo (classical CV pipeline, calibration
  tooling, Roboflow-hosted training, local cam_yolo/cam_vit pipelines, ONNX
  export + UNO Q deployment analysis, `.CLAUDE/` rules library) to extract the
  process and lessons.
- Wrote root `CLAUDE.md` — the baseline rules for every future MV project,
  centered on four mandatory gates: (1) fully understand the available data
  before making any changes; (2) survey available compute before local model
  development; (3) question the final deployment architecture before choosing
  a training platform/model (weight exportability + target compute budget);
  (4) standard results folder for every trained model.
- Wrote `docs/`: `MV_WORKFLOW.md` (the standard end-to-end procedure),
  `TILE_SORTING_CASE_STUDY.md` (the documented process/procedure followed in
  Tile_Sorting, with the lessons→rules map), `DEPLOYMENT_TARGETS.md`
  (target-first questionnaire + budget tables), `RESULTS_STANDARD.md` (results
  spec).
- Wrote `tools/compute_survey.py` (CPU/RAM/disk/GPU/CUDA report + recommended
  actions) and `tools/standard_results.py` (metrics.json, predictions.json,
  confusion_matrix.png, composite results_card.png, results.md — modeled on
  the shared artifact shape of Tile_Sorting's val.py / evaluate_grade_model.py,
  extended with confusion matrix in metrics, macro averages, and the one-look
  results card).
- Added `templates/model_dir/` (config.yaml + README skeleton following the
  `camera_models/<name>/` convention), `.gitignore` (datasets/weights never
  committed), and `requirements.txt`. The pre-existing `.CLAUDE/` library
  (generic project-brief skeleton, CLAUDE-COMMON, PROJ_STARTER, skills) was
  kept untouched — its copies are newer than Tile_Sorting's (they carry the
  Documentation Discipline section and the "ok KLM" opener rule), so the new
  root `CLAUDE.md` layers the MV baseline on top of it rather than replacing
  it.
- Verified both tools run: compute_survey against this container,
  standard_results against cam_vit's committed predictions.json (accuracy
  reproduced exactly; all five artifacts written).
- Decision: rules live in root `CLAUDE.md` (auto-loaded by Claude Code) with
  the general library kept under `.CLAUDE/`, rather than Tile_Sorting's
  `.CLAUDE/CLAUDE.md` placement — a template repo wants the binding rules
  where the tooling reads them by default.
