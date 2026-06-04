# AI Agent Guidelines

This file outlines the rules and expectations for AI agents (e.g., Mistral Vibe CLI) working on this project.

---

## **General Rules**
- **Always follow the project’s coding standards** (see below).
- **Never commit broken code**—run linters and tests before committing.
- **Ask for clarification** if a task is ambiguous.

---

## **Code Quality**
### Linting & Formatting
- **Python**: Use [`ruff`](https://docs.astral.sh/ruff/) for linting and formatting.
  - Run `ruff check --fix` and `ruff format` before committing.
- **Frontend (HTMX + Tailwind CSS)**:
  - Use [`prettier`](https://prettier.io/) to format HTML, CSS, and JavaScript files.
  - Configured via `.prettierrc` (if custom rules are needed).

### Testing
- **Backend (FastAPI)**:
  - Always run `pytest` before committing.
  - Tests must pass for the commit to be allowed.
  - Use `pytest-asyncio` for async tests.

---
## **Git Workflow**
### Atomic Commits
- **One logical change per commit**.
- **Avoid large commits**: Break changes into small, focused commits (e.g., "fix typo in API", "add user model").
- Use `git add -p` to stage changes interactively.

### Commit Messages
- Follow [Conventional Commits](https://www.conventionalcommits.org/):
  - `feat: add new feature`
  - `fix: resolve bug`
  - `docs: update README`
  - `refactor: clean up code`
- Keep messages **short and descriptive**.

---
## **Pre-Commit Hooks**
The project uses [`pre-commit`](https://pre-commit.com/) to enforce:
1. **Ruff** (Python linting/formatting).
2. **Prettier** (frontend formatting).
3. **Pytest** (backend tests).

- **Hooks run automatically** on `git commit`.
- If a hook fails, **fix the issues and commit again**.

---
## **Project Structure**
- **Backend**: FastAPI + SQLAlchemy (in `/backend`).
- **Frontend**: HTMX + Tailwind CSS (in `/frontend`).
- **Tests**: Pytest tests in `/tests`.

---
## **Commands to Remember**
   Task                     | Command                          |
 |--------------------------|----------------------------------|
 | Install dev dependencies | `uv sync --dev`                  |
 | Run linters/formatters   | `uv run pre-commit run --all-files` |
 | Run tests                | `uv run pytest`                  |
 | Start backend            | `uv run uvicorn backend.main:app` |
