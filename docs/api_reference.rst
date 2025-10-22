API Reference
==============

This section provides detailed documentation for the Constrictor framework API.

Core Modules
------------

constrictor.cli
~~~~~~~~~~~~~~~~~~~~

Command-line interface module.

.. automodule:: constrictor.cli
   :members:
   :undoc-members:
   :show-inheritance:

constrictor.yaml_parser
~~~~~~~~~~~~~~~~~~~~~~~

YAML template parser module.

.. automodule:: constrictor.yaml_parser
   :members:
   :undoc-members:
   :show-inheritance:

constrictor.blueprint_loader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Blueprint loader module.

.. automodule:: constrictor.blueprint_loader
   :members:
   :undoc-members:
   :show-inheritance:

CLI Functions
-------------

Project Creation
~~~~~~~~~~~~~~~~

.. autofunction:: constrictor.cli.new

Module Generation
~~~~~~~~~~~~~~~~~

.. autofunction:: constrictor.cli.generate

Development Server
~~~~~~~~~~~~~~~~~~

.. autofunction:: constrictor.cli.run

Testing
~~~~~~~

.. autofunction:: constrictor.cli.test

YAML Parser Classes
-------------------

YamlTemplateParser
~~~~~~~~~~~~~~~~~~

.. autoclass:: constrictor.yaml_parser.YamlTemplateParser
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Blueprint Loader Functions
--------------------------

Module Loading
~~~~~~~~~~~~~~

.. autofunction:: constrictor.blueprint_loader.load
   :no-index:

Helper Functions
~~~~~~~~~~~~~~~~

.. autofunction:: constrictor.blueprint_loader._load_module_blueprint

.. autofunction:: constrictor.blueprint_loader.get_loaded_modules
   :no-index:

Utility Functions
-----------------

Name Validation
~~~~~~~~~~~~~~~

.. autofunction:: constrictor.cli.validate_name
   :no-index:

Command Execution
~~~~~~~~~~~~~~~~~

.. autofunction:: constrictor.cli.run_command
   :no-index:

Template Generation
~~~~~~~~~~~~~~~~~~~

.. autofunction:: constrictor.yaml_parser.generate_module_from_yaml
   :no-index:

Configuration
-------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

Constrictor uses the following environment variables:

.. code-block:: python

   FLASK_APP = "app.py"
   FLASK_ENV = "development"
   FLASK_DEBUG = "True"
   FLASK_HOST = "127.0.0.1"
   FLASK_PORT = "5000"

Template Configuration
~~~~~~~~~~~~~~~~~~~~~~

YAML templates support the following configuration options:

.. code-block:: yaml

   module:
     name: "{{module_name}}"
     description: "Module description"
   
   routes:
     - path: "/path/"
       method: "GET"
       function: "function_name"
       template: "template.html"
       response_type: "html"
   
   templates:
     - name: "template.html"
       path: "path/template.html"
       content: "template content"
   
   tests:
     - name: "test_file.py"
       content: "test content"
   
   structure:
     directories:
       - "directory_name"
     files:
       - name: "file_name"
         content: "file content"

Error Handling
--------------

Custom Exceptions
~~~~~~~~~~~~~~~~~

Constrictor uses standard Python exceptions for error handling:

- ``FileNotFoundError``: When template files are not found
- ``ValueError``: When invalid parameters are provided
- ``RuntimeError``: When module loading fails

Error Codes
~~~~~~~~~~~

Constrictor uses the following error codes:

- ``1``: General error
- ``2``: Template not found
- ``3``: Module load error
- ``4``: Configuration error

Logging
-------

Logging Configuration
~~~~~~~~~~~~~~~~~~~~~

Constrictor uses Python's built-in logging module:

.. code-block:: python

   import logging
   
   logger = logging.getLogger(__name__)
   logger.setLevel(logging.INFO)

Log Levels
~~~~~~~~~~

- ``DEBUG``: Detailed information for debugging
- ``INFO``: General information about program execution
- ``WARNING``: Warning messages for potential issues
- ``ERROR``: Error messages for recoverable errors
- ``CRITICAL``: Critical error messages

Log Format
~~~~~~~~~~

.. code-block:: text

   %(asctime)s - %(name)s - %(levelname)s - %(message)s

Testing
-------

Test Configuration
~~~~~~~~~~~~~~~~~~

Constrictor uses pytest for testing:

.. code-block:: python

   import pytest
   from flask import Flask
   from constrictor.blueprint_loader import load

Test Fixtures
~~~~~~~~~~~~~

Constrictor provides pytest fixtures for testing Flask applications:

- ``app``: Flask application fixture
- ``client``: Test client fixture

Test Functions
~~~~~~~~~~~~~~

.. autofunction:: constrictor.tests.test_constrictor.test_valid_project_creation

.. autofunction:: constrictor.tests.test_constrictor.test_valid_module_creation

Performance Testing
~~~~~~~~~~~~~~~~~~~

.. autofunction:: constrictor.tests.test_performance.test_performance_large_project

.. autofunction:: constrictor.tests.test_performance.test_performance_project_creation

Integration Examples
--------------------

Basic Module Generation
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from constrictor.yaml_parser import generate_module_from_yaml
   from pathlib import Path
   
   # Generate a module
   generate_module_from_yaml("my_module", Path("."))

Custom Template Usage
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from constrictor.yaml_parser import YamlTemplateParser
   
   # Create parser instance
   parser = YamlTemplateParser()
   
   # Load custom template
   template_data = parser.load_template("custom_template.yml")
   
   # Generate module structure
   parser.generate_module_structure("my_module", template_data, Path("."))

Blueprint Loading
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from constrictor.blueprint_loader import load
   from flask import Flask
   
   # Create Flask app
   app = Flask(__name__)
   
   # Load all blueprints
   load(app)

Advanced Usage
--------------

Custom Template Variables
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from constrictor.yaml_parser import YamlTemplateParser
   
   parser = YamlTemplateParser()
   
   # Custom context
   context = {
       'module_name': 'blog',
       'author': 'John Doe',
       'version': '1.0.0'
   }
   
   # Render template with custom context
   content = parser.render_template_content(template_content, context)

Template Validation
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from constrictor.yaml_parser import YamlTemplateParser
   import yaml
   
   parser = YamlTemplateParser()
   
   # Validate YAML syntax
   try:
       template_data = parser.load_template("template.yml")
       print("Template is valid")
   except yaml.YAMLError as e:
       print(f"YAML syntax error: {e}")

Module Discovery
~~~~~~~~~~~~~~~~

.. code-block:: python

   from constrictor.blueprint_loader import get_loaded_modules
   
   # Get list of loaded modules
   modules = get_loaded_modules()
   print(f"Loaded modules: {modules}")

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Import Errors**
   Ensure all dependencies are installed and Python path is correct

**Template Errors**
   Validate YAML syntax and template structure

**Module Load Errors**
   Check module structure and import statements

**Configuration Errors**
   Verify environment variables and configuration files

Debugging
~~~~~~~~~

Enable debug mode for detailed error information:

.. code-block:: python

   import logging
   
   # Enable debug logging
   logging.basicConfig(level=logging.DEBUG)
   
   # Use debug mode in Flask
   app.config['DEBUG'] = True

Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~~

- Use lazy loading for modules
- Cache template data
- Optimize database queries
- Use connection pooling
- Monitor memory usage
