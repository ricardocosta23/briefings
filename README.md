# PDF File Sharing Application (Python Flask)

A simple, serverless web application for uploading and sharing PDF files, built with Python Flask and designed for Vercel deployment.

## Features

- **PDF Upload**: Drag-and-drop or click to upload PDF files (max 10MB)
- **Permanent Storage**: Files stored permanently in SQLite database as base64
- **Shareable Links**: Generate direct browser links for PDF viewing
- **File Management**: View, copy links, and delete uploaded files
- **Serverless Ready**: Optimized for Vercel deployment

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite with base64 file storage
- **Frontend**: Pure HTML/CSS/JavaScript with Tailwind CSS
- **Deployment**: Vercel serverless functions

## Local Development

1. Ensure Python is installed
2. Install dependencies:
   ```bash
   pip install Flask Werkzeug
   ```
3. Run the application:
   ```bash
   cd api
   python index.py
   ```
4. Open http://localhost:8080

## Vercel Deployment

### Quick Deploy

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Deploy:
   ```bash
   vercel --prod
   ```

### Manual Setup

1. Create account at [vercel.com](https://vercel.com)
2. Connect your GitHub repository
3. Deploy with these settings:
   - Framework Preset: Other
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
   - Install Command: pip install Flask Werkzeug

### Environment Variables

No environment variables required! The application uses SQLite with in-memory storage that's perfect for serverless environments.

## File Storage

- **Method**: Base64-encoded data stored in SQLite database
- **Benefits**: 
  - No external storage dependencies
  - Perfect for serverless environments
  - Files persist in database
  - No file system access needed

## API Endpoints

- `GET /` - Main application interface
- `POST /api/upload` - Upload PDF files
- `GET /api/files` - List all uploaded files
- `GET /api/files/view/<filename>` - View/download PDF files
- `DELETE /api/files/<id>` - Delete uploaded files

## Usage

1. **Upload**: Drag PDF files to upload area or click to browse
2. **Share**: Copy the generated shareable link
3. **View**: Click "Open PDF" to view in browser
4. **Manage**: Delete files when no longer needed

## File Limits

- **File Type**: PDF only
- **File Size**: Maximum 10MB
- **Storage**: Unlimited files (within database limits)

## Browser Compatibility

- All modern browsers
- Direct PDF viewing
- Mobile responsive design

## Security

- File type validation (PDF only)
- File size limits
- Secure filename generation
- Base64 encoding for safe storage

## Troubleshooting

### Deployment Issues
- Ensure `vercel.json` is configured correctly
- Check Python dependencies in requirements
- Verify Flask version compatibility

### Local Development
- Use Python 3.8 or higher
- Install Flask and Werkzeug
- Check port 8080 availability

## Support

For issues or questions, check the Vercel deployment logs or contact support.