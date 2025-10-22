Examples
=========

This section provides practical examples of using Constrictor for different types of applications.

Basic Web Application
---------------------

Creating a Blog System
~~~~~~~~~~~~~~~~~~~~~~~

This example shows how to create a simple blog system with Constrictor.

1. **Create the project**:

   .. code-block:: bash

      constrictor new blog_system
      cd blog_system

2. **Generate the blog module**:

   .. code-block:: bash

      constrictor generate blog

3. **Generate additional modules**:

   .. code-block:: bash

      constrictor generate user
      constrictor generate comment

4. **Run the application**:

   .. code-block:: bash

      constrictor run

The generated structure will look like:

.. code-block:: text

   blog_system/
   ├── app.py
   ├── modules/
   │   ├── blog/
   │   │   ├── routes.py
   │   │   ├── models.py
   │   │   ├── views.py
   │   │   └── tests/
   │   ├── user/
   │   │   ├── routes.py
   │   │   ├── models.py
   │   │   ├── views.py
   │   │   └── tests/
   │   └── comment/
   │       ├── routes.py
   │       ├── models.py
   │       ├── views.py
   │       └── tests/
   └── templates/
       ├── blog/
       ├── user/
       └── comment/

API-Only Application
--------------------

Creating a REST API
~~~~~~~~~~~~~~~~~~~

This example shows how to create a REST API using custom templates.

1. **Create a custom API template** (``api_template.yml``):

   .. code-block:: yaml

      module:
        name: "{{module_name}}"
        description: "REST API module for {{module_name}}"
      
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

2. **Create the project**:

   .. code-block:: bash

      constrictor new api_system
      cd api_system

3. **Generate API modules**:

   .. code-block:: bash

      constrictor generate product --template api_template.yml
      constrictor generate order --template api_template.yml
      constrictor generate customer --template api_template.yml

4. **Run the API server**:

   .. code-block:: bash

      constrictor run --host 0.0.0.0 --port 8000

E-commerce Application
----------------------

Creating a Full E-commerce System
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This example shows how to create a complete e-commerce system.

1. **Create the project**:

   .. code-block:: bash

      constrictor new ecommerce
      cd ecommerce

2. **Generate core modules**:

   .. code-block:: bash

      constrictor generate product
      constrictor generate category
      constrictor generate cart
      constrictor generate order
      constrictor generate payment
      constrictor generate user
      constrictor generate admin

3. **Customize modules**:

   Edit the generated files to add e-commerce specific functionality:

   **Product Module** (``modules/product/models.py``):
   .. code-block:: python

      class Product:
          def __init__(self, name, price, description, category):
              self.id = None
              self.name = name
              self.price = price
              self.description = description
              self.category = category
              self.stock = 0
              self.created_at = None
          
          def to_dict(self):
              return {
                  'id': self.id,
                  'name': self.name,
                  'price': self.price,
                  'description': self.description,
                  'category': self.category,
                  'stock': self.stock,
                  'created_at': self.created_at
              }

   **Cart Module** (``modules/cart/routes.py``):

   .. code-block:: python

      from flask import Blueprint, request, jsonify
      
      blueprint = Blueprint('cart', __name__)
      
      @blueprint.route('/cart/add', methods=['POST'])
      def add_to_cart():
          data = request.get_json()
          # Add product to cart logic
          return jsonify({'message': 'Product added to cart'})
      
      @blueprint.route('/cart/remove/<product_id>', methods=['DELETE'])
      def remove_from_cart(product_id):
          # Remove product from cart logic
          return jsonify({'message': 'Product removed from cart'})

4. **Run the application**:

   .. code-block:: bash

      constrictor run --debug

Content Management System
-------------------------

Creating a CMS
~~~~~~~~~~~~~~

This example shows how to create a content management system.

1. **Create the project**:

   .. code-block:: bash

      constrictor new cms
      cd cms

2. **Generate CMS modules**:

   .. code-block:: bash

      constrictor generate page
      constrictor generate post
      constrictor generate media
      constrictor generate user
      constrictor generate admin

3. **Create custom templates for CMS**:

   **Page Template** (``page_template.yml``):
   .. code-block:: yaml

      module:
        name: "{{module_name}}"
        description: "CMS page module for {{module_name}}"
      
      routes:
        - path: "/{{module_name}}/"
          method: "GET"
          function: "index"
          template: "{{module_name}}/index.html"
          response_type: "html"
        
        - path: "/{{module_name}}/<slug>"
          method: "GET"
          function: "show"
          template: "{{module_name}}/show.html"
          response_type: "html"
        
        - path: "/{{module_name}}/create"
          method: "GET"
          function: "create_form"
          template: "{{module_name}}/create.html"
          response_type: "html"
        
        - path: "/{{module_name}}/create"
          method: "POST"
          function: "create"
          response_type: "html"
      
      templates:
        - name: "index.html"
          path: "{{module_name}}/index.html"
          content: |
            <!DOCTYPE html>
            <html>
            <head>
                <title>{{module_name|title}} Management</title>
            </head>
            <body>
                <h1>{{module_name|title}} Management</h1>
                <a href="/{{module_name}}/create">Create New {{module_name|title}}</a>
            </body>
            </html>

