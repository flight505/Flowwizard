import yaml
from pathlib import Path
from typing import Dict, List, Optional

def detect_project_type(project_dir: Path) -> List[str]:
    """
    Detect project types based on key files in the directory.
    Returns a list of detected project types.
    """
    detected_types = []
    
    # Python detection
    python_files = [
        "requirements.txt",
        "setup.py",
        "pyproject.toml",
        "Pipfile",
        "poetry.lock"
    ]
    if any((project_dir / file).exists() for file in python_files) or list(project_dir.glob("**/*.py")):
        detected_types.append("python")
    
    # Node.js detection
    node_files = [
        "package.json",
        "tsconfig.json",
        "next.config.js",
        "webpack.config.js"
    ]
    if any((project_dir / file).exists() for file in node_files):
        detected_types.append("node")
    
    # Go detection
    go_files = ["go.mod", "go.sum"]
    if any((project_dir / file).exists() for file in go_files) or list(project_dir.glob("**/*.go")):
        detected_types.append("go")
    
    return detected_types

def merge_profile_settings(base: Dict, profile: Dict) -> Dict:
    """Merge profile settings with base settings."""
    result = base.copy()
    
    # Merge lists without duplicates
    for key in ["tree_focus", "important_dirs", "exclude_dirs", "include_extensions"]:
        if key in profile:
            result[key] = list(set(result.get(key, []) + profile[key]))
    
    return result

def load_config(config_file: Path, project_dir: Path) -> Dict:
    """
    Load and process the configuration file.
    Now supports language profiles and auto-detection.
    """
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Start with default settings
    result_config = config.get("default_settings", {}).copy()
    
    # Detect project types
    detected_types = detect_project_type(project_dir)
    
    # If no types detected, use default settings
    if not detected_types:
        return result_config
    
    # Merge settings from all detected profiles
    profiles = config.get("language_profiles", {})
    for project_type in detected_types:
        if project_type in profiles:
            profile_settings = profiles[project_type]
            result_config = merge_profile_settings(result_config, profile_settings)
    
    # Add detected types to config for reference
    result_config["detected_types"] = detected_types
    
    # Ensure max_depth is set
    result_config["max_depth"] = config.get("max_depth", 3)
    
    return result_config

def _apply_defaults(profile: str, project_dir: Path) -> dict:
    detected = detect_project_type(project_dir)
    if "node" in detected:
        return {
            "tree_focus": ["app", "api"],
            "important_dirs": ["src", "lib", "public"],
            "exclude_dirs": ["node_modules", "dist", ".git"],
            "include_extensions": [".js", ".ts", ".json", ".md"],
            "max_depth": 3
        }
    elif "python" in detected:
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
