We are going to proceed with development on a webapp. The application is
intended to serve as a way to maintain digital records of real-world inventories
using modern vision processing techniques to read physical labels and turn them
into structured data. This project only implements the image processing aspect
of the inventory.

In DESIGN.md you will find requirements, use-cases and other guidelines that
should be adhered to during development. YOU MUST NOT VIOLATE THESE GUIDELINES
UNLESS EXPLICITLY DIRECTED BY THE USER.

For development purposes, you may access an existing ollama instance with
the most relevant models already pulled at `https://ollama.home.trprince.com`.
Note that the host system has access to an NVIDIA GTX 3090 with ~24GB of VRAM.
Please do not pull new models to this system. This system should only be used
for development purposes and manual testing. It should not be referenced by the
codebase, automated testing, etc.

You should use a virtualenv at .venv/ for installing python development tools like
poetry as you are running in a sandboxed environment that does not allow write access
outside of your working directory. Because of this restricted sandbox, many development tools will fail if they attempt to write to their default global cache or configuration directories (e.g. `~/.cache`, `~/.config`). You must configure them to use local directories within your workspace. These should be stored in
a top-level '$(pwd)/.cache/ directory.

For example, when using `poetry`, set the following environment variables:
```bash
export POETRY_CONFIG_DIR=$(pwd)/.cache/poetry/config
export POETRY_CACHE_DIR=$(pwd)/.cache/poetry/cache
export POETRY_VIRTUALENVS_IN_PROJECT=true
```

When using `pre-commit`, configure it to use a local cache directory before running or installing hooks:
```bash
export PRE_COMMIT_HOME=$(pwd)/.cache/pre-commit
```

Please proceed with the first unfinished item from TODO.md. When you have finished,
present your changes for review by the user, who may make appropriate
modifications.
