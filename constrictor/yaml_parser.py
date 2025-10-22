"""
YAML Template Parser for Constrictor Framework

This module handles parsing YAML templates and generating module structures.
"""

import os
import yaml
import jinja2
from pathlib import Path
from typing import Dict, List, Any, Optional


class YamlTemplateParser:
    """Parser for YAML templates used in module generation."""
    
    def __init__(self, template_dir: str = None):
        """Initialize the YAML template parser.
        
        Args:
            template_dir: Directory containing YAML templates
        """
        if template_dir is None:
            # Default to the templates directory in the constrictor package
            template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        
        self.template_dir = Path(template_dir)
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
    
    def load_template(self, template_name: str = "module_template.yml") -> Dict[str, Any]:
        """Load a YAML template file.
        
        Args:
            template_name: Name of the template file
            
        Returns:
            Parsed YAML template as dictionary
        """
        template_path = self.template_dir / template_name
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        try:
            return yaml.safe_load(template_content)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML template: {e}")
    
    def render_template_content(self, content: str, context: Dict[str, Any]) -> str:
        """Render template content using Jinja2.
        
        Args:
            content: Template content string
            context: Context variables for rendering
            
        Returns:
            Rendered content string
        """
        template = self.jinja_env.from_string(content)
        return template.render(**context)
    
    def generate_module_structure(self, module_name: str, template_data: Dict[str, Any], 
                                output_dir: Path) -> None:
        """Generate module structure from YAML template.
        
        Args:
            module_name: Name of the module to generate
            template_data: Parsed YAML template data
            output_dir: Directory where to generate the module
        """
        context = {'module_name': module_name}
        
        # Create module directory
        module_dir = output_dir / 'modules' / module_name
        module_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate structure
        if 'structure' in template_data:
            self._generate_structure(module_name, template_data['structure'], 
                                   module_dir, context)
        
        # Generate routes
        if 'routes' in template_data:
            self._generate_routes(module_name, template_data['routes'], 
                                module_dir, context)
        
        # Generate templates
        if 'templates' in template_data:
            self._generate_templates(module_name, template_data['templates'], 
                                   output_dir, context)
        
        # Generate tests
        if 'tests' in template_data:
            self._generate_tests(module_name, template_data['tests'], 
                               module_dir, context)
    
    def _generate_structure(self, module_name: str, structure_data: Dict[str, Any], 
                          module_dir: Path, context: Dict[str, Any]) -> None:
        """Generate directory structure and files."""
        
        # Create directories
        if 'directories' in structure_data:
            for dir_name in structure_data['directories']:
                dir_path = module_dir / dir_name
                dir_path.mkdir(exist_ok=True)
                
                # Create __init__.py for Python directories
                if dir_name in ['tests', 'views', 'models']:
                    init_file = dir_path / '__init__.py'
                    with open(init_file, 'w') as f:
                        f.write(f"# {module_name} {dir_name} initialization file\n")
        
        # Create files
        if 'files' in structure_data:
            for file_data in structure_data['files']:
                file_path = module_dir / file_data['name']
                
                if 'template' in file_data:
                    # Load template file
                    template_path = self.template_dir / file_data['template']
                    with open(template_path, 'r') as f:
                        template_content = f.read()
                    rendered_content = self.render_template_content(template_content, context)
                else:
                    # Use direct content
                    rendered_content = self.render_template_content(file_data['content'], context)
                
                with open(file_path, 'w') as f:
                    f.write(rendered_content)
    
    def _generate_routes(self, module_name: str, routes_data: List[Dict[str, Any]], 
                        module_dir: Path, context: Dict[str, Any]) -> None:
        """Generate routes.py file from YAML routes definition."""
        
        routes_content = "from flask import Blueprint, render_template\n\n"
        routes_content += f"blueprint = Blueprint('{module_name}', __name__)\n\n"
        
        for route in routes_data:
            path = self.render_template_content(route['path'], context)
            function_name = route['function']
            method = route.get('method', 'GET')
            
            routes_content += f"@blueprint.route('{path}')\n"
            routes_content += f"def {function_name}():\n"
            
            if route.get('response_type') == 'html' and 'template' in route:
                template_path = self.render_template_content(route['template'], context)
                routes_content += f"    return render_template('{template_path}', module_name='{module_name}')\n"
            elif route.get('response_type') == 'json':
                routes_content += f"    return {{'module': '{module_name}', 'status': 'active'}}\n"
            else:
                routes_content += f"    return 'Hello from {module_name} module!'\n"
            
            routes_content += "\n"
        
        routes_file = module_dir / 'routes.py'
        with open(routes_file, 'w') as f:
            f.write(routes_content)
    
    def _generate_templates(self, module_name: str, templates_data: List[Dict[str, Any]], 
                          output_dir: Path, context: Dict[str, Any]) -> None:
        """Generate HTML templates from YAML definition."""
        
        # Create templates directory in project root
        templates_dir = output_dir / 'templates'
        templates_dir.mkdir(exist_ok=True)
        
        for template_data in templates_data:
            template_path = self.render_template_content(template_data['path'], context)
            template_file = templates_dir / template_path
            template_file.parent.mkdir(parents=True, exist_ok=True)
            
            rendered_content = self.render_template_content(template_data['content'], context)
            
            with open(template_file, 'w') as f:
                f.write(rendered_content)
    
    def _generate_tests(self, module_name: str, tests_data: List[Dict[str, Any]], 
                       module_dir: Path, context: Dict[str, Any]) -> None:
        """Generate test files from YAML definition."""
        
        tests_dir = module_dir / 'tests'
        tests_dir.mkdir(exist_ok=True)
        
        for test_data in tests_data:
            # Render the filename as well
            rendered_filename = self.render_template_content(test_data['name'], context)
            test_file = tests_dir / rendered_filename
            rendered_content = self.render_template_content(test_data['content'], context)
            
            with open(test_file, 'w') as f:
                f.write(rendered_content)


def generate_module_from_yaml(module_name: str, output_dir: Path, 
                            template_name: str = None) -> None:
    """Generate a module from YAML template.
    
    Args:
        module_name: Name of the module to generate
        output_dir: Directory where to generate the module
        template_name: Name of the YAML template file (defaults to module_template.yml)
    """
    if template_name is None or template_name == 'yaml':
        template_name = "module_template.yml"
    
    parser = YamlTemplateParser()
    template_data = parser.load_template(template_name)
    parser.generate_module_structure(module_name, template_data, output_dir)
