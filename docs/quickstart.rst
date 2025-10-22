Quick Start Guide
=================

This guide will help you get started with Constrictor by creating your first project and module.

Creating Your First Project
---------------------------

1. **Create a new project**:

   .. code-block:: bash

      constrictor new my_first_project

   This command creates a new directory with the following structure:

   .. code-block:: text

      my_first_project/
      ├── app.py                 # Main Flask application
      ├── __init__.py           # Package initialization
      ├── .env.example          # Environment variables template
      ├── .gitignore           # Git ignore file
      ├── requirements.txt     # Python dependencies
      └── modules/             # Application modules (empty initially)

2. **Navigate to your project**:

   .. code-block:: bash

      cd my_first_project

3. **Activate the virtual environment**:

   .. code-block:: bash

      source .venv/bin/activate  # On Windows: .venv\Scripts\activate

Generating Your First Module
----------------------------

1. **Generate a module**:

   .. code-block:: bash

      constrictor generate blog

   This creates a complete module structure:

   .. code-block:: text

      modules/
      └── blog/
          ├── __init__.py
          ├── routes.py         # Blueprint routes
          ├── models.py         # Data models
          ├── views.py          # View functions
          ├── tests/            # Module tests
          │   └── test_blog.py
          ├── views/            # Additional views
          ├── models/           # Additional models
          └── static/           # Static assets

2. **Check the generated files**:

   The module includes:
   - **routes.py**: Contains Flask routes for the blog module
   - **models.py**: Data models for blog posts
   - **views.py**: View functions and controllers
   - **tests/**: Automated tests for the module

Running Your Application
------------------------

1. **Start the development server**:

   .. code-block:: bash

      constrictor run

   The server will start on `http://localhost:5000`

2. **Test your routes**:

   Visit the following URLs in your browser:
   - `http://localhost:5000/blog/` - Blog index page
   - `http://localhost:5000/blog/hello/` - Hello message
   - `http://localhost:5000/blog/api/` - API endpoint

Running Tests
-------------

1. **Run all tests**:

   .. code-block:: bash

      constrictor test

2. **Run tests for a specific module**:

   .. code-block:: bash

      constrictor test blog

3. **Run tests with verbose output**:

   .. code-block:: bash

      constrictor test --verbose

Next Steps
----------

Now that you have a basic project running, you can:

1. **Customize your module**: Edit the generated files to add your own functionality
2. **Create more modules**: Generate additional modules for different features
3. **Use custom templates**: Create YAML templates for specific module types
4. **Add database support**: Integrate with your preferred database
5. **Deploy your application**: Follow deployment best practices

For more detailed information, see the :doc:`yaml_templates` and :doc:`cli_reference` sections.
