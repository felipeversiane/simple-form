import wsgiref.simple_server
import urllib.parse
import os
def app(environ, start_response):
    path = environ["PATH_INFO"]
    method = environ["REQUEST_METHOD"]
    data=b""
    forms_data = []
    if path == "/":
        # data = b"Hello, Web!\n"
        Root = os.path.dirname(os.path.abspath(__file__))    
        f = open(Root + 'index.html')
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
                "message" : params.get('message', [''])[0]
            }
            forms_data.append(req)
            data = b"Your feedback submitted successfully."
        if method == "GET":
             data = b"A HTML SITE HERE"
    else :
        data = b" A ERROR 404 MESSAGE SITE HERE"
            
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
