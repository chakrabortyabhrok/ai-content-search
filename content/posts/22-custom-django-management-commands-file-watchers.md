---
title: Custom Django Management Commands and File Watchers
category: Tooling
status: published
---
## Commands for one-off and repeated work
Management commands are the right place for tasks that should run outside the request cycle: importing a folder of markdown files, rebuilding a search index, or back-filling a new column. A command can be called from the shell, from a cron job, or from a process manager. It receives arguments, talks to the database, and exits with a clear status code.

Keep each command focused. One command imports posts. Another re-indexes a single post or the whole corpus. A third watches a directory. Small commands are easier to test and easier to call from scripts.

## Accepting paths and options
Use `add_arguments` to accept a directory path, a post id, or a `--force` flag. Inside `handle`, resolve the path, check that it exists, and then do the work. Print short progress messages so a developer watching the terminal knows the command is still running. Raise `CommandError` for bad input so the process exits with a non-zero code.

When the command processes many files, wrap the main loop in a transaction only if the whole batch must succeed or fail together. For independent files, commit after each successful file so a later failure does not roll back earlier work.

```python
from django.core.management.base import BaseCommand, CommandError
from pathlib import Path

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("directory", type=str)
        parser.add_argument("--force", action="store_true")

    def handle(self, *args, **options):
        root = Path(options["directory"])
        if not root.is_dir():
            raise CommandError(f"Not a directory: {root}")
        for path in root.rglob("*.md"):
            self.stdout.write(f"Processing {path.name}")
            # import or re-index logic here
```

## File watchers for local development
During development it is useful to re-index a post the moment its markdown file changes. A simple watcher can use the `watchdog` library or even a short polling loop. The watcher lives in its own management command so it can be started with `python manage.py watch_posts` and stopped with Ctrl-C.

The watcher should debounce rapid saves. Many editors write the file twice or touch a temporary file first. Wait a few hundred milliseconds of quiet before treating the change as final, then call the same import or re-index function the batch command uses. Sharing that function keeps the two entry points consistent.

## Running under process managers
In production the watcher is usually unnecessary; content changes go through the admin or an API. The batch commands, however, still need to run. Call them from a cron entry, a systemd timer, or a one-off container in the same Docker Compose file that runs the web process. Pass the same environment variables so the command sees the correct database and any API keys.

Log the command’s stdout and stderr. A failed import should be visible the next time you check the server, not only when a user reports a missing post.

## What good looks like
A developer can drop a new markdown file into a folder, run one command, and see the post appear with its search rows created. The same command can be scheduled at night to catch any files added by other means. Starting the watcher locally re-indexes a post within a second of saving it in an editor. If the import logic exists only inside the command and cannot be called from a view or a test, or if a file change is missed because the watcher reacts to every temporary write, the shared function or the debounce logic needs another look.