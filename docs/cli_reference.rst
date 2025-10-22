CLI Reference
=============

This section provides a comprehensive reference for all Constrictor command-line interface commands.

Command Overview
----------------

Constrictor provides the following main commands:

- ``new``: Create a new project
- ``generate``: Generate a new module
- ``run``: Start the development server
- ``test``: Run tests

Project Management Commands
---------------------------

constrictor new
~~~~~~~~~~~~~~~

Create a new Constrictor project.

**Usage:**
.. code-block:: bash

   constrictor new <project_name>

**Arguments:**
- ``project_name``: Name of the project to create

**Options:**
- ``--help``: Show help message

**Examples:**
.. code-block:: bash

   # Create a new project
   constrictor new my_app
   
   # Create a project with a specific name
   constrictor new blog_system

**What it does:**
- Creates a new directory with the project name
- Generates the basic project structure
- Creates a virtual environment
- Installs Flask and dependencies
- Initializes a Git repository
- Creates configuration files

**Generated Structure:**
.. code-block:: text

   project_name/
   ├── app.py
   ├── __init__.py
   ├── .env.example
   ├── .gitignore
   ├── requirements.txt
   └── modules/

Module Generation Commands
--------------------------

constrictor generate
~~~~~~~~~~~~~~~~~~~~

Generate a new module using YAML templates.

**Usage:**
.. code-block:: bash

   constrictor generate <module_name> [OPTIONS]

**Arguments:**
- ``module_name``: Name of the module to generate

**Options:**
- ``--template``, ``-t``: Template to use (default: yaml)
- ``--help``: Show help message

**Examples:**
.. code-block:: bash

   # Generate a module using default YAML template
   constrictor generate blog
   
   # Generate a module with custom template
   constrictor generate api --template custom_api.yml
   
   # Use the short alias
   constrictor g blog

**What it does:**
- Creates a new module directory
- Generates module files based on YAML template
- Creates routes, models, views, and tests
- Generates HTML templates
- Sets up module structure

**Generated Module Structure:**
.. code-block:: text

   modules/module_name/
   ├── __init__.py
   ├── routes.py
   ├── models.py
   ├── views.py
   ├── tests/
   │   └── test_module_name.py
   ├── views/
   ├── models/
   └── static/

Development Commands
--------------------

constrictor run
~~~~~~~~~~~~~~~

Start the development server.

**Usage:**
.. code-block:: bash

   constrictor run [OPTIONS]

**Options:**
- ``--host``: Host to bind to (default: 127.0.0.1)
- ``--port``: Port to bind to (default: 5000)
- ``--debug``: Enable debug mode
- ``--reload``: Enable auto-reload
- ``--help``: Show help message

**Examples:**
.. code-block:: bash

   # Start server with default settings
   constrictor run
   
   # Start server on specific host and port
   constrictor run --host 0.0.0.0 --port 8080
   
   # Start server in debug mode
   constrictor run --debug
   
   # Start server with auto-reload
   constrictor run --reload

**What it does:**
- Starts the Flask development server
- Loads all modules and blueprints
- Sets up environment variables
- Provides hot-reload functionality

Testing Commands
----------------

constrictor test
~~~~~~~~~~~~~~~

Run tests for modules.

**Usage:**
.. code-block:: bash

   constrictor test [MODULE_NAMES...] [OPTIONS]

**Arguments:**
- ``MODULE_NAMES``: Specific modules to test (optional)

**Options:**
- ``--verbose``, ``-v``: Verbose output
- ``--help``: Show help message

**Examples:**
.. code-block:: bash

   # Run all tests
   constrictor test
   
   # Run tests for specific modules
   constrictor test blog api
   
   # Run tests with verbose output
   constrictor test --verbose

**What it does:**
- Discovers test files in module directories
- Runs pytest with appropriate configuration
- Provides test results and coverage information
- Handles test failures gracefully

Command Aliases
---------------

Constrictor provides short aliases for common commands:

- ``g``: Alias for ``generate``
- ``r``: Alias for ``run``
- ``t``: Alias for ``test``

**Examples:**
.. code-block:: bash

   # Short aliases
   constrictor g blog
   constrictor r
   constrictor t

Environment Variables
---------------------

Constrictor respects the following environment variables:

- ``FLASK_APP``: Flask application file (default: app.py)
- ``FLASK_ENV``: Flask environment (development/production)
- ``FLASK_DEBUG``: Enable debug mode (True/False)
- ``FLASK_HOST``: Default host for run command
- ``FLASK_PORT``: Default port for run command

Configuration Files
-------------------

Constrictor looks for configuration in the following order:

1. Command-line arguments
2. Environment variables
3. Configuration files
4. Default values

Project Configuration
~~~~~~~~~~~~~~~~~~~~~

The ``.env.example`` file contains template environment variables:

.. code-block:: text

   # Flask Configuration
   FLASK_APP=app.py
   FLASK_ENV=development
   FLASK_DEBUG=True
   
   # Server Configuration
   FLASK_HOST=127.0.0.1
   FLASK_PORT=5000

Error Handling
--------------

Common Error Messages
~~~~~~~~~~~~~~~~~~~~~

**"Not in a constrictor project"**
   Run the command from the project root directory

**"Module already exists"**
   Choose a different module name or confirm overwrite

**"Template not found"**
   Ensure the template file exists and is accessible

**"Invalid module name"**
   Use valid Python identifier names

Troubleshooting
---------------

Command Not Found
~~~~~~~~~~~~~~~~~

If the ``constrictor`` command is not found:

.. code-block:: bash

   # Check if installed
   pip show constrictor
   
   # Reinstall if necessary
   pip install --upgrade constrictor

Permission Errors
~~~~~~~~~~~~~~~~~

If you encounter permission errors:

.. code-block:: bash

   # Use user installation
   pip install --user constrictor
   
   # Or use virtual environment
   python -m venv venv
   source venv/bin/activate
   pip install constrictor

Module Import Errors
~~~~~~~~~~~~~~~~~~~~

If modules fail to import:

.. code-block:: bash

   # Check module structure
   ls -la modules/
   
   # Verify Python path
   python -c "import sys; print(sys.path)"

Getting Help
------------

For command-specific help:

.. code-block:: bash

   # General help
   constrictor --help
   
   # Command-specific help
   constrictor generate --help
   constrictor run --help
   constrictor test --help

For additional support:
- Check the GitHub Issues page
- Review the documentation
- Test with simple examples first
