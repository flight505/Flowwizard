import yaml
from pathlib import Path

def detect_project_type(project_dir: Path) -> str:
    if (project_dir / "package.json").exists() or (project_dir / "node_modules").exists():
        return "node"
    if (project_dir / "requirements.txt").exists() or (project_dir / "pyproject.toml").exists():
        return "python"
    return "unknown"

def load_config(config_file: Path, project_dir: Path) -> dict:
    if not config_file.exists():
        return _apply_defaults("auto", project_dir)

    with open(config_file, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)

    if not isinstance(config_data, dict):
        return _apply_defaults("auto", project_dir)

    # If user sets "use_auto_detection" or something, we could handle it here.
    # For now, just return config_data as is if valid.
    return config_data

def _apply_defaults(profile: str, project_dir: Path) -> dict:
    detected = detect_project_type(project_dir)
    if detected == "node":
        return {
            "tree_focus": ["app", "api"],
            "important_dirs": ["src", "lib", "public"],
            "exclude_dirs": ["node_modules", "dist", ".git"],
            "include_extensions": [".js", ".ts", ".json", ".md"],
            "max_depth": 3
        }
    elif detected == "python":
        return {
            "tree_focus": ["src", "scripts", "tests"],
            "important_dirs": ["notebooks", "data", "configs"],
            "exclude_dirs": ["__pycache__", "venv", ".git", ".ipynb_checkpoints"],
            "include_extensions": [".py", ".ipynb", ".md", ".yaml", ".yml"],
            "max_depth": 3
        }
    else:
        return {
            "tree_focus": ["src"],
            "important_dirs": [],
            "exclude_dirs": [".git"],
            "include_extensions": [".py", ".js", ".md", ".yaml", ".json"],
            "max_depth": 3
        }
