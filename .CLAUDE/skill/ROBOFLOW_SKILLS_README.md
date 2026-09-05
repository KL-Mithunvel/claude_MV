# Roboflow skills — provenance and activation

The ten `roboflow-*` skill folders here are vendored from Roboflow's official
agent plugin repo:

- **Source**: https://github.com/roboflow/computer-vision-skills
- **Synced**: 2026-09-05, upstream commit `5816914`, plugin version 0.1.1
- **License**: Apache-2.0 (upstream's — see `LICENSE-roboflow-skills` in this
  folder; the rest of this repo stays MIT)

They supersede the older copies that lived in Tile_Sorting's
`.CLAUDE/skill/` (all nine differed from upstream; `roboflow-batch-processing`
is new entirely).

| Skill | Covers |
|---|---|
| `roboflow-api-reference` | REST + inference API references, API key management |
| `roboflow-batch-processing` | Batch processing jobs over staged media |
| `roboflow-cloud-storage` | Mirroring S3/GCS buckets into a workspace |
| `roboflow-custom-weights-upload` | Uploading locally trained weights |
| `roboflow-data-management` | Uploading, labeling, dataset organization, splits |
| `roboflow-inference` | Inference, Workflows, workflow templates, batch jobs |
| `roboflow-plans-and-pricing` | Plans and credit usage |
| `roboflow-product-navigation` | Where features live in app.roboflow.com |
| `roboflow-training-and-evaluation` | Training, evals, active learning, improvement playbook |
| `roboflow-universe` | Public datasets/models on Roboflow Universe |

## Activating them in a project

This `.CLAUDE/skill/` folder is the **library copy** (reference material,
same convention as Tile_Sorting). To make the skills live for Claude Code in
a project, pick ONE of (full detail in `docs/ROBOFLOW_SETUP.md`):

1. **Plugin install (recommended — stays up to date, bundles the MCP server):**
   `claude plugin marketplace add roboflow/computer-vision-skills` then
   `claude plugin install roboflow`
2. **Standalone skills CLI:** `npx skills add roboflow/computer-vision-skills`
   (installs into the project's `.claude/skills/`)
3. **Manual copy from this library:** copy the needed
   `.CLAUDE/skill/roboflow-<name>/` folders to `.claude/skills/` in the
   project.

## Updating this library copy

```bash
git clone --depth 1 https://github.com/roboflow/computer-vision-skills /tmp/cvs
cp -r /tmp/cvs/skills/roboflow-* .CLAUDE/skill/
cp /tmp/cvs/.mcp.json .mcp.json
```

Then update the sync date/commit at the top of this file in the same commit.
