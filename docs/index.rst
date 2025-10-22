Constrictor Documentation
========================

Constrictor is a microframework based on Flask, designed to simplify the creation and management of modular Flask applications. With features inspired by Rails, Constrictor allows for easy module generation, testing, and execution using YAML-based templates for maximum flexibility.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   architecture
   yaml_templates
   cli_reference
   api_reference
   examples
   contributing

Features
--------

* **Modular Structure**: Organize your Flask app into separate modules with ease
* **Blueprint Support**: Seamless integration with Flask Blueprints
* **YAML Templates**: Generate modules using declarative YAML templates for maximum flexibility and customization
* **Command-Line Interface**: Simplified commands for creating projects, generating modules, running the app, and testing
* **Environment Configuration**: Load configurations from `.env` files and environment variables
* **Automated Testing**: Built-in test generation and execution for all modules

Quick Start
-----------

1. Install Constrictor:

   .. code-block:: bash

      pip install constrictor

2. Create a new project:

   .. code-block:: bash

      constrictor new my_project

3. Generate a module:

   .. code-block:: bash

      constrictor generate my_module

4. Run the application:

   .. code-block:: bash

      constrictor run

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
