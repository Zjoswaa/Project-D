import requests
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from chadbot_sigma_v1 import NDWDocBot

class Chatbot_Server(BaseHTTPRequestHandler):

    bot = NDWDocBot()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            data = json.loads(post_data)
            print("Received JSON data:", data)

            query_response = self.bot.get_response(data.get("Prompt", "")),

            response = {
                "status": "success",
                "message": "Data received",
                "response": query_response
            }
            self.send_response(200)

        except Exception as e:
            print("Invalid JSON received.")
            response = {
                "status": "error",
                "message": "Invalid JSON"
            }
            self.send_response(400)

        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

if __name__ == "__main__":
    server = HTTPServer(("localhost", 8080), Chatbot_Server)
    print("Server running on http://localhost:8080")
    server.serve_forever()