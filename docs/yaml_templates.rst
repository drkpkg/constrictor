YAML Templates
==============

Constrictor uses YAML templates to define the structure and content of generated modules. This approach provides maximum flexibility and allows for easy customization.

Template Structure
------------------

Basic Template Format
~~~~~~~~~~~~~~~~~~~~~~

YAML templates follow a specific structure:

.. code-block:: yaml

   module:
     name: "{{module_name}}"
     description: "Generated module for {{module_name}}"
   
   routes:
     - path: "/{{module_name}}/"
       method: "GET"
       function: "index"
       template: "{{module_name}}/index.html"
       response_type: "html"
   
   templates:
     - name: "index.html"
       path: "{{module_name}}/index.html"
       content: |
         <!DOCTYPE html>
         <html>
         <head>
             <title>{{module_name|title}} Module</title>
         </head>
         <body>
             <h1>{{module_name|title}} Module</h1>
         </body>
         </html>
   
   tests:
     - name: "test_{{module_name}}.py"
       content: |
         import pytest
         from flask import Flask
         from modules.{{module_name}}.routes import blueprint
         
         @pytest.fixture
         def app():
             app = Flask(__name__)
             app.register_blueprint(blueprint)
             app.config['TESTING'] = True
             return app
   
   structure:
     directories:
       - "tests"
       - "views"
       - "models"
       - "static"
     
     files:
       - name: "__init__.py"
         content: "# {{module_name}} module initialization file\n"

Template Sections
-----------------

Module Configuration
~~~~~~~~~~~~~~~~~~~~

The ``module`` section defines basic module information:

.. code-block:: yaml

   module:
     name: "{{module_name}}"
     description: "Generated module for {{module_name}}"

Routes Definition
~~~~~~~~~~~~~~~~~

The ``routes`` section defines API endpoints and web routes:

.. code-block:: yaml

   routes:
     - path: "/{{module_name}}/"
       method: "GET"
       function: "index"
       template: "{{module_name}}/index.html"
       response_type: "html"
     
     - path: "/{{module_name}}/api/"
       method: "GET"
       function: "api"
       response_type: "json"

Templates Definition
~~~~~~~~~~~~~~~~~~~~

The ``templates`` section defines HTML templates:

.. code-block:: yaml

   templates:
     - name: "index.html"
       path: "{{module_name}}/index.html"
       content: |
         <!DOCTYPE html>
         <html>
         <head>
             <title>{{module_name|title}} Module</title>
         </head>
         <body>
             <h1>{{module_name|title}} Module</h1>
         </body>
         </html>

Tests Definition
~~~~~~~~~~~~~~~~

The ``tests`` section defines test files:

.. code-block:: yaml

   tests:
     - name: "test_{{module_name}}.py"
       content: |
         import pytest
         from flask import Flask
         from modules.{{module_name}}.routes import blueprint
         
         @pytest.fixture
         def app():
             app = Flask(__name__)
             app.register_blueprint(blueprint)
             app.config['TESTING'] = True
             return app

Structure Definition
~~~~~~~~~~~~~~~~~~~~

The ``structure`` section defines directories and files:

.. code-block:: yaml

   structure:
     directories:
       - "tests"
       - "views"
       - "models"
       - "static"
     
     files:
       - name: "__init__.py"
         content: "# {{module_name}} module initialization file\n"
       
       - name: "routes.py"
         template: "routes_template.py"

Template Variables
------------------

Available Variables
~~~~~~~~~~~~~~~~~~~

Templates support the following Jinja2 variables:

- ``{{module_name}}``: The name of the module being generated
- ``{{module_name|title}}``: Capitalized module name
- ``{{module_name|lower}}``: Lowercase module name
- ``{{module_name|upper}}``: Uppercase module name

Custom Variables
~~~~~~~~~~~~~~~~

You can add custom variables to the template context by modifying the YAML parser.

Template Filters
~~~~~~~~~~~~~~~~

Jinja2 filters are available for string manipulation:

- ``|title``: Capitalize first letter of each word
- ``|lower``: Convert to lowercase
- ``|upper``: Convert to uppercase
- ``|replace(old, new)``: Replace text

