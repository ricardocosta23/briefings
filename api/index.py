from flask import Flask, request, jsonify, send_file, render_template_string
import os
import base64
import json
from datetime import datetime
import tempfile
import io
from werkzeug.utils import secure_filename
import sqlite3
from contextlib import contextmanager

app = Flask(__name__)

# Database setup
DATABASE_PATH = '/tmp/app.db'

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uploaded_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_name TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            mime_type TEXT NOT NULL,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_data TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

@contextmanager
def get_db():
    """Database context manager"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def allowed_file(filename):
    """Check if file is a PDF"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

def generate_filename(original_name):
    """Generate unique filename with timestamp"""
    timestamp = str(int(datetime.now().timestamp() * 1000))
    safe_name = secure_filename(original_name)
    name_without_ext = safe_name.rsplit('.', 1)[0] if '.' in safe_name else safe_name
    return f"{timestamp}_{name_without_ext}.pdf"

# Initialize database when module loads
init_db()

@app.route('/')
def index():
    """Serve the main application"""
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF File Sharing</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
    <style>
        .drag-over { background-color: #e0f2fe !important; border-color: #0ea5e9 !important; }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <div class="container mx-auto px-4 py-8 max-w-4xl">
        <h1 class="text-3xl font-bold text-gray-900 mb-8 text-center">PDF File Sharing</h1>
        
        <!-- Upload Area -->
        <div id="upload-area" class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center bg-white mb-8 cursor-pointer hover:border-blue-400 transition-colors">
            <div class="mb-4">
                <i data-lucide="upload" class="w-12 h-12 text-gray-400 mx-auto mb-4"></i>
                <p class="text-lg text-gray-600 mb-2">Drop PDF files here or click to browse</p>
                <p class="text-sm text-gray-500">Maximum file size: 10MB</p>
            </div>
            <input type="file" id="file-input" accept=".pdf" class="hidden">
        </div>

        <!-- Upload Progress -->
        <div id="upload-progress" class="hidden mb-6">
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div class="flex items-center mb-2">
                    <i data-lucide="loader-2" class="w-5 h-5 text-blue-600 animate-spin mr-2"></i>
                    <span class="text-blue-800 font-medium">Uploading...</span>
                </div>
                <div class="w-full bg-blue-200 rounded-full h-2">
                    <div id="progress-bar" class="bg-blue-600 h-2 rounded-full transition-all duration-300" style="width: 0%"></div>
                </div>
            </div>
        </div>

        <!-- Files List -->
        <div class="bg-white rounded-lg shadow-sm border">
            <div class="p-6 border-b">
                <h2 class="text-xl font-semibold text-gray-900">Recent Uploads</h2>
            </div>
            <div id="files-list" class="divide-y divide-gray-200">
                <div id="no-files" class="p-8 text-center text-gray-500">
                    <i data-lucide="file-text" class="w-12 h-12 text-gray-300 mx-auto mb-4"></i>
                    <p>No files uploaded yet</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Toast Container -->
    <div id="toast-container" class="fixed top-4 right-4 z-50"></div>

    <script>
        // Initialize Lucide icons
        lucide.createIcons();

        const uploadArea = document.getElementById('upload-area');
        const fileInput = document.getElementById('file-input');
        const uploadProgress = document.getElementById('upload-progress');
        const progressBar = document.getElementById('progress-bar');
        const filesList = document.getElementById('files-list');
        const noFiles = document.getElementById('no-files');

        // Upload area click handler
        uploadArea.addEventListener('click', () => fileInput.click());

        // Drag and drop handlers
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            const files = e.dataTransfer.files;
            if (files.length > 0) handleFileUpload(files[0]);
        });

        // File input change handler
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) handleFileUpload(e.target.files[0]);
        });

        // Upload file function
        async function handleFileUpload(file) {
            if (file.type !== 'application/pdf') {
                showToast('Please select a PDF file', 'error');
                return;
            }

            if (file.size > 10 * 1024 * 1024) {
                showToast('File size must be less than 10MB', 'error');
                return;
            }

            const formData = new FormData();
            formData.append('file', file);

            uploadProgress.classList.remove('hidden');
            progressBar.style.width = '10%';

            try {
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });

                progressBar.style.width = '90%';

                if (response.ok) {
                    const result = await response.json();
                    progressBar.style.width = '100%';
                    showToast('File uploaded successfully!', 'success');
                    setTimeout(() => {
                        uploadProgress.classList.add('hidden');
                        progressBar.style.width = '0%';
                    }, 1000);
                    loadFiles();
                } else {
                    throw new Error('Upload failed');
                }
            } catch (error) {
                uploadProgress.classList.add('hidden');
                progressBar.style.width = '0%';
                showToast('Upload failed. Please try again.', 'error');
            }
        }

        // Load files function
        async function loadFiles() {
            try {
                const response = await fetch('/api/files');
                const files = await response.json();
                
                if (files.length === 0) {
                    noFiles.style.display = 'block';
                    return;
                }

                noFiles.style.display = 'none';
                
                filesList.innerHTML = files.map(file => `
                    <div class="p-6">
                        <div class="flex items-start justify-between">
                            <div class="flex items-start space-x-4">
                                <div class="flex-shrink-0 p-2 bg-red-50 rounded-lg">
                                    <i data-lucide="file-text" class="w-6 h-6 text-red-600"></i>
                                </div>
                                <div class="flex-1 min-w-0">
                                    <h4 class="font-medium text-gray-900 truncate">${file.original_name}</h4>
                                    <p class="text-sm text-gray-500 mt-1">
                                        Uploaded ${formatUploadTime(file.upload_time)} • ${formatFileSize(file.file_size)}
                                    </p>
                                    <div class="mt-3 p-3 bg-gray-50 rounded border">
                                        <p class="text-sm text-gray-600 mb-2">Shareable Link:</p>
                                        <div class="flex items-center space-x-2">
                                            <input type="text" value="${window.location.origin}/api/files/view/${file.file_name}" readonly 
                                                   class="flex-1 px-3 py-1 text-sm border rounded bg-white text-gray-700">
                                            <button onclick="copyLink('${window.location.origin}/api/files/view/${file.file_name}')" 
                                                    class="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700">
                                                Copy
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="flex space-x-2 ml-4">
                                <button onclick="openPDF('${window.location.origin}/api/files/view/${file.file_name}')" 
                                        class="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700">
                                    Open PDF
                                </button>
                                <button onclick="deleteFile(${file.id})" 
                                        class="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700">
                                    Delete
                                </button>
                            </div>
                        </div>
                    </div>
                `).join('');
                
                lucide.createIcons();
            } catch (error) {
                showToast('Failed to load files', 'error');
            }
        }

        // Utility functions
        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }

        function formatUploadTime(dateString) {
            const date = new Date(dateString);
            const now = new Date();
            const diffMs = now.getTime() - date.getTime();
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMins / 60);
            const diffDays = Math.floor(diffHours / 24);

            if (diffMins < 1) return 'just now';
            if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
            if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
            return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
        }

        function copyLink(url) {
            navigator.clipboard.writeText(url).then(() => {
                showToast('Link copied to clipboard!', 'success');
            });
        }

        function openPDF(url) {
            window.open(url, '_blank');
        }

        async function deleteFile(id) {
            if (!confirm('Are you sure you want to delete this file?')) return;
            
            try {
                const response = await fetch(`/api/files/${id}`, { method: 'DELETE' });
                if (response.ok) {
                    showToast('File deleted successfully', 'success');
                    loadFiles();
                } else {
                    throw new Error('Delete failed');
                }
            } catch (error) {
                showToast('Failed to delete file', 'error');
            }
        }

        function showToast(message, type = 'info') {
            const toast = document.createElement('div');
            toast.className = `mb-4 p-4 rounded-lg shadow-lg max-w-sm ${
                type === 'success' ? 'bg-green-100 border border-green-400 text-green-700' :
                type === 'error' ? 'bg-red-100 border border-red-400 text-red-700' :
                'bg-blue-100 border border-blue-400 text-blue-700'
            }`;
            toast.textContent = message;
            
            document.getElementById('toast-container').appendChild(toast);
            
            setTimeout(() => {
                toast.remove();
            }, 3000);
        }

        // Load files on page load
        loadFiles();
    </script>
