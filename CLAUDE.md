# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Constrictor is a Flask-based microframework (pip package `constrictor-framework`, CLI entry point `constrictor`) for scaffolding and running modular Flask applications. It generates *projects* which themselves contain *modules*, each module getting its own routes/models/views/tests via YAML templates rendered with Jinja2. Models are authored per-module but share one SQLAlchemy metadata object, so `constrictor db` can autogenerate and apply a single, project-wide Alembic migration history across all of them. Every project also ships built-in identity/RBAC tables (`auth_user`, `auth_role`, `auth_model_access`) and two view decorators (`roles_required`, `model_access_required`) — the latter checks a database-backed grant seeded from each module's `access.csv`, so access can change at runtime without a redeploy. This repo is the framework's own source — not a generated project.

## Commands

Install in editable/dev mode:
```bash
pip install -e ".[dev]"
```

Run the full test suite (also how `constrictor test` invokes pytest under the hood):
```bash
pytest
# or
python -m pytest -v
```

Run a single test file / test:
```bash
pytest constrictor/tests/test_swagger_generator.py
pytest constrictor/tests/test_swagger_generator.py::test_function_name -v
```

`pytest.ini` sets `testpaths = constrictor/tests` and `addopts = -v --tb=short`, so bare `pytest` from repo root picks up everything automatically.

Build docs (Sphinx, see `docs/`):
```bash
cd docs && make html
```

There's no lint/format tooling configured in this repo (no ruff/flake8/black config present) — don't invent one.

## Architecture

Constrictor has two layers that are easy to conflate: **the framework** (this repo, `constrictor/`) and **generated projects** (what `constrictor new` produces, and what `constrictor/tests/` exercises via `CliRunner`).

### Framework internals (`constrictor/`)

