import typer
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
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

FLOW_WIZARD_LOGO = """
███████╗██╗      ██████╗ ██╗    ██╗
██╔════╝██║     ██╔═══██╗██║    ██║
█████╗  ██║     ██║   ██║██║ █╗ ██║
██╔══╝  ██║     ██║   ██║██║███╗██║
██║     ███████╗╚██████╔╝╚███╔███╔╝
╚═╝     ╚══════╝ ╚═════╝  ╚══╝╚══╝ 
██╗    ██╗██╗███████╗ █████╗ ██████╗ ██████╗ 
██║    ██║██║╚══███╔╝██╔══██╗██╔══██╗██╔══██╗
██║ █╗ ██║██║  ███╔╝ ███████║██████╔╝██║  ██║
██║███╗██║██║ ███╔╝  ██╔══██║██╔══██╗██║  ██║
╚███╔███╔╝██║███████╗██║  ██║██║  ██║██████╔╝
 ╚══╝╚══╝ ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ 
"""

def display_welcome():
    """Display the welcome screen with the Flow Wizard logo"""
    logo_text = Text(FLOW_WIZARD_LOGO, style="bold cyan")
    welcome_panel = Panel(
        logo_text,
        title="[bold yellow]Welcome to Flow Wizard[/]",
        subtitle="[bold blue]by Flight 505[/]",
        border_style="cyan",
        padding=(1, 2),
    )
    console.print(welcome_panel)
    console.print("\n[bold yellow]Your AI-powered workflow assistant[/]\n")

@app.command()
def main_menu():
    """
    Main interactive menu for FlowWizard
    """
    display_welcome()
    
    while True:
        action = questionary.select(
            "Select an action:",
            choices=[
                "Generate Agents",
                "Configure Recurring Mode",
                "Exit"
            ],
            style=questionary.Style([
                ('qmark', 'fg:cyan bold'),
                ('question', 'bold'),
                ('pointer', 'fg:cyan bold'),
                ('highlighted', 'fg:cyan bold'),
                ('selected', 'fg:green'),
            ])
        ).ask()

        if action == "Generate Agents":
            _generate_agents()
        elif action == "Configure Recurring Mode":
            _configure_recurring()
        elif action == "Exit":
            console.print("\n[bold cyan]Thank you for using Flow Wizard! 👋[/]\n")
            break

def _generate_agents():
    try:
        console.print("\n[bold cyan]🤖 Agent Generation[/]\n")
        
        project_path_str = questionary.text(
            "Enter project path (or leave blank to use current directory, Ctrl+C to go back):",
            style=questionary.Style([
                ('qmark', 'fg:cyan bold'),
                ('question', 'bold'),
            ])
        ).ask()
        
        if project_path_str is None:  # User pressed Ctrl+C
            console.print("\n[yellow]↩️ Returning to main menu...[/]\n")
            return
            
        project_dir = Path(project_path_str.strip()) if project_path_str.strip() else Path.cwd()

        if not project_dir.exists():
            console.print(f"\n[bold red]❌ Error: Project directory {project_dir} does not exist.[/]")
            return

        config_dir = Path(__file__).parent
        config_file = config_dir / "config.yaml"
        config = load_config(config_file, project_dir)

        max_depth_str = questionary.text(
            "Enter max directory depth (default 3, Ctrl+C to go back):",
            style=questionary.Style([
                ('qmark', 'fg:cyan bold'),
                ('question', 'bold'),
            ])
        ).ask()
        
        if max_depth_str is None:  # User pressed Ctrl+C
            console.print("\n[yellow]↩️ Returning to main menu...[/]\n")
            return
            
        if max_depth_str.strip().isdigit():
            config["max_depth"] = int(max_depth_str.strip())
        else:
            config["max_depth"] = 3

        with console.status("[bold cyan]🔍 Analyzing project structure...[/]") as status:
            cursorrules_example = config_dir / ".cursorrules.example"
            project_cursorrules = project_dir / ".cursorrules"
            if cursorrules_example.exists() and not project_cursorrules.exists():
                shutil.copy2(cursorrules_example, project_cursorrules)
                console.print(f"[bold green]✨ Copied .cursorrules to {project_cursorrules}[/]")

            generator = ProjectTreeGenerator(project_dir, config_dir, config)
            focus_dirs = generator.find_focus_dirs(project_dir, config.get("tree_focus", []))

            processed_dirs = set()
            config_paths = {str(Path(fd)) for fd in config.get("tree_focus", [])}
            
            console.print("\n[bold cyan]📁 Processing directories:[/]")
            for focus_dir in focus_dirs:
                rel_path = focus_dir.relative_to(project_dir)
                if any(str(rel_path).startswith(str(pd)) for pd in processed_dirs):
                    continue

                console.print(f"[cyan]  ├─ Processing[/] [bold white]{rel_path}[/]")
                tree_content = generator.generate_tree(
                    focus_dir,
                    max_depth=config.get("max_depth", 3),
                    config_paths=config_paths
                )

                tree_file = config_dir / f"tree_{focus_dir.name}.txt"
                with open(tree_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(tree_content))

                processed_dirs.add(rel_path)

            console.print("[cyan]  └─ Generating agent files...[/]")
            generate_agent_files(
                [str(d.relative_to(project_dir)) for d in focus_dirs],
                config_dir,
                project_dir,
                config
            )
        
        console.print("\n[bold green]✅ Agent generation complete![/]\n")

    except KeyboardInterrupt:
        console.print("\n[yellow]↩️ Returning to main menu...[/]\n")
        return