Creating Custom Templates
-------------------------

Template Types
~~~~~~~~~~~~~~

You can create different types of templates:

**API Module Template**
   For modules that only provide API endpoints

**Web Module Template**
   For modules with HTML templates and web interfaces

**Hybrid Module Template**
   For modules that provide both API and web interfaces

**Database Module Template**
   For modules with database models and operations

Example Custom Template
~~~~~~~~~~~~~~~~~~~~~~~

Here's an example of a custom API-only template:

.. code-block:: yaml

   module:
     name: "{{module_name}}"
     description: "API module for {{module_name}}"
   
   routes:
     - path: "/{{module_name}}/api/"
       method: "GET"
       function: "list"
       response_type: "json"
     
     - path: "/{{module_name}}/api/<id>"
       method: "GET"
       function: "get"
       response_type: "json"
     
     - path: "/{{module_name}}/api/"
       method: "POST"
       function: "create"
       response_type: "json"
   
   tests:
     - name: "test_{{module_name}}.py"
       content: |
         import pytest
         from flask import Flask
         from modules.{{module_name}}.routes import blueprint
         
         @pytest.fixture
         def app():
             app = Flask(__name__)
             app.register_blueprint(blueprint)
             app.config['TESTING'] = True
             return app
         
         def test_{{module_name}}_list(client):
             response = client.get('/{{module_name}}/api/')
             assert response.status_code == 200
             assert response.is_json

Template Best Practices
-----------------------

Naming Conventions
~~~~~~~~~~~~~~~~~~

- Use descriptive names for template files
- Include the template type in the filename
- Use consistent naming patterns across templates

Content Organization
~~~~~~~~~~~~~~~~~~~~

- Keep templates focused and specific
- Use clear, readable YAML structure
- Include comprehensive documentation in comments

Testing Templates
~~~~~~~~~~~~~~~~~

- Test templates with different module names
- Verify generated files are syntactically correct
- Ensure tests pass for generated modules

Version Control
~~~~~~~~~~~~~~~

- Store custom templates in version control
- Document template changes and updates
- Tag template versions for consistency

Template Examples
-----------------

Basic Web Module
~~~~~~~~~~~~~~~~

A simple web module with HTML templates:

.. code-block:: yaml

   module:
     name: "{{module_name}}"
     description: "Basic web module for {{module_name}}"
   
   routes:
     - path: "/{{module_name}}/"
       method: "GET"
       function: "index"
       template: "{{module_name}}/index.html"
       response_type: "html"
   
   templates:
     - name: "index.html"
       path: "{{module_name}}/index.html"
       content: |
         <!DOCTYPE html>
         <html>
         <head>
             <title>{{module_name|title}} Module</title>
         </head>
         <body>
             <h1>{{module_name|title}} Module</h1>
             <p>Welcome to the {{module_name}} module!</p>
         </body>
         </html>

RESTful API Module
~~~~~~~~~~~~~~~~~~

A RESTful API module with CRUD operations:

.. code-block:: yaml

   module:
     name: "{{module_name}}"
     description: "RESTful API module for {{module_name}}"
   
   routes:
     - path: "/{{module_name}}/api/"
       method: "GET"
       function: "list"
       response_type: "json"
     
     - path: "/{{module_name}}/api/<id>"
       method: "GET"
       function: "get"
       response_type: "json"
     
     - path: "/{{module_name}}/api/"
       method: "POST"
       function: "create"
       response_type: "json"
     
     - path: "/{{module_name}}/api/<id>"
       method: "PUT"
       function: "update"
       response_type: "json"
     
     - path: "/{{module_name}}/api/<id>"
       method: "DELETE"
       function: "delete"
       response_type: "json"

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Template Not Found**
   Ensure the template file exists and is accessible

**YAML Syntax Errors**
   Validate YAML syntax using online validators

**Template Rendering Errors**
   Check Jinja2 syntax and variable names

**Generated Files Issues**
   Verify file permissions and directory structure

Getting Help
~~~~~~~~~~~~

For template-related issues:
- Check the GitHub Issues page
- Review the template examples
- Validate YAML syntax
- Test with simple templates first
