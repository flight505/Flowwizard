"""Language profiles for FlowWizard."""
from typing import Dict, Any

LANGUAGE_PROFILES: Dict[str, Dict[str, Any]] = {
    "python": {
        "name": "Python",
        "tree_focus": ["src", "scripts", "tests"],
        "important_dirs": ["notebooks", "data", "configs"],
        "exclude_dirs": ["__pycache__", "venv", ".venv", ".git", ".ipynb_checkpoints", "build", "dist", "*.egg-info"],
        "include_extensions": [".py", ".ipynb", ".pyi", ".md", ".yaml", ".yml", ".toml"],
        "detection_files": ["requirements.txt", "pyproject.toml", "setup.py"],
        "max_depth": 3,
        "domain_patterns": {
            "backend": ["api", "server", "services"],
            "data": ["data", "models", "db", "database"],
            "scripts": ["scripts", "tools", "utils"],
            "tests": ["tests", "test"]
        }
    },
    "node": {
        "name": "Node.js",
        "tree_focus": ["src", "app", "api"],
        "important_dirs": ["components", "pages", "public", "lib"],
        "exclude_dirs": ["node_modules", "dist", ".git", ".next", "build", "coverage"],
        "include_extensions": [".js", ".jsx", ".ts", ".tsx", ".json", ".md"],
        "detection_files": ["package.json", "package-lock.json", "yarn.lock"],
        "max_depth": 3,
        "domain_patterns": {
            "frontend": ["components", "pages", "views", "ui"],
            "backend": ["api", "server", "services"],
            "shared": ["lib", "utils", "helpers"],
            "tests": ["tests", "test", "__tests__"]
        }
    },
    "go": {
        "name": "Go",
        "tree_focus": ["cmd", "internal", "pkg"],
        "important_dirs": ["api", "docs", "examples"],
        "exclude_dirs": [".git", "vendor", "bin"],
        "include_extensions": [".go", ".mod", ".sum", ".md"],
        "detection_files": ["go.mod", "go.sum"],
        "max_depth": 3,
        "domain_patterns": {
            "cmd": ["cmd"],
            "internal": ["internal"],
            "pkg": ["pkg"],
            "api": ["api"],
            "tests": ["test"]
        }
    },
    "rust": {
        "name": "Rust",
        "tree_focus": ["src", "examples", "tests"],
        "important_dirs": ["benches", "docs"],
        "exclude_dirs": [".git", "target"],
        "include_extensions": [".rs", ".toml", ".md"],
        "detection_files": ["Cargo.toml", "Cargo.lock"],
        "max_depth": 3,
        "domain_patterns": {
            "src": ["src"],
            "examples": ["examples"],
            "tests": ["tests"],
            "benches": ["benches"]
        }
    }
}

def get_profile(name: str) -> Dict[str, Any]:
    """Get a language profile by name."""
    return LANGUAGE_PROFILES.get(name, LANGUAGE_PROFILES["python"])

def list_profiles() -> list[str]:
    """List all available language profiles."""
    return list(LANGUAGE_PROFILES.keys())

def merge_profiles(profiles: list[str]) -> Dict[str, Any]:
    """Merge multiple language profiles into one configuration."""
    merged = {
        "tree_focus": [],
        "important_dirs": [],
        "exclude_dirs": [],
        "include_extensions": [],
        "domain_patterns": {},
        "max_depth": 3
    }
    
    for profile_name in profiles:
        profile = get_profile(profile_name)
        merged["tree_focus"].extend(profile["tree_focus"])
        merged["important_dirs"].extend(profile["important_dirs"])
        merged["exclude_dirs"].extend(profile["exclude_dirs"])
        merged["include_extensions"].extend(profile["include_extensions"])
        merged["domain_patterns"].update(profile["domain_patterns"])
    
    # Remove duplicates while preserving order
    merged["tree_focus"] = list(dict.fromkeys(merged["tree_focus"]))
    merged["important_dirs"] = list(dict.fromkeys(merged["important_dirs"]))
    merged["exclude_dirs"] = list(dict.fromkeys(merged["exclude_dirs"]))
    merged["include_extensions"] = list(dict.fromkeys(merged["include_extensions"]))
    
    return merged 