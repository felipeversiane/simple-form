import wsgiref.simple_server
import urllib.parse
import os
import json
import jinja2


root = os.path.dirname(os.path.abspath(__file__))

def render_feedbacks(feedbacks):
    loader = jinja2.FileSystemLoader(os.path.join(root, 'form'))
    env = jinja2.Environment(loader=loader)
    template = env.get_template('forms.html')
    html = template.render(feedbacks=feedbacks)
    return html

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
        if method == "POST":
            input_obj = environ["wsgi.input"]
            input_length = int(environ["CONTENT_LENGTH"])
            body = input_obj.read(input_length).decode('utf-8')
            params = urllib.parse.parse_qs(body, keep_blank_values=True)
            req = { 
                "name" : params.get('name', [''])[0],
                "email" : params.get('email', [''])[0],
                "feedback" : params.get('feedback', [''])[0]
            }
            if "@" not in req['email']:
                start_response("400 Bad Request", [("Content-Type", "text/html; charset=utf-8")])
                return iter([b"Failure"]) 
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
        elif method == "GET":
            with open(os.path.join(root, "form/form.html"), "rb") as f:
                data = f.read()
    else:
        with open(os.path.join(root, "error/error404.html"), "rb") as f:
            data = f.read()
    start_response("200 OK", [
        ("Content-Type", "text/html; charset=utf-8"),
        ("Content-Length", str(len(data)))
    ])
    return iter([data])

if __name__ == '__main__':
    w_s = wsgiref.simple_server.make_server(
        host="",
        port=8000,
        app=app
    )
    w_s.serve_forever()