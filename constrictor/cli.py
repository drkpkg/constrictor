import click
import os
import subprocess
import sys
import re
from pathlib import Path
from typing import List, Optional
from .yaml_parser import generate_module_from_yaml


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


def run_command(command: List[str], cwd: Optional[str] = None, check: bool = True) -> subprocess.CompletedProcess:
    """
    Run a command safely using subprocess.
    
    Args:
        command: Command to run as list of strings
        cwd: Working directory
        check: Whether to raise exception on non-zero exit code
        
    Returns:
        CompletedProcess result
    """
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
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
        app_content = '''from flask import Flask
from constrictor import load

app = Flask(__name__)
load(app)


@app.route('/')
def index():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(debug=True)
'''
        
        with open(project_path / "app.py", 'w') as f:
            f.write(app_content)
        
        # Create __init__.py
        with open(project_path / "__init__.py", 'w') as f:
            f.write("# Project initialization file\n")
        
        # Create .env template
        env_content = '''# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration (if needed)
# DATABASE_URL=sqlite:///app.db

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
        requirements_content = '''Flask>=3.0.3
python-dotenv>=1.0.1
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
                run_command([str(pip_path), "install", "Flask>=3.0.3", "python-dotenv>=1.0.1"], cwd=project_name)
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
def generate_alias(module_name):
    """Generate a new module (alias for 'generate')."""
    generate(module_name)


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
            result = run_command(["python", "-m", "pytest", "-v"])
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
            result = run_command(["python", "-m", "pytest", "-v"] + valid_modules)
        
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
        # Set environment variables
        env = os.environ.copy()
        env['FLASK_APP'] = 'app.py'
        env['FLASK_ENV'] = 'development' if debug else 'production'
        env['FLASK_DEBUG'] = '1' if debug else '0'
        
        # Build flask run command
        flask_cmd = ["python", "-m", "flask", "run", "--host", host, "--port", str(port)]
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


if __name__ == '__main__':
    main()
