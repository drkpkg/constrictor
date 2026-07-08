import click
import os
import subprocess
import sys
import re
from pathlib import Path
from typing import List, Optional
from .yaml_parser import generate_module_from_yaml
from .swagger_generator import SwaggerGenerator


@click.group()
def main():
    """Constrictor: A microframework CLI tool for Flask.

    Use this tool to generate projects, modules, and manage your Flask applications.
    """
    pass


def validate_name(name: str, name_type: str = "name") -> bool:
    """
    Validate project or module names.
    
    Args:
        name: The name to validate
        name_type: Type of name (project, module, etc.)
        
    Returns:
        True if valid, False otherwise
    """
    if not name or not name.strip():
        return False
    
    # Check for invalid characters
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', name):
        return False
    
    # Check length
    if len(name) > 50:
        return False
    
    # Reserved names
    reserved_names = ['test', 'tests', 'modules', 'app', 'main', 'config', 'settings']
    if name.lower() in reserved_names:
        return False
    
    return True


def run_command(command: List[str], cwd: Optional[str] = None, check: bool = True,
                 env: Optional[dict] = None) -> subprocess.CompletedProcess:
    """
    Run a command safely using subprocess.

    Args:
        command: Command to run as list of strings
        cwd: Working directory
        check: Whether to raise exception on non-zero exit code
        env: Environment variables for the subprocess (defaults to inheriting ours)

    Returns:
        CompletedProcess result
    """
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            check=check,
            capture_output=True,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        click.echo(f"Error running command: {e}")
        click.echo(f"Output: {e.stdout}")
        click.echo(f"Error: {e.stderr}")
        raise click.Abort()
    except FileNotFoundError as e:
        click.echo(f"Command not found: {e}")
        raise click.Abort()


def project_env() -> dict:
    """
    Build a subprocess environment seeded with the current project's .env file
    (if present), falling back to the current process environment otherwise.

    Returns:
        Environment dict suitable for subprocess.run(..., env=...)
    """
    env = os.environ.copy()
    if os.path.exists('.env'):
        from dotenv import dotenv_values
        env.update({k: v for k, v in dotenv_values('.env').items() if v is not None})
    return env


@main.command()
@click.argument('project_name')
def new(project_name):
    """Create a new project.

    This command initializes a new Flask project with the specified name. It sets up the basic directory structure and provides an environment for module generation.
    """
    # Validate project name
    if not validate_name(project_name, "project"):
        click.echo(f"Error: Invalid project name '{project_name}'. Project names must:")
        click.echo("- Start with a letter")
        click.echo("- Contain only letters, numbers, underscores, and hyphens")
        click.echo("- Be 50 characters or less")
        click.echo("- Not be a reserved name")
        raise click.Abort()
    
    # Check if project already exists
    if os.path.exists(project_name):
        click.echo(f"Error: Project '{project_name}' already exists.")
        if not click.confirm("Do you want to overwrite it?"):
            raise click.Abort()
        # Remove existing project
        import shutil
        shutil.rmtree(project_name)
    
    try:
        # Create project structure
        project_path = Path(project_name)
        modules_dir = project_path / "modules"
        
        # Create directories
        modules_dir.mkdir(parents=True, exist_ok=True)
        
        # Create app.py
        app_content = '''import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask
from constrictor import load, db, migrate, login_manager

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)

load(app)


@app.route('/')
def index():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(debug=True)
'''
        
        with open(project_path / "app.py", 'w') as f:
            f.write(app_content)

        # Note: deliberately no project-root __init__.py. Flask/Alembic's
        # module discovery (`prepare_import`) treats a directory containing
        # one as a package and resolves instance_path (and thus relative
        # sqlite paths) relative to its *parent* directory instead of the
        # project root - modules/ doesn't need it either (implicit namespace
        # package is enough for `modules.<name>.routes` imports).

        # Create .env template
        env_content = '''# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration
DATABASE_URL=sqlite:///app.db

# Secret Key (change this in production!)
SECRET_KEY=your-secret-key-here
'''
        
        with open(project_path / ".env.example", 'w') as f:
            f.write(env_content)
        
        # Create .gitignore
        gitignore_content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.venv/
venv/
ENV/
env/

# Flask
instance/
.webassets-cache

# Environment variables
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
'''
        
        with open(project_path / ".gitignore", 'w') as f:
            f.write(gitignore_content)
        
        # Create requirements.txt
        requirements_content = '''constrictor-framework>=1.0.0
