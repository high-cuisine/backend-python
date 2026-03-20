import csv
import os
import re
from typing import Dict, Optional, Tuple

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.recipe.models import Recipe


class Command(BaseCommand):
    help = (
        "Copy Recipe.photo using mapping CSV by matching Recipe titles in DB.\n"
        "CSV headers expected: rus_id, eng_id, title_rus, title_eng, copy_from, copy_to.\n"
        "It finds:\n"
        "- RUS record by (language='RUS', title=title_rus) and assigns photo file named by copy_from id\n"
        "- ENG record by (language='ENG', title=title_eng) and assigns photo file named by copy_to id\n"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv-path",
            required=True,
            help="CSV path inside container.",
        )
        parser.add_argument(
            "--photos-dir",
            required=True,
            help="Directory inside container containing photos named like 2572.jpg etc.",
        )
        parser.add_argument(
            "--delimiter",
            default=",",
            help="CSV delimiter. Default ','.",
        )
        parser.add_argument(
            "--match-mode",
            default="iexact",
            choices=["exact", "iexact", "contains"],
            help="How to match Recipe.title against title_rus/title_eng.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Do not update DB, only print actions.",
        )
        parser.add_argument(
            "--language",
            default=None,
            choices=["RUS", "ENG"],
            help="Optional: update only one language.",
        )

    def handle(self, *args, **options):
        csv_path = options["csv_path"]
        photos_dir = options["photos_dir"]
        dry_run = bool(options["dry_run"])
        delimiter = options["delimiter"]
        match_mode = options["match_mode"]
        only_language = options["language"]

        if delimiter == r"\t":
            delimiter = "\t"

        if not os.path.isfile(csv_path):
            raise RuntimeError(f"--csv-path not found: {csv_path}")
        if not os.path.isdir(photos_dir):
            raise RuntimeError(f"--photos-dir not found: {photos_dir}")

        photo_map = self._build_photo_map(photos_dir)
        if not photo_map:
            self.stdout.write(self.style.WARNING(f"No photos found in {photos_dir}"))

        updated = 0
        missing_recipe = 0
        missing_photo = 0
        total = 0

        with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            required_headers = {"title_rus", "title_eng", "copy_from", "copy_to"}
            if not required_headers.issubset(set(reader.fieldnames or [])):
                raise RuntimeError(
                    f"CSV headers mismatch. Required: {sorted(required_headers)}. Found: {reader.fieldnames}"
                )

            for row in reader:
                total += 1
                title_rus = (row.get("title_rus") or "").strip()
                title_eng = (row.get("title_eng") or "").strip()
                copy_from = self._to_int(row.get("copy_from"))
                copy_to = self._to_int(row.get("copy_to"))

                if not copy_from and not copy_to:
                    continue

                if only_language in (None, "RUS") and title_rus and copy_from:
                    recipe = self._find_recipe(
                        language="RUS",
                        title=title_rus,
                        match_mode=match_mode,
                    )
                    photo_path = photo_map.get(copy_from)
                    if not recipe:
                        missing_recipe += 1
                        self.stdout.write(self.style.WARNING(f"RUS recipe not found: title={title_rus!r}"))
                    elif not photo_path:
                        missing_photo += 1
                        self.stdout.write(self.style.WARNING(f"Photo not found for copy_from={copy_from} (title={title_rus!r})"))
                    else:
                        self._assign_photo(recipe, photo_path, dry_run=dry_run)
                        updated += 1

                if only_language in (None, "ENG") and title_eng and copy_to:
                    recipe = self._find_recipe(
                        language="ENG",
                        title=title_eng,
                        match_mode=match_mode,
                    )
                    photo_path = photo_map.get(copy_to)
                    if not recipe:
                        missing_recipe += 1
                        self.stdout.write(self.style.WARNING(f"ENG recipe not found: title={title_eng!r}"))
                    elif not photo_path:
                        missing_photo += 1
                        self.stdout.write(self.style.WARNING(f"Photo not found for copy_to={copy_to} (title={title_eng!r})"))
                    else:
                        self._assign_photo(recipe, photo_path, dry_run=dry_run)
                        updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. total_rows={total}, updated={updated}, missing_recipe={missing_recipe}, missing_photo={missing_photo}"
            )
        )

    def _find_recipe(self, *, language: str, title: str, match_mode: str) -> Optional[Recipe]:
        qs = Recipe.objects.filter(language=language)
        if match_mode == "exact":
            return qs.filter(title=title).first()
        if match_mode == "iexact":
            return qs.filter(title__iexact=title).first()
        # contains
        return qs.filter(title__icontains=title).first()

    @staticmethod
    def _assign_photo(recipe: Recipe, photo_path: str, *, dry_run: bool) -> None:
        filename = os.path.basename(photo_path)
        if dry_run:
            # Print compact line only
            print(f"DRY-RUN: Recipe id={recipe.id} lang={recipe.language} <= {filename}")
            return

        with open(photo_path, "rb") as pf:
            content = pf.read()
        recipe.photo.save(filename, ContentFile(content), save=True)

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

