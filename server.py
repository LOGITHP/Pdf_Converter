import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 8000
Handler = http.server.SimpleHTTPRequestHandler

class MyHTTPRequestHandler(Handler):
    # Enable caching prevention for easier local development
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def run_server():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Try multiple ports if 8000 is occupied
    port = PORT
    server_started = False
    
    while not server_started and port < 8010:
        try:
            with socketserver.TCPServer(("", port), MyHTTPRequestHandler) as httpd:
                print(f"===========================================================")
                print(f" AeroPDF Converter Server running at: http://localhost:{port}")
                print(f" Press Ctrl+C to stop the server.")
                print(f"===========================================================")
                
                # Auto-open browser
                webbrowser.open(f"http://localhost:{port}")
                
                server_started = True
                httpd.serve_forever()
        except OSError as e:
            if e.errno == 98 or e.errno == 10048: # Address already in use
                print(f"Port {port} is busy, trying port {port + 1}...")
                port += 1
            else:
                print(f"Error starting server: {e}")
                sys.exit(1)
        except KeyboardInterrupt:
            print("\nStopping AeroPDF server. Goodbye!")
            sys.exit(0)

if __name__ == "__main__":
    run_server()
