# Repository Guidelines

## Project Structure & Module Organization
`install_id8_workflow.py` is the main entry point and contains CLI parsing, template rendering, and file write logic. Runtime assets live under `assets/id8/`:
- `templates/` for agent-specific and shared template files
- `workflow/id8_steps.md` for the core `/id8` flow content
- `mcp_manifest.json` for MCP source data

Tests are in `tests/test_install_id8_workflow.py`. Reference documentation is in `Docs/Agent_Docs/` and `Docs/MCP_Docs/`. Treat `testdir/` as local scratch/output for manual checks.

## Build, Test, and Development Commands
- `python3 install_id8_workflow.py --help`: show all installer options.
- `python3 install_id8_workflow.py`: run interactive install prompts.
- `python3 install_id8_workflow.py --non-interactive --project-dir /path/to/project --agents claude,codex,antigravity`: deterministic scripted install.
- `python3 install_id8_workflow.py --validate-only --project-dir /path/to/project --agents codex`: preview writes without modifying files.
- `python3 -m unittest discover -s tests -p "test_*.py"`: run all unit tests.

## Coding Style & Naming Conventions
Use Python 3.9+ style with 4-space indentation, `snake_case` for functions/variables, and `UPPER_CASE` for constants. Prefer type hints and `pathlib.Path` (current codebase pattern). Keep functions small and behavior-focused; avoid broad side effects outside `Installer` methods. Template placeholders should stay in `{{PLACEHOLDER}}` format and env placeholders in `${ID8_*}` format.

## Testing Guidelines
Testing uses `unittest`. Add tests in `tests/test_*.py`, with method names like `test_<behavior>`. Cover both success and failure paths (argument validation, block replacement, auth modes, and generated output content). Use `tempfile.TemporaryDirectory()` for filesystem tests and avoid writing outside temp paths.

## Commit & Pull Request Guidelines
Current history mixes minimal messages (`.`) and descriptive ones (`Update id8_steps.md`). Prefer descriptive, imperative subjects (example: `installer: validate auth mode from env`). Keep PRs small and include:
- what changed and why
- commands run for verification
- any generated file/path impacts (for example `.mcp.json`, `.codex/config.toml`, `.env.example`)

## Security & Configuration Tips
Do not commit real credentials. Keep token values in environment variables and preserve placeholder-based config output. If testing key-based auth, use local env values only and verify secrets are not written to tracked files.
