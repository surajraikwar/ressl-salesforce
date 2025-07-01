document.addEventListener('DOMContentLoaded', () => {
    // Use relative URL since we're serving the frontend from the same domain as the API
    const API_BASE_URL = ''; // Empty because we're using relative URLs

    const fileListUl = document.getElementById('fileList');
    const refreshFilesButton = document.getElementById('refreshFiles');

    const fileUploadInput = document.getElementById('fileUploadInput');
    const uploadFilesButton = document.getElementById('uploadFilesButton');

    const createFilenameInput = document.getElementById('createFilename');
    const createFileContentTextarea = document.getElementById('createFileContent');
    const createFileButton = document.getElementById('createFileButton');

    const currentFileNameH3 = document.getElementById('currentFileName');
    const fileContentArea = document.getElementById('fileContentArea');
    const editPromptInput = document.getElementById('editPrompt');
    const applyEditPromptButton = document.getElementById('applyEditPromptButton');
    const saveChangesButton = document.getElementById('saveChangesButton');

    const serverMessagesPre = document.getElementById('serverMessages');

    let currentEditingFile = null;

    // --- Utility Functions ---
    function logMessage(message, isError = false) {
        const timestamp = new Date().toLocaleTimeString();
        serverMessagesPre.textContent = `[${timestamp}] ${message}\n` + serverMessagesPre.textContent;
        if (isError) console.error(message); else console.log(message);
    }

    async function apiCall(endpoint, method = 'GET', body = null, isFileUpload = false) {
        const options = {
            method,
            headers: {},
            credentials: 'same-origin',  // Send cookies with the request if needed
            mode: 'same-origin',         // Ensure we're making same-origin requests
            cache: 'no-cache',           // Always fetch fresh data
            referrerPolicy: 'no-referrer' // Don't send referrer header
        };
        
        try {
            // Handle different types of requests
            if (isFileUpload) {
                // For file uploads, use FormData directly
                options.body = body;
                // Don't set Content-Type header - let the browser set it with the correct boundary
            } else if (body) {
                options.headers['Content-Type'] = 'application/json';
                options.body = JSON.stringify(body);
            }

            console.log(`Making ${method} request to ${endpoint}`, options);
            const response = await fetch(`${API_BASE_URL}/api${endpoint}`, options);
            
            // Handle response
            const contentType = response.headers.get('content-type');
            let result;
            
            if (contentType && contentType.includes('application/json')) {
                result = await response.json();
            } else {
                const text = await response.text();
                try {
                    result = text ? JSON.parse(text) : { message: text };
                } catch (e) {
                    result = { message: text };
                }
            }
            
            if (!response.ok) {
                const errorMsg = result.error || result.message || response.statusText || 'Unknown error';
                throw new Error(`HTTP ${response.status}: ${errorMsg}`);
            }
            
            console.log(`API ${endpoint} response:`, result);
            return result;
            
        } catch (error) {
            console.error(`API call to ${endpoint} failed:`, error);
            logMessage(`Error: ${error.message}`, true);
            throw error; // Re-throw to allow caller to handle
        }
    }

    // --- File Listing ---
    async function fetchAndDisplayFiles() {
        try {
            const result = await apiCall('/files/list');
            fileListUl.innerHTML = ''; // Clear existing list
            
            if (result && Array.isArray(result.files)) {
                if (result.files.length === 0) {
                    fileListUl.innerHTML = '<li>No files found.</li>';
                } else {
                    result.files.forEach(filename => {
                        const li = document.createElement('li');
                        li.textContent = filename;

                        const actionsDiv = document.createElement('div');
                        actionsDiv.className = 'file-actions';

                        const viewButton = document.createElement('button');
                        viewButton.textContent = 'View/Edit';
                        viewButton.onclick = () => loadFileForEditing(filename);
                        actionsDiv.appendChild(viewButton);

                        const deleteButton = document.createElement('button');
                        deleteButton.textContent = 'Delete';
                        deleteButton.onclick = () => deleteFile(filename);
                        actionsDiv.appendChild(deleteButton);

                        li.appendChild(actionsDiv);
                        fileListUl.appendChild(li);
                    });
                }
            } else {
                throw new Error('Invalid response format from server');
            }
        } catch (error) {
            console.error('Error fetching files:', error);
            fileListUl.innerHTML = '<li>Error loading files. Check console for details.</li>';
        }
    }

    // --- File Creation/Upload ---
    createFileButton.addEventListener('click', async () => {
        const filename = createFilenameInput.value.trim();
        const content = createFileContentTextarea.value;
        if (!filename) {
            logMessage('Filename cannot be empty for creation.', true);
            return;
        }
        const result = await apiCall('/files/create', 'POST', { filename, content });
        if (result) {
            createFilenameInput.value = '';
            createFileContentTextarea.value = '';
            fetchAndDisplayFiles();
        }
    });

    uploadFilesButton.addEventListener('click', async () => {
        const files = fileUploadInput.files;
        if (files.length === 0) {
            logMessage('No files selected for upload.', true);
            return;
        }

        for (const file of files) {
            const reader = new FileReader();
            reader.onload = async (e) => {
                const content = e.target.result;
                const result = await apiCall('/files/create', 'POST', { filename: file.name, content });
                if (result) {
                    fetchAndDisplayFiles(); // Refresh list after each successful upload
                }
            };
            reader.onerror = () => {
                logMessage(`Error reading file ${file.name}`, true);
            };
            reader.readAsText(file); // Assuming text files
        }
        fileUploadInput.value = ''; // Clear the input
    });


    // --- File Viewing/Editing ---
    async function loadFileForEditing(filename) {
        const result = await apiCall(`/files/view?filename=${encodeURIComponent(filename)}`);
        if (result && result.content !== undefined) {
            currentEditingFile = filename;
            currentFileNameH3.textContent = `Editing: ${filename}`;
            fileContentArea.value = result.content;
            editPromptInput.value = '';
            saveChangesButton.disabled = false;
        } else {
            currentEditingFile = null;
            currentFileNameH3.textContent = 'No file selected';
            fileContentArea.value = '';
            saveChangesButton.disabled = true;
            logMessage(`Failed to load file: ${filename}`, true);
        }
    }

    applyEditPromptButton.addEventListener('click', () => {
        if (!currentEditingFile) {
            logMessage('No file loaded to apply edits to.', true);
            return;
        }
        const prompt = editPromptInput.value.trim();
        const currentContent = fileContentArea.value;

        // Basic "REPLACE 'old' WITH 'new'" parser
        const match = prompt.match(/^REPLACE\s+'(.*?)'\s+WITH\s+'(.*?)'$/i);
        if (match) {
            const oldText = match[1];
            const newText = match[2];
            if (oldText) { // oldText can be empty string
                fileContentArea.value = currentContent.split(oldText).join(newText);
                logMessage(`Applied: REPLACE '${oldText}' WITH '${newText}' (client-side). Save changes to persist.`);
            } else {
                logMessage("Invalid REPLACE format in prompt: 'old text' cannot be empty if specified like that. For replacing everything, just paste new content.", true);
            }
        } else {
            logMessage("Invalid prompt format. Use: REPLACE 'text to find' WITH 'replacement text'", true);
        }
    });

    saveChangesButton.addEventListener('click', async () => {
        if (!currentEditingFile) {
            logMessage('No file selected to save.', true);
            return;
        }
        const newContent = fileContentArea.value;
        const result = await apiCall('/files/edit', 'PUT', { filename: currentEditingFile, content: newContent });
        if (result) {
            logMessage(`File ${currentEditingFile} saved successfully.`);
            // Optionally, could clear the editing area or reload, but for now just a message.
        }
    });

    // --- File Deletion ---
    async function deleteFile(filename) {
        if (!confirm(`Are you sure you want to delete ${filename}?`)) {
            return;
        }
        const result = await apiCall('/files/delete', 'DELETE', { filename });
        if (result) {
            logMessage(`File ${filename} deleted successfully.`);
            if (currentEditingFile === filename) { // Clear editing area if deleted file was being edited
                currentEditingFile = null;
                currentFileNameH3.textContent = 'No file selected';
                fileContentArea.value = '';
                editPromptInput.value = '';
                saveChangesButton.disabled = true;
            }
            fetchAndDisplayFiles();
        }
    }

    // --- Initial Load ---
    refreshFilesButton.addEventListener('click', fetchAndDisplayFiles);
    fetchAndDisplayFiles(); // Load files on page startup
});