</body>
</html>
    ''')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF files are allowed'}), 400
    
    try:
        # Read file content
        file_content = file.read()
        if len(file_content) > 10 * 1024 * 1024:  # 10MB limit
            return jsonify({'error': 'File too large'}), 400
        
        # Encode file as base64
        file_data = base64.b64encode(file_content).decode('utf-8')
        
        # Generate filename
        generated_filename = generate_filename(file.filename)
        
        # Store in database
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO uploaded_files (original_name, file_name, file_size, mime_type, file_data)
                VALUES (?, ?, ?, ?, ?)
            ''', (file.filename, generated_filename, len(file_content), file.content_type, file_data))
            conn.commit()
            file_id = cursor.lastrowid
        
        return jsonify({
            'id': file_id,
            'original_name': file.filename,
            'file_name': generated_filename,
            'file_size': len(file_content),
            'url': f'/api/files/view/{generated_filename}'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files', methods=['GET'])
def get_files():
    """Get all uploaded files"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, original_name, file_name, file_size, mime_type, upload_time
                FROM uploaded_files ORDER BY upload_time DESC
            ''')
            
            files = []
            for row in cursor.fetchall():
                files.append({
                    'id': row['id'],
                    'original_name': row['original_name'],
                    'file_name': row['file_name'],
                    'file_size': row['file_size'],
                    'mime_type': row['mime_type'],
                    'upload_time': row['upload_time']
                })
            
            return jsonify(files)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/view/<filename>')
def view_file(filename):
    """Serve PDF file for viewing"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT original_name, file_data, mime_type
                FROM uploaded_files WHERE file_name = ?
            ''', (filename,))
            
            row = cursor.fetchone()
            if not row:
                return jsonify({'error': 'File not found'}), 404
            
            # Decode base64 file data
            file_content = base64.b64decode(row['file_data'])
            
            # Create file-like object
            file_obj = io.BytesIO(file_content)
            
            return send_file(
                file_obj,
                mimetype=row['mime_type'],
                as_attachment=False,
                download_name=row['original_name']
            )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Delete a file"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM uploaded_files WHERE id = ?', (file_id,))
            
            if cursor.rowcount == 0:
                return jsonify({'error': 'File not found'}), 404
            
            conn.commit()
            return jsonify({'message': 'File deleted successfully'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Vercel serverless function handler
if __name__ == '__main__':
    app.run(debug=True, port=8080)