Flask>=3.0.3
python-dotenv>=1.0.1
Flask-SQLAlchemy>=3.1.1
Flask-Migrate>=4.0.7
Flask-Login>=0.6.3
'''
        
        with open(project_path / "requirements.txt", 'w') as f:
            f.write(requirements_content)
        
        # Create virtual environment
        click.echo("Creating virtual environment...")
        try:
            result = run_command([sys.executable, "-m", "venv", ".venv"], cwd=project_name)
            
            # Install Flask
            click.echo("Installing Flask...")
            pip_path = project_path / ".venv" / "bin" / "pip"
            if os.name == 'nt':  # Windows
                pip_path = project_path / ".venv" / "Scripts" / "pip.exe"
            
            if pip_path.exists():
                run_command([str(pip_path), "install", "constrictor-framework>=1.0.0", "Flask>=3.0.3",
                             "python-dotenv>=1.0.1", "Flask-SQLAlchemy>=3.1.1", "Flask-Migrate>=4.0.7",
                             "Flask-Login>=0.6.3"],
                            cwd=project_name)
            else:
                click.echo("Warning: Virtual environment creation failed, skipping package installation")
        except Exception as e:
            click.echo(f"Warning: Could not create virtual environment: {e}")
            click.echo("You can create it manually later with: python -m venv .venv")
        
        # Initialize git repository
        try:
            if not run_command(["git", "init"], cwd=project_name, check=False).returncode:
                run_command(["git", "add", "."], cwd=project_name)
                # Try to commit, but don't fail if git config is not set
                result = run_command(["git", "commit", "-m", "Initial commit"], cwd=project_name, check=False)
                if result.returncode == 0:
                    click.echo("Git repository initialized.")
                else:
                    click.echo("Git repository created but not committed (git config needed)")
        except Exception as e:
            click.echo(f"Warning: Could not initialize git repository: {e}")
        
        click.echo(f"Project '{project_name}' created successfully!")
        click.echo(f"To get started:")
        click.echo(f"  cd {project_name}")
        click.echo(f"  source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate")
        click.echo(f"  constrictor run")
        
    except Exception as e:
        click.echo(f"Error creating project: {e}")
        # Clean up on error
        if os.path.exists(project_name):
            import shutil
            shutil.rmtree(project_name)
        raise click.Abort()


@main.command()
@click.argument('module_name')
@click.option('--template', '-t', default='yaml', 
              help='Template to use for module generation (yaml or path to custom template)')
def generate(module_name, template):
    """Generate a new module.

    This command creates a new module inside the 'modules' directory of your Flask project. 
    The module will have a basic structure including routes, tests, views, and models.
    
    By default uses YAML-based templates for maximum flexibility.
    You can specify a custom template file path if needed.
    """
    # Validate module name
    if not validate_name(module_name, "module"):
        click.echo(f"Error: Invalid module name '{module_name}'. Module names must:")
        click.echo("- Start with a letter")
        click.echo("- Contain only letters, numbers, underscores, and hyphens")
        click.echo("- Be 50 characters or less")
        click.echo("- Not be a reserved name")
        raise click.Abort()
    
    # Check if we're in a constrictor project
    if not os.path.exists('modules'):
        click.echo("Error: Not in a constrictor project. Run this command from the project root directory.")
        raise click.Abort()
    
    base_path = Path('modules') / module_name
    
    # Check if module already exists
    if base_path.exists():
        click.echo(f"Error: Module '{module_name}' already exists.")
        if not click.confirm("Do you want to overwrite it?"):
            raise click.Abort()
        # Remove existing module
        import shutil
        shutil.rmtree(base_path)
    
    # Use YAML template generation by default
    try:
        generate_module_from_yaml(module_name, Path('.'), template)
        click.echo(f"Module '{module_name}' generated")
        return
    except Exception as e:
        click.echo(f"Error generating module: {e}")
        raise click.Abort()


# Add alias for generate command
@main.command(name='g')
@click.argument('module_name')
@click.option('--template', '-t', default='yaml',
              help='Template to use for module generation (yaml or path to custom template)')
@click.pass_context
def generate_alias(ctx, module_name, template):
    """Generate a new module (alias for 'generate')."""
    ctx.invoke(generate, module_name=module_name, template=template)


@main.command()
@click.argument('modules', nargs=-1)
def test(modules):
    """Run tests.

    This command runs tests for the entire application or specific modules. 
    Use it without arguments to test all modules or specify module names to test specific ones.
    """
    # Check if we're in a constrictor project
    if not os.path.exists('app.py') or not os.path.isdir('modules'):
        click.echo("Error: Not in a constrictor project. Run this command from the project root directory.")
        raise click.Abort()
    
    try:
        if not modules:
            # Run all tests
            click.echo("Running all tests...")
            result = run_command([sys.executable, "-m", "pytest", "-v"], check=False)
        else:
            # Validate module names and run specific tests
            valid_modules = []
            for module_name in modules:
                if not validate_name(module_name, "module"):
                    click.echo(f"Warning: Invalid module name '{module_name}' skipped.")
                    continue
                
                module_test_path = Path(f"modules/{module_name}/tests")
                if not module_test_path.exists():
                    click.echo(f"Warning: No tests found for module '{module_name}'")
                    continue
                
                valid_modules.append(str(module_test_path))
            
            if not valid_modules:
                click.echo("No valid modules with tests found.")
                return
            
            click.echo(f"Running tests for modules: {', '.join(modules)}")
            result = run_command([sys.executable, "-m", "pytest", "-v"] + valid_modules, check=False)

        if result.stdout:
            click.echo(result.stdout)
        if result.stderr:
            click.echo(result.stderr)

        if result.returncode == 0:
            click.echo("All tests passed!")
        elif result.returncode == 1:
            click.echo("Some tests failed - this is normal for template tests without proper setup.")
        else:
            click.echo("Tests completed with exit code: " + str(result.returncode))
            
    except Exception as e:
        click.echo(f"Error running tests: {e}")
        raise click.Abort()


@main.command()
@click.option('--host', default='127.0.0.1', help='Host to run the application on')
@click.option('--port', default=5000, help='Port to run the application on')
@click.option('--debug', is_flag=True, help='Run in debug mode')
@click.option('--reload', is_flag=True, help='Enable auto-reload')
def run(host, port, debug, reload):
    """Run the Flask application.

    This command identifies if the current directory is a valid 'constrictor' project and then runs the Flask application.
    """
    # Check if we're in a constrictor project
    if not os.path.exists('app.py') or not os.path.isdir('modules'):
        click.echo("Error: Not in a valid 'constrictor' project.")
        click.echo("Ensure you're in the project root directory and 'app.py' exists.")
        raise click.Abort()
    
    # Check if virtual environment exists
    venv_path = Path('.venv')
    if not venv_path.exists():
        click.echo("Warning: Virtual environment not found. Make sure you're in a constrictor project.")
        if not click.confirm("Do you want to continue anyway?"):
            raise click.Abort()
    
    try:
        # Set environment variables, seeded from the project's .env file if present
        env = project_env()
        env['FLASK_APP'] = 'app.py'
        env['FLASK_ENV'] = 'development' if debug else 'production'
        env['FLASK_DEBUG'] = '1' if debug else '0'
        
        # Build flask run command
        flask_cmd = [sys.executable, "-m", "flask", "run", "--host", host, "--port", str(port)]
        if reload:
            flask_cmd.append("--reload")
        
        click.echo(f"Starting Flask application on http://{host}:{port}")
        if debug:
            click.echo("Debug mode enabled")
        if reload:
            click.echo("Auto-reload enabled")
        
        # Run flask app
        subprocess.run(flask_cmd, env=env)
        
    except KeyboardInterrupt:
        click.echo("\nApplication stopped.")
    except Exception as e:
        click.echo(f"Error running application: {e}")
        raise click.Abort()


def _require_project() -> None:
    """Abort with a standard message if the cwd isn't a constrictor project."""
    if not os.path.exists('app.py') or not os.path.isdir('modules'):
        click.echo("Error: Not in a constrictor project. Run this command from the project root directory.")
        raise click.Abort()


def _discover_modules() -> List[str]:
    """List module names under modules/, in a stable order."""
    if not os.path.isdir('modules'):
        return []
    return sorted(
        name for name in os.listdir('modules')
        if os.path.isdir(os.path.join('modules', name))
    )


def _load_project_app():
    """
    Import the current project's app.py and return its Flask `app` instance.

    Importing app.py also runs constrictor.load(app), which imports every
    module's routes and models - exactly what migration hooks need to see
    a fully wired app. Loaded from an explicit absolute path under a private
    module name (rather than plain `import app`/sys.modules['app']) so this
    is correct even when called for multiple different projects within the
    same process - a plain module-name import would cache (or, on reload,
    re-execute from) whichever project's app.py was loaded first.
    """
    import importlib.util
    sys.path.insert(0, os.getcwd())
    app_path = os.path.join(os.getcwd(), 'app.py')
    module_name = '_constrictor_project_app'
    spec = importlib.util.spec_from_file_location(module_name, app_path)
    module = importlib.util.module_from_spec(spec)
    # Flask's root_path/instance_path resolution (get_root_path) looks the
    # module up in sys.modules by name while executing - without this, it
    # can't find it and silently resolves relative sqlite paths incorrectly.
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module.app


def _run_migration_hooks(hook_name: str, modules: List[str]) -> None:
    """
    Run modules/<name>/<hook_name>.py's run(app) for every module that defines
    one. Hooks are entirely optional - modules without a matching file are
    skipped silently.

    Args:
        hook_name: 'premigrate' or 'postmigrate'
        modules: module names to check, in listing order
    """
    hook_modules = [
        name for name in modules
        if os.path.exists(os.path.join('modules', name, f'{hook_name}.py'))
    ]
    if not hook_modules:
        return

    import importlib
    app = _load_project_app()

    for module_name in hook_modules:
        click.echo(f"Running {hook_name} hook for module '{module_name}'...")
        try:
            hook_module = importlib.import_module(f'modules.{module_name}.{hook_name}')
            if hasattr(hook_module, 'run'):
                hook_module.run(app)
            else:
                click.echo(f"Warning: modules/{module_name}/{hook_name}.py has no run(app) function, skipping.")
        except Exception as e:
            click.echo(f"Error running {hook_name} hook for module '{module_name}': {e}")
            raise click.Abort()


def _seed_access_csv(modules: List[str]) -> None:
    """
    Seed auth_role/auth_model_access from every module's access.csv, if
    present. Insert-if-missing only (see seed_access_from_csv) - safe to run
    on every upgrade.
    """
    csv_modules = [
        name for name in modules
        if os.path.exists(os.path.join('modules', name, 'access.csv'))
    ]
    if not csv_modules:
        return

    from constrictor.auth import seed_access_from_csv

    app = _load_project_app()
    with app.app_context():
        for module_name in csv_modules:
            csv_path = os.path.join('modules', module_name, 'access.csv')
            inserted = seed_access_from_csv(csv_path)
            if inserted:
                click.echo(f"Seeded {inserted} access grant(s) from '{module_name}/access.csv'")


def _run_flask_db_command(args: List[str]) -> subprocess.CompletedProcess:
    """Run `flask db <args>` for the current project and echo its output."""
    env = project_env()
    env['FLASK_APP'] = 'app.py'
    result = run_command([sys.executable, "-m", "flask", "db"] + args, check=False, env=env)
    if result.stdout:
        click.echo(result.stdout)
    if result.stderr:
        click.echo(result.stderr)
    return result


@main.group(name='db')
def db_group():
    """Database schema migration commands (SQLAlchemy + Alembic).

    Models live in each module's models.py as db.Model subclasses. These
    commands autogenerate and apply a single, project-wide migration history
    from all modules' models combined.
    """
    pass


@db_group.command(name='init')
def db_init():
    """Initialize the migrations/ directory. Run this once per project."""
    _require_project()
    if os.path.exists('migrations'):
        click.echo("Error: migrations/ already exists.")
        raise click.Abort()

    click.echo("Initializing migrations directory...")
    result = _run_flask_db_command(['init'])
    if result.returncode != 0:
        raise click.Abort()
    click.echo("Migrations directory created. Run 'constrictor db migrate' to create your first revision.")


@db_group.command(name='migrate')
@click.option('-m', '--message', default=None, help='Revision message')
def db_migrate(message):
    """Autogenerate a migration revision from the current models."""
    _require_project()
    if not os.path.exists('migrations'):
        click.echo("Error: No migrations/ directory found. Run 'constrictor db init' first.")
        raise click.Abort()

    args = ['migrate']
    if message:
        args += ['-m', message]

    click.echo("Generating migration revision...")
    result = _run_flask_db_command(args)
    if result.returncode != 0:
        raise click.Abort()


@db_group.command(name='upgrade')
@click.argument('revision', default='head', required=False)
def db_upgrade(revision):
    """Apply migrations up to REVISION (default: head).

    Runs each module's optional premigrate.py before, seeds auth_role/
    auth_model_access from each module's access.csv, then runs postmigrate.py.
    """
    _require_project()
    if not os.path.exists('migrations'):
        click.echo("Error: No migrations/ directory found. Run 'constrictor db init' first.")
        raise click.Abort()

    modules = _discover_modules()
    _run_migration_hooks('premigrate', modules)

    click.echo(f"Upgrading database to '{revision}'...")
    # '--' guards revisions that look like options (e.g. the '-1' default)
    # from being misparsed as flags by Click's argument parser.
    result = _run_flask_db_command(['upgrade', '--', revision])
    if result.returncode != 0:
        raise click.Abort()

    _seed_access_csv(modules)
    _run_migration_hooks('postmigrate', modules)
    click.echo("Database upgraded successfully!")


@db_group.command(name='downgrade')
@click.argument('revision', default='-1', required=False)
def db_downgrade(revision):
    """Revert migrations down to REVISION (default: one revision back).

    Runs each module's optional premigrate.py before and postmigrate.py after.
    """
    _require_project()
    if not os.path.exists('migrations'):
        click.echo("Error: No migrations/ directory found. Run 'constrictor db init' first.")
        raise click.Abort()

    modules = _discover_modules()
    _run_migration_hooks('premigrate', modules)

    click.echo(f"Downgrading database to '{revision}'...")
    result = _run_flask_db_command(['downgrade', '--', revision])
    if result.returncode != 0:
        raise click.Abort()

    _run_migration_hooks('postmigrate', modules)
    click.echo("Database downgraded successfully!")


@main.group(name='auth')
def auth_group():
    """User and role management commands.

    There's no admin UI, so these are the bootstrap path for creating the
    first role/user - e.g. `constrictor auth create-role admin` followed by
    `constrictor auth create-user you@example.com --role admin`.
    """
    pass


@auth_group.command(name='create-role')
@click.argument('name')
@click.option('--implies', default=None, help='Name of an existing role this role implies')
def auth_create_role(name, implies):
    """Create a role, optionally implying another existing role."""
    _require_project()

    try:
        from constrictor import db
        from constrictor.auth_models import Role

        app = _load_project_app()
        with app.app_context():
            if Role.query.filter_by(name=name).first():
                click.echo(f"Error: Role '{name}' already exists.")
                raise click.Abort()

            implied_role = None
            if implies:
                implied_role = Role.query.filter_by(name=implies).first()
                if implied_role is None:
                    click.echo(f"Error: Implied role '{implies}' does not exist.")
                    raise click.Abort()

            role = Role(name=name, implies=implied_role)
            db.session.add(role)
            db.session.commit()

            suffix = f" (implies '{implies}')" if implies else ""
            click.echo(f"Role '{name}' created{suffix}.")
    except click.Abort:
        raise
    except Exception as e:
        click.echo(f"Error creating role: {e}")
        click.echo("Make sure migrations have been applied: constrictor db init && constrictor db migrate && constrictor db upgrade")
        raise click.Abort()


@auth_group.command(name='create-user')
@click.argument('email')
@click.option('--role', '-r', 'roles', multiple=True, help='Role to assign (repeatable)')
@click.password_option()
def auth_create_user(email, roles, password):
    """Create a user, optionally assigning one or more existing roles."""
    _require_project()

    try:
        from constrictor import db
        from constrictor.auth_models import Role, User

        app = _load_project_app()
        with app.app_context():
            if User.query.filter_by(email=email).first():
                click.echo(f"Error: User '{email}' already exists.")
                raise click.Abort()

            user = User(email=email)
            user.set_password(password)

            for role_name in roles:
                role = Role.query.filter_by(name=role_name).first()
                if role is None:
                    click.echo(f"Error: Role '{role_name}' does not exist. Create it first with 'constrictor auth create-role'.")
                    raise click.Abort()
                user.roles.append(role)

            db.session.add(user)
            db.session.commit()

            suffix = f" with roles: {', '.join(roles)}" if roles else ""
            click.echo(f"User '{email}' created{suffix}.")
    except click.Abort:
        raise
    except Exception as e:
        click.echo(f"Error creating user: {e}")
        click.echo("Make sure migrations have been applied: constrictor db init && constrictor db migrate && constrictor db upgrade")
        raise click.Abort()


@main.group()
def swagger():
    """Swagger documentation commands."""
    pass


@swagger.command()
@click.option('--output', '-o', default='swagger.json', 
              help='Output file for Swagger documentation')
@click.option('--format', '-f', type=click.Choice(['json', 'yaml']), 
              default='json', help='Output format')
@click.option('--serve', '-s', is_flag=True, 
              help='Serve Swagger UI after generation')
@click.option('--port', '-p', default=8080, 
              help='Port for Swagger UI server (default: 8080)')
def build(output, format, serve, port):
    """Build Swagger documentation from all modules.
    
    This command scans all modules in the modules directory and generates
    comprehensive Swagger/OpenAPI documentation for the entire application.
    
    Examples:
        constrictor swagger build
        constrictor swagger build --output api-docs.yaml --format yaml
        constrictor swagger build --serve --port 8080
    """
    # Check if we're in a constrictor project
    if not os.path.exists('modules'):
        click.echo("Error: Not in a constrictor project. Run this command from the project root directory.")
        raise click.Abort()
    
    # Validate output format and adjust file extension
    if format == 'yaml' and not output.endswith(('.yaml', '.yml')):
        output = output.replace('.json', '.yaml')
    elif format == 'json' and not output.endswith('.json'):
        output = output.replace('.yaml', '.json').replace('.yml', '.json')
    
    try:
        click.echo("Building Swagger documentation...")
        
        project_path = Path('.')
        output_path = project_path / output
        
        # Generate Swagger documentation
        generator = SwaggerGenerator(project_path)
        swagger_spec = generator.build()
        generator.save_to_file(output_path, format)
        
        # Display results
        modules_found = len(generator.processed_modules)
        paths_found = len(swagger_spec.get('paths', {}))
        
        click.echo(f"✅ Swagger documentation generated successfully!")
        click.echo(f"📁 Output file: {output_path}")
        click.echo(f"📊 Modules processed: {modules_found}")
        click.echo(f"🛣️  API paths documented: {paths_found}")
        
        if modules_found == 0:
            click.echo("⚠️  No modules with routes found. Make sure you have modules with routes.py files.")
        elif paths_found == 0:
            click.echo("⚠️  No API routes found in modules. Check that your routes.py files have @blueprint.route decorators.")
        
        # Serve Swagger UI if requested
        if serve:
            click.echo(f"🌐 Starting Swagger UI server on port {port}...")
            _serve_swagger_ui(output_path, port)
            
    except Exception as e:
        click.echo(f"❌ Error generating Swagger documentation: {e}")
        raise click.Abort()


def _serve_swagger_ui(swagger_file: Path, port: int):
    """
    Serve Swagger UI for the generated documentation.
    
    Args:
        swagger_file: Path to the Swagger documentation file
        port: Port to serve on
    """
    try:
        import http.server
        import socketserver
        import webbrowser
        import json
        from urllib.parse import urljoin
        
        # Create a simple HTTP server
        class SwaggerHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(swagger_file.parent), **kwargs)
            
            def do_GET(self):
                if self.path == '/' or self.path == '/index.html':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    
                    # Generate HTML page with Swagger UI
                    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Constrictor API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui.css" />
    <style>
        html {{
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }}
        *, *:before, *:after {{
            box-sizing: inherit;
        }}
        body {{
            margin:0;
            background: #fafafa;
        }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            const ui = SwaggerUIBundle({{
                url: '{swagger_file.name}',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout"
            }});
        }};
    </script>
</body>
</html>
"""
                    self.wfile.write(html_content.encode())
                else:
                    super().do_GET()
        
        # Start server
        with socketserver.TCPServer(("", port), SwaggerHandler) as httpd:
            url = f"http://localhost:{port}"
            click.echo(f"🌐 Swagger UI available at: {url}")
            click.echo("📖 Press Ctrl+C to stop the server")
            
            # Try to open browser
            try:
                webbrowser.open(url)
            except:
                pass
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        click.echo("\n🛑 Swagger UI server stopped.")
    except Exception as e:
        click.echo(f"❌ Error serving Swagger UI: {e}")
        click.echo("💡 You can manually open the Swagger file in a browser or use an online Swagger editor.")


if __name__ == '__main__':
    main()