4. **Generate modules with custom templates**:

   .. code-block:: bash

      constrictor generate page --template page_template.yml
      constrictor generate post --template page_template.yml

5. **Run the CMS**:

   .. code-block:: bash

      constrictor run

Multi-tenant Application
------------------------

Creating a Multi-tenant System
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This example shows how to create a multi-tenant application.

1. **Create the project**:

   .. code-block:: bash

      constrictor new multitenant
      cd multitenant

2. **Generate tenant modules**:

   .. code-block:: bash

      constrictor generate tenant
      constrictor generate user
      constrictor generate subscription
      constrictor generate billing

3. **Add tenant isolation**:

   **Tenant Middleware** (``app.py``):

   .. code-block:: python

      from flask import Flask, request, g
      from constrictor.blueprint_loader import load
      
      app = Flask(__name__)
      
      @app.before_request
      def before_request():
          # Extract tenant from subdomain or header
          tenant = request.headers.get('X-Tenant-ID')
          if tenant:
              g.tenant = tenant
      
      # Load all blueprints
      load(app)
      
      if __name__ == '__main__':
          app.run(debug=True)

4. **Run the multi-tenant application**:

   .. code-block:: bash

      constrictor run --host 0.0.0.0

Testing Examples
----------------

Running Tests
~~~~~~~~~~~~~

1. **Run all tests**:

   .. code-block:: bash

      constrictor test

2. **Run tests for specific modules**:

   .. code-block:: bash

      constrictor test blog user

3. **Run tests with verbose output**:

   .. code-block:: bash

      constrictor test --verbose

Custom Test Examples
~~~~~~~~~~~~~~~~~~~~

**Testing API endpoints**:
.. code-block:: python

   def test_api_endpoint(client):
       response = client.get('/api/data/')
       assert response.status_code == 200
       assert response.is_json
       data = response.get_json()
       assert 'data' in data

**Testing form submissions**:
.. code-block:: python

   def test_form_submission(client):
       response = client.post('/form/', data={
           'name': 'Test User',
           'email': 'test@example.com'
       })
       assert response.status_code == 200
       assert 'success' in response.get_data(as_text=True)

Deployment Examples
-------------------

Docker Deployment
~~~~~~~~~~~~~~~~~

1. **Create Dockerfile**:

   .. code-block:: dockerfile

      FROM python:3.10-slim
      
      WORKDIR /app
      
      COPY requirements.txt .
      RUN pip install -r requirements.txt
      
      COPY . .
      
      EXPOSE 5000
      
      CMD ["constrictor", "run", "--host", "0.0.0.0"]

2. **Create docker-compose.yml**:

   .. code-block:: yaml

      version: '3.8'
      services:
        web:
          build: .
          ports:
            - "5000:5000"
          environment:
            - FLASK_ENV=production
            - FLASK_DEBUG=False

3. **Deploy with Docker**:

   .. code-block:: bash

      docker-compose up -d

Production Deployment
~~~~~~~~~~~~~~~~~~~~~

1. **Configure production environment**:

   .. code-block:: bash

      export FLASK_ENV=production
      export FLASK_DEBUG=False

2. **Use production WSGI server**:

   .. code-block:: bash

      pip install gunicorn
      gunicorn -w 4 -b 0.0.0.0:5000 app:app

3. **Set up reverse proxy with Nginx**:

   .. code-block:: nginx

      server {
          listen 80;
          server_name your-domain.com;
          
          location / {
              proxy_pass http://127.0.0.1:5000;
              proxy_set_header Host $host;
              proxy_set_header X-Real-IP $remote_addr;
          }
      }

Best Practices
--------------

Project Organization
~~~~~~~~~~~~~~~~~~~~

- Use descriptive module names
- Keep modules focused on single responsibilities
- Organize related functionality together
- Use consistent naming conventions

Template Management
~~~~~~~~~~~~~~~~~~~

- Store custom templates in version control
- Document template variables and usage
- Test templates with different module names
- Keep templates simple and maintainable

Testing Strategy
~~~~~~~~~~~~~~~~

- Write tests for all modules
- Test both success and error cases
- Use fixtures for common test setup
- Maintain high test coverage

Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~~

- Use lazy loading for modules
- Cache frequently accessed data
- Optimize database queries
- Monitor application performance

Security Considerations
~~~~~~~~~~~~~~~~~~~~~~~

- Validate all input data
- Use secure session management
- Implement proper authentication
- Keep dependencies updated
