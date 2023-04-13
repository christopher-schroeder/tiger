from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
# from flask_socketio import SocketIO

db = SQLAlchemy()

# class Freeban(Flask):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.pages = dict()
#         self.config['SECRET_KEY'] = "123"
#         self.config['SECRET_KEY'] = 'secret'
#         self.config['SESSION_TYPE'] = 'filesystem'
#         self.config['SECRET_KEY'] = 'secret-key-goes-here'
#         self.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

#         self.wsgi_app = ReverseProxied(self.wsgi_app)

#         self.jinja_env.trim_blocks = True

#     def run(self, *args, config="", **kwargs):
#         """
#         Imports all views and then runs the Flask application.
#         """
#         import freeban.views
#         import freeban.filters as filters
#         for view in freeban.views.__all__:
#             __import__("freeban.views.%s" % view)
#         super().run(*args, **kwargs)


class ReverseProxied(object):
    """Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    :param app: the WSGI application
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get("HTTP_X_SCRIPT_NAME", "")
        if script_name:
            environ["SCRIPT_NAME"] = script_name
            path_info = environ["PATH_INFO"]
            if path_info.startswith(script_name):
                environ["PATH_INFO"] = path_info[len(script_name) :]

        scheme = environ.get("HTTP_X_SCHEME", "")
        if scheme:
            environ["wsgi.url_scheme"] = scheme
        return self.app(environ, start_response)


app = Flask(__name__, template_folder="templates", static_folder="static")
app.debug = True
app.config["SECRET_KEY"] = "secret"
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "secret-key-goes-here"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///variants.no_intergenic.sqlite"
app.wsgi_app = ReverseProxied(app.wsgi_app)
# app.jinja_env.trim_blocks = True

db.init_app(app)

Session(app)
# socketio = SocketIO(app, manage_session=False)
