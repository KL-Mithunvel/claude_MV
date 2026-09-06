# Roboflow Setup — basic requirements for any project from this template

Everything a new machine vision project needs to work with Roboflow: skills,
the MCP server, API keys, Python dependencies, and the template's Roboflow
tools. Distilled from how Tile_Sorting actually used Roboflow (dataset
hosting, labeling, hosted training, hosted-model evaluation).

> **Gate 3 reminder (`CLAUDE.md`):** Roboflow is great for dataset
> management, labeling, quick baselines, and active learning even when the
> deployment target is edge — but Roboflow's **hosted ViT training exports no
> weights** (inference API only). If the end system must run locally/offline,
> the production model path must export weights (train locally, or a local
> twin of the hosted recipe — Tile_Sorting's `cam_vit` pattern). Decide this
> before training.

---

## 1. Account, workspace, API key

1. A Roboflow account + workspace (Tile_Sorting used workspace `aida-hutc5`).
2. Create a **`.env` file at the project root** (gitignored — this template's
   `.gitignore` already excludes `.env`) with:

   ```bash
   ROBOFLOW_API_KEY=<private api key>
   ROBOFLOW_WORKSPACE=<workspace id>
   ```

3. **Never commit or paste private API keys** — they live only in `.env` /
   the shell environment. Publishable `rf_<workspaceId>` keys are
   browser-safe; private keys are not. Key management details:
   `.CLAUDE/skill/roboflow-api-reference/api-key-management.md`.

Verify the whole setup at any time:

```bash
python tools/roboflow_check.py
```

## 2. MCP server (live Roboflow tools in Claude Code)

The repo root's **`.mcp.json`** (copied from Roboflow's official plugin repo)
registers the hosted Roboflow MCP server (`https://mcp.roboflow.com/mcp`) —
projects, images, annotation, versions, training, Workflows, evals, Universe,
all as live tools. Auth defaults to OAuth on first use; for headless/CLI
environments that can't complete an OAuth redirect, it falls back to
`ROBOFLOW_API_KEY` from the environment.

Projects created from this template inherit `.mcp.json` automatically —
nothing else to configure.

## 3. Skills

The ten official `roboflow-*` skills are vendored in `.CLAUDE/skill/`
(provenance + full list: `.CLAUDE/skill/ROBOFLOW_SKILLS_README.md`).
Activate them in a project via ONE of:

| Route | Command | When |
|---|---|---|
| **Plugin (recommended)** | `claude plugin marketplace add roboflow/computer-vision-skills` then `claude plugin install roboflow` | Normal case — tracks upstream, bundles skills + MCP config. Add `--scope local` for per-project API keys. |
| Standalone skills CLI | `npx skills add roboflow/computer-vision-skills` | Agent reads `.claude/skills/` but not plugin manifests. |
| Manual copy | copy `.CLAUDE/skill/roboflow-<name>/` → `.claude/skills/` | Offline / pinned-version use of the vendored library copy. |

## 4. Python dependencies

```bash
# venv active first (per User Rules)
pip install -r requirements-roboflow.txt
```

`requirements-roboflow.txt` covers the SDK (`roboflow`), `.env` loading
(`python-dotenv`), and the HTTP client for the serverless inference API
(`requests`). The base `requirements.txt` already provides
numpy/matplotlib/PyYAML for the results tooling.

## 5. Template tools for the Roboflow workflow

All three read `ROBOFLOW_API_KEY`/`ROBOFLOW_WORKSPACE` from `.env`
automatically. Generalized from Tile_Sorting's `development/` scripts.

### `tools/roboflow_check.py` — setup verifier

Checks `.env`/environment keys, installed packages, `.mcp.json` presence,
and validates the API key against the live REST API. Run it first on any new
machine/project; it prints what to fix.

### `tools/roboflow_upload.py` — dataset uploader

Uploads a local **folder-per-class** dataset
(`<dataset_dir>/<class>/*.jpg|png`) to a Roboflow project:

```bash
python tools/roboflow_upload.py \
    --dataset-dir data/my_dataset \
    --project my-classification-project \
    --batch-name initial-import-2026-09-05 \
    [--as-classification]        # folder name becomes the class label
    [--tag source:dslr]          # extra tag(s) on every image
```

Without `--as-classification` images upload unlabeled (for detection/
segmentation projects to annotate in Roboflow). Per-image failures are
counted and reported, never silently dropped — same behavior Tile_Sorting's
uploader had.

### `tools/roboflow_eval.py` — hosted-model evaluation → standard results

Evaluates a Roboflow-hosted classification model version against a local
folder-per-class dataset via the serverless inference API, and writes the
**standard results folder (Gate 4)** through `tools/standard_results.py`:

```bash
python tools/roboflow_eval.py \
    --dataset-dir data/my_dataset_heldout \
    --project my-classification-project --version 2 \
    --classes A B C \
    --eval-set "held-out set, n=19, never uploaded to training" \
    --output-dir models/roboflow_hosted/results_v2
```

**Honest-numbers rule (from Tile_Sorting):** only images that were *not* in
the model's training data give a generalization estimate. Evaluating the
full local dataset a model trained on measures training-set fit (98.1% vs
the honest 84.2% on Tile_Sorting) — if you do it anyway, say so in
`--eval-set` and `--notes` so `metrics.json` carries the caveat.

## 6. Where Roboflow fits the workflow

| Phase (`docs/MV_WORKFLOW.md`) | Roboflow role |
|---|---|
| Phase 2 — data audit | Upload AFTER the local audit; local raw data stays authoritative, uploads scripted (`roboflow_upload.py`). |
| Phase 4 — dataset prep | Hosted labeling/annotation jobs, versions, splits (`roboflow-data-management` skill). |
| Phase 5 — training | Quick hosted baselines OK; production path must satisfy Gate 3 (weight export). |
| Phase 6 — evaluation | `roboflow_eval.py` → standard results, same format as local models. |
| Phase 9 — close the loop | Active learning: route low-confidence production samples back for review (`roboflow-training-and-evaluation/active-learning.md`). |
