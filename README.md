# Constrictor

Constrictor is a microframework based on Flask, designed to simplify the creation and management of modular Flask applications. With features inspired by Rails, Constrictor allows for easy module generation, testing, and execution.

## Features

- **Modular Structure**: Organize your Flask app into separate modules with ease.
- **Blueprint Support**: Seamless integration with Flask Blueprints.
- **Command-Line Interface**: Simplified commands for creating projects, generating modules, running the app, and testing.
- **Environment Configuration**: Load configurations from `.env` files and environment variables.

## Installation

Install Constrictor via pip:

```bash
pip install constrictor
```

## Quick Start

1. **Create a New Project**:
   
   ```bash
   constrictor new project_name
   ```

2. **Generate a New Module**:

   ```bash
   constrictor g module module_name
   ```

3. **Run the App**:

   ```bash
   constrictor run
   ```

4. **Run Tests for All Modules**:

   ```bash
   constrictor test
   ```

5. **Run Tests for Specific Modules**:

   ```bash
   constrictor test module1 module2
   ```

## Documentation

In construction.