- `cli.py` — Click-based CLI (`main` group). Commands: `new`, `generate`/`g`, `run`, `test`, `db init/migrate/upgrade/downgrade`, `auth create-role/create-user`, `swagger build`. All project/module-scaffolding commands validate names via `validate_name()` (must start with a letter, alnum/`_`/`-` only, ≤50 chars, not a reserved word like `test`/`app`/`config`) and shell out via `run_command()` (wraps `subprocess.run`, always invokes `sys.executable` rather than a bare `"python"` string, aborts the CLI with `click.Abort()` on failure unless `check=False`). Commands that need to run inside a generated project first sanity-check for `app.py` + `modules/` in the cwd (`_require_project()`). `project_env()` merges the project's `.env` file (via `python-dotenv`'s `dotenv_values`) into the subprocess environment for `run` and the `db` commands.
- `blueprint_loader.py` — `load(app)` is what a generated project's `app.py` calls. It walks `<project_root>/modules/*` and, per module, imports `modules.<name>.routes` (registers `routes.blueprint`, a Flask `Blueprint`, with the app) and best-effort imports `modules.<name>.models` (so its `db.Model` subclasses register onto the shared metadata). Missing `routes.py`/`blueprint` or missing `models.py` is logged and skipped, not fatal — one broken module shouldn't take down the whole app.
- `db.py` — defines the framework-wide `db = SQLAlchemy()` and `migrate = Migrate()` singletons, re-exported from `constrictor/__init__.py`. Every module's `models.py` imports `db` from here (never creates its own `SQLAlchemy()`) so all modules' tables land on one metadata object — this is what lets `constrictor db migrate` autogenerate a single project-wide revision from models scattered across independent module files.
- `auth_models.py` — built-in `User`/`Role`/`ModelAccess` (`db.Model` subclasses, tables `auth_user`/`auth_role`/`auth_user_role`/`auth_model_access`), imported directly by `constrictor/__init__.py` — not inside any generated module — so they're part of `db.metadata` (and the first migration) before any user module is walked. `Role.implies_role_id` is self-referential; `User._all_roles()` walks that chain (with cycle protection) to resolve the transitive closure, used by both `has_role()` and `can()`.
- `auth.py` — wraps Flask-Login (`login_manager`, re-exports `login_required`/`current_user`/`login_user`/`logout_user`) and adds two view decorators: `roles_required(*names)` (code-based) and `model_access_required(model_name, action)` (checks `User.can()` against `auth_model_access`, i.e. database-backed and runtime-editable). Also has `seed_access_from_csv()`, called from `cli.py`'s `db upgrade`.
- `yaml_parser.py` — `YamlTemplateParser` loads a YAML template (default `templates/module_template.yml`), then for each of its top-level sections (`structure`, `routes`, `templates`, `tests`) generates the corresponding files under `modules/<name>/` (and HTML under the project's top-level `templates/`). All string content in the YAML is passed through a Jinja2 environment (`render_template_content`) with `{module_name: ...}` in context, so template YAML/files use `{{module_name}}`, `{{module_name|title}}`, etc. `_generate_routes()` emits `@blueprint.route(...)` **before** any `@roles_required`/`@model_access_required` decorator from a route's optional `roles:`/`model_access:` YAML keys — Flask's `route()` captures the raw function object it's given, so an auth decorator emitted *above* it would silently never run (this was a real, shipped bug once; there's a regression test for it in `test_auth.py`). `generate_module_from_yaml()` is the public entry point used by `cli.py generate`.
- `templates/module_template.yml` — the default module blueprint: defines routes (index/hello/api/CRUD-ish users endpoints, with `model_access:` grants on the JSON ones), the HTML template, generated pytest tests, and the `structure` section (directories to create, and file content for `__init__.py`/`access.csv`/`models.py`/`views.py`; `routes.py` itself is generated separately by `_generate_routes()` from the `routes:` section, described above). Custom templates follow the same schema (see README's "Creating Custom Templates" section) and can be pointed to via `constrictor generate <name> --template <path>`.
- `templates/routes_template.py` — a fuller, hand-written example `routes.py` (real in-memory CRUD, validation) kept as reference material for anyone authoring a custom template. **Not used by the default template** — `structure.files` used to point `routes.py` at it, but `_generate_routes()` always ran afterward and silently overwrote that file, so the entry was removed. Don't re-add a `structure.files` entry naming `routes.py` without removing/adjusting `_generate_routes()`, or the same silent-overwrite bug comes back.
- `swagger_generator.py` — `SwaggerGenerator` builds an OpenAPI 3.0 spec by statically parsing each module's `routes.py` with `ast` (no imports/execution): it finds the `blueprint = Blueprint(...)` assignment, walks `FunctionDef` nodes for `@blueprint.route(...)` decorators, and derives path/method/summary/description from the decorator and docstring. If a module also has a `template.yml`/`swagger.yml` file with a `routes[].swagger` block, that metadata (parameters, requestBody, responses, tags) overrides/enhances the AST-derived info — this is how the YAML templates' `swagger:` sections end up documented (see `module_template.yml`'s `swagger:` blocks per route). Invoked via `constrictor swagger build`; `--serve` spins up a stdlib `http.server` that serves a Swagger-UI HTML shell pointing at the generated spec file.

### Generated-project shape

A `constrictor new <name>` project looks like:
```
project_name/
├── app.py            # Flask() + db/migrate/login_manager.init_app() + constrictor.load(app)
├── migrations/        # created by `constrictor db init`; Alembic history (single, project-wide)
├── modules/
│   └── <module>/
│       ├── routes.py       # defines `blueprint`, registered automatically by load()
│       ├── models.py       # db.Model subclasses, registered automatically by load()
│       ├── views.py
│       ├── access.csv      # default auth_role/auth_model_access grants, seeded on `db upgrade`
│       ├── premigrate.py   # optional: run(app), executed before `db upgrade`/`downgrade`
│       ├── postmigrate.py  # optional: run(app), executed after `db upgrade`/`downgrade`
│       └── tests/
└── templates/         # centralized HTML, module_name/-namespaced
```
Deliberately **no** `__init__.py` at the project root — `modules/` works as an implicit namespace package without one, and having one makes Flask/Alembic's import machinery (`prepare_import`) treat the whole project as a package, which relocates `instance_path` (and therefore relative SQLite URLs like `sqlite:///app.db`) to the *parent* of the project directory instead of inside it. This bit `constrictor db upgrade` during development; don't reintroduce the file.

The framework's own `constrictor/tests/` largely tests this generation flow itself — using Click's `CliRunner` + `tmpdir`/`isolated_filesystem` to actually run `constrictor new`/`generate` and assert on the files produced, rather than mocking. When editing `cli.py`, `yaml_parser.py`, or the templates, expect tests to spin up real temp projects end-to-end.

### Key coupling to watch

- `yaml_parser.py`, `swagger_generator.py`, and `templates/module_template.yml` must stay in sync: route metadata under a route's `swagger:` key in the YAML is matched against the AST-parsed function by `function` name + `path` (see `SwaggerGenerator._enhance_with_template_metadata`) — renaming a route's `function` or `path` in the YAML without updating both breaks swagger enrichment silently (it just falls back to bare AST-derived docs).
- `blueprint_loader.load()` assumes `modules.<name>.routes`/`modules.<name>.models` are importable, which requires the generated project's root to be on `sys.path` — this is why `cli.py run`/`db *` refuse to proceed unless `app.py` and `modules/` exist in the cwd.
- Migrations are a single, project-wide Alembic history (not per-module) — `db.metadata` is shared across every module's models, so `constrictor db migrate` diffs the DB against *all* modules' models at once. `constrictor db upgrade`/`downgrade` discover every module's optional `premigrate.py`/`postmigrate.py` (a `run(app)` function) via `_run_migration_hooks()` in `cli.py`, importing the project's real `app.py` (via `_load_project_app()`) so hooks get a fully-wired Flask app.
- `_load_project_app()` deliberately does **not** do a plain `import app` / `sys.modules['app']` lookup — it loads `app.py` from an explicit absolute path under a private module name via `importlib.util.spec_from_file_location`, and registers that name in `sys.modules` *before* `exec_module()` (required for Flask's `get_root_path()`/`instance_path` resolution to find it during execution). A plain import or `importlib.reload()` would return/re-execute whichever project's `app.py` happened to be loaded first in the process — fine for the real CLI (one process per invocation) but wrong the moment anything loads more than one project's app in-process, which the test suite does.
- `auth_model_access.model_name` is a plain string, not a foreign key — Constrictor resolves it against `db.metadata.tables` (built once at startup) rather than a persisted model registry, since modules are a closed set loaded from disk once, unlike systems (e.g. Odoo) where modules can be installed/uninstalled at runtime. `constrictor db upgrade` seeds grants from each module's `access.csv` via `seed_access_from_csv()` (insert-if-missing only — never overwrites an existing `(role, model)` row, so a grant changed at runtime survives a later `db upgrade`).