def _configure_recurring():
    try:
        console.print("\n[bold cyan]⚙️  Recurring Mode Configuration[/]\n")
        
        minute_str = questionary.text(
            "Enter interval in minutes (default 1, Ctrl+C to go back):",
            style=questionary.Style([
                ('qmark', 'fg:cyan bold'),
                ('question', 'bold'),
            ])
        ).ask()
        
        if minute_str is None:  # User pressed Ctrl+C
            console.print("\n[yellow]↩️ Returning to main menu...[/]\n")
            return
            
        try:
            interval = int(minute_str)
        except:
            interval = 1

        project_path_str = questionary.text(
            "Enter project path (or leave blank to use current directory, Ctrl+C to go back):",
            style=questionary.Style([
                ('qmark', 'fg:cyan bold'),
                ('question', 'bold'),
            ])
        ).ask()
        
        if project_path_str is None:  # User pressed Ctrl+C
            console.print("\n[yellow]↩️ Returning to main menu...[/]\n")
            return
            
        project_dir = Path(project_path_str.strip()) if project_path_str.strip() else Path.cwd()

        if not project_dir.exists():
            console.print(f"\n[bold red]❌ Error: Project directory {project_dir} does not exist.[/]")
            return

        config_dir = Path(__file__).parent
        config_file = config_dir / "config.yaml"
        config = load_config(config_file, project_dir)

        cursorrules_example = config_dir / ".cursorrules.example"
        project_cursorrules = project_dir / ".cursorrules"
        if cursorrules_example.exists() and not project_cursorrules.exists():
            shutil.copy2(cursorrules_example, project_cursorrules)
            console.print(f"[bold green]✨ Copied .cursorrules to {project_cursorrules}[/]")

        console.print(f"\n[bold cyan]🔄 Starting recurring mode (interval: {interval} minutes)[/]")
        console.print("[yellow]Note: Press Ctrl+C to stop and return to main menu[/]\n")
        
        while True:
            try:
                with console.status("[bold cyan]🔍 Processing project...[/]") as status:
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
                    
                console.print("[bold green]✅ Agent generation cycle complete![/]")
                console.print(f"[cyan]⏰ Waiting {interval} minutes until next cycle...[/]")
                console.print("[yellow](Press Ctrl+C to stop and return to main menu)[/]\n")
                time.sleep(interval * 60)
                
            except KeyboardInterrupt:
                console.print("\n[yellow]↩️ Stopping recurring mode and returning to main menu...[/]\n")
                return

    except KeyboardInterrupt:
        console.print("\n[yellow]↩️ Returning to main menu...[/]\n")
        return

if __name__ == "__main__":
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[bold cyan]Thank you for using Flow Wizard! 👋[/]\n")
        sys.exit(0)
