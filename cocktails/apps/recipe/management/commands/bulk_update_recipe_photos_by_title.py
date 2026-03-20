import csv
import os
import re
from typing import Dict, Optional, Tuple

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.recipe.models import Recipe


class Command(BaseCommand):
    help = (
        "Update Recipe.photo by matching recipe title in DB to title from CSV, "
        "while photo files are named by an external id from the CSV."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv-path",
            required=True,
            help="Path to CSV (inside container) that contains photo_id and recipe titles.",
        )
        parser.add_argument(
            "--photos-dir",
            default="/cocktails/tmp/bulk_photos",
            help="Directory with extracted photos (filenames start with photo_id digits).",
        )
        parser.add_argument(
            "--delimiter",
            default="\\t",
            help=r"CSV delimiter. Default is tab: \t",
        )
        parser.add_argument(
            "--photo-id-col",
            type=int,
            default=0,
            help="0-based column index that contains photo_id used in filenames.",
        )
        parser.add_argument(
            "--title-col",
            type=int,
            default=2,
            help="0-based column index that contains recipe title in DB language.",
        )
        parser.add_argument(
            "--match-mode",
            default="iexact",
            choices=["exact", "iexact", "contains"],
            help="How to match Recipe.title against CSV title.",
        )
        parser.add_argument(
            "--language",
            default=None,
            choices=["RUS", "ENG"],
            help="Optional: filter recipes by Recipe.language.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Do not update DB, only print what would be updated.",
        )

    def handle(self, *args, **options):
        delimiter_raw = options["delimiter"]
        delimiter = "\t" if delimiter_raw == r"\t" else delimiter_raw

        csv_path: str = options["csv_path"]
        photos_dir: str = options["photos_dir"]
        photo_id_col: int = options["photo_id_col"]
        title_col: int = options["title_col"]
        match_mode: str = options["match_mode"]
        language: Optional[str] = options["language"]
        dry_run: bool = options["dry_run"]

        if not os.path.isfile(csv_path):
            raise RuntimeError(f"--csv-path not found: {csv_path}")
        if not os.path.isdir(photos_dir):
            raise RuntimeError(f"--photos-dir not found: {photos_dir}")

        photo_map: Dict[int, str] = self._build_photo_map(photos_dir)
        if not photo_map:
            self.stdout.write(self.style.WARNING(f"No photo files found in {photos_dir}"))

        updated = 0
        missing_photo = 0
        missing_recipe = 0

        with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f, delimiter=delimiter)
            for i, row in enumerate(reader, start=1):
                if not row:
                    continue
                if len(row) <= max(photo_id_col, title_col):
                    continue

                photo_id_raw = (row[photo_id_col] or "").strip()
                title = (row[title_col] or "").strip()

                if not photo_id_raw.isdigit() or not title:
                    # Probably header or malformed row
                    continue

                photo_id = int(photo_id_raw)
                photo_path = photo_map.get(photo_id)
                if not photo_path:
                    missing_photo += 1
                    self.stdout.write(f"[row {i}] photo_id={photo_id} not found on disk (skip)")
                    continue

                qs = Recipe.objects.all()
                if language:
                    qs = qs.filter(language=language)

                if match_mode == "exact":
                    qs = qs.filter(title=title)
                elif match_mode == "iexact":
                    qs = qs.filter(title__iexact=title)
                else:
                    qs = qs.filter(title__icontains=title)

                recipes = list(qs)
                if not recipes:
                    missing_recipe += 1
                    self.stdout.write(f"[row {i}] recipe title not found in DB: {title!r} (skip)")
                    continue

                filename = os.path.basename(photo_path)
                with open(photo_path, "rb") as pf:
                    data = pf.read()

                if dry_run:
                    self.stdout.write(
                        f"DRY-RUN: would set Recipe.photo for {len(recipes)} recipe(s) "
                        f"title={title!r} from photo_id={photo_id} file={filename}"
                    )
                    updated += len(recipes)
                    continue

                content_file = ContentFile(data)
                for recipe in recipes:
                    recipe.photo.save(filename, content_file, save=True)
                    updated += 1

                self.stdout.write(
                    f"Updated {len(recipes)} recipe(s) title={title!r} photo_id={photo_id} file={filename}"
                )

        self.stdout.write(self.style.SUCCESS(f"Done. updated={updated}, missing_photo={missing_photo}, missing_recipe={missing_recipe}"))

    @staticmethod
    def _build_photo_map(photos_dir: str) -> Dict[int, str]:
        """
        Map: photo_id (digits prefix in filename) -> full path.
        If multiple files match the same id, choose the first with preferred extensions.
        """
        preferred_ext = {".jpg", ".jpeg", ".png", ".webp"}
        photo_map: Dict[int, str] = {}

        for root, _, files in os.walk(photos_dir):
            for filename in files:
                lower = filename.lower()
                if not any(lower.endswith(ext) for ext in preferred_ext):
                    continue
                m = re.match(r"^(\d+)", filename)
                if not m:
                    continue
                photo_id = int(m.group(1))
                full_path = os.path.join(root, filename)
                if photo_id not in photo_map:
                    photo_map[photo_id] = full_path
                else:
                    # keep existing (first) unless current has preferred ext and existing doesn't (rare)
                    pass

        return photo_map

