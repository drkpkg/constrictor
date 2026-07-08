import os
import sqlite3

import pytest
from click.testing import CliRunner
from flask import Flask

from constrictor.cli import main
from constrictor.db import db
from constrictor.auth_models import User, Role, ModelAccess
from constrictor.auth import login_manager, roles_required, model_access_required


# ---------------------------------------------------------------------------
# Model-level: role implication, password hashing, access checks
# ---------------------------------------------------------------------------

@pytest.fixture
def app_ctx():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    app.config['SECRET_KEY'] = 'test'
    db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def test_role_implication_is_transitive(app_ctx):
    admin = Role(name='admin')
    editor = Role(name='editor', implies=admin)
    viewer = Role(name='viewer', implies=editor)
    db.session.add_all([admin, editor, viewer])
    db.session.commit()

    user = User(email='a@example.com')
    user.set_password('x')
    user.roles.append(viewer)
    db.session.add(user)
    db.session.commit()

    assert user.role_names() == {'viewer', 'editor', 'admin'}
    assert user.has_role('admin')
    assert not user.has_role('nonexistent')


def test_role_implication_cycle_does_not_hang(app_ctx):
    a = Role(name='a')
    b = Role(name='b')
    db.session.add_all([a, b])
    db.session.commit()
    a.implies_role_id = b.id
    b.implies_role_id = a.id
    db.session.commit()

    user = User(email='a@example.com')
    user.set_password('x')
    user.roles.append(a)
    db.session.add(user)
    db.session.commit()

    assert user.role_names() == {'a', 'b'}


def test_password_hashing(app_ctx):
    user = User(email='a@example.com')
    user.set_password('correct-horse')
    assert user.check_password('correct-horse')
    assert not user.check_password('wrong')
    assert user.password_hash != 'correct-horse'


def test_can_respects_role_implication(app_ctx):
    """Regression: can() must resolve the full implied-role closure, not
    just directly-assigned roles - a grant on an implied role must apply."""
    admin = Role(name='admin')
    editor = Role(name='editor', implies=admin)
    db.session.add_all([admin, editor])
    db.session.commit()

    db.session.add(ModelAccess(role_id=admin.id, model_name='blog', can_read=True))
    db.session.commit()

    user = User(email='a@example.com')
    user.set_password('x')
    user.roles.append(editor)
    db.session.add(user)
    db.session.commit()

    assert user.can('blog', 'read')
    assert not user.can('blog', 'delete')


def test_can_with_null_role_grant_applies_to_any_authenticated_user(app_ctx):
    db.session.add(ModelAccess(role_id=None, model_name='blog', can_read=True))
    db.session.commit()

    user = User(email='a@example.com')
    user.set_password('x')
    db.session.add(user)
    db.session.commit()

    assert user.can('blog', 'read')
    assert not user.can('blog', 'create')


# ---------------------------------------------------------------------------
# Decorator behavior against a real Flask test client
# ---------------------------------------------------------------------------

@pytest.fixture
def client_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    app.config['SECRET_KEY'] = 'test'
    db.init_app(app)
    login_manager.init_app(app)

    @app.route('/admin-only')
    @roles_required('admin')
    def admin_only():
        return 'ok'

    @app.route('/blog-read')
    @model_access_required('blog', 'read')
    def blog_read():
        return 'ok'

    with app.app_context():
        db.create_all()
        admin = Role(name='admin')
        db.session.add(admin)
        db.session.commit()

        haver = User(email='haver@example.com')
        haver.set_password('x')
        haver.roles.append(admin)

        plain = User(email='plain@example.com')
        plain.set_password('x')

        db.session.add_all([haver, plain])
        db.session.add(ModelAccess(role_id=admin.id, model_name='blog', can_read=True))
        db.session.commit()

        yield app, haver.id, plain.id

        db.session.remove()
        db.drop_all()


def _login_as(client, user_id):
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user_id)


def test_roles_required_blocks_unauthenticated(client_app):
    app, haver_id, plain_id = client_app
    client = app.test_client()
    assert client.get('/admin-only').status_code == 401


def test_roles_required_blocks_wrong_role(client_app):
    app, haver_id, plain_id = client_app
    client = app.test_client()
    _login_as(client, plain_id)
    assert client.get('/admin-only').status_code == 403


def test_roles_required_allows_correct_role(client_app):
    app, haver_id, plain_id = client_app
    client = app.test_client()
    _login_as(client, haver_id)
    assert client.get('/admin-only').status_code == 200


def test_model_access_required_blocks_without_grant(client_app):
    app, haver_id, plain_id = client_app
    client = app.test_client()
    _login_as(client, plain_id)
    assert client.get('/blog-read').status_code == 403


def test_model_access_required_allows_with_grant(client_app):
    app, haver_id, plain_id = client_app
    client = app.test_client()
    _login_as(client, haver_id)
    assert client.get('/blog-read').status_code == 200


# ---------------------------------------------------------------------------
# Codegen: decorator order and access.csv generation
# ---------------------------------------------------------------------------

def test_generated_route_decorator_order_is_route_first():
    """Regression: @blueprint.route(...) must be emitted before (above) any
    auth decorator - Flask's route() captures the raw function reference, so
    an auth decorator placed above it would never actually run."""
    from pathlib import Path
    from constrictor.yaml_parser import generate_module_from_yaml
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        generate_module_from_yaml('blog', Path(tmp), None)
        content = (Path(tmp) / 'modules' / 'blog' / 'routes.py').read_text()

    route_idx = content.index("@blueprint.route('/blog/api/', methods=['GET'])")
    access_idx = content.index("@model_access_required('blog', 'read')")
    assert route_idx < access_idx


