"""Upload a local folder-per-class image dataset to a Roboflow project.

Generalized from Tile_Sorting's development/roboflow_upload.py. Expects the
standard layout this template's dataset prep produces:

    <dataset_dir>/<class_name>/*.jpg|jpeg|png

Reads ROBOFLOW_API_KEY and ROBOFLOW_WORKSPACE from the environment / a
gitignored .env at the repo root (docs/ROBOFLOW_SETUP.md). Per-image upload
failures are counted and reported, never silently dropped.

Usage:
    python tools/roboflow_upload.py \
        --dataset-dir data/my_dataset \
        --project my-classification-project \
        --batch-name initial-import-2026-09-05 \
        --as-classification            # folder name becomes the class label
        --tag source:dslr              # optional, repeatable

Without --as-classification the images upload unlabeled (for detection/
segmentation projects, to be annotated in Roboflow afterwards). Every image
is tagged class:<folder> either way, so provenance survives in Roboflow.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def iter_dataset_images(dataset_dir: Path):
    for class_dir in sorted(p for p in dataset_dir.iterdir() if p.is_dir()):
        for path in sorted(class_dir.iterdir()):
            if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                yield path, class_dir.name


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dataset-dir", type=Path, required=True, help="Folder-per-class dataset root")
    parser.add_argument("--project", required=True, help="Roboflow project id (slug)")
    parser.add_argument("--batch-name", required=True, help="Upload batch name, e.g. initial-import-YYYY-MM-DD")
    parser.add_argument("--split", default="train", choices=["train", "valid", "test"], help="Split to assign (default train)")
    parser.add_argument(
        "--as-classification",
        action="store_true",
        help="Single-label classification project: use each image's folder name as its label",
    )
    parser.add_argument("--tag", action="append", default=[], help="Extra tag on every image (repeatable)")
    args = parser.parse_args()

    try:
        from dotenv import load_dotenv  # noqa: PLC0415 — checked by roboflow_check.py
        import roboflow  # noqa: PLC0415
    except ImportError as exc:
        raise SystemExit(f"missing dependency ({exc.name}) — pip install -r requirements-roboflow.txt")

    load_dotenv(REPO_ROOT / ".env")
    api_key = os.environ.get("ROBOFLOW_API_KEY")
    workspace_name = os.environ.get("ROBOFLOW_WORKSPACE")
    if not api_key or not workspace_name:
        raise SystemExit("ROBOFLOW_API_KEY / ROBOFLOW_WORKSPACE not set — see docs/ROBOFLOW_SETUP.md")

    if not args.dataset_dir.is_dir():
        raise SystemExit(f"{args.dataset_dir} is not a directory")
    images = list(iter_dataset_images(args.dataset_dir))
    if not images:
        raise SystemExit(f"no {'/'.join(sorted(SUPPORTED_EXTENSIONS))} images under {args.dataset_dir}/<class>/")

    project = roboflow.Roboflow(api_key=api_key).workspace(workspace_name).project(args.project)
    print(f"Uploading {len(images)} images from {args.dataset_dir} to {workspace_name}/{args.project} "
          f"(batch: {args.batch_name}, split: {args.split}, "
          f"{'labeled by folder' if args.as_classification else 'unlabeled'})\n")

    uploaded = failed = 0
    for i, (path, class_name) in enumerate(images, start=1):
        kwargs = {
            "image_path": str(path),
            "split": args.split,
            "batch_name": args.batch_name,
            "tag_names": [f"class:{class_name.lower()}", *args.tag],
        }
        if args.as_classification:
            kwargs["annotation_path"] = class_name
        try:
            project.upload(**kwargs)
            uploaded += 1
        except Exception as exc:
            failed += 1
            print(f"  [{i}/{len(images)}] FAILED {path.name}: {exc}")
        if i % 25 == 0 or i == len(images):
            print(f"  ...{i}/{len(images)} processed")

    print(f"\n{args.project}: {uploaded} uploaded, {failed} failed")
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
