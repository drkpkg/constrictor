import os
import pytest
from click.testing import CliRunner
from constrictor.cli import main
from pathlib import Path

@pytest.fixture
def mock_project(tmpdir):
    """Set up a mock constrictor project."""
    project_dir = tmpdir.mkdir("mock_project")
    app_file = project_dir.join("app.py")
    modules_dir = project_dir.mkdir("modules")
    app_file.write("print('Mock App')")
    return project_dir

def test_valid_project_creation():
    """Test creating a new project."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ['new', 'test_project'])
        assert result.exit_code == 0
        assert os.path.isdir('test_project')
        assert os.path.isdir('test_project/modules')
        assert os.path.isfile('test_project/app.py')
        assert os.path.isfile('test_project/requirements.txt')
        assert os.path.isfile('test_project/.gitignore')

def test_existing_project_creation():
    """Test creating a project that already exists."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.makedirs('existing_project')
        result = runner.invoke(main, ['new', 'existing_project'], input='y\n')
        assert result.exit_code == 0
        assert "Project already exists" in result.output

def test_invalid_project_name():
    """Test creating a project with invalid name."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ['new', '123invalid'])
        assert result.exit_code != 0
        assert "Invalid project name" in result.output

def test_valid_module_creation():
    """Test creating a new module."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.makedirs('modules')
        result = runner.invoke(main, ['generate', 'test_module'])
        assert result.exit_code == 0
        assert os.path.isdir('modules/test_module')
        assert os.path.isfile('modules/test_module/routes.py')
        assert os.path.isdir('modules/test_module/tests')
        assert os.path.isdir('modules/test_module/templates')

def test_module_alias_g():
    """Test using the 'g' alias for generate command."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.makedirs('modules')
        result = runner.invoke(main, ['g', 'test_module_g'])
        assert result.exit_code == 0
        assert os.path.isdir('modules/test_module_g')

def test_existing_module_creation():
    """Test creating a module that already exists."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.makedirs('modules/existing_module')
        result = runner.invoke(main, ['generate', 'existing_module'], input='y\n')
        assert result.exit_code == 0
        assert "Module already exists" in result.output


def test_run_missing_app():
    """Test run command when app.py is missing."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.makedirs('modules')
        result = runner.invoke(main, ['run'])
        assert result.exit_code != 0
        assert "Not in a valid 'constrictor' project" in result.output

def test_run_missing_modules_dir():
    """Test run command when modules directory is missing."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('app.py', 'w') as f:
            f.write("print('This is a mock app')")
        result = runner.invoke(main, ['run'])
        assert result.exit_code != 0
        assert "Not in a valid 'constrictor' project" in result.output

def test_testing_all_modules():
    """Test running all tests."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.makedirs('app.py', exist_ok=True)
        os.makedirs('modules/module1/tests')
        os.makedirs('modules/module2/tests')
        result = runner.invoke(main, ['test'])
        # Should not crash, even if no tests exist
        assert result.exit_code in [0, 5]  # 5 is pytest's exit code for no tests found

def test_testing_specific_modules():
    """Test running tests for specific modules."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('app.py', 'w') as f:
            f.write("print('Mock app')")
        os.makedirs('modules/module1/tests')
        os.makedirs('modules/module2/tests')
        result = runner.invoke(main, ['test', 'module1'])
        assert "Running tests for modules: module1" in result.output

def test_testing_invalid_module_name():
    """Test running tests with invalid module name."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('app.py', 'w') as f:
            f.write("print('Mock app')")
        os.makedirs('modules')
        result = runner.invoke(main, ['test', '123invalid'])
        assert "Invalid module name '123invalid'" in result.output

def test_module_with_no_tests():
    """Test running tests for module without test directory."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('app.py', 'w') as f:
            f.write("print('Mock app')")
        os.makedirs('modules/module_without_tests')
        result = runner.invoke(main, ['test', 'module_without_tests'])
        assert "No tests found for module 'module_without_tests'" in result.output

def test_invalid_commands():
    """Test running invalid commands."""
    runner = CliRunner()
    result = runner.invoke(main, ['nonexistent_command'])
    assert result.exit_code != 0
    assert "No such command" in result.output

def test_invalid_arguments():
    """Test running commands with missing arguments."""
    runner = CliRunner()
    result = runner.invoke(main, ['new'])
    assert result.exit_code != 0
    assert "Missing argument" in result.output

def test_full_workflow():
    """Test complete workflow: create project, generate module, run tests."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create project
        result = runner.invoke(main, ['new', 'integration_project'])
        assert result.exit_code == 0
        
        # Change to project directory
        os.chdir('integration_project')
        
        # Generate module
        result = runner.invoke(main, ['generate', 'integration_module'])
        assert result.exit_code == 0
        assert os.path.isdir('modules/integration_module')
        
        # Test module
        result = runner.invoke(main, ['test', 'integration_module'])
        # Should not crash even if no actual tests exist

def test_special_characters():
    """Test module name with special characters."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.makedirs('modules')
        result = runner.invoke(main, ['generate', 'module$#!'])
        assert result.exit_code != 0
        assert "Invalid module name" in result.output

def test_long_names():
    """Test module name that's too long."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.makedirs('modules')
        long_name = "a" * 300
        result = runner.invoke(main, ['generate', long_name])
        assert result.exit_code != 0
        assert "Invalid module name" in result.output

def test_empty_names():
    """Test empty module name."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.makedirs('modules')
        result = runner.invoke(main, ['generate', ''])
        assert result.exit_code != 0
        assert "Missing argument" in result.output
