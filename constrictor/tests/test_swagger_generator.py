"""
Tests for Swagger Generator functionality.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, mock_open
import json
import yaml

from constrictor.swagger_generator import SwaggerGenerator, generate_swagger_docs


class TestSwaggerGenerator:
    """Test cases for SwaggerGenerator class."""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project structure for testing."""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir)
        
        # Create modules directory
        modules_dir = project_path / "modules"
        modules_dir.mkdir()
        
        # Create a test module
        test_module_dir = modules_dir / "test_module"
        test_module_dir.mkdir()
        
        # Create routes.py file
        routes_content = '''
from flask import Blueprint, jsonify

blueprint = Blueprint('test_module', __name__)

@blueprint.route('/test_module/')
def index():
    """Get test module index page"""
    return jsonify({"message": "Hello from test module"})

@blueprint.route('/test_module/api/')
def api():
    """Get test module API data"""
    return {"module": "test_module", "status": "active"}

@blueprint.route('/test_module/users/<int:user_id>/')
def get_user(user_id):
    """Get user by ID"""
    return {"id": user_id, "name": "Test User"}
'''
        
        routes_file = test_module_dir / "routes.py"
        routes_file.write_text(routes_content)
        
        yield project_path
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def temp_project_with_metadata(self):
        """Create a temporary project with template metadata."""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir)
        
        # Create modules directory
        modules_dir = project_path / "modules"
        modules_dir.mkdir()
        
        # Create a test module
        test_module_dir = modules_dir / "test_module"
        test_module_dir.mkdir()
        
        # Create routes.py file
        routes_content = '''
from flask import Blueprint, jsonify

blueprint = Blueprint('test_module', __name__)

@blueprint.route('/test_module/')
def index():
    """Get test module index page"""
    return jsonify({"message": "Hello from test module"})

@blueprint.route('/test_module/api/users/')
def get_users():
    """Get users list"""
    return {"users": [], "total": 0}
'''
        
        routes_file = test_module_dir / "routes.py"
        routes_file.write_text(routes_content)
        
        # Create template metadata file
        template_metadata = {
            'routes': [
                {
                    'path': '/test_module/',
                    'method': 'GET',
                    'function': 'index',
                    'swagger': {
                        'summary': 'Get test module index page',
                        'description': 'Returns the main page for test module',
                        'tags': ['test_module'],
                        'responses': {
                            '200': {
                                'description': 'Successful response',
                                'content': {
                                    'application/json': {
                                        'schema': {
                                            'type': 'object',
                                            'properties': {
                                                'message': {'type': 'string'}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                {
                    'path': '/test_module/api/users/',
                    'method': 'GET',
                    'function': 'get_users',
                    'swagger': {
                        'summary': 'Get users list',
                        'description': 'Returns a list of users',
                        'tags': ['test_module', 'users'],
                        'parameters': [
                            {
                                'name': 'limit',
                                'in': 'query',
                                'description': 'Maximum number of users to return',
                                'required': False,
                                'schema': {'type': 'integer', 'minimum': 1, 'maximum': 100}
                            }
                        ],
                        'responses': {
                            '200': {
                                'description': 'List of users returned successfully',
                                'content': {
                                    'application/json': {
                                        'schema': {
                                            'type': 'object',
                                            'properties': {
                                                'users': {'type': 'array'},
                                                'total': {'type': 'integer'}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            ]
        }
        
        template_file = test_module_dir / "template.yml"
        with open(template_file, 'w') as f:
            yaml.dump(template_metadata, f)
        
        yield project_path
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_init(self, temp_project):
        """Test SwaggerGenerator initialization."""
        generator = SwaggerGenerator(temp_project)
        
        assert generator.project_path == temp_project
        assert generator.modules_path == temp_project / "modules"
        assert generator.swagger_spec["openapi"] == "3.0.0"
        assert generator.swagger_spec["info"]["title"] == "Constrictor API"
        assert generator.processed_modules == set()
    
    def test_discover_modules(self, temp_project):
        """Test module discovery."""
        generator = SwaggerGenerator(temp_project)
        modules = generator._discover_modules()
        
        assert len(modules) == 1
        assert "test_module" in modules
    
    def test_discover_modules_empty(self):
        """Test module discovery with no modules."""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir)
        
        try:
            generator = SwaggerGenerator(project_path)
            modules = generator._discover_modules()
            assert modules == []
        finally:
            shutil.rmtree(temp_dir)
    
    def test_extract_blueprint_name(self, temp_project):
        """Test blueprint name extraction."""
        generator = SwaggerGenerator(temp_project)
        
        routes_file = temp_project / "modules" / "test_module" / "routes.py"
        content = routes_file.read_text()
        
        import ast
        tree = ast.parse(content)
        blueprint_name = generator._extract_blueprint_name(tree)
        
        assert blueprint_name == "test_module"
    
    def test_parse_route_decorator(self, temp_project):
        """Test route decorator parsing."""
        generator = SwaggerGenerator(temp_project)
        
        routes_file = temp_project / "modules" / "test_module" / "routes.py"
        content = routes_file.read_text()
        
        import ast
        tree = ast.parse(content)
        
        # Find the first function with route decorator
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "index":
                for decorator in node.decorator_list:
                    if (isinstance(decorator, ast.Call) and 
                        isinstance(decorator.func, ast.Attribute) and
                        decorator.func.attr == 'route'):
                        
                        route_info = generator._parse_route_decorator(decorator, node, "test_module")
                        assert route_info is not None
                        assert route_info['path'] == '/test_module/'
                        assert route_info['method'] == 'GET'
                        assert route_info['function_name'] == 'index'
                        assert route_info['module_name'] == 'test_module'
                        break
    
    def test_extract_path_parameters(self, temp_project):
        """Test path parameter extraction."""
        generator = SwaggerGenerator(temp_project)
        
        # Test with path parameters
        parameters = generator._extract_path_parameters('/test_module/users/<int:user_id>/')
        assert len(parameters) == 1
        assert parameters[0]['name'] == 'user_id'
        assert parameters[0]['in'] == 'path'
        assert parameters[0]['required'] is True
        assert parameters[0]['schema']['type'] == 'int'
        
        # Test without path parameters
        parameters = generator._extract_path_parameters('/test_module/')
        assert parameters == []
    
    def test_build_basic(self, temp_project):
        """Test basic Swagger spec building."""
        generator = SwaggerGenerator(temp_project)
        swagger_spec = generator.build()
        
        assert "paths" in swagger_spec
        assert len(swagger_spec["paths"]) > 0
        assert "test_module" in generator.processed_modules
        
        # Check if routes were added
        assert "/test_module/" in swagger_spec["paths"]
        assert "/test_module/api/" in swagger_spec["paths"]
    
    def test_build_with_metadata(self, temp_project_with_metadata):
        """Test Swagger spec building with template metadata."""
        generator = SwaggerGenerator(temp_project_with_metadata)
        swagger_spec = generator.build()
        
        assert "paths" in swagger_spec
        assert len(swagger_spec["paths"]) > 0
        
        # Check if enhanced metadata was used
        test_path = swagger_spec["paths"].get("/test_module/", {})
        if test_path:
            get_op = test_path.get("get", {})
            assert "summary" in get_op
            assert "description" in get_op
            assert "responses" in get_op
    
    def test_load_template_metadata(self, temp_project_with_metadata):
        """Test template metadata loading."""
        generator = SwaggerGenerator(temp_project_with_metadata)
        metadata = generator._load_template_metadata("test_module")
        
        assert len(metadata) == 2
        assert metadata[0]['path'] == '/test_module/'
        assert metadata[1]['path'] == '/test_module/api/users/'
    
    def test_enhance_with_template_metadata(self, temp_project):
        """Test route enhancement with template metadata."""
        generator = SwaggerGenerator(temp_project)
        
        route_info = {
            'path': '/test_module/',
            'method': 'GET',
            'function_name': 'index',
            'module_name': 'test_module',
            'summary': 'Basic summary',
            'description': 'Basic description'
        }
        
        template_metadata = [
            {
                'path': '/test_module/',
                'function': 'index',
                'swagger': {
                    'summary': 'Enhanced summary',
                    'description': 'Enhanced description',
                    'tags': ['test_module', 'api']
                }
            }
        ]
        
        enhanced = generator._enhance_with_template_metadata(route_info, template_metadata)
        
        assert enhanced['summary'] == 'Enhanced summary'
        assert enhanced['description'] == 'Enhanced description'
        assert 'swagger_metadata' in enhanced
        assert enhanced['swagger_metadata']['tags'] == ['test_module', 'api']
    
    def test_save_to_file_json(self, temp_project):
        """Test saving Swagger spec to JSON file."""
        generator = SwaggerGenerator(temp_project)
        swagger_spec = generator.build()
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.save_to_file(output_path, 'json')
            
            # Verify file was created and contains valid JSON
            assert output_path.exists()
            with open(output_path, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data["openapi"] == "3.0.0"
            assert "paths" in saved_data
        finally:
            output_path.unlink()
    
    def test_save_to_file_yaml(self, temp_project):
        """Test saving Swagger spec to YAML file."""
        generator = SwaggerGenerator(temp_project)
        swagger_spec = generator.build()
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.save_to_file(output_path, 'yaml')
            
            # Verify file was created and contains valid YAML
            assert output_path.exists()
            with open(output_path, 'r') as f:
                saved_data = yaml.safe_load(f)
            
            assert saved_data["openapi"] == "3.0.0"
            assert "paths" in saved_data
        finally:
            output_path.unlink()
    
    def test_generate_swagger_docs_function(self, temp_project):
        """Test the generate_swagger_docs function."""
        # Create temporary output file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            swagger_spec = generate_swagger_docs(temp_project, output_path, 'json')
            
            # Verify function returns valid spec
            assert swagger_spec["openapi"] == "3.0.0"
            assert "paths" in swagger_spec
            
            # Verify file was created
            assert output_path.exists()
        finally:
            output_path.unlink()
    
    def test_error_handling_invalid_project(self):
        """Test error handling for invalid project path."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create a directory without modules
            project_path = Path(temp_dir)
            generator = SwaggerGenerator(project_path)
            
            # Should not raise exception, just return empty spec
            swagger_spec = generator.build()
            assert swagger_spec["paths"] == {}
        finally:
            shutil.rmtree(temp_dir)
    
    def test_add_module_tags(self, temp_project):
        """Test adding module tags to Swagger spec."""
        generator = SwaggerGenerator(temp_project)
        generator.processed_modules.add("test_module")
        generator.processed_modules.add("another_module")
        
        generator._add_module_tags()
        
        tags = generator.swagger_spec["tags"]
        assert len(tags) == 2
        
        tag_names = [tag["name"] for tag in tags]
        assert "test_module" in tag_names
        assert "another_module" in tag_names
