import os
import sqlite3

from click.testing import CliRunner

from constrictor.cli import main


def _make_project(runner, module_name):
    """Create a project and generate one module, without depending on the
    project's own .venv (db commands run via sys.executable, in-process
    with the test's own installed dependencies)."""
    result = runner.invoke(main, ['new', 'proj'])
    assert result.exit_code == 0
    os.chdir('proj')
    result = runner.invoke(main, ['generate', module_name])
    assert result.exit_code == 0


def test_db_commands_require_project():
    runner = CliRunner()
    with runner.isolated_filesystem():
        for args in (['db', 'init'], ['db', 'migrate'], ['db', 'upgrade'], ['db', 'downgrade']):
            result = runner.invoke(main, args)
            assert result.exit_code != 0
            assert "Not in a constrictor project" in result.output


def test_db_migrate_requires_init_first():
    runner = CliRunner()
    with runner.isolated_filesystem():
        _make_project(runner, 'articles')
        result = runner.invoke(main, ['db', 'migrate'])
        assert result.exit_code != 0
        assert "constrictor db init" in result.output


def test_db_upgrade_requires_init_first():
    runner = CliRunner()
    with runner.isolated_filesystem():
        _make_project(runner, 'events')
        result = runner.invoke(main, ['db', 'upgrade'])
        assert result.exit_code != 0
        assert "constrictor db init" in result.output


def test_db_init_creates_migrations_dir():
    runner = CliRunner()
    with runner.isolated_filesystem():
        _make_project(runner, 'orders')
        result = runner.invoke(main, ['db', 'init'])
        assert result.exit_code == 0
        assert os.path.isdir('migrations')
        assert os.path.isdir('migrations/versions')


def test_db_init_twice_errors():
    runner = CliRunner()
    with runner.isolated_filesystem():
        _make_project(runner, 'invoices')
        assert runner.invoke(main, ['db', 'init']).exit_code == 0
        result = runner.invoke(main, ['db', 'init'])
        assert result.exit_code != 0
        assert "already exists" in result.output


def test_db_migrate_and_upgrade_creates_table():
    runner = CliRunner()
    with runner.isolated_filesystem():
        _make_project(runner, 'products')
        assert runner.invoke(main, ['db', 'init']).exit_code == 0

        result = runner.invoke(main, ['db', 'migrate', '-m', 'create products table'])
        assert result.exit_code == 0
        revisions = [f for f in os.listdir('migrations/versions') if f.endswith('.py')]
        assert len(revisions) == 1

        result = runner.invoke(main, ['db', 'upgrade'])
        assert result.exit_code == 0

        db_path = os.path.join('instance', 'app.db')
        assert os.path.exists(db_path)
        con = sqlite3.connect(db_path)
        tables = {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert 'products' in tables


def test_db_downgrade_reverts_migration():
    runner = CliRunner()
    with runner.isolated_filesystem():
        _make_project(runner, 'reviews')
        assert runner.invoke(main, ['db', 'init']).exit_code == 0
        assert runner.invoke(main, ['db', 'migrate', '-m', 'create reviews table']).exit_code == 0
        assert runner.invoke(main, ['db', 'upgrade']).exit_code == 0

        result = runner.invoke(main, ['db', 'downgrade'])
        assert result.exit_code == 0

        con = sqlite3.connect(os.path.join('instance', 'app.db'))
        tables = {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert 'reviews' not in tables


def test_premigrate_and_postmigrate_hooks_run_in_order():
    runner = CliRunner()
    with runner.isolated_filesystem():
        _make_project(runner, 'comments')
        assert runner.invoke(main, ['db', 'init']).exit_code == 0
        assert runner.invoke(main, ['db', 'migrate', '-m', 'create comments table']).exit_code == 0

        with open('modules/comments/premigrate.py', 'w') as f:
            f.write(
                "def run(app):\n"
                "    with open('hook_order.txt', 'a') as log:\n"
                "        log.write('pre\\n')\n"
            )
        with open('modules/comments/postmigrate.py', 'w') as f:
            f.write(
                "def run(app):\n"
                "    with open('hook_order.txt', 'a') as log:\n"
                "        log.write('post\\n')\n"
            )

        result = runner.invoke(main, ['db', 'upgrade'])
        assert result.exit_code == 0
        assert "Running premigrate hook for module 'comments'" in result.output
        assert "Running postmigrate hook for module 'comments'" in result.output

        with open('hook_order.txt') as f:
            assert f.read().splitlines() == ['pre', 'post']


def test_missing_hook_run_function_warns_without_failing():
    runner = CliRunner()
    with runner.isolated_filesystem():
        _make_project(runner, 'tags')
        assert runner.invoke(main, ['db', 'init']).exit_code == 0
        assert runner.invoke(main, ['db', 'migrate', '-m', 'create tags table']).exit_code == 0

        with open('modules/tags/premigrate.py', 'w') as f:
            f.write("# no run() defined\n")

        result = runner.invoke(main, ['db', 'upgrade'])
        assert result.exit_code == 0
        assert "no run(app) function" in result.output
