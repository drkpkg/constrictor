Contributing
=============

We welcome contributions to Constrictor! This guide will help you get started with contributing to the project.

Getting Started
---------------

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:

   .. code-block:: bash

      git clone https://github.com/your-username/constrictor.git
      cd constrictor

3. **Create a virtual environment**:

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate  # On Windows: venv\Scripts\activate

4. **Install in development mode**:

   .. code-block:: bash

      pip install -e .[dev]

Development Setup
-----------------

Install Development Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install -e .[dev]

This installs:
- Sphinx for documentation
- pytest for testing
- black for code formatting
- flake8 for linting

Code Style
----------

Formatting
~~~~~~~~~~

We use Black for code formatting:

.. code-block:: bash

   black constrictor/
   black tests/

Linting
~~~~~~~

We use flake8 for linting:

.. code-block:: bash

   flake8 constrictor/
   flake8 tests/

Type Hints
~~~~~~~~~~

We encourage the use of type hints:

.. code-block:: python

   from typing import List, Dict, Optional
   
   def process_data(data: List[str]) -> Dict[str, int]:
       """Process data and return results."""
       pass

Testing
-------

Running Tests
~~~~~~~~~~~~~

Run all tests:

.. code-block:: bash

   pytest

Run tests with coverage:

.. code-block:: bash

   pytest --cov=constrictor

Run specific test files:

.. code-block:: bash

   pytest tests/test_cli.py
   pytest tests/test_yaml_parser.py

Writing Tests
~~~~~~~~~~~~~

Test Structure
~~~~~~~~~~~~~~

Follow this structure for tests:

.. code-block:: python

   import pytest
   from constrictor.cli import validate_name
   
   def test_validate_name_valid():
       """Test valid name validation."""
       assert validate_name("test_module", "module") == True
   
   def test_validate_name_invalid():
       """Test invalid name validation."""
       assert validate_name("123invalid", "module") == False

Test Naming
~~~~~~~~~~~

Use descriptive test names:

- ``test_function_name_scenario``
- ``test_class_name_method_name_scenario``
- ``test_module_name_feature_scenario``

Test Coverage
~~~~~~~~~~~~~

Maintain high test coverage:
- Aim for 90%+ coverage
- Test both success and error cases
- Test edge cases and boundary conditions

Documentation
-------------

Code Documentation
~~~~~~~~~~~~~~~~~~

Document all public functions and classes:

.. code-block:: python

   def generate_module(module_name: str, template: str = None) -> None:
       """Generate a new module using YAML templates.
       
       Args:
           module_name: Name of the module to generate
           template: Optional custom template to use
       
       Raises:
           ValueError: If module name is invalid
           FileNotFoundError: If template is not found
       """
       pass

Docstring Format
~~~~~~~~~~~~~~~~

Use Google-style docstrings:

.. code-block:: python

   def function_name(param1: str, param2: int) -> bool:
       """Brief description of the function.
       
       Longer description if needed.
       
       Args:
           param1: Description of param1
           param2: Description of param2
       
       Returns:
           Description of return value
       
       Raises:
           ValueError: Description of when this exception is raised
       """
       pass

Documentation Updates
~~~~~~~~~~~~~~~~~~~~~

When adding new features:
1. Update the relevant documentation files
2. Add examples if applicable
3. Update the API reference
4. Update the CLI reference

Pull Request Process
--------------------

1. **Create a feature branch**:

   .. code-block:: bash

      git checkout -b feature/new-feature

2. **Make your changes**:
   - Write code following the style guidelines
   - Add tests for new functionality
   - Update documentation
   - Ensure all tests pass

3. **Commit your changes**:

   .. code-block:: bash

      git add .
      git commit -m "Add new feature: description"

4. **Push to your fork**:

   .. code-block:: bash

      git push origin feature/new-feature

5. **Create a Pull Request** on GitHub

Pull Request Guidelines
-----------------------

Title and Description
~~~~~~~~~~~~~~~~~~~~~

- Use clear, descriptive titles
- Provide detailed descriptions
- Reference related issues
- Include screenshots for UI changes

Code Quality
~~~~~~~~~~~~

- Ensure all tests pass
- Maintain code coverage
- Follow style guidelines
- Add appropriate documentation

Review Process
~~~~~~~~~~~~~~

- Address review comments promptly
- Make requested changes
- Respond to feedback constructively
- Keep PRs focused and manageable

Issue Reporting
---------------

Bug Reports
~~~~~~~~~~~

When reporting bugs, include:

- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Error messages and stack traces

Feature Requests
~~~~~~~~~~~~~~~~

When requesting features, include:

- Clear description of the feature
- Use cases and motivation
- Proposed implementation (if applicable)
- Examples of similar features in other projects

Development Workflow
--------------------

Branch Strategy
~~~~~~~~~~~~~~~

- ``main``: Stable, production-ready code
- ``develop``: Integration branch for features
- ``feature/*``: Feature development branches
- ``bugfix/*``: Bug fix branches
- ``hotfix/*``: Critical bug fixes

Commit Messages
~~~~~~~~~~~~~~~

Follow the conventional commit format:

.. code-block:: text

   type(scope): description
   
   [optional body]
   
   [optional footer]

Types:
- ``feat``: New feature
- ``fix``: Bug fix
- ``docs``: Documentation changes
- ``style``: Code style changes
- ``refactor``: Code refactoring
- ``test``: Test additions/changes
- ``chore``: Maintenance tasks

Examples:

.. code-block:: text

   feat(cli): add support for custom templates
   fix(yaml): handle missing template files
   docs(api): update API reference
   test(parser): add tests for template validation

Release Process
---------------

Version Numbering
~~~~~~~~~~~~~~~~~

We use semantic versioning (MAJOR.MINOR.PATCH):

- ``MAJOR``: Breaking changes
- ``MINOR``: New features, backward compatible
- ``PATCH``: Bug fixes, backward compatible

Release Steps
~~~~~~~~~~~~~

1. Update version numbers
2. Update changelog
3. Create release tag
4. Build and test package
5. Publish to PyPI
6. Update documentation

Community Guidelines
--------------------

Code of Conduct
~~~~~~~~~~~~~~~

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Follow the golden rule

Communication
~~~~~~~~~~~~~

- Use clear, professional language
- Be patient with newcomers
- Ask questions when unsure
- Share knowledge and experience

Getting Help
------------

- Check existing issues and PRs
- Join our community discussions
- Ask questions in GitHub Discussions
- Contact maintainers for urgent issues

Resources
---------

- `GitHub Repository <https://github.com/daniel/constrictor>`_
- `Issue Tracker <https://github.com/daniel/constrictor/issues>`_
- `Pull Requests <https://github.com/daniel/constrictor/pulls>`_
- `Discussions <https://github.com/daniel/constrictor/discussions>`_

Thank you for contributing to Constrictor!
