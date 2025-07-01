import os
import shutil
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'mcp_uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def is_filename_safe(filename):
    """Checks if a filename is safe and doesn't try to escape the UPLOAD_FOLDER."""
    if ".." in filename or filename.startswith("/"):
        return False
    return True

@app.route('/files/create', methods=['POST'])
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

@app.route('/files/edit', methods=['PUT'])
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

@app.route('/files/delete', methods=['DELETE'])
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

@app.route('/files/list', methods=['GET'])
def list_files():
    try:
        files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))]
        return jsonify({"files": files}), 200
    except Exception as e:
        return jsonify({"error": f"Error listing files: {str(e)}"}), 500

@app.route('/files/view', methods=['GET'])
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

if __name__ == '__main__':
    # For development, it's often useful to enable debug mode.
    # For a more production-like environment, you'd use a WSGI server like Gunicorn.
    app.run(debug=True, port=5001)
