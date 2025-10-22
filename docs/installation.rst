Installation
============

Prerequisites
-------------

Constrictor requires Python 3.8 or higher. Make sure you have Python installed on your system.

Installation Methods
--------------------

Install from PyPI
~~~~~~~~~~~~~~~~~

The recommended way to install Constrictor is using pip:

.. code-block:: bash

   pip install constrictor

Install from Source
~~~~~~~~~~~~~~~~~~~

To install from source, clone the repository and install in development mode:

.. code-block:: bash

   git clone https://github.com/drkpkg/constrictor.git
   cd constrictor
   pip install -e .

Verify Installation
-------------------

After installation, verify that Constrictor is properly installed:

.. code-block:: bash

   constrictor --help

You should see the Constrictor CLI help message.

Dependencies
------------

Constrictor automatically installs the following dependencies:

* **Flask**: Web framework
* **Click**: Command-line interface
* **PyYAML**: YAML template processing
* **pytest**: Testing framework
* **pytest-flask**: Flask testing utilities
* **python-dotenv**: Environment variable management

Development Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~

For development, additional dependencies are available:

.. code-block:: bash

   pip install constrictor[dev]

This installs:

* **Sphinx**: Documentation generation
* **myst-parser**: Markdown parsing for documentation
* **sphinx-rtd-theme**: Read the Docs theme

Troubleshooting
---------------

Common Installation Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Permission Errors**
   If you encounter permission errors, try using the `--user` flag:

   .. code-block:: bash

      pip install --user constrictor

**Virtual Environment Issues**
   Make sure you're using a virtual environment:

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate  # On Windows: venv\Scripts\activate
      pip install constrictor

**Python Version Issues**
   Ensure you're using Python 3.8 or higher:

   .. code-block:: bash

      python --version

If you continue to have issues, please check the `GitHub Issues <https://github.com/drkpkg/constrictor/issues>`_ page.
