"""Evaluate a Roboflow-hosted classification model against a local dataset,
writing the standard results folder (CLAUDE.md Gate 4) via standard_results.py.

Generalized from Tile_Sorting's development/evaluate_grade_model.py: calls
the serverless inference API (https://serverless.roboflow.com/<project>/<ver>)
for every image in a folder-per-class dataset (ground truth = folder name)
and produces metrics.json / predictions.json / confusion_matrix.png /
results_card.png / results.md — the same artifacts local models get, so
hosted and local results stay directly comparable.

HONEST-NUMBERS RULE (docs/ROBOFLOW_SETUP.md): only images the model did NOT
train on measure generalization. Evaluating the training images measures
dataset fit (Tile_Sorting: 98.1% full-dataset vs 84.2% held-out for the same
model) — if that's what you're doing, say so in --eval-set/--notes so
metrics.json carries the caveat.

Usage:
    python tools/roboflow_eval.py \
        --dataset-dir data/my_dataset_heldout \
        --project my-classification-project --version 2 \
        --classes A B C \
        --eval-set "held-out set, n=19, never uploaded to training" \
        --output-dir models/roboflow_hosted/results_v2
"""

from __future__ import annotations

import argparse
import base64
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from standard_results import write_standard_results  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def load_dataset(dataset_dir: Path) -> list[tuple[Path, str]]:
    samples = []
    for class_dir in sorted(p for p in dataset_dir.iterdir() if p.is_dir()):
        for path in sorted(class_dir.iterdir()):
            if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                samples.append((path, class_dir.name))
    return samples


def infer_image(session, url: str, api_key: str, image_path: Path, retries: int = 3) -> dict:
    encoded = base64.b64encode(image_path.read_bytes())
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            resp = session.post(
                url,
                params={"api_key": api_key},
                data=encoded,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=60,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            last_exc = exc
            print(f"    retry {attempt + 1}/{retries} after error on {image_path.name}: {exc}")
    raise last_exc


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dataset-dir", type=Path, required=True, help="Folder-per-class dataset (ground truth = folder)")
    parser.add_argument("--project", required=True, help="Roboflow project id (slug)")
    parser.add_argument("--version", type=int, required=True, help="Trained model version number")
    parser.add_argument("--classes", nargs="+", required=True, help="Class names, in display order")
    parser.add_argument("--eval-set", required=True, help="Which set, n, and provenance — held-out or training-set fit")
    parser.add_argument("--notes", default="", help="Caveats recorded into metrics.json")
    parser.add_argument("--output-dir", type=Path, required=True, help="Standard results folder to write")
    parser.add_argument("--max-workers", type=int, default=6, help="Parallel inference requests (default 6)")
    args = parser.parse_args()

    try:
        from dotenv import load_dotenv  # noqa: PLC0415 — checked by roboflow_check.py
        import requests  # noqa: PLC0415
    except ImportError as exc:
        raise SystemExit(f"missing dependency ({exc.name}) — pip install -r requirements-roboflow.txt")

    load_dotenv(REPO_ROOT / ".env")
    api_key = os.environ.get("ROBOFLOW_API_KEY")
    if not api_key:
        raise SystemExit("ROBOFLOW_API_KEY not set — see docs/ROBOFLOW_SETUP.md")

    samples = load_dataset(args.dataset_dir)
    if not samples:
        raise SystemExit(f"no images under {args.dataset_dir}/<class>/")
    unknown = {label for _, label in samples} - set(args.classes)
    if unknown:
        raise SystemExit(f"dataset folders not in --classes: {sorted(unknown)}")

    url = f"https://serverless.roboflow.com/{args.project}/{args.version}"
    print(f"Evaluating {args.project}/v{args.version} on {len(samples)} images from {args.dataset_dir}\n")

    session = requests.Session()
    rows: list[dict | None] = [None] * len(samples)

    def _run(i: int, path: Path, true_label: str) -> None:
        pred = infer_image(session, url, api_key, path)
        top = pred["predictions"][0]
        rows[i] = {
            "image": str(path.relative_to(args.dataset_dir)),
            "true": true_label,
            "pred": top["class"],
            "confidence": float(top["confidence"]),
        }

    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        futures = {executor.submit(_run, i, path, label): i for i, (path, label) in enumerate(samples)}
        done = 0
        for future in as_completed(futures):
            future.result()
            done += 1
            if done % 25 == 0 or done == len(samples):
                print(f"  ...{done}/{len(samples)} processed")

    metrics = write_standard_results(
        args.output_dir,
        rows,
        args.classes,
        model_name=f"Roboflow hosted {args.project}/v{args.version}",
        weights=f"https://app.roboflow.com — {args.project}/{args.version} (hosted, no exportable weights)",
        eval_set=args.eval_set,
        notes=args.notes,
    )
    print(f"\naccuracy: {metrics['num_correct']}/{metrics['num_total']} = {metrics['accuracy']:.4f}")
    print(f"Wrote standard results to {args.output_dir}")


if __name__ == "__main__":
    main()
