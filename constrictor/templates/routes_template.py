from flask import Blueprint, render_template

blueprint = Blueprint('{{module_name}}', __name__)

@blueprint.route('/{{module_name}}/')
def index():
    return render_template('{{module_name}}/index.html', module_name='{{module_name}}')

@blueprint.route('/{{module_name}}/hello/')
def hello():
    return "Hello from {{module_name}} module!"

@blueprint.route('/{{module_name}}/api/')
def api():
    return {"module": "{{module_name}}", "status": "active"}
