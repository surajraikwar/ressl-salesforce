import os
import shutil
from flask import Flask, request, jsonify, send_from_directory, send_file
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin

# Get the absolute path to the project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CLIENT_FOLDER = os.path.join(PROJECT_ROOT, 'mcp_client')

app = Flask(__name__, static_folder=CLIENT_FOLDER)

# Configure CORS
cors = CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5001", "http://127.0.0.1:5001"],
        "supports_credentials": True,
        "allow_headers": ["Content-Type", "Authorization"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    }
})

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mcp_uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    print(f"Created upload directory at: {UPLOAD_FOLDER}")

def is_filename_safe(filename):
    """Checks if a filename is safe and doesn't try to escape the UPLOAD_FOLDER."""
    if ".." in filename or filename.startswith("/"):
        return False
    return True

@app.route('/api/files/create', methods=['POST'])
def create_file():
    data = request.get_json()
    if not data or 'filename' not in data or 'content' not in data:
        return jsonify({"error": "Missing filename or content"}), 400

    filename = secure_filename(data['filename'])
    if not is_filename_safe(filename):
        return jsonify({"error": "Invalid filename"}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if os.path.exists(filepath):
        return jsonify({"error": f"File '{filename}' already exists"}), 409

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(data['content'])
        return jsonify({"message": f"File '{filename}' created successfully", "filename": filename}), 201
    except Exception as e:
        return jsonify({"error": f"Error creating file: {str(e)}"}), 500

@app.route('/api/files/edit', methods=['PUT'])
def edit_file():
    data = request.get_json()
    if not data or 'filename' not in data or 'content' not in data:
        return jsonify({"error": "Missing filename or content"}), 400

    filename = secure_filename(data['filename'])
    if not is_filename_safe(filename):
        return jsonify({"error": "Invalid filename"}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if not os.path.exists(filepath):
        return jsonify({"error": f"File '{filename}' not found"}), 404

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(data['content'])
        return jsonify({"message": f"File '{filename}' updated successfully", "filename": filename}), 200
    except Exception as e:
        return jsonify({"error": f"Error updating file: {str(e)}"}), 500

@app.route('/api/files/delete', methods=['DELETE'])
def delete_file():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Missing filename"}), 400

    filename = secure_filename(data['filename'])
    if not is_filename_safe(filename):
        return jsonify({"error": "Invalid filename"}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if not os.path.exists(filepath):
        return jsonify({"error": f"File '{filename}' not found"}), 404

    try:
        os.remove(filepath)
        return jsonify({"message": f"File '{filename}' deleted successfully", "filename": filename}), 200
    except Exception as e:
        return jsonify({"error": f"Error deleting file: {str(e)}"}), 500

@app.route('/api/files/list', methods=['GET'])
def list_files():
    try:
        files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))]
        return jsonify({"files": files}), 200
    except Exception as e:
        return jsonify({"error": f"Error listing files: {str(e)}"}), 500

@app.route('/api/files/view', methods=['GET'])
def view_file():
    filename_param = request.args.get('filename')
    if not filename_param:
        return jsonify({"error": "Missing filename query parameter"}), 400

    filename = secure_filename(filename_param)
    if not is_filename_safe(filename):
        return jsonify({"error": "Invalid filename"}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if not os.path.exists(filepath):
        return jsonify({"error": f"File '{filename}' not found"}), 404

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({"filename": filename, "content": content}), 200
    except Exception as e:
        return jsonify({"error": f"Error viewing file: {str(e)}"}), 500

# Serve the main page and static files
@app.route('/')
def serve_frontend():
    return send_file(os.path.join(CLIENT_FOLDER, 'index.html'))

# Serve static files from the client directory
@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(CLIENT_FOLDER, path)):
        return send_from_directory(CLIENT_FOLDER, path)
    return 'Not Found', 404

# API Routes
@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy", "message": "MCP Server is running"}), 200

if __name__ == '__main__':
    # Ensure the upload folder exists
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), UPLOAD_FOLDER)
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    print(f"Serving static files from: {CLIENT_FOLDER}")
    print(f"Upload directory: {upload_dir}")
    
    # Run the Flask app
    app.run(debug=True, port=5001, host='0.0.0.0')
