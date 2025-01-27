import typer
import questionary
from rich.console import Console
from typing import Optional, List

import sys
import time
import shutil
from pathlib import Path

from fw.config_loader import load_config, detect_project_type
from fw.project_tree_generator import ProjectTreeGenerator
from fw.agent_generator import generate_agent_files

app = typer.Typer()
console = Console()

@app.command()
def main_menu():
    """
    Main interactive menu for FlowWizard
    """
    while True:
        action = questionary.select(
            "Select an action:",
            choices=[
                "Generate Agents",
                "Configure Recurring Mode",
                "Exit"
            ],
        ).ask()

        if action == "Generate Agents":
            _generate_agents()
        elif action == "Configure Recurring Mode":
            _configure_recurring()
        elif action == "Exit":
            break

def _generate_agents():
    project_path_str = questionary.text(
        "Enter project path (or leave blank to use current directory):"
    ).ask()
    project_dir = Path(project_path_str.strip()) if project_path_str.strip() else Path.cwd()

    if not project_dir.exists():
        console.print(f"[red]Error: Project directory {project_dir} does not exist.")
        return

    config_dir = Path(__file__).parent
    config_file = config_dir / "config.yaml"
    config = load_config(config_file, project_dir)

    max_depth_str = questionary.text(
        "Enter max directory depth (default 3):"
    ).ask()
    if max_depth_str.strip().isdigit():
        config["max_depth"] = int(max_depth_str.strip())
    else:
        config["max_depth"] = 3

    cursorrules_example = config_dir / ".cursorrules.example"
    project_cursorrules = project_dir / ".cursorrules"
    if cursorrules_example.exists() and not project_cursorrules.exists():
        shutil.copy2(cursorrules_example, project_cursorrules)
        console.print(f"[green]Copied .cursorrules to {project_cursorrules}")

    generator = ProjectTreeGenerator(project_dir, config_dir, config)
    focus_dirs = generator.find_focus_dirs(project_dir, config.get("tree_focus", []))

    processed_dirs = set()
    config_paths = {str(Path(fd)) for fd in config.get("tree_focus", [])}
    for focus_dir in focus_dirs:
        rel_path = focus_dir.relative_to(project_dir)
        if any(str(rel_path).startswith(str(pd)) for pd in processed_dirs):
            continue

        tree_content = generator.generate_tree(
            focus_dir,
            max_depth=config.get("max_depth", 3),
            config_paths=config_paths
        )

        tree_file = config_dir / f"tree_{focus_dir.name}.txt"
        with open(tree_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(tree_content))

        processed_dirs.add(rel_path)

    generate_agent_files(
        [str(d.relative_to(project_dir)) for d in focus_dirs],
        config_dir,
        project_dir,
        config
    )
    console.print("[green]Agent generation complete.")

def _configure_recurring():
    minute_str = questionary.text("Enter interval in minutes (default 1):").ask()
    try:
        interval = int(minute_str)
    except:
        interval = 1

    project_path_str = questionary.text(
        "Enter project path (or leave blank to use current directory):"
    ).ask()
    project_dir = Path(project_path_str.strip()) if project_path_str.strip() else Path.cwd()

    if not project_dir.exists():
        console.print(f"[red]Error: Project directory {project_dir} does not exist.")
        return

    config_dir = Path(__file__).parent
    config_file = config_dir / "config.yaml"
    config = load_config(config_file, project_dir)

    cursorrules_example = config_dir / ".cursorrules.example"
    project_cursorrules = project_dir / ".cursorrules"
    if cursorrules_example.exists() and not project_cursorrules.exists():
        shutil.copy2(cursorrules_example, project_cursorrules)
        console.print(f"[green]Copied .cursorrules to {project_cursorrules}")

    while True:
        generator = ProjectTreeGenerator(project_dir, config_dir, config)
        focus_dirs = generator.find_focus_dirs(project_dir, config.get("tree_focus", []))

        processed_dirs = set()
        config_paths = {str(Path(fd)) for fd in config.get("tree_focus", [])}
        for focus_dir in focus_dirs:
            rel_path = focus_dir.relative_to(project_dir)
            if any(str(rel_path).startswith(str(pd)) for pd in processed_dirs):
                continue

            tree_content = generator.generate_tree(
                focus_dir,
                max_depth=config.get("max_depth", 3),
                config_paths=config_paths
            )
            tree_file = config_dir / f"tree_{focus_dir.name}.txt"
            with open(tree_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(tree_content))

            processed_dirs.add(rel_path)

        generate_agent_files(
            [str(d.relative_to(project_dir)) for d in focus_dirs],
            config_dir,
            project_dir,
            config
        )
        console.print("[green]Agent generation cycle complete.")
        time.sleep(interval * 60)

if __name__ == "__main__":
    app()
