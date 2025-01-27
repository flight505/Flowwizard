from pathlib import Path
from gitignore_parser import parse_gitignore

class ProjectTreeGenerator:
    def __init__(self, project_root: Path, config_dir: Path, config: dict):
        self.project_root = project_root
        self.config_dir = config_dir
        self.include_extensions = set(config.get("include_extensions", []))
        self.important_dirs = set(config.get("important_dirs", []))
        self.exclude_dirs = set(config.get("exclude_dirs", []))

        gitignore_path = project_root / ".gitignore"
        if gitignore_path.exists():
            self.matches = parse_gitignore(gitignore_path)
        else:
            temp_ignore = project_root / ".temp_gitignore"
            with open(temp_ignore, 'w', encoding='utf-8') as f:
                for e in self.exclude_dirs:
                    f.write(f"{e}/\n")
            self.matches = parse_gitignore(temp_ignore)
            temp_ignore.unlink()

    def generate_tree(self, directory: Path, max_depth: int = 3, config_paths: set = None):
        tree_lines = []

        def _generate(dir_path: Path, prefix: str = "", depth: int = 0):
            if depth > max_depth:
                return

            items = sorted(list(dir_path.iterdir()), key=lambda x: (not x.is_file(), x.name))
            for i, item in enumerate(items):
                rel_path = str(item.relative_to(self.project_root))
                if item.is_dir():
                    if item.name in self.exclude_dirs or self.matches(str(item)):
                        continue
                    if config_paths and any(cp.startswith(rel_path) for cp in config_paths if cp != rel_path):
                        continue
                    is_last = i == len(items) - 1
                    tree_lines.append(f"{prefix}{'└── ' if is_last else '├── '}{item.name}/")
                    _generate(item, prefix + ("    " if is_last else "│   "), depth + 1)
                else:
                    if any(item.name.endswith(ext) for ext in self.include_extensions):
                        is_last = i == len(items) - 1
                        tree_lines.append(f"{prefix}{'└── ' if is_last else '├── '}{item.name}")

        _generate(directory)
        return tree_lines

    def find_focus_dirs(self, directory: Path, focus_dirs: list):
        found_dirs = []
        for fd in focus_dirs:
            path_candidate = directory / fd
            if path_candidate.exists() and path_candidate.is_dir():
                found_dirs.append(path_candidate)
        return found_dirs
