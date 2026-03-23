import csv
import os
import re
from dataclasses import dataclass
from typing import Iterable, Optional, Tuple

import requests
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.recipe.models import Recipe, Tool


@dataclass(frozen=True)
class PhotoTarget:
    obj_id: int
    photo_source: str  # local path or http(s) url


class Command(BaseCommand):
    help = "Bulk update Recipe.photo/Tool.photo from local files or URLs"

    def add_arguments(self, parser):
        parser.add_argument(
            "--model",
            choices=["recipe", "tool"],
            default="recipe",
            help="Which model field to update (photo).",
        )
        parser.add_argument(
            "--source-dir",
            default="/cocktails/tmp/bulk_photos",
            help="Where local files live (used when mapping paths are relative).",
        )
        parser.add_argument(
            "--mapping",
            default=None,
            help="Optional CSV file: columns like (id, path_or_url).",
        )
        parser.add_argument(
            "--id-regex",
            default=r"^([0-9]+)",
            help="Used when --mapping is not provided. Extract object id from filename.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Do not save to DB, only print what would be updated.",
        )

    def handle(self, *args, **options):
        model = options["model"]
        source_dir = options["source_dir"]
        mapping_path = options["mapping"]
        id_regex = re.compile(options["id_regex"])
        dry_run = options["dry_run"]

        if model == "recipe":
            targets = self._collect_targets_from_mapping_or_dir(
                mapping_path=mapping_path,
                source_dir=source_dir,
                id_regex=id_regex,
                expected_prefix="recipe",
            )
            self._bulk_update_recipe_photos(targets=targets, source_dir=source_dir, dry_run=dry_run)
        elif model == "tool":
            targets = self._collect_targets_from_mapping_or_dir(
                mapping_path=mapping_path,
                source_dir=source_dir,
                id_regex=id_regex,
                expected_prefix="tool",
            )
            self._bulk_update_tool_photos(targets=targets, source_dir=source_dir, dry_run=dry_run)

    def _collect_targets_from_mapping_or_dir(
        self,
        *,
        mapping_path: Optional[str],
        source_dir: str,
        id_regex: re.Pattern,
        expected_prefix: str,
    ) -> Iterable[PhotoTarget]:
        if mapping_path:
            yield from self._collect_targets_from_csv(mapping_path=mapping_path, source_dir=source_dir)
            return

        if not os.path.isdir(source_dir):
            raise RuntimeError(f"--source-dir does not exist: {source_dir}")

        for root, _, files in os.walk(source_dir):
            for filename in files:
                # Skip non-images quickly (we don't enforce strict types, but keep noise down).
                if not filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                    continue
                m = id_regex.search(filename)
                if not m:
                    continue
                obj_id = int(m.group(1))
                full_path = os.path.join(root, filename)
                self.stdout.write(f"Found {expected_prefix} id={obj_id} file={full_path}")
                yield PhotoTarget(obj_id=obj_id, photo_source=full_path)

    def _collect_targets_from_csv(self, *, mapping_path: str, source_dir: str) -> Iterable[PhotoTarget]:
        if not os.path.isfile(mapping_path):
            raise RuntimeError(f"--mapping does not exist: {mapping_path}")

        with open(mapping_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        if not rows:
            return []

        # Detect header by first row non-numeric first column.
        start_idx = 0
        if rows and rows[0] and not rows[0][0].strip().isdigit():
            start_idx = 1

        for row in rows[start_idx:]:
            if not row or len(row) < 2:
                continue
            obj_id_raw, src = row[0].strip(), row[1].strip()
            if not obj_id_raw.isdigit():
                continue
            obj_id = int(obj_id_raw)
            # If the path is relative - resolve it inside source_dir.
            if not (src.startswith("http://") or src.startswith("https://")) and not os.path.isabs(src):
                src = os.path.join(source_dir, src)
            yield PhotoTarget(obj_id=obj_id, photo_source=src)

    def _bulk_update_recipe_photos(self, *, targets: Iterable[PhotoTarget], source_dir: str, dry_run: bool):
        updated = 0
        skipped = 0

        for t in targets:
            try:
                recipe = Recipe.objects.get(id=t.obj_id)
            except Recipe.DoesNotExist:
                skipped += 1
                self.stdout.write(self.style.WARNING(f"Recipe id={t.obj_id} not found, skip"))
                continue

            # Assign file to ImageField
            photo_name_hint = self._guess_filename_from_source(t.photo_source, prefix=f"recipe_{t.obj_id}")
            content_file, filename = self._read_content_as_django_file(photo_source=t.photo_source, fallback_filename=photo_name_hint)

            if dry_run:
                self.stdout.write(f"DRY-RUN: update Recipe id={t.obj_id} photo={filename}")
                continue

            recipe.photo.save(filename, content_file, save=True)
            updated += 1

        self.stdout.write(self.style.SUCCESS(f"Recipe photos updated={updated}, skipped={skipped}"))

    def _bulk_update_tool_photos(self, *, targets: Iterable[PhotoTarget], source_dir: str, dry_run: bool):
        updated = 0
        skipped = 0

        for t in targets:
            try:
                tool = Tool.objects.get(id=t.obj_id)
            except Tool.DoesNotExist:
                skipped += 1
                self.stdout.write(self.style.WARNING(f"Tool id={t.obj_id} not found, skip"))
                continue

            photo_name_hint = self._guess_filename_from_source(t.photo_source, prefix=f"tool_{t.obj_id}")
            content_file, filename = self._read_content_as_django_file(photo_source=t.photo_source, fallback_filename=photo_name_hint)

            if dry_run:
                self.stdout.write(f"DRY-RUN: update Tool id={t.obj_id} photo={filename}")
                continue

            tool.photo.save(filename, content_file, save=True)
            updated += 1

        self.stdout.write(self.style.SUCCESS(f"Tool photos updated={updated}, skipped={skipped}"))

    @staticmethod
    def _guess_filename_from_source(photo_source: str, *, prefix: str) -> str:
        if photo_source.startswith("http://") or photo_source.startswith("https://"):
            # URL path might contain filename; otherwise fallback.
            basename = os.path.basename(photo_source.split("?")[0].rstrip("/"))
            return basename if basename else f"{prefix}.jpg"
        basename = os.path.basename(photo_source)
        return basename if basename else f"{prefix}.jpg"

    @staticmethod
    def _resolve_local_photo_path(photo_source: str) -> str:
        """If path has no extension and the file is missing, try .jpg / .jpeg / .png / .webp."""
        if photo_source.startswith("http://") or photo_source.startswith("https://"):
            return photo_source
        if os.path.isfile(photo_source):
            return photo_source
        base = os.path.basename(photo_source)
        if "." in base:
            return photo_source
        for ext in (".jpg", ".jpeg", ".png", ".webp"):
            candidate = photo_source + ext
            if os.path.isfile(candidate):
                return candidate
        return photo_source

    @staticmethod
    def _read_content_as_django_file(*, photo_source: str, fallback_filename: str) -> Tuple[File, str]:
        """
        Returns: (ContentFile-like object, filename)
        """
        if photo_source.startswith("http://") or photo_source.startswith("https://"):
            resp = requests.get(photo_source, stream=True, timeout=60)
            resp.raise_for_status()
            filename = Command._guess_filename_from_source(photo_source, prefix=fallback_filename)
            return ContentFile(resp.content), filename

        photo_source = Command._resolve_local_photo_path(photo_source)
        filename = os.path.basename(photo_source) or fallback_filename
        with open(photo_source, "rb") as f:
            # ContentFile copies bytes; simplest/robust for many files.
            data = f.read()
        return ContentFile(data), filename

