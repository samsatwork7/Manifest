from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

class RichProgress:
    """Unified Rich-based progress manager"""

    def __init__(self):
        self.console = Console()
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}" if "{task.total}" else ""),
            TimeElapsedColumn(),
            expand=True,
        )
        self.tasks = {}

    def __enter__(self):
        self.progress.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.progress.stop()

    def add_task(self, name, description, total=0):
        task_id = self.progress.add_task(description, total=total)
        self.tasks[name] = task_id

    def update(self, name, advance=1, total=None, description=None):
        tid = self.tasks[name]
        self.progress.update(tid, advance=advance,
                             total=total if total else self.progress.tasks[tid].total,
                             description=description if description else self.progress.tasks[tid].description)

    def complete(self, name, description=None):
        tid = self.tasks[name]
        self.progress.update(tid, completed=100, total=100,
                             description=description or self.progress.tasks[tid].description)
