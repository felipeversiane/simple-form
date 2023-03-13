import wsgiref.simple_server
import urllib.parse
import os

root = os.path.dirname(os.path.abspath(__file__))

def app(environ, start_response):
    path = environ["PATH_INFO"]
    method = environ["REQUEST_METHOD"]
    data=b""
    forms_data = []


    if path == "/":  
        data=b"a HOME HTML HERE"
    if path == "/feedback":
        if method == "POST":
            input_obj = environ["wsgi.input"]
            input_length = int(environ["CONTENT_LENGTH"])
            body = input_obj.read(input_length).decode('utf-8')
            params = urllib.parse.parse_qs(body, keep_blank_values=True)
            req = { 
                "name" : params.get('name', [''])[0],
                "email" : params.get('email', [''])[0],
                "message" : params.get('message', [''])[0]
            }
            forms_data.append(req)
            data = b"Your feedback submitted successfully."
        if method == "GET":
            data= b"a form HERE"
    elif path != "/" and path!= "/feedback":
        data = b"a 404 ERROR PAGE HERE"
            
    start_response("200 OK", [
        ("Content-Type", "text/plain"),
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