"""
Swagger Documentation Generator for Constrictor Framework

This module provides functionality to generate Swagger/OpenAPI documentation
from Constrictor modules automatically by analyzing the routes and blueprints.
"""

import ast
import inspect
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime


class SwaggerGenerator:
    """Generator for Swagger/OpenAPI documentation from Constrictor modules."""
    
    def __init__(self, project_path: Path):
        """
        Initialize the Swagger generator.
        
        Args:
            project_path: Path to the Constrictor project root
        """
        self.project_path = project_path
        self.modules_path = project_path / "modules"
        self.swagger_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Constrictor API",
                "version": "1.0.0",
                "description": "API documentation for Constrictor modules",
                "contact": {
                    "name": "Constrictor Framework"
                },
                "license": {
                    "name": "MIT"
                }
            },
            "servers": [
                {
                    "url": "http://localhost:5000",
                    "description": "Development server"
                }
            ],
            "paths": {},
            "components": {
                "schemas": {},
                "responses": {},
                "parameters": {}
            },
            "tags": []
        }
        self.processed_modules: Set[str] = set()
    
    def build(self) -> Dict[str, Any]:
        """
        Build Swagger documentation from all modules.
        
        Returns:
            Complete Swagger/OpenAPI specification
        """
        modules = self._discover_modules()
        
        if not modules:
            return self.swagger_spec
        
        # Process each module
        for module_name in modules:
            self._process_module(module_name)
        
        # Add module tags
        self._add_module_tags()
        
        return self.swagger_spec
    
    def _discover_modules(self) -> List[str]:
        """
        Discover all modules in the modules directory.
        
        Returns:
            List of module names that have routes.py
        """
        if not self.modules_path.exists():
            return []
        
        modules = []
        for module_dir in self.modules_path.iterdir():
            if (module_dir.is_dir() and 
                (module_dir / "routes.py").exists()):
                modules.append(module_dir.name)
        
        return modules
    
    def _process_module(self, module_name: str) -> None:
        """
        Process a single module and extract API information.
        
        Args:
            module_name: Name of the module to process
        """
        routes_file = self.modules_path / module_name / "routes.py"
        
        if not routes_file.exists():
            return
        
        try:
            # Parse the routes.py file
            with open(routes_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Extract blueprint information
            blueprint_name = self._extract_blueprint_name(tree)
            
            # Try to find template metadata first
            template_metadata = self._load_template_metadata(module_name)
            
            # Process each function in the file
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Try to match with template metadata
                    route_info = self._extract_route_info(node, module_name, blueprint_name, template_metadata)
                    if route_info:
                        self._add_path_to_swagger(route_info)
            
            self.processed_modules.add(module_name)
            
        except Exception as e:
            print(f"Warning: Could not process module '{module_name}': {e}")
    
    def _load_template_metadata(self, module_name: str) -> Dict[str, Any]:
        """
        Load template metadata for a module if available.
        
        Args:
            module_name: Name of the module
            
        Returns:
            Dictionary with template metadata or empty dict
        """
        # Look for template files in the module directory
        module_dir = self.modules_path / module_name
        template_files = [
            module_dir / "template.yml",
            module_dir / "template.yaml",
            module_dir / "swagger.yml",
            module_dir / "swagger.yaml"
        ]
        
        for template_file in template_files:
            if template_file.exists():
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        template_data = yaml.safe_load(f)
                    return template_data.get('routes', [])
                except Exception as e:
                    print(f"Warning: Could not load template metadata from {template_file}: {e}")
        
        return []
    
    def _extract_blueprint_name(self, tree: ast.AST) -> Optional[str]:
        """
        Extract blueprint name from the AST.
        
        Args:
            tree: AST tree of the routes.py file
            
        Returns:
            Blueprint name if found, None otherwise
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == 'blueprint':
                        if isinstance(node.value, ast.Call):
                            if len(node.value.args) > 0:
                                if isinstance(node.value.args[0], ast.Constant):
                                    return node.value.args[0].value
        return None
    
    def _extract_route_info(self, func_node: ast.FunctionDef, 
                           module_name: str, blueprint_name: str, 
                           template_metadata: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Extract route information from a function node.
        
        Args:
            func_node: AST function definition node
            module_name: Name of the module
            blueprint_name: Name of the blueprint
            template_metadata: Template metadata for enhanced documentation
            
        Returns:
            Dictionary with route information or None
        """
        route_info = None
        
        # Look for @blueprint.route decorators
        for decorator in func_node.decorator_list:
            if (isinstance(decorator, ast.Call) and 
                isinstance(decorator.func, ast.Attribute) and
                decorator.func.attr == 'route'):
                
                route_info = self._parse_route_decorator(decorator, func_node, module_name)
                break
        
        if route_info:
            # Try to enhance with template metadata
            route_info = self._enhance_with_template_metadata(route_info, template_metadata)
        
        return route_info
    
    def _enhance_with_template_metadata(self, route_info: Dict[str, Any], 
                                       template_metadata: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Enhance route information with template metadata.
        
        Args:
            route_info: Basic route information
            template_metadata: Template metadata
            
        Returns:
            Enhanced route information
        """
        # Try to find matching route in template metadata
        for template_route in template_metadata:
            if (template_route.get('function') == route_info['function_name'] and
                template_route.get('path') == route_info['path']):
                
                # Enhance with Swagger metadata if available
                if 'swagger' in template_route:
                    swagger_data = template_route['swagger']
                    
                    # Override basic information with template data
                    if 'summary' in swagger_data:
                        route_info['summary'] = swagger_data['summary']
                    if 'description' in swagger_data:
                        route_info['description'] = swagger_data['description']
                    
                    # Add enhanced metadata
                    route_info['swagger_metadata'] = swagger_data
                    
                    # Extract parameters, responses, etc.
                    if 'parameters' in swagger_data:
                        route_info['parameters'] = swagger_data['parameters']
                    if 'responses' in swagger_data:
                        route_info['responses'] = swagger_data['responses']
                    if 'requestBody' in swagger_data:
                        route_info['requestBody'] = swagger_data['requestBody']
                    if 'tags' in swagger_data:
                        route_info['tags'] = swagger_data['tags']
                
                break
        
        return route_info
    
    def _parse_route_decorator(self, decorator: ast.Call, func_node: ast.FunctionDef, 
                              module_name: str) -> Optional[Dict[str, Any]]:
        """
        Parse route decorator to extract route information.
        
        Args:
            decorator: AST call node representing the route decorator
            func_node: Function definition node
            module_name: Name of the module
            
        Returns:
            Dictionary with route information or None
        """
        try:
            # Extract path from decorator arguments
            if not decorator.args:
                return None
            
            path_arg = decorator.args[0]
            if isinstance(path_arg, ast.Constant):
                path = path_arg.value
            elif isinstance(path_arg, ast.Str):  # Python < 3.8 compatibility
                path = path_arg.s
            else:
                return None
            
            # Extract method from keyword arguments
            method = 'GET'  # Default method
            for kw in decorator.keywords:
                if kw.arg == 'methods' and isinstance(kw.value, ast.List):
                    if kw.value.elts:
                        method_node = kw.value.elts[0]
                        if isinstance(method_node, ast.Constant):
                            method = method_node.value.upper()
                        elif isinstance(method_node, ast.Str):
                            method = method_node.s.upper()
            
            return {
                'path': path,
                'method': method,
                'function_name': func_node.name,
                'module_name': module_name,
                'summary': self._generate_summary(func_node.name),
                'description': self._generate_description(func_node, module_name)
            }
            
        except Exception as e:
            print(f"Warning: Could not parse route decorator: {e}")
            return None
    
    def _generate_summary(self, function_name: str) -> str:
        """
        Generate a summary from function name.
        
        Args:
            function_name: Name of the function
            
        Returns:
            Generated summary
        """
        return function_name.replace('_', ' ').title()
    
    def _generate_description(self, func_node: ast.FunctionDef, module_name: str) -> str:
        """
        Generate description from function docstring or name.
        
        Args:
            func_node: Function definition node
            module_name: Name of the module
            
        Returns:
            Generated description
        """
        if (func_node.body and 
            isinstance(func_node.body[0], ast.Expr) and
            isinstance(func_node.body[0].value, ast.Constant)):
            return func_node.body[0].value.value.strip()
        
        return f"Endpoint for {module_name} module - {func_node.name}"
    
    def _add_path_to_swagger(self, route_info: Dict[str, Any]) -> None:
        """
        Add a path to the Swagger specification.
        
        Args:
            route_info: Dictionary containing route information
        """
        path = route_info['path']
        method = route_info['method'].lower()
        
        # Convert Flask path parameters to OpenAPI format
        openapi_path = path.replace('<', '{').replace('>', '}')
        
        if openapi_path not in self.swagger_spec["paths"]:
            self.swagger_spec["paths"][openapi_path] = {}
        
        # Generate operation ID
        operation_id = f"{route_info['module_name']}_{route_info['function_name']}"
        
        # Start with basic operation
        operation = {
            "tags": route_info.get('tags', [route_info['module_name']]),
            "summary": route_info['summary'],
            "description": route_info['description'],
            "operationId": operation_id
        }
        
        # Use enhanced metadata if available
        if 'swagger_metadata' in route_info:
            swagger_data = route_info['swagger_metadata']
            
            # Add parameters if defined
            if 'parameters' in swagger_data:
                operation["parameters"] = swagger_data['parameters']
            
            # Add request body if defined
            if 'requestBody' in swagger_data:
                operation["requestBody"] = swagger_data['requestBody']
            
            # Add enhanced responses if defined
            if 'responses' in swagger_data:
                operation["responses"] = swagger_data['responses']
            else:
                # Fallback to basic response
                operation["responses"] = {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object"
                                }
                            }
                        }
                    }
                }
        else:
            # Fallback to basic responses
            operation["responses"] = {
                "200": {
                    "description": "Successful response",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object"
                            }
                        }
                    }
                }
            }
        
        # Extract parameters from path if not already defined
        if 'parameters' not in operation:
            path_parameters = self._extract_path_parameters(path)
            if path_parameters:
                operation["parameters"] = path_parameters
        
        self.swagger_spec["paths"][openapi_path][method] = operation
    
    def _extract_path_parameters(self, path: str) -> List[Dict[str, Any]]:
        """
        Extract parameters from Flask path.
        
        Args:
            path: Flask path string
            
        Returns:
            List of parameter definitions
        """
        parameters = []
        
        # Simple parameter extraction - can be enhanced
        if '<' in path and '>' in path:
            import re
            param_pattern = r'<([^:>]+)(?::([^>]+))?>'
            matches = re.findall(param_pattern, path)
            
            for converter, variable_name in matches:
                # Flask syntax is <converter:name> or just <name> (converter omitted).
                # When a converter is present it's captured first, so the variable
                # name is the second group; otherwise the first group is the name.
                param_name = variable_name if variable_name else converter
                param_type = converter if variable_name else "string"
                parameter = {
                    "name": param_name,
                    "in": "path",
                    "required": True,
                    "schema": {
                        "type": param_type
                    }
                }
                parameters.append(parameter)
        
        return parameters
    
    def _add_module_tags(self) -> None:
        """Add module tags to the Swagger specification."""
        for module_name in self.processed_modules:
            tag = {
                "name": module_name,
                "description": f"Operations for {module_name} module"
            }
            self.swagger_spec["tags"].append(tag)
    
    def save_to_file(self, output_path: Path, format: str = 'json') -> None:
        """
        Save Swagger specification to file.
        
        Args:
            output_path: Path where to save the file
            format: Output format ('json' or 'yaml')
        """
        if format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.swagger_spec, f, indent=2, ensure_ascii=False)
        elif format == 'yaml':
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.swagger_spec, f, default_flow_style=False, 
                         allow_unicode=True, sort_keys=False)
        else:
            raise ValueError(f"Unsupported format: {format}")


def generate_swagger_docs(project_path: Path, output_path: Path, 
                         format: str = 'json') -> Dict[str, Any]:
    """
    Generate Swagger documentation for a Constrictor project.
    
    Args:
        project_path: Path to the Constrictor project root
        output_path: Path where to save the documentation
        format: Output format ('json' or 'yaml')
        
    Returns:
        Generated Swagger specification
    """
    generator = SwaggerGenerator(project_path)
    swagger_spec = generator.build()
    generator.save_to_file(output_path, format)
    return swagger_spec