def test_generated_module_ships_access_csv():
    from pathlib import Path
    from constrictor.yaml_parser import generate_module_from_yaml
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        generate_module_from_yaml('blog', Path(tmp), None)
        csv_path = Path(tmp) / 'modules' / 'blog' / 'access.csv'
        assert csv_path.exists()
        rows = csv_path.read_text().splitlines()
        assert rows[0] == 'model,role,can_read,can_create,can_update,can_delete'
        assert any(row.startswith('blog,admin,') for row in rows)


# ---------------------------------------------------------------------------
# End-to-end through the CLI: db upgrade seeds access.csv, auth commands work
# ---------------------------------------------------------------------------

def _make_project(runner, module_name):
    result = runner.invoke(main, ['new', 'proj'])
    assert result.exit_code == 0
    os.chdir('proj')
    result = runner.invoke(main, ['generate', module_name])
    assert result.exit_code == 0


def test_db_upgrade_seeds_access_from_csv():
    runner = CliRunner()
    with runner.isolated_filesystem():
        _make_project(runner, 'articles')
        assert runner.invoke(main, ['db', 'init']).exit_code == 0
        assert runner.invoke(main, ['db', 'migrate', '-m', 'initial']).exit_code == 0

        result = runner.invoke(main, ['db', 'upgrade'])
        assert result.exit_code == 0
        assert "Seeded" in result.output

        con = sqlite3.connect(os.path.join('instance', 'app.db'))
        roles = con.execute("SELECT name FROM auth_role").fetchall()
        assert ('admin',) in roles

        grants = con.execute(
            "SELECT model_name, can_read, can_create FROM auth_model_access"
        ).fetchall()
        assert ('articles', 1, 1) in grants


def test_db_upgrade_seeding_does_not_duplicate_or_overwrite():
    runner = CliRunner()
    with runner.isolated_filesystem():
        _make_project(runner, 'articles')
        assert runner.invoke(main, ['db', 'init']).exit_code == 0
        assert runner.invoke(main, ['db', 'migrate', '-m', 'initial']).exit_code == 0
        assert runner.invoke(main, ['db', 'upgrade']).exit_code == 0

        con = sqlite3.connect(os.path.join('instance', 'app.db'))
        con.execute("UPDATE auth_model_access SET can_delete = 1 WHERE model_name = 'articles' AND role_id IS NOT NULL")
        con.commit()
        con.close()

        result = runner.invoke(main, ['db', 'upgrade'])
        assert result.exit_code == 0
        assert "Seeded" not in result.output

        con = sqlite3.connect(os.path.join('instance', 'app.db'))
        rows = con.execute("SELECT * FROM auth_model_access WHERE model_name = 'articles'").fetchall()
        assert len(rows) == 2
        can_delete_values = con.execute(
            "SELECT can_delete FROM auth_model_access WHERE model_name = 'articles' AND role_id IS NOT NULL"
        ).fetchall()
        assert can_delete_values == [(1,)]


def test_auth_create_role_and_user():
    runner = CliRunner()
    with runner.isolated_filesystem():
        _make_project(runner, 'articles')
        assert runner.invoke(main, ['db', 'init']).exit_code == 0
        assert runner.invoke(main, ['db', 'migrate', '-m', 'initial']).exit_code == 0
        assert runner.invoke(main, ['db', 'upgrade']).exit_code == 0

        result = runner.invoke(main, ['auth', 'create-role', 'editor', '--implies', 'admin'])
        assert result.exit_code == 0
        assert "created" in result.output

        result = runner.invoke(main, ['auth', 'create-role', 'admin'])
        assert result.exit_code != 0
        assert "already exists" in result.output

        result = runner.invoke(
            main, ['auth', 'create-user', 'owner@example.com', '--role', 'editor'],
            input="s3cret123\ns3cret123\n",
        )
        assert result.exit_code == 0
        assert "created" in result.output

        result = runner.invoke(
            main, ['auth', 'create-user', 'nobody@example.com', '--role', 'ghost'],
            input="x\nx\n",
        )
        assert result.exit_code != 0
        assert "does not exist" in result.output

        con = sqlite3.connect(os.path.join('instance', 'app.db'))
        assert con.execute("SELECT email FROM auth_user").fetchall() == [('owner@example.com',)]
        assert con.execute("SELECT name, implies_role_id FROM auth_role WHERE name = 'editor'").fetchall()


def test_protected_route_blocks_unauthenticated_end_to_end():
    """Regression, at the real HTTP level: a freshly generated module's
    model_access-gated route must reject an unauthenticated request."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        _make_project(runner, 'articles')
        assert runner.invoke(main, ['db', 'init']).exit_code == 0
        assert runner.invoke(main, ['db', 'migrate', '-m', 'initial']).exit_code == 0
        assert runner.invoke(main, ['db', 'upgrade']).exit_code == 0

        from constrictor.cli import _load_project_app
        client = _load_project_app().test_client()

        response = client.get('/articles/api/')
        assert response.status_code == 401

        response = client.get('/articles/hello/')
        assert response.status_code == 200
