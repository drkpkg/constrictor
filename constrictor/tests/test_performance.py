import time
import os
from click.testing import CliRunner
from constrictor.cli import main

def test_performance_large_project():
    """Test performance when creating many modules."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Set up a constrictor project first
        result = runner.invoke(main, ['new', 'perf_test_project'])
        assert result.exit_code == 0
        
        os.chdir('perf_test_project')
        
        start_time = time.time()
        
        # Create 10 modules (reduced from 100 for faster tests)
        for i in range(10):
            result = runner.invoke(main, ['generate', f'module_{i}'])
            assert result.exit_code == 0
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should create 10 modules in less than 30 seconds
        assert duration < 30
        assert os.path.isdir('modules/module_0')
        assert os.path.isdir('modules/module_9')

def test_performance_project_creation():
    """Test performance of project creation."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        start_time = time.time()
        
        result = runner.invoke(main, ['new', 'perf_project'])
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Project creation should be fast
        assert result.exit_code == 0
        assert duration < 10  # Should create project in less than 10 seconds
