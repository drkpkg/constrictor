from flask import Blueprint, render_template, request, jsonify
from datetime import datetime

blueprint = Blueprint('{{module_name}}', __name__)

# Sample data for demonstration
users_data = [
    {"id": 1, "name": "John Doe", "email": "john@example.com", "created_at": "2023-01-01T00:00:00Z"},
    {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "created_at": "2023-01-02T00:00:00Z"},
    {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "created_at": "2023-01-03T00:00:00Z"}
]

@blueprint.route('/{{module_name}}/')
def index():
    """Get {{module_name}} index page"""
    return render_template('{{module_name}}/index.html', module_name='{{module_name}}')

@blueprint.route('/{{module_name}}/hello/')
def hello():
    """Hello endpoint for {{module_name}}"""
    return "Hello from {{module_name}} module!"

@blueprint.route('/{{module_name}}/api/')
def api():
    """Get {{module_name}} API data"""
    return {"module": "{{module_name}}", "status": "active"}

@blueprint.route('/{{module_name}}/api/users/', methods=['GET'])
def get_users():
    """Get users list"""
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Validate parameters
    if limit < 1 or limit > 100:
        return jsonify({"error": "Limit must be between 1 and 100"}), 400
    if offset < 0:
        return jsonify({"error": "Offset must be non-negative"}), 400
    
    # Get paginated users
    total = len(users_data)
    start = offset
    end = min(offset + limit, total)
    users = users_data[start:end]
    
    return jsonify({
        "users": users,
        "total": total,
        "limit": limit,
        "offset": offset
    })

@blueprint.route('/{{module_name}}/api/users/', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    # Validate required fields
    if 'name' not in data or 'email' not in data:
        return jsonify({"error": "Name and email are required"}), 400
    
    # Validate email format (basic validation)
    if '@' not in data['email']:
        return jsonify({"error": "Invalid email format"}), 400
    
    # Create new user
    new_user = {
        "id": len(users_data) + 1,
        "name": data['name'],
        "email": data['email'],
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    
    # Add age if provided
    if 'age' in data:
        if not isinstance(data['age'], int) or data['age'] < 0 or data['age'] > 120:
            return jsonify({"error": "Age must be an integer between 0 and 120"}), 400
        new_user['age'] = data['age']
    
    users_data.append(new_user)
    
    return jsonify(new_user), 201

@blueprint.route('/{{module_name}}/api/users/<int:user_id>/')
def get_user(user_id):
    """Get user by ID"""
    user = next((u for u in users_data if u['id'] == user_id), None)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(user)
