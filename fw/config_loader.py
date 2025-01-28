import yaml
from pathlib import Path
from typing import List, Optional
from .profiles import LANGUAGE_PROFILES, get_profile, merge_profiles

def detect_project_types(project_dir: Path) -> List[str]:
    """Detect all language profiles that match the project."""
    detected_types = []
    
    for lang, profile in LANGUAGE_PROFILES.items():
        if any((project_dir / file).exists() for file in profile["detection_files"]):
            detected_types.append(lang)
    
    return detected_types or ["python"]  # Default to python if nothing detected

def load_config(config_file: Path, project_dir: Path) -> dict:
    """Load configuration with support for language profiles."""
    config_data = {}
    
    # Try to load user's config file
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f) or {}
    
    # Handle profiles in config
    profiles = config_data.get("profiles", [])
    if not profiles:
        # Auto-detect if no profiles specified
        profiles = detect_project_types(project_dir)
    
    # Get base config from profiles
    base_config = merge_profiles(profiles)
    
    # Override with user's custom settings
    for key in ["tree_focus", "important_dirs", "exclude_dirs", "include_extensions", "max_depth"]:
        if key in config_data:
            if isinstance(config_data[key], list):
                # For lists, extend the base config
                base_config[key].extend(config_data[key])
                # Remove duplicates while preserving order
                base_config[key] = list(dict.fromkeys(base_config[key]))
            else:
                # For non-lists (like max_depth), just override
                base_config[key] = config_data[key]
    
    # Add custom domain patterns if specified
    if "domain_patterns" in config_data:
        base_config["domain_patterns"].update(config_data["domain_patterns"])
    
    # Store detected/specified profiles in config
    base_config["detected_profiles"] = profiles
    
    return base_config

def create_default_config(project_dir: Path, profiles: Optional[List[str]] = None) -> dict:
    """Create a default config file for the project."""
    if profiles is None:
        profiles = detect_project_types(project_dir)
    
    config = merge_profiles(profiles)
    config["profiles"] = profiles
    
    return config

def save_config(config: dict, config_file: Path) -> None:
    """Save configuration to a file."""
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)
