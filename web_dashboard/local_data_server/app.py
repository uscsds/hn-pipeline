from flask import Flask, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/example_data/<path:filename>')
def serve_file(filename):
    return send_from_directory('example_data', filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
