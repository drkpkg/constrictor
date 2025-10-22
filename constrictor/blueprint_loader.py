"""
Blueprint loader module for Constrictor framework.

This module is responsible for loading all the blueprints from the modules 
directory and registering them with the Flask app. It provides robust error 
handling and logging for module loading operations.
"""

import os
import logging
from importlib import import_module
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)


def load(app) -> None:
    """
    Load all blueprints from the modules directory and register them with the app.
    
    Args:
        app: Flask application instance
        
    Raises:
        FileNotFoundError: If modules directory doesn't exist
        ImportError: If there are issues importing module routes
    """
    root_path = app.root_path
    modules_dir = os.path.join(root_path, "modules")
    
    # Validate modules directory exists
    if not os.path.exists(modules_dir):
        logger.warning(f"Modules directory not found at {modules_dir}")
        return
    
    if not os.path.isdir(modules_dir):
        logger.error(f"Modules path exists but is not a directory: {modules_dir}")
        return
    
    # Get list of directories in modules folder
    try:
        module_names = [name for name in os.listdir(modules_dir) 
                       if os.path.isdir(os.path.join(modules_dir, name))]
    except OSError as e:
        logger.error(f"Error reading modules directory: {e}")
        return
    
    if not module_names:
        logger.info("No modules found in modules directory")
        return
    
    logger.info(f"Found {len(module_names)} modules: {', '.join(module_names)}")
    
    # Load each module with error handling
    for module_name in module_names:
        try:
            _load_module_blueprint(app, module_name, modules_dir)
        except Exception as e:
            logger.error(f"Failed to load module '{module_name}': {e}")
            continue


def _load_module_blueprint(app, module_name: str, modules_dir: str) -> None:
    """
    Load a specific module blueprint.
    
    Args:
        app: Flask application instance
        module_name: Name of the module to load
        modules_dir: Path to the modules directory
        
    Raises:
        ImportError: If the module cannot be imported
        AttributeError: If the module doesn't have a blueprint attribute
    """
    module_path = os.path.join(modules_dir, module_name)
    routes_file = os.path.join(module_path, "routes.py")
    
    # Check if routes.py exists
    if not os.path.exists(routes_file):
        logger.warning(f"Module '{module_name}' has no routes.py file")
        return
    
    # Import the routes module
    try:
        routes_module_name = f"modules.{module_name}.routes"
        routes = import_module(routes_module_name)
        
        # Check if blueprint exists in the module
        if not hasattr(routes, 'blueprint'):
            logger.warning(f"Module '{module_name}' routes.py doesn't define a 'blueprint' variable")
            return
        
        # Register the blueprint with the app
        app.register_blueprint(routes.blueprint)
        logger.info(f"Successfully loaded blueprint for module '{module_name}'")
        
    except ImportError as e:
        logger.error(f"Failed to import routes from module '{module_name}': {e}")
        raise
    except AttributeError as e:
        logger.error(f"Module '{module_name}' doesn't have required blueprint attribute: {e}")
        raise


def get_loaded_modules() -> list:
    """
    Get list of currently loaded modules.
    
    Returns:
        List of module names that have been successfully loaded
    """
    # This could be enhanced to track loaded modules
    # For now, return empty list as we don't track this
    return []