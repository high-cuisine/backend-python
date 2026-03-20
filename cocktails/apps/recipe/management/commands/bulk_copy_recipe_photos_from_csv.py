import csv
import os
import re
from typing import Dict, Optional

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.recipe.models import Recipe


class Command(BaseCommand):
    help = (
        "Copy photos into Recipe.photo using an id mapping CSV.\n"
        "Expects a tab-separated file with headers: rus_id, eng_id, copy_from, copy_to.\n"
        "For each row:\n"
        "- set Recipe(id=rus_id, language='RUS').photo from file named by copy_from.*\n"
        "- set Recipe(id=eng_id, language='ENG').photo from file named by copy_to.*"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv-path",
            required=True,
            help="CSV path inside container. Must have headers: rus_id, eng_id, copy_from, copy_to.",
        )
        parser.add_argument(
            "--photos-dir",
            required=True,
            help="Directory inside container with extracted photos. Filenames must start with numeric photo_id (e.g. 2572.jpg).",
        )
        parser.add_argument(
            "--delimiter",
            default="\\t",
            help=r"CSV delimiter. Default is tab: \t",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Do not write to DB, only print what would be updated.",
        )

    def handle(self, *args, **options):
        csv_path = options["csv_path"]
        photos_dir = options["photos_dir"]
        dry_run = bool(options["dry_run"])

        delimiter_raw = options["delimiter"]
        delimiter = "\t" if delimiter_raw == r"\t" else delimiter_raw

        if not os.path.isfile(csv_path):
            raise RuntimeError(f"--csv-path not found: {csv_path}")
        if not os.path.isdir(photos_dir):
            raise RuntimeError(f"--photos-dir not found: {photos_dir}")

        photo_map = self._build_photo_map(photos_dir)
        if not photo_map:
            self.stdout.write(self.style.WARNING(f"No photo files found in {photos_dir}"))

        updated = 0
        missing_files = 0
        missing_recipes = 0
        total_rows = 0

        with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            required_headers = {"rus_id", "eng_id", "copy_from", "copy_to"}
            if not required_headers.issubset(set(reader.fieldnames or [])):
                raise RuntimeError(
                    f"CSV headers mismatch. Required: {sorted(required_headers)}. Found: {reader.fieldnames}"
                )

            for row in reader:
                total_rows += 1
                rus_id = self._to_int(row.get("rus_id"))
                eng_id = self._to_int(row.get("eng_id"))
                copy_from = self._to_int(row.get("copy_from"))
                copy_to = self._to_int(row.get("copy_to"))

                if rus_id is None or eng_id is None or copy_from is None or copy_to is None:
                    self.stdout.write(f"[row {total_rows}] skip: some ids are empty: {row}")
                    continue

                # Update RUS record
                self._update_one(
                    target_id=rus_id,
                    language="RUS",
                    photo_id=copy_from,
                    photo_map=photo_map,
                    dry_run=dry_run,
                )
                # Update ENG record
                self._update_one(
                    target_id=eng_id,
                    language="ENG",
                    photo_id=copy_to,
                    photo_map=photo_map,
                    dry_run=dry_run,
                )

        # Note: _update_one prints details; for compact counters we rely on its return values.
        self.stdout.write(self.style.SUCCESS(
            f"Done. Processed rows={total_rows}. "
            f"(See log above for skips/missing items.)"
        ))

    def _update_one(
        self,
        *,
        target_id: int,
        language: str,
        photo_id: int,
        photo_map: Dict[int, str],
        dry_run: bool,
    ) -> None:
        recipe = Recipe.objects.filter(id=target_id, language=language).first()
        if recipe is None:
            self.stdout.write(self.style.WARNING(
                f"Recipe not found: id={target_id} lang={language} (skip)"
            ))
            return

        photo_path = photo_map.get(photo_id)
        if not photo_path:
            self.stdout.write(self.style.WARNING(
                f"Photo file not found for photo_id={photo_id} (skip)."
            ))
            return

        filename = os.path.basename(photo_path)
        if dry_run:
            self.stdout.write(
                f"DRY-RUN: Recipe id={target_id} lang={language} <= file={filename}"
            )
            return

        with open(photo_path, "rb") as pf:
            data = pf.read()
        content_file = ContentFile(data)
        recipe.photo.save(filename, content_file, save=True)
        self.stdout.write(self.style.SUCCESS(
            f"Updated Recipe id={target_id} lang={language} with file={filename}"
        ))

    @staticmethod
    def _to_int(v: Optional[str]) -> Optional[int]:
        if v is None:
            return None
        s = str(v).strip()
        if not s:
            return None
        try:
            return int(s)
        except ValueError:
            return None

    @staticmethod
    def _build_photo_map(photos_dir: str) -> Dict[int, str]:
        preferred_ext = {".jpg", ".jpeg", ".png", ".webp"}
        photo_map: Dict[int, str] = {}
        id_re = re.compile(r"^(\d+)")

        for root, _, files in os.walk(photos_dir):
            for filename in files:
                lower = filename.lower()
                if not any(lower.endswith(ext) for ext in preferred_ext):
                    continue
                m = id_re.match(filename)
                if not m:
                    continue
                photo_id = int(m.group(1))
                full_path = os.path.join(root, filename)
                if photo_id not in photo_map:
                    photo_map[photo_id] = full_path

        return photo_map

