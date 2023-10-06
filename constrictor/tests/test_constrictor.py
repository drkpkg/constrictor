import os
import pytest
from click.testing import CliRunner
from constrictor import main

@pytest.fixture
def mock_project(tmpdir):
    """Set up a mock constrictor project."""
    project_dir = tmpdir.mkdir("mock_project")
    app_file = project_dir.join("app.py")
    modules_dir = project_dir.mkdir("modules")
    app_file.write("print('Mock App')")
    return project_dir

def test_run_command_on_valid_project(mock_project):
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.chdir(mock_project)
        result = runner.invoke(main, ['run'])
        assert "This doesn't seem to be a valid 'constrictor' project." not in result.output
        assert " * Serving Flask app" in result.output

def test_valid_project_creation():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ['new', 'test_project'])
        assert result.exit_code == 0
        assert os.path.isdir('test_project')
        assert os.path.isdir('test_project/modules')

def test_existing_project_creation():
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.makedirs('existing_project')
        result = runner.invoke(main, ['new', 'existing_project'])
        assert result.exit_code != 0
        assert "Project already exists" in result.output  # Assuming you handle this scenario with this message

def test_valid_module_creation():
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.makedirs('modules')
        result = runner.invoke(main, ['generate', 'test_module'])
        assert result.exit_code == 0
        assert os.path.isdir('modules/test_module')

def test_existing_module_creation():
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.makedirs('modules/existing_module')
        result = runner.invoke(main, ['generate', 'existing_module'])
        assert result.exit_code != 0
        assert "Module already exists" in result.output  # Assuming you handle this scenario with this message


def test_run_missing_app():
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.makedirs('modules')
        result = runner.invoke(main, ['run'])
        assert "app.py file is missing" in result.output  # Assuming you handle this scenario with this message

def test_run_missing_modules_dir():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('app.py', 'w') as f:
            f.write("print('This is a mock app')")
        result = runner.invoke(main, ['run'])
        assert "modules directory is missing" in result.output  # Assuming you handle this scenario with this message

def test_testing_all_modules():
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.makedirs('modules/module1/tests')
        os.makedirs('modules/module2/tests')
        result = runner.invoke(main, ['test'])
        assert result.exit_code == 0

def test_testing_specific_modules():
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.makedirs('modules/module1/tests')
        os.makedirs('modules/module2/tests')
        result = runner.invoke(main, ['test', 'module1'])
        # Assuming some output indicating which module's tests are being run
        assert "Running tests for module1" in result.output
        assert "Running tests for module2" not in result.output

def test_testing_invalid_module_name():
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.makedirs('modules/module1/tests')
        result = runner.invoke(main, ['test', 'nonexistent_module'])
        assert "Module 'nonexistent_module' not found" in result.output  # Assuming you handle this scenario with this message

def test_module_with_no_tests():
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.makedirs('modules/module_without_tests')
        result = runner.invoke(main, ['test', 'module_without_tests'])
        assert "No tests found for module_without_tests" in result.output  # Assuming you handle this scenario with this message

def test_invalid_commands():
    runner = CliRunner()
    result = runner.invoke(main, ['nonexistent_command'])
    assert "No such command 'nonexistent_command'" in result.output

def test_invalid_arguments():
    runner = CliRunner()
    result = runner.invoke(main, ['new'])  # Assuming 'new' requires a project name argument
    assert "Missing argument" in result.output

def test_loading_dotenv():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('.env', 'w') as f:
            f.write("TEST_ENV_VAR=Success")
        result = runner.invoke(main, ['some_command_that_uses_env_var'])  # Replace with an actual command that uses the env var
        assert "Success" in result.output

def test_overriding_variables(monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('.env', 'w') as f:
            f.write("TEST_ENV_VAR=Success")
        monkeypatch.setenv("TEST_ENV_VAR", "Override")
        result = runner.invoke(main, ['some_command_that_uses_env_var'])  # Replace with an actual command that uses the env var
        assert "Override" in result.output

def test_full_workflow():
    runner = CliRunner()
    with runner.isolated_filesystem():
        runner.invoke(main, ['new', 'integration_project'])
        runner.invoke(main, ['generate', 'integration_module'])
        runner.invoke(main, ['run'])
        test_result = runner.invoke(main, ['test', 'integration_module'])
        assert test_result.exit_code == 0

def test_special_characters():
    runner = CliRunner()
    result = runner.invoke(main, ['generate', 'module$#!'])
    assert "Module name contains invalid characters" in result.output  # Assuming you handle this scenario with this message

def test_long_names():
    runner = CliRunner()
    long_name = "a" * 300
    result = runner.invoke(main, ['generate', long_name])
    assert "Module name is too long" in result.output  # Assuming you handle this scenario with this message

def test_empty_names():
    runner = CliRunner()
    result = runner.invoke(main, ['generate', ''])
    assert "Module name is required" in result.output  # Assuming you handle this scenario with this message
