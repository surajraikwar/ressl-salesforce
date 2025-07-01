# MCP (Managed Content Platform)

A web-based file management system with a Flask backend and a simple HTML/JavaScript frontend.

## Prerequisites

- Python 3.7+
- Flask
- Modern web browser

## Setup and Installation

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ressl-salesforce/mcp_server
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt  # If you have a requirements file
   ```

3. **Run the MCP Server**
   ```bash
   python app.py
   ```

4. **Verify the server is running**
   - The server will start on `http://127.0.0.1:5001` by default
   - The `mcp_uploads` directory will be automatically created if it doesn't exist

### Frontend Setup

1. **Open the client interface**
   - Navigate to `mcp_project/mcp_client/index.html`
   - You can open it by:
     - Dragging the file into a web browser
     - Using `File -> Open File...` in your browser
     - Or using a local web server

## Features

### File Management
- **List Files**: View all managed files
- **Create Files**: Create new text files with custom content
- **Upload Files**: Upload multiple files at once
- **View/Edit**: View and modify file contents directly
- **Delete Files**: Remove files from the system

### Advanced Editing
- **Text Replacement**: Use commands to perform find-and-replace operations
- **Real-time Preview**: See changes before saving
- **Server Feedback**: Get immediate feedback on all operations

## Usage Guide

### Basic Operations

1. **Viewing Files**
   - Click "Refresh File List" to see all available files
   - Click "View/Edit" next to any file to view or modify its contents

2. **Creating Files**
   - Enter a filename (e.g., `example.txt`)
   - Add your content in the text area
   - Click "Create File" to save

3. **Uploading Files**
   - Click "Choose Files" and select one or more files
   - Click "Upload Selected Files" to add them to the system

### Advanced Features

#### Editing Files
1. Load a file using "View/Edit"
2. Make changes in the text area
3. Click "Save Changes to Server" to update

#### Using Edit Commands
1. Load a file using "View/Edit"
2. Enter a command in the "Edit via Prompt" field, for example:
   ```
   REPLACE 'old text' WITH 'new text'
   ```
3. Click "Apply Prompt to Content" to preview changes
4. Click "Save Changes to Server" to confirm

## Troubleshooting

- **Server Not Starting**: Ensure port 5001 is available and no other service is using it
- **File Upload Issues**: Check browser console for JavaScript errors
- **Changes Not Saving**: Verify the `mcp_uploads` directory has write permissions

## License

[Specify your license here]

## Contributing

[Add contribution guidelines if applicable]
