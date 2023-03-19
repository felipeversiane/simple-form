import wsgiref.simple_server
import urllib.parse
import os
import json

root = os.path.dirname(os.path.abspath(__file__))

def render_feedbacks(feedbacks):
    html = "<h1>Feedbacks:</h1>\n<ul>\n"
    for feedback in feedbacks:
        html += "<li>Name: {}<br>Email: {}<br>Feedback: {}</li>\n".format(
            feedback["name"],
            feedback["email"],
            feedback["feedback"]
        )
    html += "</ul>"
    return html

def app(environ, start_response):
    path = environ["PATH_INFO"]
    method = environ["REQUEST_METHOD"]
    data=b""
    forms_data = []

    if path == "/forms":
        feedbacks = []
        with open(os.path.join(root, "feedbacks.json"), "r") as f:
            feedbacks = json.load(f)
        html = render_feedbacks(feedbacks)
        data = html.encode("utf-8")
    if path == "/":  
        with open(os.path.join(root, "home/home.html"),"rb") as f:
            data=f.read()
    if path == "/formsucess":
        with open(os.path.join(root, "form/form-sucessfully.html"), "rb") as f:
            data = f.read()
    if path == "/feedback":
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
            feedbacks = []
            with open(os.path.join(root, "feedbacks.json"), "r") as f:
                feedbacks = json.load(f)
            feedbacks.append(req)
            with open(os.path.join(root, "feedbacks.json"), "w") as f:
                json.dump(feedbacks, f, indent=4)
            start_response("302 Found", [
                ("Location", "/formsucess"),
            ])
            return iter([])
        if method == "GET":
            with open(os.path.join(root, "form/form.html"), "rb") as f:
                data = f.read()
    elif path != "/" and path != "/feedback" and path!= "/formsucess" and path!= "/forms":
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