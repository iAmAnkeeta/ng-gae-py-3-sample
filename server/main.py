from services.autoload import activate_virtual_env
activate_virtual_env()

import os
from flask import Flask, render_template, request, redirect, url_for, session
from services.config import FLASK_APP_SECRET

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.

# Flask default location for template if template folder
# app = Flask(__name__)

# If needs to render template from different location
abs_path = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(abs_path, "dist")
app = Flask(__name__, template_folder=template_dir, static_folder=template_dir)
app.secret_key = FLASK_APP_SECRET



@app.route('/', defaults={'path': ''}, methods=["GET"])
@app.route('/<path:path>', methods=["GET"])
def index(path: str):
    """
    Catch the default route to the app and any other Angular route
    :param path: {path} the url path
    :return: App rendered template
    """
    return render_template("/index.html")


if __name__ == "__main__":
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    # Run `python3 main.py`
    app.run(host='127.0.0.1', port=8080, debug=True)