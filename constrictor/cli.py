import click
import os
import subprocess


@click.group()
def main():
    """Constrictor: A microframework CLI tool for Flask.

    Use this tool to generate projects, modules, and manage your Flask applications.
    """
    pass


@main.command()
@click.argument('project_name')
def new(project_name):
    """Create a new project.

    This command initializes a new Flask project with the specified name. It sets up the basic directory structure and provides an environment for module generation.
    """
    os.makedirs(os.path.join(project_name, "modules"), exist_ok=True)
    with open(os.path.join(project_name, "app.py"), 'w') as f:
        f.write("""
from flask import Flask
from constrictor import blueprint_loader

app = Flask(__name__)
blueprint_loader.load(app)


@app.route('/')
def index():
    return 'Hello, World!'

""")
    with open(os.path.join(project_name, "__init__.py"), 'w') as f:
        f.write("# Project initialization file\n")
    os.system(f"cd {project_name} && python -m venv .venv")
    os.system(f"cd {project_name} && .venv/bin/pip install Flask")
    os.system(f"cd {project_name} && git init")
    with open(os.path.join(project_name, ".gitignore"), 'w') as f:
        f.write(".venv\n__pycache__\n*.pyc\n")

    os.system(f"cd {project_name} && .venv/bin/pip freeze > requirements.txt")
    click.echo(f"Project {project_name} created successfully.")


@main.command()
@click.argument('module_name')
def generate(module_name):
    """Generate a new module.

    This command creates a new module inside the 'modules' directory of your Flask project. The module will have a basic structure including routes, tests, views, and models.
    """
    base_path = os.path.join(os.getcwd(), 'modules', module_name)

    # Create the main module directory
    os.makedirs(base_path, exist_ok=True)

    # Create __init__.py inside the module directory
    with open(os.path.join(base_path, '__init__.py'), 'w') as f:
        f.write("# Module initialization file\n")

    # Create routes.py with a sample route
    with open(os.path.join(base_path, 'routes.py'), 'w') as f:
        f.write("""
from flask import Blueprint

blueprint = Blueprint('{}', __name__)

@blueprint.route('/{}/')
def index():
    return "Hello from {} module!"
""".format(module_name, module_name, module_name))

    # Create directories for tests, views, and models with __init__.py files
    for sub_dir in ['tests', 'views', 'models']:
        os.makedirs(os.path.join(base_path, sub_dir), exist_ok=True)
        with open(os.path.join(base_path, sub_dir, '__init__.py'), 'w') as f:
            f.write("# {} initialization file\n".format(sub_dir.capitalize()))

    # Add more commands and logic as needed


@main.command()
@click.argument('modules', nargs=-1)
def test(modules):
    """Run tests.

    This command runs tests for the entire application or specific modules. 
    Use it without arguments to test all modules or specify module names to test specific ones.
    """
    if not modules:
        pytest_command = "pytest"
    else:
        module_test_paths = [
            f"modules/{module_name}/tests" for module_name in modules]
        pytest_command = f"pytest {' '.join(module_test_paths)}"

    subprocess.run(pytest_command.split())


@main.command()
def run():
    """Run the Flask application.

    This command identifies if the current directory is a valid 'constrictor' project and then runs the Flask application.
    """
    if not os.path.exists('app.py') or not os.path.isdir('modules'):
        click.echo(
            "This doesn't seem to be a valid 'constrictor' project. Ensure you're in the project root and 'app.py' exists.")
        return

    os.system('flask run')


if __name__ == '__main__':
    main()
