import re
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from blog.models import Post, Category


class Command(BaseCommand):
    help = "Load markdown posts from content/posts/ into the database"

    def handle(self, *args, **options):
        folder = Path("content/posts")
        if not folder.exists():
            self.stdout.write(self.style.ERROR(f"Folder not found: {folder}"))
            return

        files = list(folder.glob("*.md"))
        if not files:
            self.stdout.write(self.style.WARNING("No .md files found"))
            return

        created = 0
        updated = 0

        for path in sorted(files):
            text = path.read_text(encoding="utf-8")

            # Parse front matter
            match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
            if not match:
                self.stdout.write(self.style.WARNING(f"Skipped (no front matter): {path.name}"))
                continue

            front, body = match.groups()
            meta = {}
            for line in front.splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    meta[key.strip()] = value.strip()

            title = meta.get("title")
            category_name = meta.get("category", "Uncategorized")
            if not title:
                self.stdout.write(self.style.WARNING(f"Skipped (no title): {path.name}"))
                continue

            slug = slugify(title)
            category, _ = Category.objects.get_or_create(
                name=category_name,
                defaults={"slug": slugify(category_name)},
            )

            post, was_created = Post.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "category": category,
                    "content": body.strip(),
                    "status": "published",
                },
            )

            if was_created:
                created += 1
                self.stdout.write(f"Created: {title}")
            else:
                updated += 1
                self.stdout.write(f"Updated: {title}")

        self.stdout.write(
            self.style.SUCCESS(f"Done. Created: {created}, Updated: {updated}")
        )