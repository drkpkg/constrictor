# Blueprint loader:
# 
# This function is responsible for loading all the blueprints from the modules directory and registering them with the Flask app. It is called from the app.py file to set up the application.
# The function iterates over all the directories in the modules directory and imports the routes module from each directory.

def load(app):
    """Load all blueprints from the modules directory and register them with the app."""
    import os
    from importlib import import_module

    # Using app.instance_path
    root_path = app.root_path
    modules_dir = os.path.join(root_path, "modules")
    
    # Iterate over all directories in the modules directory
    for module_name in os.listdir(modules_dir):
        module_path = os.path.join(modules_dir, module_name)

        # Check if the module is a directory
        if os.path.isdir(module_path):
            # Import the routes module from the directory
            routes_module = f"modules.{module_name}.routes"
            routes = import_module(routes_module)

            # Register the blueprint with the app
            app.register_blueprint(routes.blueprint)