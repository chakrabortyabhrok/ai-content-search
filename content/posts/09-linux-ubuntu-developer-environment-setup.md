---
title: Linux Ubuntu Developer Environment Setup
category: Tooling
status: published
---
## Start from a clean base
A fresh Ubuntu install is easier to trust than a machine that has accumulated years of packages. After the first boot, update the system, install the basic build tools, and enable the firewall. Then add only what the current projects actually need. This keeps the environment small and makes it straightforward to recreate on a new laptop or a cloud VM.

Install git, curl, build-essential, and the libraries required by Python and Node. Set the timezone and locale once so logs and file timestamps stay consistent. Create a non-root user for daily work and give it sudo rights. All development happens as that user.

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl build-essential python3-venv
sudo ufw enable
```

## Language runtimes without system conflicts
Python and Node change often. Installing them through the system package manager locks you to Ubuntu’s versions and can break when the distribution updates. Use a version manager instead.

For Python, pyenv or a simple set of virtual environments per project is enough. Each project gets its own directory with its own interpreter and packages. Never install project dependencies into the system Python. For Node, nvm or fnm lets you switch versions per repository. A `.nvmrc` or `.python-version` file in the project root makes the correct version automatic when you enter the directory.

## Editor, terminal, and shell
VS Code or a similar editor with the Python, Docker, and Git extensions covers most needs. Install the editor from the official repository or as a snap so updates arrive cleanly. Configure it to use the project’s virtual environment automatically so linting and debugging see the right packages.

The terminal should be fast and predictable. The default GNOME terminal is fine. Add a few aliases for common git and docker commands, but keep the shell configuration short. A large `.bashrc` full of custom functions becomes another thing to debug. Use tmux or a simple terminal multiplexer only if you regularly need many long-running sessions; otherwise the editor’s integrated terminal is sufficient.

## Docker and databases
Install Docker from the official repository and add your user to the docker group so you do not need sudo for every command. Docker Compose comes with it. This lets you run Postgres, Redis, and the application containers the same way on every machine.

For local Postgres you can either use the Docker container from the project’s compose file or install the system package. The compose approach is usually better because it matches production more closely and disappears when you remove the project. Keep database data in a named volume so it survives container restarts.

## What good looks like
A new repository can be cloned, its dependencies installed, and its tests run with three or four commands and no global package changes. Switching between two projects that need different Python versions requires no manual exports or path edits. If a system update breaks a project, or if you must remember a list of global pip packages to reinstall after a reinstall, the environment has become coupled to the machine and needs to be moved back into per-project isolation.