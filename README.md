# FlowWizard

A sophisticated **multi-domain** tool for managing AI agents in complex codebases through **intelligent file-tree partitioning**. It prevents conflicts and maintains coherence by creating **clear boundaries** for each AI assistant, allowing you to **focus** on specific areas (frontend, backend, data, etc.) without stepping on each other’s toes.

---

## Overview

FlowWizard tackles the challenge of coordinating multiple AI assistants in large, polyglot (Node/Python/other) projects by:

1. **Creating distinct domains** (frontend, backend, data, scripts, etc.)
2. **Generating domain-specific context files** for each area
3. **Enforcing strict boundaries** through file-tree partitioning rules
4. **Providing clear domain rules** and context prompts for each AI assistant
5. **Auto-detecting** whether a project is Node or Python (optional) and applying **sensible defaults** if a config is missing
6. **Recursively** or **on-demand** updating agent files to always reflect the current directory structure

**Key features and changes** from earlier versions:

-  **Flexible `config.yaml`**: Provide one config for Node, Python, or both.  
-  **Optional Auto-Detection**: If no config is found, FlowWizard intelligently checks for `package.json` or `requirements.txt` to pick a default profile.  
-  **Separated config directory** (where FlowWizard lives) from the target project directory (where agents and tree files are generated).  
-  **Automatic copying** of `.cursorrules` to the project directory for AI-friendly IDE boundary enforcement.  
-  **Recurring Mode**: Auto-regenerate domain files every X minutes (configurable).  
-  **Interactive CLI** using [Typer](https://typer.tiangolo.com/), [Questionary](https://github.com/tmbo/questionary), and [Rich](https://github.com/Textualize/rich) for a user-friendly experience.  
-  **Integration** with [uv](https://github.com/varsion/uv) for quick local or ephemeral installations.

---

## Usage Instructions 🛠️

### 1. Clone the Repository

```bash
git clone https://github.com/flight505/Flowwizard.git
cd Flowwizard
```

### 2. Set Up the Environment (Using uv)

```bash
uv sync
```

Alternatively, use a standard Python virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the CLI in Interactive Mode

You can now launch the main menu:

```bash
uv python -m flowwizard.cli main-menu
```

or without uv:

```bash
python -m flowwizard.cli main-menu
```

You’ll see an interactive menu asking whether you want to Generate Agents or Configure Recurring Mode, etc.

### Ephemeral Installation with uvx

Don’t want to install FlowWizard permanently? You can use uvx to install it from Git and run it on the fly, removing it afterward (but caching for faster future runs):

```bash
uvx --from git+https://github.com/flight505/Flowwizard@main flowwizard main-menu
```

This command will:
-  Clone & install FlowWizard in a temporary environment.
-  Run the main-menu command.
-  Tear down the environment, leaving only a cache so subsequent uses are faster.

### What FlowWizard Will Do 🔧

-  Creates/Updates “Domain Agents” in your project directory (e.g., agent_frontend.md, agent_backend.md, etc.).
-  Generates a hierarchical tree (e.g., tree_backend.txt) for each domain in the FlowWizard folder, capturing the code structure relevant to that domain.
-  Copies .cursorrules from the FlowWizard directory to your project if it doesn’t already exist (helpful for Cursor IDE).
-  (Optional) Recurring Mode: Re-runs the partitioning process every N minutes, ensuring your domain agents are always fresh.

### Configuration

**config.yaml**

FlowWizard looks for config.yaml in the same directory as the tool (i.e., Flowwizard/). If found, it uses your definitions. If no config is found, FlowWizard attempts to auto-detect Node or Python project defaults.

A sample config.yaml:

```yaml
project_title: "my-project"

tree_focus:
  - "frontend"     # UI components
  - "backend"      # API services
  - "database"     # Data layer
  - "shared"       # Common utilities

important_dirs:
  - "app"
  - "src"
  - "tests"

exclude_dirs:
  - "node_modules"
  - "dist"
  - "build"
  - "__pycache__"
  - "venv"
  - ".git"

include_extensions:
  - ".py"
  - ".js"
  - ".ts"
  - ".md"
  - ".json"

max_depth: 3
```

FlowWizard uses these keys:
-  **tree_focus**: A list of top-level (or nested) directories you want to partition out.
-  **important_dirs**: Additional directories the tree generator should always include.
-  **exclude_dirs**: Directories to skip entirely.
-  **include_extensions**: File types to include in the generated tree.
-  **max_depth**: How deeply to recurse when building the directory tree.

### Running with a Project Path

Instead of letting the CLI prompt you, you can also pass arguments to main.py (if you’re using a direct Python script approach). For instance:

```bash
python main.py --project-path /Users/Projects/YourProject
```

Or recurring:

```bash
python main.py --recurring --project-path /Users/Projects/YourProject
```

### Generated Agents

FlowWizard automatically creates one .md file per domain under your project directory. For example, if your config has:

```yaml
tree_focus:
  - frontend
  - backend
  - shared
```

You’ll see:
-  agent_frontend.md
-  agent_backend.md
-  agent_shared.md

Each contains a specialized prompt instructing an AI assistant to only reference and modify files within that domain’s directory tree.

### Best Practices

**Domain Separation**
-  Keep domains small and highly cohesive.
-  Limit to 3-5 concurrent domains/agents to avoid fragmentation.
-  Review domain boundaries periodically.

**File Organization**
-  Use semantic naming (e.g., backend/controllers, frontend/components).
-  Keep tests close to relevant code or in a well-structured tests/ directory.
-  Document domain interfaces clearly so AI agents know how they interrelate.

**Agent Management**
-  One agent per domain for clarity.
-  Run FlowWizard after major refactors or new features to keep domain boundaries updated.
-  If an agent needs code outside its domain, you can temporarily add that directory to tree_focus or ask the user to generate a new agent specifically for that domain.

### Additional “Super Cool” Features

-  **Composite Agents**: Combine multiple focus directories (e.g., frontend + backend) into a single “fullstack” agent. This is possible by adding a “combined agent” option in your config or using an advanced CLI flow.
-  **Live Watch Mode**: In addition to recurring time-based generation, FlowWizard can watch your project for file changes (using watchdog) to immediately regenerate domain agents as soon as you add or remove files.
-  **Auto-Sync with Git**: FlowWizard can auto-commit updated agent files and tree diagrams to a dedicated branch or commit message. This is handy if your team wants these domain boundaries versioned or regularly updated.
-  **Flexible Profiles**: Add multiple language “profiles” in your config (e.g., Node, Python, Go) so FlowWizard can seamlessly handle polyglot repos or submodules.
-  **Remote Collaboration**: Combine ephemeral installation (uvx) with a direct Git branch or commit reference. Share a link like:  
  ```bash
  uvx --from git+https://github.com/flight505/Flowwizard@feature/composite-agents fw main-menu
  ```
  so collaborators can instantly run your in-progress version of FlowWizard without any local installation headaches.

### IDE Support

Optimized for:
-  Cursor IDE (primary) with .cursorrules
-  VS Code with AI extensions
-  JetBrains IDEs with AI plugins
-  Other AI-enhanced editors

FlowWizard ensures each domain is well-defined, so your AI-powered IDE can limit context to the domain’s files, preventing cross-domain confusion.

### Technical Details

-  **Language**: Python
-  **CLI**: Typer, Questionary, Rich
-  **Configuration**: YAML-based
-  **Tree Generation**: Intelligent file-tree analysis, skipping excluded dirs
-  **Automatic Boundary Enforcement**: .cursorrules copying for Cursor IDE or boundary hints for other IDEs

### License

MIT License — see LICENSE for details.

### Contributing

-  Fork the repository
-  Create a new branch for your feature or bugfix
-  Install using uv venv or standard virtual env
-  Test your changes, ensuring no breakage to existing flows
-  Submit a pull request describing your improvements

We welcome feature requests, bug reports, and contributions of all types. Let’s keep FlowWizard flowing and help AI developers stay in their lanes without collisions!

Happy coding with FlowWizard! 🎉 We hope it brings clarity and seamless AI integration to your next big project.

