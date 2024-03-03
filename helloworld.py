from flask import Flask
from markupsafe import escape
app = Flask(__name__)

# @app.route("/")
# def hello_world():
#     return "<p>Hello, World!!</p>"

# @app.route("/hello/<name>")
# def hello_name(name):
#     return f"Hello, {escape(name)}!"

# @app.route("/hello/attack")
# def hello_attack():
#     malicious = "<script>alert('bad')</script>"
#     return f'Hello, {escape(malicious)}'

# @app.route('/projects/')
# def projects():
#     return 'The project page'

# @app.route('/about')
# def about():
#     return 'The about page'

