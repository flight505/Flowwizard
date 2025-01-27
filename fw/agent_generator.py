from pathlib import Path

def generate_agent_files(focus_dirs, config_dir: Path, project_dir: Path, config: dict):
    created_files = set()
    for dir_path in focus_dirs:
        try:
            dir_obj = Path(dir_path)
            agent_name = _build_agent_filename(dir_obj)
            if agent_name in created_files:
                continue

            tree_file = config_dir / f"tree_{dir_obj.name}.txt"
            tree_content = ""
            if tree_file.exists():
                with open(tree_file, 'r', encoding='utf-8') as f:
                    tree_content = f.read()

            description = f"the {dir_obj.name} directory"
            if dir_obj.parent != Path('.'):
                description = f"the {dir_obj.name} directory within {dir_obj.parent}"

            agent_content = f"""You are an agent specialized in {description} of this project.

Your focus directory structure:

{tree_content}

Only reference and modify files within this directory unless explicitly allowed otherwise.
"""

            output_path = project_dir / agent_name
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(agent_content)
            created_files.add(agent_name)
        except Exception:
            continue

def _build_agent_filename(dir_obj: Path):
    parts = list(dir_obj.parts)
    if len(parts) > 1:
        joined = "_".join(parts)
        return f"agent_{joined}.md"
    else:
        return f"agent_{parts[0]}.md"
