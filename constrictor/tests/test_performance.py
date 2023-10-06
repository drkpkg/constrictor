import time
from click.testing import CliRunner
from constrictor import main

def test_performance_large_project():
    runner = CliRunner()
    start_time = time.time()
    
    for i in range(100):  # Create 100 modules
        runner.invoke(main, ['generate', f'module_{i}'])
    
    end_time = time.time()
    assert end_time - start_time < 60  # For instance, ensure that creating 100 modules takes less than 60 seconds
