from wsgiref import simple_server
import urllib.parse
import os
import json
import jinja2
import cgi
from orator import DatabaseManager
from orator import Model
import psycopg2



root = os.path.dirname(os.path.abspath(__file__))

def render_feedbacks(feedbacks):
    loader = jinja2.FileSystemLoader(os.path.join(root, 'form'))
    env = jinja2.Environment(loader=loader)
    template = env.get_template('forms.html')
    html = template.render(feedbacks=feedbacks)
    return html


def render_form(name="", email="", feedback="", error=""):
    with open(os.path.join(root, "form/form.html"), "rb") as f:
        data = f.read().decode("utf-8")
        data = data.replace("__name__", name)
        data = data.replace("__email__", email)
        data = data.replace("__feedback__", feedback)
        data = data.replace("__error__", error)
    return data.encode("utf-8")

def app(environ, start_response):
    path = environ["PATH_INFO"]
    method = environ["REQUEST_METHOD"]
    data = b""

    if path == "/forms":
        feedbacks = []
        with open(os.path.join(root, "feedbacks.json"), "r") as f:
            feedbacks = json.load(f)
        html = render_feedbacks(feedbacks)
        data = html.encode("utf-8")
    elif path == "/":
        with open(os.path.join(root, "home/home.html"), "rb") as f:
            data = f.read()
    elif path == "/formsucess":
        with open(os.path.join(root, "form/form-sucessfully.html"), "rb") as f:
            name = ""
            qs = urllib.parse.parse_qs(environ.get('QUERY_STRING', ''))
            if "name" in qs:
                name = qs["name"][0]
            data = f.read().replace(b"__NAME__", name.encode())
    elif path == "/feedback":
        with open(os.path.join(root, "form/form.html"), "rb") as f:
            data = f.read()
        html = ""
        if method == "POST":
            form = cgi.FieldStorage(fp=environ["wsgi.input"], environ=environ)
            req = {}
            req["name"] = form.getvalue("name", "")
            req["email"] = form.getvalue("email", "")
            req["feedback"] = form.getvalue("feedback", "")
            html = data.decode()
            if "@" in req['email']:
                feedbacks = []
                with open(os.path.join(root, "feedbacks.json"), "r") as f:
                    feedbacks = json.load(f)
                feedbacks.append(req)
                with open(os.path.join(root, "feedbacks.json"), "w") as f:
                    json.dump(feedbacks, f, indent=4)
                start_response("302 Found", [
                    ("Location", "/formsucess?name=" + req["name"]),
                ])
                return iter([])
            else : 
                html = html.replace("__name__", req['name'])
                html = html.replace("__email__", req['email'])
                html = html.replace("__feedback__", req['feedback'])
                html = html.replace("__error__", 'Email deve conter @')
                data = html.encode("utf-8")

        else:
            html = data.decode("utf-8")
            html = html.replace("__name__", "")
            html = html.replace("__email__", "")
            html = html.replace("__feedback__", "")
            html = html.replace("__error__", "")

        data = html.encode("utf-8")

         
            
    else:
        with open(os.path.join(root, "error/error404.html"), "rb") as f:
            data = f.read()

    start_response("200 OK", [
        ("Content-Type", "text/html; charset=utf-8"),
        ("Content-Length", str(len(data)))
    ])
    return [data]

if __name__ == '__main__':
    w_s = simple_server.make_server(
        host="",
        port=8000,
        app=app
    )
    w_s.serve_forever()